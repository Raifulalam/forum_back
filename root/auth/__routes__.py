from root.auth.auth import ForgetPassword, Login, UserLogout, UserRegister
from root.general.currenUser import CurrentUser,FollowUser,UnfollowUser




# auth/__routes__.py
from flask_restful import Api,Resource
from . import auth_api

 # Adjust based on your structure

# Register the resources with the API
auth_api.add_resource(Login, "/api/login")
auth_api.add_resource(UserRegister, "/api/register")
auth_api.add_resource(ForgetPassword, "/api/forget-password")
auth_api.add_resource(UserLogout, "/api/user/logout")
auth_api.add_resource(CurrentUser, "/api/currentUser")
auth_api.add_resource(FollowUser,"/api/follow/<string:user_id>")
auth_api.add_resource(UnfollowUser,"/api/unfollow/<string:user_id>")

