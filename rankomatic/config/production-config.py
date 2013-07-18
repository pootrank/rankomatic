import os

DEBUG = False
TESTING = False
mongohq_url = os.environ.get('MONGOHQ_URL')
if mongohq_url:
    MONGODB_SETTINGS = {'HOST': mongohq_url,
                        'DB': os.path.basename(mongohq_url)}
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
