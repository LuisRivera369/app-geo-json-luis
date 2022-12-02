import rasterio
import geopandas as gpd
from rasterio import features
from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r"/*":{
        "origins": "*"
    }
})

with rasterio.open('images/Pronostico_Agosto_TMin.tiff') as dataset:
    band = dataset.read()
    mask = band != 0
    shapes = features.shapes(band, mask=mask, transform=dataset.transform)

# Funcion de compresion : generator object
fc = ({"geometry": shape, "properties": {"value": value}}
      for shape, value in shapes)

jsonData = gpd.GeoDataFrame.from_features(fc).to_json()

@app.route('/')
def index():
    return "<h3>Server running!!<h3>"

@app.route('/geoJSON')
def pint():
    return json.loads(jsonData)

if __name__ == '__main__':
    app.run(debug= True)