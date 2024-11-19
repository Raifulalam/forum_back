from flask import Blueprint,jsonify,request
from .profile import profile_collection
from bson.objectid import ObjectId

profile_bp = Blueprint('profile',__name__)

@profile_bp.route("/user/<user_id>", methods=["GET"])
def fetch_profile(user_id):
    user_data = get_profile(user_id)
    if user_data:
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404


@profile_bp.route("/update_bio", methods=["POST"])
def update_user_bio():
    data = request.json
    user_id = data.get("userId")
    bio = data.get("bio")
    if update_bio(user_id, bio):
        return jsonify({"message": "Bio updated successfully"}), 200
    return jsonify({"error": "Failed to update bio"}), 400

# Route to update interests
@profile_bp.route("/update_interests", methods=["POST"])
def update_user_interests():
    data = request.json
    user_id = data.get("userId")
    interests = data.get("interests")
    if update_interests(user_id, interests):
        return jsonify({"message": "Interests updated successfully"}), 200
    return jsonify({"error": "Failed to update interests"}), 400

# Route to follow/unfollow
@profile_bp.route("/toggle_follow", methods=["POST"])
def follow_unfollow():
    data = request.json
    user_id = data.get("userId")
    follow_user_id = data.get("followUserId")
    action = data.get("action")
    if toggle_follow(user_id, follow_user_id, action):
        return jsonify({"message": f"User {action}ed successfully"}), 200
    return jsonify({"error": "Failed to perform action"}), 400

# Get user profile data from MongoDB
def get_profile(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return {
            "fullName": user.get("fullName"),
            "email": user.get("email"),
            "avatarUrl": user.get("avatarUrl", "/avatar.png"),
            "bio": user.get("bio", ""),
            "interests": user.get("interests", ""),
            "followers": len(user.get("followers", [])),
            "following": len(user.get("following", []))
        }
    return None

# Update user bio in MongoDB
def update_bio(user_id, bio):
    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"bio": bio}})
    return result.modified_count > 0

# Update user interests in MongoDB
def update_interests(user_id, interests):
    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"interests": interests}})
    return result.modified_count > 0

# Handle follow/unfollow logic
def toggle_follow(user_id, follow_user_id, action):
    if action == "follow":
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"following": follow_user_id}}
        )
        db.users.update_one(
            {"_id": ObjectId(follow_user_id)},
            {"$addToSet": {"followers": user_id}}
        )
    else:  # unfollow
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"following": follow_user_id}}
        )
        db.users.update_one(
            {"_id": ObjectId(follow_user_id)},
            {"$pull": {"followers": user_id}}
        )
    
    return result.modified_count > 0

