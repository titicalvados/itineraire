import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/telecharger-et-archiver', methods=['GET'])
def download_and_archive():
    url = "https://diffuseur.datatourisme.fr/webservice/faa865a44fc4b68d82b54901dcb692ee/f39995e9-0c1a-4aee-bc57-7338d1ef5eef"
    local_dir = os.environ.get('LOCAL_DIR', 'path_non_defini')
    local_file_path = os.path.join(local_dir, 'datatourisme.zip')

    # Télécharger le fichier .zip
    response = requests.get(url)
    with open(local_file_path, 'wb') as file:
        file.write(response.content)

    # Extraire le contenu du .zip
    with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
        zip_ref.extractall(local_dir)

    return jsonify({'local_file_path': local_file_path})

if __name__ == '__main__':
    app.run(debug=True)
