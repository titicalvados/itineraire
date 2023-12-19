from flask import Flask, jsonify, render_template
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import folium
import pandas as pd

app = Flask(__name__)

# Endpoint pour effectuer le clustering et renvoyer les résultats
@app.route('/cluster', methods=['GET'])
def cluster_data():
    # URI de récupération de données
    api_url = "http://localhost:5005/getpoislistbytype/EntertainmentAndEvent"
    response = requests.get(api_url)

    # Vérifiez si la requête a réussi (code 200)
    if response.status_code == 200:
        # Chargez les données depuis le fichier JSON de la réponse de l'API
        api_data = response.json()

        # Extrait les coordonnées des POIs depuis les données de l'API
        data = [[poi['latitude'], poi['longitude']] for poi in api_data]

        # Transformez la liste en un tableau NumPy
        data = np.array(data)

        # Normalisez les données
        scaler = StandardScaler()
        data_normalized = scaler.fit_transform(data)

        # Appliquez K-means
        k = 8
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(data_normalized)

        # Les centres des clusters sont stockés dans kmeans.cluster_centers_
        centres_clusters = scaler.inverse_transform(kmeans.cluster_centers_)

        # L'attribution des points à un cluster est stockée dans kmeans.labels_
        cluster_assignments = kmeans.labels_

        # Créez une carte centrée sur une latitude et une longitude spécifiques
        m = folium.Map(location=[48.5, -3], zoom_start=8)
        # Définissez une liste de couleurs pour les clusters (une couleur par cluster)
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'darkblue', 'gray']

        # Ajoutez des marqueurs pour chaque point, en utilisant des couleurs différentes pour chaque cluster
        for i in range(len(data)):
            cluster = cluster_assignments[i]
            folium.CircleMarker([data[i, 0], data[i, 1]], radius=5, color=colors[cluster], fill=True,
                                fill_color=colors[cluster], stroke=False).add_to(m)

        # Sauvegardez la carte en tant que fichier HTML
        m.save('templates/clustering_map.html')
        
        # Continuez avec le reste du code pour le clustering

        #création df originales et les attributions de cluster
        df = pd.DataFrame(data, columns=['Latitude', 'Longitude'])
        df['Cluster'] = cluster_assignments

        # Calculez le nombre de points dans chaque cluster
        cluster_counts = df['Cluster'].value_counts()

        # Calculez la moyenne des coordonnées de latitude et de longitude pour chaque cluster
        cluster_means = df.groupby('Cluster').agg({'Latitude': 'mean', 'Longitude': 'mean'})

        # Renvoyer les résultats sous forme de JSON
        results = {
            "cluster_assignments": cluster_assignments.tolist(),
            "centres_clusters": centres_clusters.tolist(),
            "cluster_counts": cluster_counts.to_dict(),
            "cluster_means": cluster_means.to_dict()
        }

        return jsonify(results)

    else:
        return jsonify({"error": "Erreur lors de la requête à l'API. Code de statut : {}".format(response.status_code)})

# Endpoint pour afficher la carte Folium
@app.route('/map', methods=['GET'])
def show_map():
    return render_template('clustering_map.html')

if __name__ == '__main__':
    app.run(debug=True, port=5004)

