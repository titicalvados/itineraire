import json, os, requests, json
from werkzeug.wrappers import Response
from bson import json_util
from fnmatch import fnmatch
from pymongo import MongoClient
from time import time
from flask import Flask, jsonify
from bson.json_util import dumps
from pydantic import BaseModel
from flask_pydantic import validate

client = MongoClient(host="127.0.0.1", port = 27017)

datatourisme = client["datatourisme"]

collection_poi = datatourisme.get_collection(name="poi")

selectedTypes = ["AccommodationProduct","Visit","Rental","Store","Accommodation","FoodEstablishment","EntertainmentAndEvent","SportsAndLeisurePlace","CulturalSite","Tour","CampingAndCaravanning","ReligiousSite","NaturalHeritage","TouristInformationCenter"]

class Query(BaseModel):
    id:str
    neighbourhoodDistance:int

app = Flask(__name__)

#get POIs from mongo
nb_poi = collection_poi.count_documents({})
print("Nombre de POIs: ",nb_poi)

@app.route("/getpoiinfos/<id>")
def get_poi_infos(id):
    poi = collection_poi.aggregate([{'$match'  : {'dc:identifier':id}},{'$project': { '_id':0,'identifier': '$dc:identifier','label': '$label','types': '$types','comment':'$comment','shortDescription':'$shortDescription','locality': '$addressLocality','postalCode':'$postalCode','email':'$email','telephone1':'$telephone1','web':'$web','latitude':'$latitude','longitude':'$longitude'}}])
    return Response(dumps(list(poi)[0]), mimetype='application/json')


@app.route("/getpoineighbours")
@validate()
def get_poi_neighbours(query:Query):
    poi = collection_poi.aggregate([{'$match'  : {'dc:identifier':query.id}},{'$project': { '_id':0,'identifier': '$dc:identifier','latitude':'$latitude','longitude':'$longitude'}}])
    coord=list(poi)[0]
    long=coord["longitude"]
    lat=coord["latitude"]
    neighbours = collection_poi.aggregate([{'$geoNear': {'near': { 'coordinates': [float(long) , float(lat)] },'distanceField':'distance','maxDistance': query.neighbourhoodDistance }},{'$project': { '_id':0 ,'origin': query.id, 'end': '$dc:identifier', 'distance':'$distance'}}])
    return Response(dumps(list(neighbours)),mimetype='application/json')


@app.route("/gettypeslist")
def get_types_list():
    return jsonify(types = selectedTypes)


@app.route("/getpoislistbytype/<type>")
def get_pois_list(type):
    poi = collection_poi.aggregate([{'$match'  : {'types':{'$in' : [type]}}},{'$project': { '_id':0,'identifier': '$dc:identifier','label':'$label','latitude':'$latitude','longitude':'$longitude'}}])
    return Response(dumps(list(poi)),mimetype='application/json')


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5005,debug=True)
