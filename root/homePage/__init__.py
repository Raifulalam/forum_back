# __init__.py
from flask import Flask
from flask_cors import CORS
from .__route__ import home_bp 

def create_app():
    app = Flask(__name__)
    CORS(app) 
    app.register_blueprint(home_bp) 
    return app
