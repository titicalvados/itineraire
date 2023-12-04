import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
#import json

from dash import dcc
from dash import html 
from dash import State 
from dash.dependencies import Input, Output
from neo4j import GraphDatabase

#delete temporary file used
if os.path.exists('clicked.csv'):
    os.remove('clicked.csv')

#neo4j driver
driver_neo4j = GraphDatabase.driver('bolt://0.0.0.0:7687',
                              auth=('neo4j', 'neo4j'))

#----------------------------------------------------------
# neo4j graph reset 
#
# first: deletion

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

# then new initialisation 
query_init_graph = '''
CALL gds.graph.project(
    'myGraph',
    'POI',
    { 
        NEIGHBOUR: {
            type: 'NEIGHBOUR', 
            orientation: 'UNDIRECTED'
        }
    },
    {
        relationshipProperties: 'distance'
    }
)
'''
with driver_neo4j.session() as session:
    try:
        result = session.run(query_init_graph).data()
    except:
        print("Can't init Graph with name myGraph")

# URI de récupération des POIs
api_url = "http://localhost:5001/getpoislistbytype/EntertainmentAndEvent"
response = requests.get(api_url)

# Vérifiez si la requête a réussi (code 200)
if response.status_code == 200:
    api_data = response.json()
    poi_df = pd.DataFrame.from_dict(api_data)

# number of clicks
iti_click = 0;

#----------------------------------------------------------------
# map definition function for the layout 
#
# intput : dataframe with at least 'latitude' 'longitude' and 'lable' columns
def iti_map(df):
    fig = px.scatter_mapbox(poi_df, lat="latitude", lon="longitude",
                            height=800, width=1600,
                            size_max=175,
                            color_continuous_scale='viridis',
                            mapbox_style="carto-positron", 
                            hover_name="label"
                            )
    return fig


#----------------------------------------------------------------
#creation de l'appli dash
app = dash.Dash()
 

#----------------------------------------------------------------
# layout definition
# - title
# - dropdown list for theme categories (no action yet)
# - map 
# - list of 'start' and 'end' itinerary POIs
# - button to lauch itinerary computation

app.layout = html.Div(
    [
        html.H1(
            'Projet DE itinéraire', 
            style={'textAlign': 'center', 'color': 'mediumturquoise'}
        ),
        html.Div(
            dcc.Dropdown(
                options= [
                    {'label': 'EntertainmentAndEvent', 'value': 'val_event'},
                    {'label': 'CulturalSite', 'value': 'val_cult'},
                    {'label': 'Accomodation', 'value': 'val_acco'}],
                id = 'iti_theme',
                value= 'val_event'
            )
        ),
        html.Div(
            [
                dcc.Graph(id='iti_map', figure=iti_map(poi_df))
            ],
            style={'width': '80%', 'display': 'inline-block'}
        ),
        html.Div([
            html.Ul(
                id='view_POI_info',
                children=[
                    html.Li(''),            
                    html.Li(''),            
                    html.Li(''),            
                    html.Li('')
                ]
            )
        ]),
        html.Div([
            html.Ul(
                id='view_click',
                children=[
                    html.Li('départ  : '),            
                    html.Li('arrivée : ')
                ]
            )
        ]),
        html.Div([
            html.Button('itinéraire', id='compute_iti', n_clicks=0),
        ])
    ], 
    style = {'background' : 'beige'}
)


#----------------------------------------------------------------
# callback when clicking on a POI on the map
# - input action : click on the map
# - output action : edit list of 'start' and 'end' itinerary POIs
#
# NOTE: format sample of 'clickData':
# {
#   'points': 
#       [
#           {
#               'curveNumber': 0, 
#               'pointNumber': 0, 
#               'pointIndex': 0, 
#               'lon': -1.98505, 
#               'lat': 48.52627, 
#               'hovertext': 'Festival Douce Rance', 
#               'bbox': {
#                   'x0': 451.67455330439236, 
#                   'x1': 453.67455330439236, 
#                   'y0': 356.9861280537602, 
#                   'y1': 358.9861280537602
#               }
#           }
#       ]
#  }

