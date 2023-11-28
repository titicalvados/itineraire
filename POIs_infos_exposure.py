import json, os, requests, jsonify, json
from werkzeug.wrappers import Response
from bson import json_util
from fnmatch import fnmatch
from pymongo import MongoClient
from time import time
from flask import Flask
from bson.json_util import dumps

client = MongoClient(host="127.0.0.1", port = 27017)

datatourisme = client["datatourisme"]

collection_poi = datatourisme.get_collection(name="poi")

t0 = time()

app = Flask(__name__)

#get POIs from mongo
nb_poi = collection_poi.count_documents({})
print("Nombre de POIs: ",nb_poi)


@app.route("/getpoiinfos/<id>")
def get_poi_infos(id):
    poi = collection_poi.aggregate([{'$match'  : {'dc:identifier':id}},{'$project': { '_id':0,'identifier': '$dc:identifier','label': '$label','types': '$types','locality': '$addressLocality','postalCode':'$postalCode','latitude':'$latitude','longitude':'$longitude'}}])
    #return dumps(list(poi)[0])
    return Response(dumps(list(poi)[0]), mimetype='application/json')


@app.route("/getpoislistbytype/<type>")
def get_pois_list(type):
    poi = collection_poi.aggregate([{'$match'  : {'types':{'$in' : [type]}}},{'$project': { '_id':0,'identifier': '$dc:identifier','latitude':'$latitude','longitude':'$longitude'}}])
    return Response(dumps(list(poi)),mimetype='application/json')


#poislist = collection_poi.aggregate([{'$match'  : {'types':{'$in' : [types_list]}}},{'$project': { 'identifier': '$dc:identifier'}}])

poi = collection_poi.aggregate([{'$match'  : {'dc:identifier':"FMABRE029V53N109"}},{'$project': { 'identifier': '$dc:identifier','label': '$label','types': '$types','locality': '$addressLocality','postalCode':'$postalCode','latitude':'$latitude','longitude':'$longitude'}}])

#pois = collection_poi.aggregate([{'$project': { 'identifier': '$dc:identifier','label': '$label','types': '$types','locality': '$addressLocality','postalCode':'$postalCode','latitude':'$latitude','longitude':'$longitude'}}])


print(list(poi))


selectedTypes = ["AccommodationProduct","Visit","Rental","Store","Accommodation","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","CampingAndCaravanning","ReligiousSite","NaturalHeritage","TouristInformationCenter"]


#with driver_neo4j.session() as session:
    #insert poi by poi
 #   for row in pois:
 #      id = row["identifier"]
  #      label = row["label"]
     #filtrage sur les erreurs latitude longitude hors France métropolaine
#        if (51.10>= float(row["latitude"])>=41.30) and (9.57>= float(row["longitude"]) >=-5.17):
 #           latitude = float(row["latitude"])
  #          longitude = float(row["longitude"])
   #     else:
    #        continue
     #   originalTypes = row["types"]
      #  insertedTypes = []
       # for type in originalTypes:
        #    if type in selectedTypes:
         #       if (type == "AccommodationProduct") and ("Accommodation" not in insertedTypes):
          #          insertedTypes.append("Accommodation")
           #     elif (type == "Accommodation") and ("Accommodation" not in insertedTypes):
            #        insertedTypes.append("Accommodation")
             #   else:
              #      insertedTypes.append(type)
#        locality = row["locality"]
#        postalCode = row["postalCode"]
 #       query = '''
  #      CREATE (:POI {id: $i,
   #     label: $lab,
    #    types: $t,
     #   locality: $l,
      # postalCode: $p,
#        longitude: $lon,
 #       latitude : $la,
  #      location : point({longitude: $lon, latitude: $la})
   #     });
    #    '''
        #result = session.run(query, i = id, lab = label, t=insertedTypes, l = locality, p = postalCode, lon = longitude, la = latitude)

   # session.close()

# driver_neo4j.close()

tt = time() - t0
print("Réalisé en {} secondes".format(round(tt,3)))


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
