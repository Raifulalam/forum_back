# app/__init__.py
from flask import Flask
from flask_cors import CORS
from .routes import report_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(report_bp)

    return app
