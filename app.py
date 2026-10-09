import os
import rasterio
import numpy as np
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TIFF_PATH = os.path.join(os.path.dirname(__file__), 'images', 'Pronostico_Agosto_TMin.tiff')

@app.route('/api/raster-data')
def get_raster_data():
    with rasterio.open(TIFF_PATH) as dataset:
        # 1. Leer la primera banda como float para manejar decimales y NoData
        data = dataset.read(1).astype(float)
        
        # 2. Obtener el valor de NoData del dataset (o definirlo si es 0 / -9999 / nan)
        nodata = dataset.nodata
        
        # 3. Limpiar valores NoData e Infinitos usando funciones de NumPy
        if nodata is not None:
            data[data == nodata] = np.nan
            
        # Reemplazar valores no válidos (NaN o Inf) con None explícito de Python
        cleaned_data = [
            [
                None if (np.isnan(val) or np.isinf(val)) else round(float(val), 2)
                for val in row
            ]
            for row in data
        ]

        return jsonify({
            "bounds": [
                [dataset.bounds.bottom, dataset.bounds.left],
                [dataset.bounds.top, dataset.bounds.right]
            ],
            "width": dataset.width,
            "height": dataset.height,
            "data": cleaned_data
        })

@app.route('/')
def index():
    return "<h3>Server running!!</h3>"  # ← faltaba cerrar la etiqueta

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
