import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env file

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))