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
    poi = collection_poi.aggregate([{'$match'  : {'dc:identifier':id}},{'$project': { '_id':0,'identifier': '$dc:identifier','label': '$label','types': '$types','shortDescription':'$shortDescription','locality': '$addressLocality','postalCode':'$postalCode','email':'$email','telephone1':'$telephone1','web':'$web','latitude':'$latitude','longitude':'$longitude'}}])
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

tt = time() - t0
print("Réalisé en {} secondes".format(round(tt,3)))


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
