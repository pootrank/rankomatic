"""
File: config.py
Author: Cameron Jeffers
Email: cwjeffers18@gmail.com

Configuration objects to provide options for the OT Flask webapp. This is
reusable, just edit the options as desired.
"""
import os

class Config(object):
    DEBUG = False
    TESTING = False
    MONGODB_SETTINGS = { 'DB': 'rankomatic' }
    SECRET_KEY = 'ThisShouldBeSecret'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    mongohq_url = os.environ.get('MONGOHQ_URL')
    MONGODB_SETTINGS = {'HOST': mongohq_url,
                        'DB': os.path.basename(mongohq_url)}
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')

class TestingConfig(Config):
    TESTING = True
