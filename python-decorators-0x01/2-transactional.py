#!/usr/bin/env python3
"""
"""
import sqlite3
import functools


def transactional(func_to_wrap):
    """
    A decorator that ensures a database operation is wrapped inside a transaction.
    If the decorated function raises an error, the transaction is rolled back;
    otherwise, the transaction is committed.
    Expects the database connection object to be passed as the first argument
    to the decorated function (typically by with_db_connection).
    """
    @functools.wraps(func_to_wrap)
    def wrapper_transactional(conn, *args, **kwargs): # Expects 'conn' as first arg
        try:
            result = func_to_wrap(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception as rb_e:
                    pass
            raise
    return wrapper_transactional


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
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
