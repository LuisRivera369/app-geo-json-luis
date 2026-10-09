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
        # Leer primera banda
        data = dataset.read(1)
        # Reemplazar valores NoData o nan por None
        nodata = dataset.nodata if dataset.nodata is not None else 0
        data = np.where(data == nodata, None, data)
        
        # Limitar decimales para reducir el tamaño del JSON
        data_rounded = np.where(data != None, np.round(data.astype(float), 2), None).tolist()

        return jsonify({
            "bounds": [
                [dataset.bounds.bottom, dataset.bounds.left],
                [dataset.bounds.top, dataset.bounds.right]
            ],
            "width": dataset.width,
            "height": dataset.height,
            "data": data_rounded
        })

@app.route('/')
def index():
    return "<h3>Server running!!</h3>"  # ← faltaba cerrar la etiqueta

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
