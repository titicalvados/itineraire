import dash
import requests
from dash import Dash, html, dcc, Input, Output, ctx, callback
import json

# appli dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# layout definition
# - title
# - 4 buttons sending request and display result in result area
# 1 - Importer les données Datatourisme 
# 2 - ETL to Load in mongo
# 3 - Detect cluster
# 4 - See cluster map


# Le layout de base de l'application
app.layout = html.Div(
    [
        html.Br(),
        html.H1(
            'Service Manager',
            style={'margin':'2% auto auto auto','textAlign': 'center', 'color': 'purple'}
        ),
        html.Br(),
        html.Div([
            html.Button('Importer données web Datatourisme', id='import_web', n_clicks=0)
            ],
            style={'margin':'auto','text-align':'center'}
        ),
        html.Br(),
        html.Div([
            html.Button('Nettoyer/Transformer données Datatourisme et Importer dans mongo', id='etl_mongo', n_clicks=0)
            ],
            style={'margin':'auto','text-align':'center'}
        ),
        html.Br(),
        html.Div([
            html.Button('Detecter Clusters', id='detect_clusters',n_clicks=0)
            ],
            style={'margin':'auto','text-align':'center'}
        ),
        html.Br(),
        html.Div([
            html.A(html.Button('Voir Clusters'), href='http://localhost:5004/map',id='see_clusters')
            ],
            style={'margin':'auto','text-align':'center'}
        ),
        html.Br(),
        html.Div([
            html.Button('Importer POIs dans Neo4J', id='import_neo4j', n_clicks=0)
            ],
            style={'margin':'auto','text-align':'center'}
        ),
        html.Div(
            dcc.Dropdown(
                options= [
                    {'label': 'Créer relations Neo4J pour EntertainmentAndEvent', 'value': 'val_event'},
                    {'label': 'Créer relations Neo4J pour CulturalSite', 'value': 'val_cult'},
                    {'label': 'Créer relations Neo4J pour Accomodation', 'value': 'val_acco'}],
                id = 'iti_theme',
                value= 'val_event'
            ),
            style={'margin':'2% auto auto auto','textAlign': 'center', 'color': 'mediumturquoise','opacity': '0.0 - 1.0', 'width':'40%'}
        ),
        html.Br(),
        html.Div([
            html.Span(
                id='request_result_info',
                children='Request result'
            )
            ],
            style={'margin':'2% auto auto auto','textAlign': 'left', 'color': 'purple','background': 'lightgrey','width':'40%', 'border':'solid'}
        ),
    ]
)

@app.callback(Output('request_result_info', 'children'),
              Input('import_web', 'n_clicks'),
              Input('etl_mongo', 'n_clicks'),
              Input('detect_clusters', 'n_clicks'),
              Input('import_neo4j', 'n_clicks')
)
def displayClick(btn1, btn2, btn3, btn4):
    msg = "Waiting for request result"
    if "import_web" == ctx.triggered_id:
        # URI microservice
        api_url = "http://localhost:5002/telecharger-et-archiver"
        try:
            response = requests.get(api_url)
        except:
            msg = "microservice 2 non accessible"
        else:
            if response.status_code == 200:
                msg = json.dumps(response.json())
            else:
                msg = "microservice 2 response code "+str(response.status_code)
    elif "etl_mongo" == ctx.triggered_id:
        api_url = "http://localhost:5003/loadinmongo"
        try:
            response = requests.get(api_url)
        except:
            msg = "microservice 3 non accessible"
        else:
            if response.status_code == 200:
                msg = json.dumps(response.json())
            else:
                msg = "microservice 3 response code "+str(response.status_code)
    elif "detect_clusters" == ctx.triggered_id:
        api_url = "http://localhost:5004/cluster"
        try:
            response = requests.get(api_url)
        except:
            msg = "microservice 4 non accessible"
        else:
            if response.status_code == 200:
                msg = json.dumps(response.json())
            else:
                msg = "microservice 4 response code "+str(response.status_code)
    elif "import_neo4j" == ctx.triggered_id:
        msg = "neo4j was most recently clicked"
    return msg


if __name__ == '__main__':
  app.run_server(debug=True, host='0.0.0.0', port=5001)
