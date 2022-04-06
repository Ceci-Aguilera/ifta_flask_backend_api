from datetime import timedelta
from decouple import config
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = config('SECRET_KEY', "SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    UPLOAD_FOLDER = "uploads/"
    ALLOWED_EXTENSIONS = set(['pdf'])
    SECURITY_PASSWORD_SALT = config(
        'SECURITY_PASSWORD_SALT', 'SECURITY_PASSWORD_SALT')
    ADMIN_EMAIL_CREDENTIAL = config(
        'ADMIN_EMAIL_CREDENTIAL', 'ADMIN_EMAIL_CREDENTIAL')
    ADMIN_PASSWORD_CREDENTIAL = config(
        'ADMIN_PASSWORD_CREDENTIAL', 'ADMIN_PASSWORD_CREDENTIAL')
    SECURITY_POST_LOGIN_VIEW = '/admin'
    LOGIN_DISABLED = False
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = config('MAIL_SERVER', 'MAIL_SERVER')
    MAIL_PORT = config('MAIL_PORT', 'MAIL_PORT')
    MAIL_USERNAME = config('MAIL_USERNAME', 'MAIL_USERNAME')
    MAIL_PASSWORD = config('MAIL_PASSWORD', 'MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_STRING_ID = config('MAIL_STRING_ID', 'MAIL_STRING_ID')
    CORS_ORIGINS=[config('FRONTEND_APP', default="http://localhost:3000")]


class ProductionConfig(Config):
    DEVELOPMENT = False
    TESTING = False
    DEBUG = False
    UPLOAD_FOLDER = "uploads/"
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(config(
        'POSTGRES_DB_USER_PRODUCTION', default="NONE"), config('POSTGRES_DB_PASS_PRODUCTION', default="NONE"),
        config('POSTGRES_DB_HOST_PRODUCTION', default="NONE"),  config(
            'POSTGRES_DB_PORT_PRODUCTION', default="5432"),
        config('POSTGRES_DB_NAME_PRODUCTION', default="NONE"))


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(config(
        'POSTGRES_DB_USER_DEV', default="test_user"), config('POSTGRES_DB_PASS_DEV', default="test_pass"),
        config('POSTGRES_DB_HOST_DEV', default="localhost"),  config(
            'POSTGRES_DB_PORT_DEV', default="5432"),
        config('POSTGRES_DB_NAME_DEV', default="test_db"))
    STRIPE_TEST_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY', default="None")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(config(
        'POSTGRES_DB_USER_TEST', default="NONE"), config('POSTGRES_DB_PASS_TEST', default="NONE"),
        config('POSTGRES_DB_HOST_TEST', default="db"),  config(
            'POSTGRES_DB_PORT_TEST', default="5432"),
        config('POSTGRES_DB_NAME_TEST', default="NONE"))
