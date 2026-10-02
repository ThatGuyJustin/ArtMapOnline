import os
import sys

from flask import Flask, send_from_directory

from routes.api import api
from routes.artwork import artwork
from routes.media import media
from util.colors import setup_colors

app = Flask(__name__, static_folder='static')

with app.app_context():
    app.CACHE = getattr(sys.modules['builtins'], 'GLOBAL_SHARED_CACHE', {})
    app.color_map = setup_colors()

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(artwork, url_prefix='/api/artwork')
app.register_blueprint(media, url_prefix='/api/media')


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_or_spa(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_RUN_PORT', '8000')),
        use_reloader=True,
        reloader_type='stat',
        reloader_interval=1,
    )
