from mslib.config import config
import mysql.connector as mysql

mydb = mysql.connect(
    host=config.DB_CREDENTIALS['host'],
    user=config.DB_CREDENTIALS['username'],
    password=config.DB_CREDENTIALS['password']
)

print(mydb)