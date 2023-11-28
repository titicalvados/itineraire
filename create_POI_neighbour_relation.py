import json, os
from bson import json_util
from fnmatch import fnmatch
from pymongo import MongoClient
from neo4j import GraphDatabase
from time import time


t0 = time()

client = MongoClient(host="127.0.0.1", port = 27017)

datatourisme = client["datatourisme"]

collection_poi = datatourisme.get_collection(name="poi")

#get POIs from mongo
nb_poi = collection_poi.count_documents({})
print("Nombre de POIs: ",nb_poi)

allowedTypes = ["Accommodation","Visit","Rental","Store","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","CampingAndCaravanning","ReligiousSite","NaturalHeritage","TouristInformationCenter"] 

userMostSelectedTypes = ["Accommodation","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace"]
userLeastSelectedTypes = ["Rental","Store","NaturalHeritage","TouristInformationCenter"]
userSelectedTypes = ["EntertainmentAndEvent"]


pois = collection_poi.aggregate([{'$match': { 'types' : {'$in':userSelectedTypes}}},{'$project': { 'identifier': '$dc:identifier','longitude':'$longitude','latitude':'$latitude'}}])

orArray=[]
for type in userSelectedTypes:
    orArray.append({'types' : type})
print(orArray)

#neo4j driver
driver_neo4j = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))

query = '''
MATCH ()-[r:NEIGHBOUR]-()
        DELETE r
'''

with driver_neo4j.session() as session:
    result = session.run(query).data()

treatedPOIs=[]

#retrieve neighbours for all nodes and create relation with distance weight
neighbourhoodDistance = 50000
print("considéré comme voisin (en m) si moins de :",neighbourhoodDistance)
for row in pois:
    treatedPOIs.append(row["identifier"])
    #affichage du progrès et du temps de mise à jour tous les 1000 POIs
    if len(treatedPOIs) % 1000 == 0:
        ti = time() - t0
        print("{} POIs traités en {} secondes".format(len(treatedPOIs),round(ti,3)))
    #filtrage sur les erreurs latitude longitude hors France métropolaine
    if not (51.10>= float(row["latitude"])>=41.30) or not (9.57>= float(row["longitude"]) >=-5.17):
        continue
    neighbours = collection_poi.aggregate([{'$geoNear': {'near': { 'coordinates': [float(row["longitude"]) , float(row["latitude"])] },'distanceField': 'distance','maxDistance': neighbourhoodDistance,'query': { '$or': orArray}}},{'$project': { 'identifier': '$dc:identifier','distance':'$distance'}}])
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

driver_neo4j.close()


tt = time() - t0
print("Réalisé en {} secondes".format(round(tt,3)))

