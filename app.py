import os
import rasterio
import geopandas as gpd
from rasterio import features
from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # ← una sola vez, con origins por defecto (todas)

# Cargar el TIFF una sola vez al arrancar
TIFF_PATH = os.path.join(os.path.dirname(__file__), 'images', 'Pronostico_Agosto_TMin.tiff')

with rasterio.open(TIFF_PATH) as dataset:
    band = dataset.read()
    mask = band != 0
    shapes = features.shapes(band, mask=mask, transform=dataset.transform)

fc = ({"geometry": shape, "properties": {"value": value}}
      for shape, value in shapes)

jsonData = gpd.GeoDataFrame.from_features(fc).to_json()

@app.route('/')
def index():
    return "<h3>Server running!!</h3>"  # ← faltaba cerrar la etiqueta

@app.route('/geoJSON')
def geojson():
    return jsonify(json.loads(jsonData))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
