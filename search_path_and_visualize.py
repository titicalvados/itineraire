import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx

from neo4j import GraphDatabase

#neo4j driver
driver_neo4j = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))

#----------------------------------------------------------
# suppression du graphe
query_drop_graph = '''
CALL gds.graph.drop(
    'myGraph'
)
'''

with driver_neo4j.session() as session:
    try:
        result = session.run(query_drop_graph).data()
    except:
        print("Graph with name myGraph does not exist on database neo4j")

#----------------------------------------------------------
# initialisation du graphe
query_init_graph = '''
CALL gds.graph.project(
    'myGraph',
    'POI',
    { NEIGHBOUR: {type: 'NEIGHBOUR', orientation: 'UNDIRECTED'}},
    {
        relationshipProperties: 'distance'
    }
)
'''

#with driver_neo4j.session() as session:
#    result = session.run(query_init_graph).data()


#----------------------------------------------------------
# requete neo4j de recherche de plus cours chemin
# ATTENTION : les IDS des POI sont ici en dur
query_pcc = '''
MATCH (source:POI {id: 'FMABRE022V53N86X'}), (target:POI {id: 'FMABRE035V52C18P'})
CALL gds.shortestPath.dijkstra.stream('myGraph', {
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: 'distance'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
    index,
    gds.util.asNode(sourceNode).name AS sourceNodeName,
    gds.util.asNode(targetNode).name AS targetNodeName,
    totalCost,
    [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
    costs,
    nodes(path) as path
ORDER BY index
'''

with driver_neo4j.session() as session:
    result = session.run(query_pcc).data()

#affichage de debug - résultat de la requete
print(result[0]["path"])

# reformatage de la sortie de la requete pour coller à l'appel de 'dlx.dicts_to_geojson'
poi_dict = [dict(
    postalCode=p["postalCode"], 
    lat=p["latitude"], 
    lon=p["longitude"], 
    locality=p["locality"],
    label=p["label"],
    poi_id=p["id"],
    types=p["types"]
    ) for p in result[0]["path"]]

#affichage de debug
print(poi_dict)

#creation de l'appli dash
app = dash.Dash()
 
# création d'un 'geojson' à partir des points issus de la requète
# note : 'tooltip' : ce qui sera affiché lorsque la souris survolera le point sur la carte
geojson_poi = dlx.dicts_to_geojson(
   [{
       **poi, 
#       **dict(tooltip=poi["label"]+', '+poi["locality"]+', '+poi["postalCode"]+', '+poi["poi_id"]+', '+poi["types"][0])
       **dict(tooltip=poi["label"]+', '+poi["locality"]+', '+poi["postalCode"])
       } 
       for poi in poi_dict]
)
 
# création d'une liste de couples [latitude,longitude] qui vont servir à tracer des lignes entre les coordonnées
poi_coord = [[poi["lat"],poi["lon"]] for poi in poi_dict]
polyline = dl.Polyline(positions=poi_coord)

# initialisation d'une carte dans le layout de l'application, avec le geojson des poi et la polyline entre les poi
app.layout = dl.Map(
   [dl.TileLayer(), dl.GeoJSON(data=geojson_poi, id="geojson", zoomToBounds=True),polyline],
   style={"width": "1000px", "height": "500px"},
)
 
# lancement de l'appli 
if __name__ == "__main__":
   app.run_server()
