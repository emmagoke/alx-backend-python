#!/usr/bin/env python3
"""
This script contains an asynchronous generator
"""
import mysql.connector


def connect_db():
    """
    This function connects to the mysql database server
    """
    db_connection = None
    try:
        print("Connecting to MySQL database...")
        db_connection = mysql.connector.connect(
            user="user_name",
            password="password",
            host="hostname",
            # port="22505",
            # database="defaultdb"
        )
        return db_connection
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return db_connection


def create_database(connection):
    """
    This function takes the connection and
    creates creates the database ALX_prodev if it does not exist
    """
    DB_NAME = "ALX_prodev"
    try:
        cursor = connection.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {}".format(DB_NAME)
            )
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
