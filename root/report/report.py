from flask import jsonify, request
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['gla1']
reports_collection = db['reports']
threads_collection = db['threads']  # Ensure you have the threads collection

def get_reports():
    reports = list(reports_collection.find({}, {'_id': 1, 'reason': 1, 'details': 1, 'threadId': 1, 'timestamp': 1, 'approved': 1, 'approvalStatus': 1}))
    for report in reports:
        report['_id'] = str(report['_id'])
    return jsonify(reports), 200

def add_reports():
    data = request.json
    reason = data.get('reason')
    details = data.get('details')
    threadid = data.get('threadId')
    
    if not reason or not details or not threadid:
        return jsonify({'error': 'Reason, details, and thread ID are required'}), 400

    # Check if the thread ID exists in the threads collection
    if not threads_collection.find_one({'_id': ObjectId(threadid)}):
        return jsonify({'error': 'Invalid thread ID'}), 400

    report = {
        'reason': reason,
        'details': details,
        'threadId': threadid,
        'timestamp': datetime.now(),
        'approved': False,  # Default to not approved
        'approvalStatus': 'Pending'  # Initial status
    }
    result = reports_collection.insert_one(report)

    return jsonify({'message': 'Reported successfully', 'reportId': str(result.inserted_id), 'timestamp': report['timestamp']}), 201

def delete_report(report_id):
    try:
        report_id = ObjectId(report_id)  # Convert string ID to ObjectId
    except Exception as e:
        return jsonify({'error': 'Invalid report ID'}), 400

    result = reports_collection.delete_one({'_id': report_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Report not found'}), 404

    return jsonify({'message': 'Report deleted successfully'}), 200

def approve_report(report_id):
    try:
        report_id = ObjectId(report_id)  # Convert string ID to ObjectId
    except Exception as e:
        return jsonify({'error': 'Invalid report ID'}), 400

    result = reports_collection.update_one(
        {'_id': report_id},
        {'$set': {'approved': True, 'approvalStatus': 'Approved by Admin'}}
    )

    if result.modified_count == 0:
        return jsonify({'error': 'Report not found or already approved'}), 404

    return jsonify({'message': 'Report approved successfully'}), 200
