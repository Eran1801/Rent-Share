# standalone_delete.py
import os
import mysql.connector
from datetime import datetime,timedelta


def delete_old_verification_codes():
    # Database configuration from environment variables
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'port': os.getenv('DB_PORT'),
        'passwd': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
        
    # SQL query to delete old records
    delete_query = """
    DELETE FROM Users_passwordresetcode
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE);
    """

    # Execute the deletion
    cursor.execute(delete_query)
    # Commit the changes to the database
    conn.commit()
    
    # Close the connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    delete_old_verification_codes()
