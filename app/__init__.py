import os
from flask import Flask, jsonify, g
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config_name):
    """Create an application instance"""
    app = Flask(__name__)

    # apply configuration
    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)

    # initialize extensions
    db.init_app(app)

    # import blueprints
    from .api_v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    from .api_auth import api_auth as api_authentication
    app.register_blueprint(api_authentication, url_prefix='/auth')

    # authentication token route
    from .auth import auth

    return app
