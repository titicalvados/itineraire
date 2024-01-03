import json, os 
from bson import json_util
from fnmatch import fnmatch
from pymongo import MongoClient
from neo4j import GraphDatabase
from time import time
from flask import Flask, jsonify
from bson.json_util import dumps
from pydantic import BaseModel
from flask_pydantic import validate


client = MongoClient(host="127.0.0.1", port = 27017)
datatourisme = client["datatourisme"]
collection_poi = datatourisme.get_collection(name="poi")

#get POIs from mongo
nb_poi = collection_poi.count_documents({})
print("Nombre de POIs: ",nb_poi)

#neo4j driver
driver_neo4j = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))

allowedTypes = ["AccommodationProduct","Visit","Rental","Store","Accommodation","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","CampingAndCaravanning","ReligiousSite","NaturalHeritage","TouristInformationCenter"]

class Query(BaseModel):
    type:str
    maxdistance:int
    mindistance:int

app = Flask(__name__)

#Endpoint pour créer les relations dans neo4j
@app.route('/createrelations', methods=['GET'])
@validate()
def relations_neo4j(query:Query):
    t0 = time()
    userSelectedType = []
    userSelectedType.append(query.type)
    orArray=[]
    for type in userSelectedType:
        orArray.append({'types' : type})
    pois_count = collection_poi.aggregate([{'$match': { 'types' : {'$in':userSelectedType}}},{'$project': { 'identifier': '$dc:identifier','longitude':'$longitude','latitude':'$latitude'}}])
    cursorPoiList = [p for p in pois_count]
    print("Nombre de POIs in selected types: ",len(cursorPoiList))
    pois = collection_poi.aggregate([{'$match': { 'types' : {'$in':userSelectedType}}},{'$project': { 'identifier': '$dc:identifier','longitude':'$longitude','latitude':'$latitude'}}])
    #clean neo4j relations
    query_delete_relations = '''
    CALL apoc.periodic.iterate(
        'MATCH ()-[r:NEIGHBOUR]-() RETURN r',
        'DELETE r',
        {batchSize:500000}
    )
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query_delete_relations).data()
        except:
            print("Can't delete relations")
    session.close()
    td = time() - t0
    print("Suppression réalisée en {} secondes".format(round(td,3)))

    treatedPOIs=[]

    #retrieve neighbours for all nodes and create relation with distance weight 
    neighbourhoodDistance = query.maxdistance*1000
    minDistance = query.mindistance*1000
    print("considéré comme voisin (en m) si moins de :",neighbourhoodDistance)
    for row in pois:
        treatedPOIs.append(row["identifier"])
        #affichage du progrès et du temps de mise à jour tous les 1000 POIs
        if len(treatedPOIs) % 100 == 0:
            ti = time() - t0
            print("{} POIs traités en {} secondes".format(len(treatedPOIs),round(ti,3)))
        #filtrage sur les erreurs latitude longitude hors France métropolaine
        if not (51.10>= float(row["latitude"])>=41.30) or not (9.57>= float(row["longitude"]) >=-5.17):
            continue
        neighbours = collection_poi.aggregate([{'$geoNear': {'near': { 'coordinates': [float(row["longitude"]) , float(row["latitude"])] },'distanceField': 'distance','minDistance':minDistance,'maxDistance': neighbourhoodDistance,'query': { '$or': orArray}}},{'$project': { 'identifier': '$dc:identifier','distance':'$distance'}}])
        for neighbour in neighbours:
            if neighbour["identifier"] in treatedPOIs:
                continue
            #create neighbour relationship
            with driver_neo4j.session() as session:
                query = '''
                MATCH (p:POI) where p.id = $row_id
                MATCH (q:POI) where q.id = $neighbour_identifier
                MERGE (p)-[r:NEIGHBOUR]->(q)
                SET r.distance = $distance
                '''
                result = session.run(query, row_id=row["identifier"],neighbour_identifier=neighbour["identifier"],distance = neighbour["distance"]).data()

    #----------------------------------------------------------
    # neo4j graph deletion and initialization for itineray calculation with Djikstra algo
    query_drop_graph = '''
    CALL gds.graph.drop(
        'myGraph'
    )
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query_drop_graph).data()
        except:
            print("Graph with name myGraph does not exist on database neo4j")

    query_init_graph = '''
    CALL gds.graph.project(
        'myGraph',
        'POI',
        {
            NEIGHBOUR: {
                type: 'NEIGHBOUR',
                orientation: 'UNDIRECTED'
            }
        },
        {
            relationshipProperties: 'distance'
        }
    )
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query_init_graph).data()
        except:
            print("Can't init Graph with name myGraph")

    session.close()
    tt = time() - t0
    status = 'Relations neo4j et graph construits en {} secondes'.format(round(tt,3)) 
    return jsonify({'status': status})

#Endpoint pour ajouter les pois dans neo4j
@app.route('/loadinneo4j', methods=['GET'])
def load_neo4j():
    t0 = time()
    pois = collection_poi.aggregate([{'$project': { 'identifier': '$dc:identifier','label': '$label','types': '$types','locality': '$addressLocality','postalCode':'$postalCode','latitude':'$latitude','longitude':'$longitude'}}])
    #clean neo4j database
    query_delete_nodes = '''
    CALL apoc.periodic.iterate(
        'MATCH (n) RETURN n',
        'DETACH DELETE n',
        {batchSize:5000}
    )
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query_delete_nodes).data()
        except:
            print("Can't delete nodes")
    session.close()
    td = time() - t0
    print("Suppression réalisée en {} secondes".format(round(td,3)))

    query2 = '''
    CREATE INDEX FOR (var:POI) on var.id
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query2).data()
        except:
            print("index already exists")
    session.close()

    with driver_neo4j.session() as session:
        #insert poi by poi
        for row in pois:
            id = row["identifier"]
            label = row["label"]
            #filtrage sur les erreurs latitude longitude hors France métropolaine
            if (51.10>= float(row["latitude"])>=41.30) and (9.57>= float(row["longitude"]) >=-5.17):
                latitude = float(row["latitude"])
                longitude = float(row["longitude"])
            else:
                continue
            originalTypes = row["types"]
            insertedTypes = []
            for type in originalTypes:
                if type in allowedTypes:
                    if (type == "AccommodationProduct") and ("Accommodation" not in insertedTypes):
                        insertedTypes.append("Accommodation")
                    elif (type == "Accommodation") and ("Accommodation" not in insertedTypes):
                        insertedTypes.append("Accommodation")
                    else:
                        insertedTypes.append(type)
            locality = row["locality"]
            postalCode = row["postalCode"]
            query1 = '''
            CREATE (:POI {id: $i,
            label: $lab,
            types: $t,
            locality: $l,
            postalCode: $p,
            longitude: $lon,
            latitude : $la,
            location : point({longitude: $lon, latitude: $la})
            });
            '''
            result = session.run(query1, i = id, lab = label, t=insertedTypes, l = locality, p = postalCode, lon = longitude, la = latitude)
    session.close()

    tt = time() - t0
    status = 'Import neo4j fait en {} secondes'.format(round(tt,3)) 
    return jsonify({'status': status})


#Endpoint pour créer index dans neo4j
@app.route('/createindexneo4j', methods=['GET'])
def index_neo4j():
    t0 = time()
    query2 = '''
    CREATE INDEX FOR (var:POI) on var.id
    '''
    with driver_neo4j.session() as session:
        try:
            result = session.run(query2).data()
        except:
            print("index already exists")

    session.close()
    ts = time() - t0
    return "index fait en {} secondes".format(round(ts,3))

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5006,debug=True)

driver_neo4j.close()
