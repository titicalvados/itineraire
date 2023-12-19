FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3.11 python3-pip

WORKDIR /home

EXPOSE 5000

ADD ./7_front_end.py ./
ADD ./requirements.txt ./

RUN pip3 install -r requirements.txt

CMD python3 7_front_end.py

