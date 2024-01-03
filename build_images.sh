#!/bin/bash

docker image build --network=host -t pois_service_manager:latest ./docker_service_manager
docker image build --network=host -t extract_datatourisme:latest ./docker_extract_datatourisme
docker image build --network=host -t import_mongo_datatourisme:latest ./docker_import_mongo
docker image build --network=host -t pois_clustering:latest ./docker_clustering
docker image build --network=host -t docker_pois_infos:latest ./docker_pois_infos
docker image build --network=host -t neo4j_pois:latest ./docker_neo4j
docker image build --network=host -t front_end:latest ./docker_front_end
