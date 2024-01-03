# itineraire
Ce dépôt GIT contient le code utilisé dans le cadre de notre projet école itinéraire avec DataScientest.

L’objectif du projet est la création d’une application permettant de proposer un itinéraire passant par des POIs (Points Of Interest) à partir de données DATAtourisme https://www.datatourisme.fr/

L'application a été décomposée en 7 micro services python.
Chacun des fichiers pythons se trouve dans un répertoire docker_xxx avec les fichiers requirement.txt et Dockerfile associés pour construire l'image docker du micro service

Le projet a été développé/testé sur Ubuntu 22.04

Pour l'éxécuter il faut un PC disposant de Docker, Docker Compose, MongoDB et Neo4J avec les plugins apoc et graph-data-science

Si vous n'avez pas installé Neo4J vous pouvez le faire par docker avec la commande suivante
- docker run --name my_neo4j -p7474:7474 -p7687:7687 -d -v $HOME/neo4j/data:/data -v $HOME/neo4j/logs:/logs -v $HOME/neo4/import:/var/lib/neo4j/import -v $HOME/neo4j/plugins:/plugins -e NEO4J_AUTH=none  --env NEO4J_PLUGINS='["graph-data-science",”apoc”]' neo4j:latest

Si vous n'avez pas installé MongoDB vous pouvez le faire par docker avec la commande suivante
- docker run -d -p 27017:27017 --name my_mongo -v mongo_volume:/data/db mongo:latest

Ensuite 
1) Cloner le projet https://github.com/titicalvados/itineraire.git et se positionner dans le répertoire racine
2) Exécuter le fichier build_images.sh => ./build_images.sh
3) Lancer le docker-compose => docker-compose up -d
4) Ouvrir votre navigateur préféré sur les urls http://localhost:5001 (service manager, l'orchestrateur qui importe/prépare les données et reste à automatiser avec Airflow) et http://localhost:5000 (front end utilisateur final)
5) Docker-compose down lorsque vous avez terminé

Remarques : la construction des relations "neighbour" préalable au calcul d'itinéraire est relativement longue dans Neo4J.
Pour commencer le faire pour les POIs de type Accommodation (environ 3 minutes constaté). Pour EntertainmentAndEvent il faut au moins 9 minutes et pour CulturalSite 28 minutes est un minimum le nombre de POIs étant beaucoup plus important
