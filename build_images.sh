#!/bin/bash

docker image build -t pois_service_manager:latest ./docker_service_manager
docker image build -t extract_datatourisme:latest ./docker_extract_datatourisme
docker image build -t import_mongo_datatourisme:latest ./docker_import_mongo
docker image build -t pois_clustering:latest ./docker_clustering
docker image build -t docker_pois_infos:latest ./docker_pois_infos
docker image build -t neo4j_pois:latest ./docker_neo4j
docker image build -t front_end:latest ./docker_front_end
