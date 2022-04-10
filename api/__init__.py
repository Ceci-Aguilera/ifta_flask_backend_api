import os
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
import click
from flask.cli import with_appcontext
from flask_restx import Api
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_jwt_extended import JWTManager

from flask_security import current_user, login_required, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin

from flask_cors import CORS
from flask_mail import Mail


from config import db,config

from .user_account.models import User, Driver, Truck
from .quarter_entries.models import NewEntry, Quarter, StateQuarterReport, StateTax
from .admin.models import UserAdmin, Role

from .user_account.views import user_account_namespace
from .quarter_entries.views import quarter_taxes_namespace, staff_namespace
from .admin.views import *



mail = Mail()



# ========================================================
# Create App
# ========================================================
def create_app(config_env='testing'):
    config_map = {
            'development': config.DevelopmentConfig(),
            'testing': config.TestingConfig(),
            'production': config.ProductionConfig(),
    }

    config_obj = config_map[config_env]

    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    CORS(app)

    app.config.from_object(config_obj)

    user_datastore = SQLAlchemyUserDatastore(db, UserAdmin, Role)
    security = Security(app, user_datastore)

    
    db.init_app(app)
    migrate = Migrate(app, db)

    jwt = JWTManager(app)


    api = Api(app, doc='/api')

    api.add_namespace(user_account_namespace, path='/user-account')
    api.add_namespace(quarter_taxes_namespace, path='/quarter-taxes')

    admin = Admin(app)
    admin.add_view(UserView(User, db.session))
    admin.add_view(DriverView(Driver, db.session))
    admin.add_view(TruckView(Truck, db.session))
    admin.add_view(NewEntryView(NewEntry, db.session))
    admin.add_view(QuarterView(Quarter, db.session))
    admin.add_view(StateQuarterReportView(StateQuarterReport, db.session))
    admin.add_view(StateTaxView(StateTax, db.session))
    admin.add_view(UserAdminView(UserAdmin, db.session))
    admin.add_view(RoleAdminView(Role, db.session))

    

    mail.init_app(app)

    app.register_blueprint(staff_namespace)



    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
            "Driver": Driver,
            "Truck": Truck,
            "NewEntry": NewEntry,
            "Quarter": Quarter,
            "StateQuarterReport": StateQuarterReport,
            "StateTax": StateTax
        }




    @app.before_first_request
    def create_user():


        if not user_datastore.find_user(email=config_obj.ADMIN_EMAIL_CREDENTIAL):
            db.create_all()
            user_datastore.find_or_create_role(name='admin', description='Administrator')
            db.session.commit()
            user_datastore.create_user(email=config_obj.ADMIN_EMAIL_CREDENTIAL, password=config_obj.ADMIN_PASSWORD_CREDENTIAL, roles=['admin'])
            db.session.commit()
            
        else:
            pass



    @app.route('/login')
    @login_required
    def login():
        return redirect('/admin')



    return app