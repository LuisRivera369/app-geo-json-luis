import os
import rasterio
import numpy as np
from rasterio.warp import transform_bounds  # ← Cambiado .warper por .warp
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TIFF_PATH = os.path.join(os.path.dirname(__file__), 'images', 'Pronostico_Agosto_TMin.tiff')

@app.route('/api/raster-data')
def get_raster_data():
    with rasterio.open(TIFF_PATH) as dataset:
        data = dataset.read(1).astype(float)
        nodata = dataset.nodata
        
        if nodata is not None:
            data[data == nodata] = np.nan

        # Transformar los límites a EPSG:4326 (Lat/Lng) si el TIFF viene en otro sistema (ej. UTM)
        if dataset.crs and dataset.crs.to_string() != 'EPSG:4326':
            wgs84_bounds = transform_bounds(dataset.crs, 'EPSG:4326', *dataset.bounds)
        else:
            wgs84_bounds = dataset.bounds

        cleaned_data = [
            [
                None if (np.isnan(val) or np.isinf(val)) else round(float(val), 2)
                for val in row
            ]
            for row in data
        ]

        return jsonify({
            "bounds": [
                [wgs84_bounds[1], wgs84_bounds[0]], # [South, West]
                [wgs84_bounds[3], wgs84_bounds[2]]  # [North, East]
            ],
            "width": dataset.width,
            "height": dataset.height,
            "data": cleaned_data
        })

@app.route('/')
def index():
    return "<h3>Server running!!</h3>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
