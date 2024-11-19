import logging
import uuid
from flask import request, jsonify, url_for
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from marshmallow import Schema, fields, validates, ValidationError
from root.db import mdb
from root.general.commonUtilis import (
    bcryptPasswordHash,
    cleanupEmail,
    maskEmail,
    mdbObjectIdToStr,
    verifyPassword,
)
from root.general.authUtils import validate_auth
from root.static import G_ACCESS_EXPIRES
from flask_limiter import Limiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=lambda: request.remote_addr)

# Validation schema for User Registration
# Validation schema for User Registration
class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=lambda p: len(p) >= 6)
    fullName = fields.String(required=True)
    avatarUrl = fields.String(missing="/avatar.svg")
    bio = fields.String(missing="")
    interests = fields.List(fields.String(), missing=[]) 
    skills = fields.List(fields.String(), missing=[])     
    location = fields.String(missing="")
    dob = fields.String(missing="")
    education = fields.String(missing="")
    occupation = fields.String(missing="")
    followers = fields.List(fields.String(), missing=[])  # New field
    following = fields.List(fields.String(), missing=[])  # New field

    @validates('email')
    def validate_email(self, value):
        if len(value) == 0:
            raise ValidationError('Email cannot be empty.')

    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError('Password must be at least 6 characters long.')


# Validation schema for Login
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

def handle_error(message, status_code=400, payload=None):
    logger.error(message)
    response = {
        "status": 0,
        "cls": "error",
        "msg": message,
        "payload": payload or {}
    }
    return jsonify(response), status_code

class Login(Resource):
    @limiter.limit("5 per minute")  # Rate limit for login attempts
    def post(self):
        data = request.get_json()

        # Validate input data
        schema = LoginSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            logger.error(f"Login validation error: {err.messages}")
            return jsonify({
                "status": 0,
                "cls": "error",
                "msg": "Invalid input",
                "payload": err.messages
            }), 400

        email = validated_data.get("email")
        password = validated_data.get("password")

        return login({"email": email, "password": password}, {})

def login(data, filter, isRedirect=True):
    email = cleanupEmail(data.get("email"))
    filter = {"email": email, "status": {"$nin": ["deleted", "removed", "suspended"]}}

    userDoc = mdb.users.find_one(filter)

    if not (userDoc and "_id" in userDoc):
        logger.warning(f"Login failed for email: {email}")
        return jsonify({
            "status": 0,
            "cls": "error",
            "msg": "Invalid credentials. Please try again.",
        })

    userStatus = userDoc.get("status")
    if userStatus == "pending":
        return jsonify({
            "status": 0,
            "cls": "error",
            "msg": "Your request is still pending. Contact admin for more info",
            "payload": {
                "redirect": "/adminApproval",
                "userMeta": userDoc,
            },
        })

    if not verifyPassword(userDoc["password"], data.get("password")):
        logger.warning(f"Incorrect password attempt for email: {email}")
        return jsonify({
            "status": 0,
            "cls": "error",
            "msg": "Invalid credentials. Please try again.",
        })

    uid = mdbObjectIdToStr(userDoc["_id"])
    access_token = create_access_token(identity=uid, expires_delta=G_ACCESS_EXPIRES)

    payload = {
        "accessToken": access_token,
        "uid": uid,
        "redirectUrl": "/dashboard",
    }

    logger.info(f"User {email} logged in successfully.")
    return jsonify({
        "status": 1,
        "cls": "success",
        "msg": "Login successful. Redirecting...",
        "payload": payload,
    })

class UserLogout(Resource):
    @validate_auth(optional=True)
    def post(self, suid, suser):
        logger.info(f"User {suid} logged out successfully.")
        return jsonify({
            "status": 1,
            "cls": "success",
            "msg": "Logged out successfully!",
        })



