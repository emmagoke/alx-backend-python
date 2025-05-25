#!/usr/bin/env python3
"""
This script calculates the average age of users from a database
in a memory-efficient way using a generator.
"""
import mysql.connector


DB_CONFIG = {
    "user": "username",
    "password": "password",
    "host": "host",
    "port": "port",
    "database": "ALX_prodev" 
}


def stream_user_ages():
    """
    Connects to the database and yields user ages one by one.
    This is a generator function.
    """
    connection = None
    cursor = None
    # print("DEBUG: stream_user_ages: Attempting to connect to database...", file=sys.stderr)
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()  # Default cursor returns tuples

        cursor.execute("SELECT age FROM user_data;")

        while True:
            row_tuple = cursor.fetchone()  # Fetches one row at a time
            if row_tuple is None:  # No more rows left
                break
            
            age_value = row_tuple[0]  # Age is the first (and only) element
            
            if age_value is not None:
                try:
                    numeric_age = int(age_value) # Ensures age is an integer
                    yield numeric_age
                except (ValueError, TypeError):
                    pass

    except mysql.connector.Error as err:
        print(f"MySQL Error in stream_user_ages: {err}")
    finally:
        # print("DEBUG: stream_user_ages: Finalizing and closing resources.", file=sys.stderr)
        if cursor:
            try:
                cursor.close()
            except mysql.connector.Error as e:
                print(f"MySQL error closing cursor: {e}")
        if connection:
            try:
                connection.close()
            except mysql.connector.Error as e:
                print(f"MySQL error closing connection: {e}")


def calculate_and_print_average_age():
    """
    Uses the stream_user_ages generator to calculate the average age
    without loading the entire dataset into memory and prints the result.
    """
    total_age = 0
    user_count = 0

    for age in stream_user_ages():
        if isinstance(age, (int, float)): # Ensures we are working with a number
            total_age += age
            user_count += 1

    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}") 
    else:

        print("Average age of users: N/A (no users found or no valid age data)")


if __name__ == "__main__":
    calculate_and_print_average_age()
