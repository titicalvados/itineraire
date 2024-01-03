FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3.11 python3-pip

WORKDIR /home

ADD ./4_clusterin_poi_kmeans.py ./
ADD ./requirements.txt ./

RUN pip3 install -r requirements.txt

CMD python3 4_clusterin_poi_kmeans.py
