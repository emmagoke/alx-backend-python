#!/usr/bin/env python3
"""
This script a function that uses a generator to fetch
rows one by one from the user_data table.
"""
import mysql.connector


def stream_users():
    """
    This function uses a generator to fetch
    rows one by one from the user_data table.
    """
    try:
        connection = mysql.connector.connect(
            user="user",
            password="password",
            host="host",
            port="port",
            database="ALX_prodev"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data;")
        while cursor is not None:  # or while True
            row = cursor.fetchone()
            if row is None:
                break
            yield row
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
    finally:
        # cursor.close()
        connection.close()
