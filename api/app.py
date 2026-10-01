import logging
import os

from flask import Flask, Blueprint, current_app, request
from flask_cors import CORS

from routes.artwork import artwork
from routes.media import media
from util.colors import setup_colors

app = Flask(__name__)

with app.app_context():
    app.CACHE = {}
    app.color_map = setup_colors()

api = Blueprint('api', __name__)

ENABLE_DEBUG = bool(os.environ.get('ENABLE_DEBUG', False))
FLASK_HOST = os.environ.get('FLASK_HOST', 'localhost')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))

@api.get('/hello-world')
def hello_world():
    return { 'code': 200, "message": "Hello World. 🌍" }

@api.get('/colors')
def get_colors():
    return app.color_map


if __name__ == '__main__':
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(artwork, url_prefix='/api/artwork')
    app.register_blueprint(media, url_prefix='/api/media')

    CORS(app)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=ENABLE_DEBUG)