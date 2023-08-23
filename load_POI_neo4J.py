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




pois = collection_poi.aggregate([{'$project': { 'identifier': '$dc:identifier','label': '$label','types': '$types','locality': '$addressLocality','postalCode':'$postalCode','latitude':'$latitude','longitude':'$longitude'}}])

#for poi in pois:
#    print(poi)

#neo4j driver
driver_neo4j = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))


#clean neo4j database
query = ''' 
MATCH (n)
DETACH DELETE n
'''

with driver_neo4j.session() as session:
    result = session.run(query).data()

print(result)

selectedTypes = ["AccommodationProduct","Visit","Rental","Store","Accommodation","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","CampingAndCaravanning","ReligiousSite","NaturalHeritage","TouristInformationCenter"]


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
            if type in selectedTypes:
                if (type == "AccommodationProduct") and ("Accommodation" not in insertedTypes):
                    insertedTypes.append("Accommodation")
                elif (type == "Accommodation") and ("Accommodation" not in insertedTypes):
                    insertedTypes.append("Accommodation")
                else:
                    insertedTypes.append(type)
        locality = row["locality"]
        postalCode = row["postalCode"]
        query = '''
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
        result = session.run(query, i = id, lab = label, t=insertedTypes, l = locality, p = postalCode, lon = longitude, la = latitude)

    session.close()

driver_neo4j.close()

tt = time() - t0
print("Réalisé en {} secondes".format(round(tt,3)))

