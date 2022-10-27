from mslib.config import config
import mysql.connector

my_db = mysql.connector.connect(
    host=config.DB_CREDENTIALS['host'],
    user=config.DB_CREDENTIALS['username'],
    password=config.DB_CREDENTIALS['password'],
    database=config.DB_CREDENTIALS['db_name']
)

print(f'db connected at {my_db._database} {my_db._user}@{my_db._host}') 
