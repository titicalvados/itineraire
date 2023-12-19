FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3.11 python3-pip

WORKDIR /home

ADD ./3_import_pois_in_mongo.py ./
ADD ./requirements.txt ./

RUN pip3 install -r requirements.txt

CMD python3 3_import_pois_in_mongo.py
