#!/usr/bin/env python3
"""
"""
import sqlite3
import functools


def retry_on_failure(retries=3, delay=2):
    """
    A decorator that retries a function if it raises an exception.

    Args:
        retries (int): The maximum number of times to retry.
        delay (int): The number of seconds to wait between retries.
    """
    def decorator(func_to_wrap):
        @functools.wraps(func_to_wrap)
        def wrapper_retry(*args, **kwargs):
            for attempt in range(1, retries + 2): # retries + 1 actual attempts, +1 for range
                try:
                    return func_to_wrap(*args, **kwargs)
                except Exception as e:
                    # print(f"DEBUG retry_on_failure: Attempt {attempt} for '{func_to_wrap.__name__}' failed: {e}")
                    if attempt > retries: # Last attempt also failed
                        # print(f"DEBUG retry_on_failure: All {retries} retries failed for '{func_to_wrap.__name__}'. Raising last exception.")
                        raise # Re-raise the last exception
                    
                    # print(f"DEBUG retry_on_failure: Retrying '{func_to_wrap.__name__}' in {delay} seconds...")
                    time.sleep(delay)
            
            return None # Should not be reached in normal flow with retries >= 0
        return wrapper_retry
    return decorator


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
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)
