
import os
import io
from flask import Flask, jsonify, abort, send_file
from lumc import LUMCPollenClient, PollenNotFound

app = Flask(__name__)
client = LUMCPollenClient()

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/pollen')
def list_pollen():
    table = client.get_table()
    return jsonify(table)

@app.get('/pollen/<string:name>/total')
def pollen_total(name: str):
    try:
        total = client.get_total(name)
    except PollenNotFound:
        abort(404, description=f"Pollen '{name}' not found")
    return jsonify({'name': name, 'total': total})

@app.get('/pollen/<string:name>/history/url')
def pollen_history_url(name: str):
    try:
        url = client.get_history_graph_url(name)
    except PollenNotFound:
        abort(404, description=f"Pollen '{name}' not found")
    return jsonify({'name': name, 'url': url})

@app.get('/pollen/<string:name>/history/image')
def pollen_history_image(name: str):
    try:
        png_bytes = client.get_history_graph_png(name)
    except PollenNotFound:
        abort(404, description=f"Pollen '{name}' not found")
    # Stream the PNG bytes directly
    return send_file(io.BytesIO(png_bytes), mimetype='image/png', download_name=f"{name}.png")

@app.get('/pollen/names')
def pollen_names():
    names = client.list_names()
    return jsonify(names)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)
