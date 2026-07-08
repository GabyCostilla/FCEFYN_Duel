import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://uxptrus7w0ecmtsp:CqdDi2gvhj5fkz6bt5RV@b2umcwbwbpnvfcfhzeoe-mysql.services.clever-cloud.com:3306/b2umcwbwbpnvfcfhzeoe'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'studyduel-secret'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'ssl': {'ssl_disabled': True}
        }
    }
