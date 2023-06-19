from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))

#################################################################################"
# deleting previous data if still there

print('Deleting previous data')

query_clean1 = '''
MATCH (n) 
DETACH DELETE n
'''

with driver.session() as session:
    print(query_clean1)
    session.run(query_clean1)

print('initial cleaning done\n')

print('loading communes as nodes')

query = '''
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/lblin3/test/main/liste_communes2.csv' AS row
CREATE (:Commune {insee : row.Code_commune_INSEE,
                  nom_commune : row.Nom_commune,
                  code_postal : row.Code_postal,
                  x : toFloat(row.coordonnees_geographiques_x),
                  y : toFloat(row.coordonnees_geographiques_y)
});
'''

with driver.session() as session:
    print(query)
    session.run(query)

print('communes loading done\n')


print('loading vicinities as relations')

query = '''
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/lblin3/test/main/communes_adjacentes_2022_toutes_simplifie.csv' AS row
MATCH (c1:Commune) WHERE c1.insee = row.insee_origine
MATCH (c2:Commune) WHERE c2.insee = row.insee_destination
CREATE (c1)-[:VOISINE {distance: SQRT((c1.x-c2.x)^2+(c1.y-c2.y)^2)}]->(c2);
'''

# ATTENTION : la requete précédente associe à chaque relation ':VOISINE' un attribut 'distance'
# la formule de calcul de cette distance à partir des coordonnées GPS est incorrecte et devra être revue

with driver.session() as session:
    print(query)
    session.run(query)

print('vicinities loading done\n')

