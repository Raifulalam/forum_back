# homePage.py
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

# Initialize the Blueprint
home_bp = Blueprint('home', __name__)
CORS(home_bp)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['gla1']
threads_collection = db['threads']

