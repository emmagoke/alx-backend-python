#!/usr/bin/env python3
"""
This script contains a decorator to log SQL queries
"""
import sqlite3
import functools
from datetime import datetime


def log_queries(func):
    """
    A decorator that logs the SQL query of the decorated function
    before executing it.

    It attempts to find an argument named 'query' (either keyword or
    the first positional if the first parameter is named 'query')
    and logs its value if it's a string.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sql_query_to_log = None

        if 'query' in kwargs:
            potential_query = kwargs['query']
            if isinstance(potential_query, str):
                sql_query_to_log = potential_query
        
        elif args:
            try:
                param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
                if param_names and param_names[0] == 'query':

                    potential_query = args[0]
                    if isinstance(potential_query, str):
                        sql_query_to_log = potential_query
            except AttributeError:
                pass
            except IndexError:
                pass

        if sql_query_to_log:
            print(f"LOG: Executing query: {sql_query_to_log} at {datetime.now(datetime.timezone.utc)}")
        else:
            func_name = func.__name__
            try:
                # Attempt to get parameter names for a more informative message
                param_names_str = ", ".join(func.__code__.co_varnames[:func.__code__.co_argcount])
            except Exception:
                param_names_str = "unknown" # Fallback if introspection fails
    
            print(f"LOG: Calling function '{func_name}'. Could not identify a string SQL query from an argument named 'query' "
                  f"(checked keyword 'query' and first positional argument if first param is named 'query'). "
                  f"Function params: [{param_names_str}]. Called with args: {args}, kwargs: {kwargs}.")

        # Execute the original decorated function with its arguments
        result = func(*args, **kwargs)
        return result
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
