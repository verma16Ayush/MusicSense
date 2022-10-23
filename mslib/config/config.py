from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

# database configuration / credentials. taken from the .env file
DB_CREDENTIALS : Dict[str, str] = {
    'db_name' : os.getenv('DATABASE_NAME') or '',
    'username' : os.getenv('DATABASE_USERNAME') or '',
    'password' : os.getenv('DATABASE_PASSWORD') or '',
    'host' : os.getenv('DATABASE_HOST') or '',
}


