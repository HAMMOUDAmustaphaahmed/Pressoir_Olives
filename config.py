import os

class Config:
    SECRET_KEY = 'votre_cle_secrete_tres_securisee'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/pressoir_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}