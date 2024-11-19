from flask import Blueprint, jsonify, request
from bson import ObjectId
from .homePage import threads_collection  # Importing the threads collection

home_bp = Blueprint('home', __name__)

# Existing route to get all threads
@home_bp.route('/threads', methods=['GET'])
def get_threads():
    try:
        threads = list(threads_collection.find({}, {'_id': 1, 'title': 1, 'content': 1, 'comments': 1}))
        for thread in threads:
            thread['_id'] = str(thread['_id'])
        return jsonify(threads), 200
    except Exception as e:
        return jsonify({'error': 'Unable to fetch threads', 'details': str(e)}), 500

@home_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    try:
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)})
        if thread:
            thread['_id'] = str(thread['_id'])
            return jsonify(thread), 200
        else:
            return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to fetch thread', 'details': str(e)}), 500

# Existing route to add a new thread
@home_bp.route('/threads', methods=['POST'])
def add_thread():
    data = request.json
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    try:
        thread = {'title': title, 'content': content, 'comments': [], 'likes': 0, 'dislikes': 0}
        inserted_id = threads_collection.insert_one(thread).inserted_id
        return jsonify({'message': 'Thread created successfully', '_id': str(inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': 'Unable to create thread', 'details': str(e)}), 500

# New route to delete a thread
@home_bp.route('/threads/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    try:
        result = threads_collection.delete_one({'_id': ObjectId(thread_id)})

        if result.deleted_count == 1:
            return jsonify({'message': 'Thread deleted successfully'}), 200
        else:
            return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to delete thread', 'details': str(e)}), 500

# Route to add a comment
@home_bp.route('/threads/<thread_id>/comments', methods=['POST'])
def add_comment(thread_id):
    data = request.json
    comment_text = data.get('text')

    if not comment_text:
        return jsonify({'error': 'Comment text is required'}), 400

    try:
        comment_id = str(ObjectId())
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$push': {'comments': {'_id': comment_id, 'text': comment_text, 'replies': []}}}  # Add replies array
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Comment added successfully', '_id': comment_id}), 201
        else:
            return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to add comment', 'details': str(e)}), 500

# New route to get comments for a thread
@home_bp.route('/threads/<thread_id>/comments', methods=['GET'])
def get_comments(thread_id):
    try:
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)}, {'comments': 1})
        if thread:
            return jsonify(thread.get('comments', [])), 200
        else:
            return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to fetch comments', 'details': str(e)}), 500

# New route to delete a comment
@home_bp.route('/threads/<thread_id>/comments', methods=['DELETE'])
def delete_comment(thread_id):
    data = request.json
    comment_id = data.get('_id')

    if not comment_id:
        return jsonify({'error': 'Comment ID is required'}), 400

    try:
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$pull': {'comments': {'_id': comment_id}}}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Comment deleted successfully'}), 200
        else:
            return jsonify({'error': 'Comment not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to delete comment', 'details': str(e)}), 500




# Route to like a thread
@home_bp.route('/threads/<thread_id>/like', methods=['POST'])
def like_thread(thread_id):
    user_id = request.json.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)})

        if not thread:
            return jsonify({"error": "Thread not found"}), 404

        if user_id in thread.get('liked_by', []):
            return jsonify({"message": "User already liked this thread"}), 400

        # If the user has disliked the thread, remove them from 'disliked_by'
        if user_id in thread.get('disliked_by', []):
            threads_collection.update_one(
                {'_id': ObjectId(thread_id)},
                {'$pull': {'disliked_by': user_id}, '$inc': {'dislikes': -1}}
            )

        # Add the user to 'liked_by' and increment the like count
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$push': {'liked_by': user_id}, '$inc': {'likes': 1}}
        )

        if result.modified_count == 1:
            return jsonify({"message": "Thread liked successfully"}), 200
        else:
            return jsonify({"error": "Unable to like the thread"}), 500
    except Exception as e:
        return jsonify({'error': 'Error liking thread', 'details': str(e)}), 500


# Route to dislike a thread
@home_bp.route('/threads/<thread_id>/dislike', methods=['POST'])
def dislike_thread(thread_id):
    user_id = request.json.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)})

        if not thread:
            return jsonify({"error": "Thread not found"}), 404

        if user_id in thread.get('disliked_by', []):
            return jsonify({"message": "User already disliked this thread"}), 400

        # If the user has liked the thread, remove them from 'liked_by'
        if user_id in thread.get('liked_by', []):
            threads_collection.update_one(
                {'_id': ObjectId(thread_id)},
                {'$pull': {'liked_by': user_id}, '$inc': {'likes': -1}}
            )

        # Add the user to 'disliked_by' and increment the dislike count
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$push': {'disliked_by': user_id}, '$inc': {'dislikes': 1}}
        )

        if result.modified_count == 1:
            return jsonify({"message": "Thread disliked successfully"}), 200
        else:
            return jsonify({"error": "Unable to dislike the thread"}), 500
    except Exception as e:
        return jsonify({'error': 'Error disliking thread', 'details': str(e)}), 500


# Route to unlike a thread
@home_bp.route('/threads/<thread_id>/unlike', methods=['POST'])
def unlike_thread(thread_id):
    user_id = request.json.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$pull': {'liked_by': user_id}, '$inc': {'likes': -1}}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Thread unliked successfully'}), 200
        else:
            return jsonify({'error': 'Thread not found or user has not liked this thread'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to unlike thread', 'details': str(e)}), 500


# Route to undislike a thread
@home_bp.route('/threads/<thread_id>/undislike', methods=['POST'])
def undislike_thread(thread_id):
    user_id = request.json.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id)},
            {'$pull': {'disliked_by': user_id}, '$inc': {'dislikes': -1}}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Thread undisliked successfully'}), 200
        else:
            return jsonify({'error': 'Thread not found or user has not disliked this thread'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to undislike thread', 'details': str(e)}), 500

@home_bp.route('/threads/<thread_id>/likes_dislikes', methods=['GET'])
def get_likes_dislikes(thread_id):
    try:
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)}, {'likes': 1, 'dislikes': 1})

        if thread:
            return jsonify({
                'likes': thread.get('likes', 0),
                'dislikes': thread.get('dislikes', 0),
               
            }), 200
        else:
            return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to fetch likes/dislikes', 'details': str(e)}), 500

# Route to reply to a comment
@home_bp.route('/threads/<thread_id>/comments/<comment_id>/reply', methods=['POST'])
def reply_to_comment(thread_id, comment_id):
    data = request.json
    reply_text = data.get('text')
    
    if not reply_text:
        return jsonify({"error": "Reply text is required"}), 400
    
    try:
        # Add reply to the specified comment
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id), 'comments._id': comment_id},
            {'$push': {'comments.$.replies': reply_text}}  # Use positional operator to target the correct comment
        )

        if result.modified_count == 1:
            return jsonify({"message": "Reply added successfully"}), 201
        else:
            return jsonify({"error": "Comment not found"}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to add reply', 'details': str(e)}), 500

# Route to edit a comment
@home_bp.route('/threads/<thread_id>/comments/<comment_id>', methods=['PUT'])
def edit_comment(thread_id, comment_id):
    data = request.json
    new_text = data.get('text')

    if not new_text:
        return jsonify({'error': 'New text is required'}), 400

    try:
        result = threads_collection.update_one(
            {'_id': ObjectId(thread_id), 'comments._id': comment_id},
            {'$set': {'comments.$.text': new_text}}  # Update the comment text
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Comment edited successfully'}), 200
        else:
            return jsonify({'error': 'Comment not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Unable to edit comment', 'details': str(e)}), 500
