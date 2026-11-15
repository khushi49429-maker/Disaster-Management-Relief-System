import mysql.connector

def get_db_connection():
    try: 
        connection =mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="disaster_management"
        )
        return connection
    
    except mysql.connector.Error as error:
        print("Databsae connection failed:",error)
        return None