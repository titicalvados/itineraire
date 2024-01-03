from fnmatch import fnmatch
from pymongo import MongoClient,GEOSPHERE
from time import time
from datetime import datetime
from flask import Flask, jsonify
import json,os

client = MongoClient(host="127.0.0.1", port = 27017)
datatourisme = client["datatourisme"]

date_today = datetime.now().strftime('%Y-%m-%d')
destination_dir = os.path.join('/home/datatourisme', date_today+"/objects")
print("retrieving files in", destination_dir)
pattern ="*.json"

app = Flask(__name__)

@app.route("/loadinmongo")
def load_poi_in_mongo():
    t0 = time()
    # get an empty mongo poi collection
    try:
        col = datatourisme.get_collection(name="poi")
        col.drop()
    except:
        col = datatourisme.create_collection(name="poi")

    try:
        col.create_index([("location", GEOSPHERE)])
    except:
        print("index déjà créé")

    # get files
    files = []
    for (path, subdirs, file_names) in os.walk(destination_dir):
        for name in file_names:
            if fnmatch(name,pattern):
                files.append(os.path.join(path,name))

    # read file in files
    for file in files:
        with open(file, 'r') as myfile:
            content=myfile.read()

        # parse file
        data = json.loads(content)

        #keep only useful data
        clean_data = {i: data[i] for i in ["dc:identifier","isLocatedAt"]}
        clean_data["types"] = data["@type"]
        clean_data["label"] = data["rdfs:label"]["fr"][0]
        if "rdfs:comment" in data:
            if "fr" in data["rdfs:comment"]:
                clean_data["comment"] = data["rdfs:comment"]["fr"][0]

        if "hasAudience" in data:
           if "rdfs:label" in data["hasAudience"][0]:
                if "fr" in data["hasAudience"][0]["rdfs:label"]:
                    clean_data["audience"] =  data["hasAudience"][0]["rdfs:label"]["fr"][0]

        if "hasDescription" in data:
           if "dc:description" in data["hasDescription"][0]:
               if "fr" in data["hasDescription"][0]["dc:description"]:
                   clean_data["shortDescription"] = data["hasDescription"][0]["dc:description"]["fr"][0]
    
        if "hasContact" in data:
            if "schema:email" in data["hasContact"][0]:
                clean_data["email"] = data["hasContact"][0]["schema:email"][0]
            if "schema:telephone" in data["hasContact"][0]:
                clean_data["telephone1"] = data["hasContact"][0]["schema:telephone"][0]
                if len(data["hasContact"][0]["schema:telephone"])==2:
                    clean_data["telephone2"] = data["hasContact"][0]["schema:telephone"][1]
            if "foaf:homepage" in data["hasContact"][0]:
                clean_data["web"] = data["hasContact"][0]["foaf:homepage"][0]
            if "schema:address" in data["hasContact"][0]:
                if "schema:addressLocality" in data["hasContact"][0]["schema:address"][0]:
                    clean_data["locality"] = data["hasContact"][0]["schema:address"][0]["schema:addressLocality"]
                if "schema:postalCode" in data["hasContact"][0]["schema:address"][0]:
                    clean_data["postalCode"] = data["hasContact"][0]["schema:address"][0]["schema:postalCode"]
                if "schema:streetAddress" in data["hasContact"][0]["schema:address"][0]:
                    clean_data["streetAddress1"] = data["hasContact"][0]["schema:address"][0]["schema:streetAddress"][0]
                    if len(data["hasContact"][0]["schema:address"][0]["schema:streetAddress"])==2:
                        clean_data["streetAddress2"] = data["hasContact"][0]["schema:address"][0]["schema:streetAddress"][1]

        if "offers" in data:
           if "schema:priceSpecification" in data["offers"][0]:
               if "schema:price" in data["offers"][0]["schema:priceSpecification"][0]:
                   clean_data["price"] = data["offers"][0]["schema:priceSpecification"][0]["schema:price"]
               if "appliesOnPeriod" in data["offers"][0]["schema:priceSpecification"][0]:
                   if "endDate" in data["offers"][0]["schema:priceSpecification"][0]["appliesOnPeriod"][0]:
                       clean_data["endDate"] = data["offers"][0]["schema:priceSpecification"][0]["appliesOnPeriod"][0]["endDate"]
                   if "startDate" in data["offers"][0]["schema:priceSpecification"][0]["appliesOnPeriod"][0]:
                       clean_data["startDate"] = data["offers"][0]["schema:priceSpecification"][0]["appliesOnPeriod"][0]["startDate"]


        if "reducedMobilityAccess" in data:
            clean_data["reducedMobilityAccess"] = data["reducedMobilityAccess"]

        if "tourDistance" in data:
            clean_data["tourDistance"] = data["tourDistance"]

        clean_data["addressLocality"] = clean_data["isLocatedAt"][0]["schema:address"][0]["schema:addressLocality"]
        clean_data["postalCode"] = clean_data["isLocatedAt"][0]["schema:address"][0]["schema:postalCode"]
        clean_data["longitude"] = float(clean_data["isLocatedAt"][0]["schema:geo"]["schema:longitude"])
        clean_data["latitude"] = float(clean_data["isLocatedAt"][0]["schema:geo"]["schema:latitude"])

        if (180>=clean_data["longitude"]>=-180) and (90>= clean_data["latitude"]>=-90):
            clean_data["location"]={"type":"Point","coordinates": [clean_data["longitude"],clean_data["latitude"]]}
        else:
            clean_data["location"]={"type":"Point","coordinates": [0,0]}

        del clean_data["isLocatedAt"]
    
        #save in mongo
        col.insert_one(clean_data)

    tt = time() - t0
    status = 'Import mongo fait en {} secondes'.format(round(tt,3))
    return jsonify({'status': status})


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5003,debug=True)

