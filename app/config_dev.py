import logging
from app.config_common import *

DEBUG = True

LOG_LEVEL = logging.DEBUG
LOG_MAXBYTES = 1024
LOG_BACKUPS = 0

DEBUG_TB_INTERCEPT_REDIRECTS = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
