from flask_restful import Api, Resource
from flask import request, jsonify
from root.db import mdb
from root.general.authUtils import validate_auth
from root.general.commonUtilis import strToMongoId
import os

class CurrentUser(Resource):
    @validate_auth(optional=True)
    def get(self, suid=None, suser=None):
        if not suid:
            return {"status": 0, "msg": "Not logged in", "payload": {}}

        dbUsers = "users"
        data = mdb[dbUsers].find_one(
            {"$or": [{"_id": strToMongoId(suid)}, {"uid": suid}]}
        )

        if not (data and "_id" in data):
            return {"status": 0, "msg": "Not logged in"}

        # Extracting user data
        user = {
            "fullName": data.get("fullName", ""),
            "avatarUrl": data.get("avatarUrl", ""),
            "userType": data.get("userType", ""),
            "ruid": data.get("_id", ""),
            "email": data.get("email", ""),
            "forceRedirectUrl": data.get("forceRedirectUrl", ""),
            "status": data.get("status", ""),
            "bio": data.get("bio", ""),
            "interests": data.get("interests", []),
            "skills": data.get("skills", []),
            "location": data.get("location", ""),
            "dob": data.get("dob", ""),
            "education": data.get("education", ""),
            "occupation": data.get("occupation", ""),
            "followers": data.get("followers", []),
            "following": data.get("following", []),
        }

        return {
            "status": 1,
            "msg": "Success",
            "payload": user,
        }

    @validate_auth(optional=True)
    def put(self, suid=None, suser=None):
        if not suid:
            return {"status": 0, "msg": "Not logged in", "payload": {}}

        input_data = request.form.to_dict()  # Changed to handle form data

        # Handle image upload
        avatar_file = request.files.get('avatar')
        if avatar_file:
            # Save the file
            upload_folder = 'path/to/upload/directory'  # Set your upload directory
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            avatar_filename = f"{suid}_{avatar_file.filename}"
            avatar_path = os.path.join(upload_folder, avatar_filename)
            avatar_file.save(avatar_path)

            # Update the avatar URL in the database
            input_data['avatarUrl'] = avatar_path  # Update the path as needed

        # Define the fields you want to update
        update_fields = {
            "fullName": input_data.get("fullName"),
            "avatarUrl": input_data.get("avatarUrl"),
            "bio": input_data.get("bio"),
            "interests": input_data.get("interests"),
            "skills": input_data.get("skills"),
            "location": input_data.get("location"),
            "dob": input_data.get("dob"),
            "education": input_data.get("education"),
            "occupation": input_data.get("occupation"),
        }

        # Clean up empty fields to avoid overwriting with None
        update_fields = {k: v for k, v in update_fields.items() if v is not None}

        # Optionally restrict updates to followers and following
        if 'followers' in input_data or 'following' in input_data:
            return {
                "status": 0,
                "msg": "You cannot directly update followers or following.",
                "payload": {}
            }, 400

        # Update the user in the database
        result = mdb["users"].update_one(
            {"$or": [{"_id": strToMongoId(suid)}, {"uid": suid}]},
            {"$set": update_fields}
        )

        if result.modified_count > 0:
            return {
                "status": 1,
                "msg": "Profile updated successfully.",
                "payload": {}
            }
        else:
            return {
                "status": 0,
                # "msg": "No changes made or user not found.",
                "payload": {}
            }
class FollowUser(Resource):
    @validate_auth(optional=False)
    def post(self, user_id, suid=None, suser=None):
        if not user_id:
            return {"status": 0, "msg": "No user specified"}

        current_user = mdb["users"].find_one({"_id": strToMongoId(suid)})
        if user_id in current_user.get("following", []):
            return {"status": 0, "msg": "Already following"}

        mdb["users"].update_one(
            {"_id": strToMongoId(suid)},
            {"$addToSet": {"following": user_id}}
        )

        mdb["users"].update_one(
            {"_id": strToMongoId(user_id)},
            {"$addToSet": {"followers": suid}}
        )

        return {"status": 1, "msg": "Followed successfully"}

class UnfollowUser(Resource):
    @validate_auth(optional=False)
    def post(self, user_id, suid=None, suser=None):
        if not user_id:
            return {"status": 0, "msg": "No user specified"}

        current_user = mdb["users"].find_one({"_id": strToMongoId(suid)})
        if user_id not in current_user.get("following", []):
            return {"status": 0, "msg": "Not following the user"}

        mdb["users"].update_one(
            {"_id": strToMongoId(suid)},
            {"$pull": {"following": user_id}}
        )

        mdb["users"].update_one(
            {"_id": strToMongoId(user_id)},
            {"$pull": {"followers": suid}}
        )

        return {"status": 1, "msg": "Unfollowed successfully"}
