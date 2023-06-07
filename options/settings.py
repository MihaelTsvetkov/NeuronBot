import logging
import dotenv
import os

environ = os.environ
DATA_DIR = environ.get("DATA_DIR", "data")
DEFAULT_DOTENV_PATH = os.path.join(DATA_DIR, '.env')
dotenv_path = environ.get('DOTENV_PATH', DEFAULT_DOTENV_PATH)
print(f"Reading env from {os.path.abspath(dotenv_path)}", flush=True)
dotenv.load_dotenv(dotenv_path)

DEBUG_FILE_PATH = environ.get("DEBUG_FILE_PATH", os.path.join(DATA_DIR, 'debug.log'))
INFO_FILE_PATH = environ.get("INFO_FILE_PATH", os.path.join(DATA_DIR, 'info.log'))

API_TOKEN = environ["API_TOKEN"]
BOT_TOKEN = environ["BOT_TOKEN"]
LANGUAGE = environ["LANGUAGE"]

DATABASE_HOST = environ["DATABASE_HOST"]
DATABASE_USER = environ["DATABASE_USER"]
DATABASE_PASSWD = environ["DATABASE_PASSWD"]
DATABASE_PORT = int(environ["DATABASE_PORT"])
DATABASE = environ["DATABASE"]

LOGGING_LEVEL = logging.DEBUG if environ["LOGGING_LEVEL"] == 'DEBUG' \
    else logging.INFO if environ["LOGGING_LEVEL"] == 'INFO' \
    else None

OGG_FILE_PATH = environ["OGG_FILE_PATH"]
MP3_FILE_PATH = environ["MP3_FILE_PATH"]

NUMBER_OF_QUESTIONS_AND_ANSWERS_STORED = int(environ.get("NUMBER_OF_QUESTIONS_AND_ANSWERS_STORED"))
