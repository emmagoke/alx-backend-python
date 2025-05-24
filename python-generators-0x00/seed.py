#!/usr/bin/env python3
"""
This script database connection functions
"""
import mysql.connector
from uuid import uuid4
import csv
import random


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


def connect_to_prodev():
    """
    This function connects to the ALX_prodev database
    """
    db_connection = None
    try:
        db_connection = mysql.connector.connect(
            user="user",
            password="password",
            host="host",
            port="port",
            database="ALX_prodev"
        )
        return db_connection
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return db_connection


def create_table(connection):
    """
    This function creates the table user_data if it does not exist
    with the required fields
    """
    TABLE_COMMAND = """
        CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL 
        );
    """
    #  age DECIMAL(3, 0) NOT NULL can 

    CREATE_INDEX_SQL = """
        CREATE INDEX idx_users_user_id ON user_data (user_id)
    """
    try:
        cursor = connection.cursor()
        # cursor.execute("DROP TABLE IF EXISTS user_data")
        print("Executing: CREATE TABLE IF NOT EXISTS user_data...")
        cursor.execute(TABLE_COMMAND)
        print("Table 'user_data' statement executed.")

        print("Executing: CREATE INDEX IF NOT EXISTS idx_users_user_id...")
        cursor.execute(CREATE_INDEX_SQL)
        print("Index 'idx_users_user_id' statement executed.")
        connection.commit()
        print("Table user_data created successfully")
        # cursor.close()
        
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        connection.rollback()


def insert_data(connection, data):
    """
    This function inserts data into the user_data table
    if it does not exist
    """
    try:
        cursor = connection.cursor()
        with open(data, 'r') as f:
            reader = csv.DictReader(f)  # or csv.DictReader(f)
            # csv.reader(f) return ['name', 'email', 'age'], ['Johnnie Mayer', 'Ross.Reynolds21@hotmail.com', '35']
            # csv.DictReader(f) returns {'name': 'Johnnie Mayer', 'email': 'Ross.Reynolds21@hotmail.com', 'age': '35'}
            print("Inserting user data...")
            skipped_count = 0
            for row in reader:
                user_id = str(uuid4())
                name = row['name']
                email = row['email']
                age = row['age']
                sql = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s);
                """

                # Basic validation for presence of essential data
                if name is None or email is None or age is None:
                    print(f"Warning: Row {row} has missing name, email, or age: {row}. Skipping.")
                    skipped_count += 1
                    continue
                try:
                    age = int(age)
                except ValueError:
                    age = random.randint(1, 60)
                cursor.execute(
                    sql, (user_id, name, email, age)
                )
        connection.commit()
        print("{} rows skipped".format(skipped_count))
        print("Successfully inserted user data")
        # cursor.close()
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        connection.rollback()
