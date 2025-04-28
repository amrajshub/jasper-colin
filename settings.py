import os
import sys
import logging
import logging.config

# Load the logging configuration from the INI file
logging.config.fileConfig("log.ini")

from dotenv import load_dotenv

dotenv_path = "/app/.env"
load_dotenv(dotenv_path=dotenv_path)


database_url = os.getenv("DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

REDIS_URL = os.getenv("REDIS_URL")
