import os
from dotenv import load_dotenv

load_dotenv('.env')
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # 3X-UI data
    X_UI_LINK = str(os.getenv('X_UI_LINK'))
    X_UI_LOGIN = str(os.getenv('X_UI_LOGIN'))
    X_UI_PASSWORD = str(os.getenv('X_UI_PASSWORD'))

    # VLESS data
    VLESS_HOST = str(os.getenv('VLESS_HOST'))
    VLESS_PORT = int(os.getenv('VLESS_PORT'))

    VLESS_CONFIGS_PATH = str(os.getenv('VLESS_CONFIGS_PATH'))

    # DATABASE data
    DB_HOST = str(os.getenv('DB_HOST'))
    DB_PORT = int(os.getenv('DB_PORT'))
    DB_NAME = str(os.getenv('DB_NAME'))
    DB_USER = str(os.getenv('DB_USER'))
    DB_PASSWORD = str(os.getenv('DB_PASSWORD'))

    # LOGS data
    X_UI_LOGS_PATH = str(os.getenv('X_UI_LOGS_PATH'))

    # BACKUPS data
    X_UI_BACKUPS_PATH = str(os.getenv('X_UI_BACKUPS_PATH'))

    PORT_RANGE_MIN = int(os.getenv('PORT_RANGE_MIN'))
    PORT_RANGE_MAX = int(os.getenv('PORT_RANGE_MAX'))