class UserRegister(Resource):
    @validate_auth(optional=True)
    def post(self, suid, suser):
        input_data = request.get_json(silent=True)

        schema = UserRegistrationSchema()
        try:
            validated_data = schema.load(input_data)
        except ValidationError as err:
            logger.error(f"Registration validation error: {err.messages}")
            return jsonify({
                "status": 0,
                "cls": "error",
                "msg": "Invalid input",
                "payload": err.messages
            }), 400

        email = validated_data["email"].lower().strip()
        
        # Ensure interests and skills are lists
        validated_data['interests'] = validated_data.get('interests', [])
        validated_data['skills'] = validated_data.get('skills', [])
        validated_data['followers'] = []  # Initialize followers
        validated_data['following'] = []  # Initialize following

        # Check if email already exists
        existing_user = mdb.users.find_one({"email": email})
        if existing_user:
            maskedEmail = maskEmail(email)
            logger.warning(f"Registration failed: Email ID ({maskedEmail}) already exists.")
            return jsonify({
                "status": 0,
                "cls": "error",
                "msg": f"Email ID ({maskedEmail}) already exists. Please use a different email.",
                "payload": {}
            }), 400

        # Create a new user if no existing user is found
        password = validated_data["password"]
        newPassword = bcryptPasswordHash(password)

        newUser = {
            "email": email,
            "password": newPassword,
            "fullName": validated_data["fullName"],
            "avatarUrl": validated_data.get("avatarUrl", "/avatar.svg"),
            "status": "active",
            "bio": validated_data["bio"],
            "interests": validated_data["interests"],
            "skills": validated_data["skills"],
            "location": validated_data["location"],
            "dob": validated_data["dob"],
            "education": validated_data["education"],
            "occupation": validated_data["occupation"],
            "followers": validated_data['followers'],  # Include followers
            "following": validated_data['following'],  # Include following
        }

        mdb.users.insert_one(newUser)
        logger.info(f"New user registered: {validated_data['fullName']} ({email})")

        return jsonify({
            "status": 1,
            "cls": "success",
            "msg": "Registration successful. You can now log in.",
            "payload": {
                "redirectUrl": "/login"  # Include redirect URL for client-side handling
            }
        }), 201

class ForgetPasswordSchema(Schema):
    email = fields.Email(required=True)

class ForgetPassword(Resource):
    def post(self):
        data = request.get_json()

        # Validate input data using the schema
        schema = ForgetPasswordSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            logger.error(f"Password reset validation error: {err.messages}")
            return {
                "status": 0,
                "cls": "error",
                "msg": "Invalid input",
                "payload": err.messages
            }, 400

        email = cleanupEmail(validated_data.get("email"))
        user = mdb.users.find_one({"email": email})

        if not (user and "_id" in user):
            logger.warning(f"Password reset attempt for non-existing email: {email}")
            return {
                "status": 0,
                "cls": "error",
                "msg": "User not found",
                "payload": {},
            }

        # Generate reset token
        reset_token = str(uuid.uuid4())
        reset_link = url_for('reset_password', token=reset_token, _external=True)  # Create a reset link
        
        # Store the token in the database with the user
        mdb.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"reset_token": reset_token}}  # Save the reset token for validation
        )

        logger.info(f"Password reset link sent to email: {newUser.email}. Link: {reset_link}")
        return {
            "status": 1,
            "cls": "success",
            "msg": "A password reset link has been sent to your email address.",
            "payload": {}
        }

class CurrentUser(Resource):
    @validate_auth()
    def get(self):
        user_id = request.user['ruid']  # Assuming user ID is stored in request context
        user = mdb.users.find_one({"_id": strToMongoId(user_id)}, {"password": 0})  # Exclude password field

        if user:
            logger.info(f"Retrieved user info for user ID: {user_id}")
            return jsonify({
                "status": 1,
                "msg": "User info retrieved successfully",
                "payload": user
            }), 200
        else:
            logger.warning(f"User not found for user ID: {user_id}")
            return jsonify({
                "status": 0,
                "msg": "User not found",
                "payload": {}
            }), 404

class UserUpdate(Resource):
    @validate_auth()
    def post(self):
        user_id = request.user['ruid']
        input_data = request.form.to_dict()  # Accept form data

        # Handle avatar upload
        avatar_file = request.files.get('avatar')
        if avatar_file:
            # Save the uploaded file
            upload_folder = 'path/to/upload/directory'  # Set your upload directory
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            avatar_filename = f"{user_id}_{avatar_file.filename}"
            avatar_path = os.path.join(upload_folder, avatar_filename)
            avatar_file.save(avatar_path)

            # Update the avatar URL in the input data
            input_data['avatarUrl'] = avatar_path  # Update with the correct path

        # Ensure interests and skills are lists
        if 'interests' in input_data and not isinstance(input_data['interests'], list):
            input_data['interests'] = [input_data['interests']]
        if 'skills' in input_data and not isinstance(input_data['skills'], list):
            input_data['skills'] = [input_data['skills']]

        # Update user in the database
        result = mdb.users.update_one({"_id": strToMongoId(user_id)}, {"$set": input_data})

        if result.modified_count > 0:
            logger.info(f"User ID {user_id} updated successfully.")
            return jsonify({
                "status": 1,
                "msg": "User updated successfully."
            }), 200
        else:
            logger.warning(f"No changes made for User ID: {user_id}.")
            return jsonify({
                "status": 0,
                "msg": "No changes made."
            }), 400

    