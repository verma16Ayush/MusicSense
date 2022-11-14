import mysql.connector
from mysql.connector import errorcode
from mslib.config import config

try:
    my_db = mysql.connector.connect(
        host=config.DB_CREDENTIALS['host'],
        user=config.DB_CREDENTIALS['username'],
        password=config.DB_CREDENTIALS['password'],
        database=config.DB_CREDENTIALS['db_name']
    )
    print(f'db connected at {my_db._database} {my_db._user}@{my_db._host}') 
    
except mysql.connector.Error as e :
    if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('cannot access DB. Recheck DB credentials')
    if e.errno == errorcode.ER_BAD_DB_ERROR:
        print('specified DB probably does not exist')
