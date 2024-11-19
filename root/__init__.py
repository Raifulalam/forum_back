from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.debug = True
    CORS(app, resources={r"/*": {"origins": "*"}})

    jwt = JWTManager()

    api = Api(app)

    from root.home import Home
    api.add_resource(Home, "/", endpoint="Home")

    from root.auth import auth_bp
    app.register_blueprint(auth_bp)
    from root.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    
    from root.report import report_bp
    app.register_blueprint(report_bp, url_prefix="/")
    
    from root.homePage import home_bp
    app.register_blueprint(home_bp,url_prefix="/")
    
    from root.ranking import ranking_bp
    app.register_blueprint(ranking_bp, url_prefix="/")



    api.init_app(app)
    jwt.init_app(app)

    return app