@app.callback([
    Output(component_id='view_click', component_property='children'),
    Output(component_id='view_POI_info', component_property='children')],
    [Input(component_id='iti_map', component_property='clickData')],
    State('iti_map', 'figure'),
    prevent_initial_call=True
)
def update_map(clickData, f):
    if clickData:
        # if something really clicked
        global iti_click
        
        #updating the global number of clicks 
        iti_click = iti_click + 1

        # the list of clicked POIs is updated and stored in a file in the current directory
        # THIS IS NOT THE BEST WAY TO REMEMBER CONTEXT BETWEEN CALLBACKS, BUT MY FIRST TRIES FAILED (using 'dcc.Store')
        # THIS WAY WORKS...

        # if file with previously clicked POIs exists, then loading it (csv format for dataframe)
        # else initiating a new empty dataframe (same structure as global POI dataframe 
        if os.path.exists('clicked.csv'):
            click_df = pd.read_csv('clicked.csv')
        else:
            click_df = poi_df.head(0)

        # concatenating the current dataframe of clicked POIs with a the (only) line from the global POI dataframe 
        # where the 'label' value matches with the POI clicked
        # (it would be better to match with the ID value, but the clickData structure does not provide it ;
        # it could be investigated furhter)
        click_df = pd.concat([click_df, poi_df.loc[poi_df['label'] == clickData['points'][0]['hovertext']]])
        #print(click_df)

        # storing the new list of clicked POIs
        click_df.to_csv('clicked.csv',index=False)

        # preparing the list of 'start' and 'end' POIs to be displayed
        if (iti_click == 1):
           if os.path.exists('clicked.csv'):
               click_dep = click_df.iloc[-1]['label']
               click_arr = ''
               click_id = click_df.iloc[-1]['identifier']
           else:                      
               # very first click of the app: this will be the 'start', and the 'end' will be empty.
               click_dep = click_df.iloc[0]['label']
               click_arr = ''
               click_id = click_df.iloc[0]['identifier']
        else:
            # not the first click: the 'start' will be the previously clicked POI (the previous end),
            # and the 'end' will be the current clicked POI
            click_dep = click_df.iloc[-2]['label']
            click_arr = click_df.iloc[-1]['label']
            click_id = click_df.iloc[-1]['identifier']

        # API call with the "/getpoiinfos" endpoint to get infos about the POI from mongoDB  
        api_url = 'http://localhost:5001/getpoiinfos/'+click_id
        #print(api_url)
        POI_info_label = ''
        POI_info_description = ''
        POI_info_localisation = ''
        POI_info_contact = ''

        response = requests.get(api_url)
        if response.status_code == 200:
            # getting the result json structure from the response 
            POI_info_json = response.json()
            #print(POI_info_json)

    
            # building the 4-item list of information to be displayed
            if 'label' in POI_info_json:
                POI_info_label = POI_info_label + POI_info_json['label']

            if 'shortDescription' in POI_info_json:
                POI_info_description = POI_info_description + POI_info_json['shortDescription']

            if 'locality' in POI_info_json:
                POI_info_localisation = POI_info_localisation + POI_info_json['locality'] + ',  '
            if 'postalCode' in POI_info_json:
                POI_info_localisation = POI_info_localisation + POI_info_json['postalCode']

            if 'telephone1' in POI_info_json:
                POI_info_contact = POI_info_contact + POI_info_json['telephone1'] + ', '
            if 'email' in POI_info_json:
                POI_info_contact = POI_info_contact + POI_info_json['email'] + ', '
            if 'web' in POI_info_json:
                POI_info_contact = POI_info_contact + POI_info_json['web']

        html_POI_info = [
                html.Li(POI_info_label),
                html.Li(POI_info_description),
                html.Li(POI_info_localisation),
                html.Li(POI_info_contact)
        ]

        # building the 2-item list of itinerary 'start' and 'end' POIs to be displayed 
        html_POI_list = [
                html.Li('départ  : '+click_dep),
                html.Li('arrivée : '+click_arr)
                #,html.Li(iti_click) # click counter for debug
        ]

        # callback return: the info list AND the 'start-end' list of values
        return html_POI_info, html_POI_list

    # it nothing clicked, no update    
    return dash.no_update


