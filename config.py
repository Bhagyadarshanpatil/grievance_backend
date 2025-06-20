import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

print("DB user from .env:", os.getenv("DB_USER"))  # ✅ DEBUG LINE

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}
