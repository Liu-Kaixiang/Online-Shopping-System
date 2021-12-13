import sqlite3, hashlib
import pypyodbc
import config


# Return the sql connection 
def getConnection():
     connection = pypyodbc.connect("Driver= {"+config.DATABASE_CONFIG["Driver"]+"} ;Server=" + config.DATABASE_CONFIG["Server"] + ";Database=" + config.DATABASE_CONFIG["Database"] + ";uid=" + config.DATABASE_CONFIG["UID"] + ";pwd=" + config.DATABASE_CONFIG["Password"])
     return connection

# conn = getConnection()

# cursor = conn.cursor()
# cursor.execute('''SELECT * FROM goods''')
# data = cursor.fetchall()
# print(data)

