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
userSelectedTypes = ["EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","ReligiousSite","Store","NaturalHeritage"]


pois = collection_poi.aggregate([{'$match': { 'types' : {'$in':['Accommodation','FoodEstablishment','EntertainmentAndEvent','SportsAndLeisurePlace']}}},{'$project': { 'identifier': '$dc:identifier','longitude':'$longitude','latitude':'$latitude'}}])

#for poi in pois:
#    print(poi)

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

#retrieve neighbours for all nodes and create relation with distance weight
for row in pois:
    #filtrage sur les erreurs latitude longitude hors France métropolaine
    if not (51.10>= float(row["latitude"])>=41.30) or not (9.57>= float(row["longitude"]) >=-5.17):
        continue
    #orArray = [{ 'types': 'Accommodation' },{'types': 'FoodEstablishment'}]
    neighbours = collection_poi.aggregate([{'$geoNear': {'near': { 'coordinates': [ -4.75698 , 48.520412 ] },'distanceField': 'distance','maxDistance': 40000,'query': { '$or': orArray}}},{'$project': { 'identifier': '$dc:identifier','distance':'$distance'}}])
    for neighbour in neighbours:
        if neighbour["identifier"] == row["identifier"]:
            continue
        #create neighbour relationship
        with driver_neo4j.session() as session:
            query = '''
            MATCH (p:POI) where p.id = $row_id
            MATCH (q:POI) where q.id = $neighbour_identifier
            MERGE (q)-[r:NEIGHBOUR]-(p)
            SET r.distance = $distance
            '''
            result = session.run(query, row_id=row["identifier"],neighbour_identifier=neighbour["identifier"],distance = neighbour["distance"]).data()

driver_neo4j.close()


tt = time() - t0
print("Réalisé en {} secondes".format(round(tt,3)))

