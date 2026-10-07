import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql://"
    f"{os.environ['POSTGRES_PIPELINE_USER']}:"
    f"{os.environ['POSTGRES_PIPELINE_PASSWORD']}@"
    "127.0.0.1:"
    f"{os.environ['POSTGRES_PORT']}/"
    f"{os.environ['POSTGRES_DB']}"
)
