import os
import requests
import zipfile
from datetime import datetime
from flask import Flask, jsonify
import shutil


app = Flask(__name__)

def create_and_clear_directory(directory):
    # Créer le répertoire s'il n'existe pas
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        # Vider le répertoire s'il n'est pas vide
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)


@app.route('/telecharger-et-archiver', methods=['GET'])
def download_and_archive():
    url = "https://diffuseur.datatourisme.fr/webservice/faa865a44fc4b68d82b54901dcb692ee/f39995e9-0c1a-4aee-bc57-7338d1ef5eef"
    local_dir = os.environ.get('LOCAL_DIR', 'path_non_defini')
    # Créer un répertoire avec la date du jour
    date_today = datetime.now().strftime('%Y-%m-%d')
    destination_dir = os.path.join(local_dir, date_today)
    
    # Créer et vider le répertoire
    create_and_clear_directory(destination_dir)

    local_file_path = os.path.join(destination_dir, 'datatourisme.zip')

    # Télécharger le fichier .zip
    response = requests.get(url)
    with open(local_file_path, 'wb') as file:
        file.write(response.content)

    # Extraire le contenu du .zip
    with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)

    # Supprimer le fichier .zip
    os.remove(local_file_path)

    return jsonify({'local_directory': destination_dir})
if __name__ == '__main__':
    app.run(debug=True, port=5002)
