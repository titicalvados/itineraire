# itineraire
Ce dépôt GIT contient le code utilisé dans le cadre de notre projet école itinéraire
To be completed later


2023/06/19
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

    com1 , ... , com1_voisine1|com1_voisne2|com1_voisine3, ...
    com2 , ... , com2_voisine1|com2_voisne2 , ...
    com3 , ... , com3_voisine1|com3_voisne2|com3_voisine3|com3_voisine4|com3_voisine5|com3_voisine6 , ...
    com4 , ... , com4_voisine1|com4_voisne2|com4_voisine3|com4_voisine4|com4_voisine5 , ...
    ...

  Un pré-traitement de ce fichier pour le simplifier est nécessaire et ne garder qu'un couple par ligne
  (et se passer des autres informations)

    com1 , com1_voisine1
    com1 , com1_voisine2
    com1 , com1_voisine3
    com2 , com2_voisine1
    com2 , com2_voisine2
    com3 , com3_voisine1
    com3 , com3_voisine2
    com3 , com3_voisine3
    com3 , com3_voisine4
    com3 , com3_voisine5
    com3 , com3_voisine6
    com4 , com4_voisine1
    com4 , com4_voisine2
    com4 , com4_voisine3
    com4 , com4_voisine4
    com4 , com4_voisine5
    ...
 
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
