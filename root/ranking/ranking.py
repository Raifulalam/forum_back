# app/ranking.py

from flask import jsonify, request
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import random

client = MongoClient('mongodb://localhost:27017/')
db = client['gla1']  # Use the existing database gla1
users_collection = db['users']  # Use the existing users collection
activities_collection = db['activities']  # Ensure you have the activities collection

def get_users():
    users = list(users_collection.find({}, {'_id': False}))
    return jsonify(sorted(users, key=lambda x: x['points'], reverse=True))

def get_activities():
    activities = list(activities_collection.find({}, {'_id': False}).sort('timestamp', -1).limit(10))
    return jsonify(activities)

def update_points():
    users = list(users_collection.find())
    for user in users:
        # Check if 'name' key exists
        if 'fullName' not in user:
            continue  # Skip this user if the name is missing
        
        points_increase = random.randint(0, 10)
        users_collection.update_one({'_id': user['_id']}, {'$inc': {'points': points_increase}})

        if points_increase > 0:
            activity = {
                'user': user['fullName'],
                'action': f'earned {points_increase} points',
                'timestamp': datetime.now().isoformat()
            }
            activities_collection.insert_one(activity)

    return jsonify({'message': 'Points updated successfully'})

