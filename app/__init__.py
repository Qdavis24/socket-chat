from flask import Flask
import os


from .extensions import socketio
from .views import views


def create_app():
    app = Flask(__name__)
    socketio.init_app(app)
    app.config['SECRET_KEY'] = os.environ.get('secret_key')
    app.register_blueprint(views)

    return app, socketio
