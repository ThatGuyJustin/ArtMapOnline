from flask import Flask

from routes.api import api
from routes.artwork import artwork
from routes.media import media
from util.colors import setup_colors

app = Flask(__name__, static_folder='static', static_url_path='')

with app.app_context():
    app.CACHE = {}
    app.color_map = setup_colors()

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(artwork, url_prefix='/api/artwork')
app.register_blueprint(media, url_prefix='/api/media')

@app.get("/")
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()