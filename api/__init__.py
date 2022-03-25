import os
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
import click
from flask.cli import with_appcontext
from flask_restx import Api

from flask_jwt_extended import JWTManager

from flask_security import current_user, login_required, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin

from flask_cors import CORS


from config import db,config

from .user_account.models import User, Driver, Truck
from .quarter_entries.models import NewEntry, Quarter, StateQuarterReport, StateTax

from .user_account.views import user_account_namespace
from .quarter_entries.views import quarter_taxes_namespace







# ========================================================
# Create App
# ========================================================
def create_app(config_env='development'):
    config_map = {
            'development': config.DevelopmentConfig(),
            'testing': config.TestingConfig(),
            'production': config.ProductionConfig(),
    }

    config_obj = config_map[config_env]

    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    CORS(app)

    app.config.from_object(config_obj)

    
    db.init_app(app)
    migrate = Migrate(app, db)

    jwt = JWTManager(app)


    api = Api(app, doc='/api')

    api.add_namespace(user_account_namespace, path='/user-account')
    api.add_namespace(quarter_taxes_namespace, path='/quarter-taxes')

    


    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
        }



    return app