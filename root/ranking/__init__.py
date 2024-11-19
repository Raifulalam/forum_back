# app/__init__.py

from flask import Flask
from flask_cors import CORS
from .routes import ranking_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(ranking_bp)

    return app
