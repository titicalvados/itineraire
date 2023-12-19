# Utilisez l'image Python officielle
FROM python:3.9-slim

# Définissez la variable d'environnement PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED 1

# Définissez une variable d'environnement pour le répertoire de travail
ARG APP_DIR=/app
WORKDIR $APP_DIR

# Copiez d'abord seulement le fichier requirements.txt
COPY requirements.txt $APP_DIR/requirements.txt

# Installez les dépendances directement
RUN pip install --no-cache-dir --use-feature=fast-deps -r $APP_DIR/requirements.txt

# Copiez le reste du code
COPY . $APP_DIR

# Exposez le port sur lequel l'application Flask écoute
EXPOSE 5004

# Commande pour exécuter l'application Flask
CMD python3 clustering_poi_kmeans.py
