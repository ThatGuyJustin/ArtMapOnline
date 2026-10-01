from flask import current_app, Blueprint

api = Blueprint('api', __name__)

@api.get('/hello-world')
def hello_world():
    return {'code': 200, "message": "Hello World. 🌍"}


@api.get('/colors')
def get_colors():
    return current_app.color_map
