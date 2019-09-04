import os

# application name
APP_NAME = "AH WEB"

# app name second line
APP_NAME_SECOND_LINE = "May god blesses you all"

# copy right notice
COPY_RIGHT = "implemented by ohahlev@gmail.com"

# current timezone
TIMEZONE = "Asia/Bangkok"

# Secret key for generating tokens
SECRET_KEY = "houdini"

# Configuration of a Gmail account for sending mails
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get("ADMIN_EMAIL")
MAIL_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMINS = [os.environ.get("ADMIN_EMAIL")]

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 12

# Size of upload data
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# upload
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg"])

# Log
if not os.path.exists("logs"):
    os.makedirs("logs")
LOG_FILENAME = os.path.join("logs", "activity.log")

# max length of text to truncate in jinja
MAX_TRUNCATE = 10

# default date time format
DATE_TIME_FORMAT = "YYYY-MM-DD HH:mm:ss"

BABEL_TRANSLATION_DIRECTORIES = "./translations"

LANG = "km_KH"