import os
import requests
import zipfile
from time import time
from datetime import datetime
from flask import Flask, jsonify
import shutil


app = Flask(__name__)

def create_and_clear_directory(directory):
    # Supprimer le répertoire et tout son contenu s'il existe
    if os.path.exists(directory):
        shutil.rmtree(directory)
    # le créer
    os.makedirs(directory)

@app.route('/telecharger-et-archiver', methods=['GET'])
def download_and_archive():
    t0 = time()
    url = "https://diffuseur.datatourisme.fr/webservice/faa865a44fc4b68d82b54901dcb692ee/f39995e9-0c1a-4aee-bc57-7338d1ef5eef"
    # Créer un répertoire avec la date du jour
    date_today = datetime.now().strftime('%Y-%m-%d')
    destination_dir = os.path.join('/home/datatourisme', date_today)
    print("répertoire d'importation:",destination_dir) 
    
    # Créer et vider le répertoire
    create_and_clear_directory(destination_dir)

    local_file_path = os.path.join(destination_dir, 'datatourisme.zip')

    # Télécharger le fichier .zip
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        # Extraire le contenu du .zip
        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            zip_ref.extractall(destination_dir)

        # Supprimer le fichier .zip
        os.remove(local_file_path)
    
    tt = time() - t0
    status = 'Import datatourisme fait en {} secondes'.format(round(tt,3))
    return jsonify({'datatourisme_response_code':response.status_code,'status':status,'local_directory': destination_dir})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
