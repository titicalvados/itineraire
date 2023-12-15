# itineraire
Ce dépôt GIT contient le code utilisé dans le cadre de notre projet école itinéraire
To be completed later


2023/06/19 :
répertoire 'graph':
premiers éléments pour initialiser un graphe des communes métropolitaines

2 sources de données :

- https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/
  liste de codes postaux des communes françaises, avec entre autres nom de commune, code insee 
  et coordonnées géographiques
  -> peut servir de base pour construire les noeuds du graphe

- https://www.data.gouv.fr/fr/datasets/liste-des-adjacences-des-communes-francaises/
  liste des communes françaises avec pour chacune la liste des communes voisines
  ne contient pas les codes postaux mais fait référence aux communes par leurs codes insee
  -> peut servir à relier les communes de france 
  (en faisant l'hypothèse que si 2 communes sont voisines alors il existe une route qui les relie)
  
  Une ligne de ce fichier correspond à une commune et contient la liste des communes voisines 
  (de longueur variable pour chaque commune) :

    - com1 , ... , com1_voisine1|com1_voisne2|com1_voisine3, ...
    - com2 , ... , com2_voisine1|com2_voisne2 , ...
    - com3 , ... , com3_voisine1|com3_voisne2|com3_voisine3|com3_voisine4|com3_voisine5|com3_voisine6 , ...
    - com4 , ... , com4_voisine1|com4_voisne2|com4_voisine3|com4_voisine4|com4_voisine5 , ...
    - ...

  Un pré-traitement de ce fichier pour le simplifier est nécessaire et ne garder qu'un couple par ligne
  (et se passer des autres informations)

    - com1 , com1_voisine1
    - com1 , com1_voisine2
    - com1 , com1_voisine3
    - com2 , com2_voisine1
    - com2 , com2_voisine2
    - com3 , com3_voisine1
    - com3 , com3_voisine2
    - com3 , com3_voisine3
    - com3 , com3_voisine4
    - com3 , com3_voisine5
    - com3 , com3_voisine6
    - com4 , com4_voisine1
    - com4 , com4_voisine2
    - com4 , com4_voisine3
    - com4 , com4_voisine4
    - com4 , com4_voisine5
    - ...
 
    C'est le rôle du script 'preprocess_communes_adjacentes.py'


Chargement de la base Neo4j

Le script python 'neo4j_load_communes.py' contient essentiellement 2 requetes pour charger la base Neo4j 
pour mettre en forme le graphe.
- une requete pour créer les noeuds du graphe à partir de la liste des communes
- une requete pour créer les relations entre communes à partir de la liste des codes insee voisins

Les premiers tests on été effectués avec la VM DataScientest et le docker neo4j fourni avec. 

Le schéma 'graphe_liste_communes2.png' illustre le résulat obtenu à partir d  communes contenues dans le fichier :
- liste_communes_28.csv'
(liste de 28 communes voisines préselectionnées, sur les 2 codes postaux 22140 et 22300)

Les autres listes de communes :
- liste_communes_100.csv
- liste_communes_1000.csv
- liste_communes_5000.csv
- liste_communes_10000.csv
- liste_communes_toutes.csv
  
sont des listes plus ou moins longues pour tester la vitesse de chargement de la base. 

Ajout de 3 fichiers pythons
1) import_POIs_in_MongoDB.py
   Crée une collection mongoDB poi à partir des fichiers datatourism. A lancer depuis un endroit ou se trouve un dossier data\POI_Bretagne (modifiable dans le fichier py)
2) load_POI_neo4j.py
   Lit la collection poi mongo pour aller créer un noeud par poi avec les infos de label, types et position   
3) create_POI_neighbour_relation.py
   Lit la collection poi mongo pour récupérer les poi puis poi par poi requête mongo pour récupérer les pois voisins dans un rayon de 40 km pour une liste de types donnés (paramétrable dans l'appli)
   Problèmes de performance rencontrés, c'est très lent
4) clustering_poi_kmeans:
Api Flask pour le Clustering de POI avec K-means :

Objectif : L'application utilise Flask pour effectuer le clustering de points d'intérêt (POI) en fesant appele à l'api  url = "http://localhost:5005/getpoislistbytype/EntertainmentAndEvent". Il permet  d'appliquer l'algorithme K-means, génèrer une carte interactive avec Folium, et exposer des endpoints pour visualiser la carte et récupérer les résultats du clustering.

Endpoints :

    /cluster (GET) :
        Endpoint pour effectuer le clustering.
    /map (GET) :
    Endpoint pour afficher la carte générée avec Folium.
    Renvoie la page HTML contenant la carte interactive.
Exécution :

    Exécutez le script Python.
    Accédez à l'URL http://localhost:5004/cluster pour déclencher le clustering et obtenir les résultats en format JSON.
    Accédez à l'URL http://localhost:5004/map pour visualiser la carte interactive générée.
5) extract_datatourisme.py
   Ce code représente une application Flask qui télécharge un fichier ZIP à partir d'une URL (flux de données datatourisme), extrait son contenu dans un répertoire local, et renvoie le chemin du répertoire local nouvellement créé.
   
    Endpoint /telecharger-et-archiver (GET) :
   
        Télécharge un fichier ZIP à partir d'une URL spécifiée (url).
        Crée un répertoire local basé sur la date actuelle.
        Télécharge le fichier ZIP et l'enregistre localement dans le répertoire créé.
        Extrait le contenu du fichier ZIP dans le même répertoire.
        Supprime le fichier ZIP après extraction.
        Renvoie le chemin du répertoire local créé.
   
    Exécution :
   
        L'application Flask écoute sur le port 5002.
        Accédez à l'URL http://localhost:5002/telecharger-et-archiver pour déclencher le téléchargement, l'extraction et           obtenir le chemin du répertoire local.
