import os


DEBUG = True
# IGNORE_AUTH = True
SECRET_KEY = 'the-secret!'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    os.path.dirname(__file__), '../data-dev.sqlite3?check_same_thread=False')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