#----------------------------------------------------------------
# callback when clicking on the 'itinerary' button
# - input action : click on the button
# - output action : edit map to show the itinerary between 'start' and 'end'

@app.callback(
    Output('iti_map', 'figure'),
    Input('compute_iti', 'n_clicks'),
    #    State('input-on-submit', 'value'),
    prevent_initial_call=True
)
def icompute_itineraire(n_clicks):
    # checking that the file containing the list of previouly clicked POIs exists
    if os.path.exists('clicked.csv'):
        # loading the file (dataframe format) and checking that it contains at least 2 lines (2 POIs clicked)
        global iti_click
        click_df = pd.read_csv('clicked.csv')
        #print("compute itineraire")
        if (iti_click >=2) and (click_df.index.size >=2):
            poi_dep = click_df.iloc[-2]['poi_id']
            poi_arr = click_df.iloc[-1]['poi_id']

            # the map will still contains the global POIs (from the mail 'poi_df' dataframe)
            new_fig = iti_map(poi_df)
            # and it will be updated with the itinerary: POI colored differently and linked with a line

            # first, computing the itinerary using the neo4j database content
            # (building a request to search for the shortest path between 'stat' and 'end' POIs 
            # using the dijkstra algorithm)
            new_query_pcc = "MATCH (source:POI {id: '"+str(poi_dep)+"'}),(target:POI {id: '"+str(poi_arr)+"'})"\
            +" CALL gds.shortestPath.dijkstra.stream('myGraph', {"\
            +" sourceNode: source,"\
            " targetNode: target,"\
            " relationshipWeightProperty: 'distance'})"\
            " YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path"\
            " RETURN index,"\
            " gds.util.asNode(sourceNode).name AS sourceNodeName,"\
            " gds.util.asNode(targetNode).name AS targetNodeName,"\
            " totalCost,"\
            " [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,"\
            " costs,"\
            " nodes(path) as path"\
            " ORDER BY index"
            #print(new_query_pcc)
            with driver_neo4j.session() as session:
                result2 = session.run(new_query_pcc).data()

            #affichage de debug - résultat de la requete
            #print(result2)
            #print("------------------------------------------------------")
            #print(result2[0]["path"])

            # reformating the output of the request as to store it in a dataframe
            # - first bulding a dictionnary
            # - then using it to set the dataframe
            iti_poi_dict = [dict(
                postalCode=p["postalCode"],
                lat=p["latitude"],
                lon=p["longitude"],
                locality=p["locality"],
                label=p["label"],
                poi_id=p["id"],
                types=p["types"]
            ) for p in result2[0]["path"]]
            iti_poi_df = pd.DataFrame(data = iti_poi_dict)

            #print(iti_poi_df['lon'])
            #print(iti_poi_df['lat'])

            # updating the map with the dataframe
            new_fig.add_trace(go.Scattermapbox(
                mode = "markers+lines",
                lon = iti_poi_df['lon'],
                lat = iti_poi_df['lat'],
                hovertext = iti_poi_df['label'],
                marker = {'size': 10}
                )
            )             

            #resetting the click counter
            iti_click = 0

            # callback result: returning the figure
            return new_fig
        print("not enough data")
        return dash.no_update
    print("no click file")
    return dash.no_update



#----------------------------------------------------------------
# application launch 
if __name__ == "__main__":
    app.run_server(debug = True, host = '0.0.0.0', port = 5000)
