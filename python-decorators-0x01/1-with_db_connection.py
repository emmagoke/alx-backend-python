#!/usr/bin/env python3

import sqlite3
import functools

def with_db_connection(db_name_param):
    """
    A decorator that automatically handles opening and closing an SQLite3
    database connection. It passes the connection object as the first
    argument to the decorated function.

    Args:
        db_name_param (str): The name of the SQLite database file.
    """
    def decorator(func_to_wrap):
        @functools.wraps(func_to_wrap)
        def wrapper_function(*args, **kwargs):
            db_connection = None
            try:
                # Open the database connection
                db_connection = sqlite3.connect(db_name_param)
                
                result = func_to_wrap(db_connection, *args, **kwargs)
                
                return result
            except Exception as e:
                raise
            finally:
                # Ensure the connection is closed if it was successfully opened
                if db_connection:
                    db_connection.close()
        return wrapper_function
    return decorator


@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 
#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)
