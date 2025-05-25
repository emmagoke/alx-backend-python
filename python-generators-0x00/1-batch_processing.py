#!/usr/bin/env python3
"""
This script contains a generator to fetch and process data in
batches from the users database
"""
import mysql.connector


def stream_users_in_batches(batch_size):
    """
    This function uses a generator to fetch and process data in
    batches from the users database
    """
    try:
        connection = mysql.connector.connect(
            user="username",
            password="password",
            host="host",
            port="port",
            database="ALX_prodev"
        )
        # dictionary=True  get rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data;")
        while cursor is not None:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            # print("Success: ", type(rows))
            yield rows
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
    finally:
        # cursor.close()
        connection.close()


def batch_processing(batch_size):
    """"
    This function processes each batch to filter
    users over the age of 25
    """
    batchs = stream_users_in_batches(batch_size)
    result = []
    for users in batchs:
        result = []
        for user in users:
            try:
                # print("user: {}, age: {}".format(user["name"], user["age"]))
                if int(user["age"]) > 25:
                    print(user)
                    result.append(user)
            except (ValueError, TypeError):
                print(f"Skipping user {user.get('user_id', 'Unknown ID')} due to invalid age format: '{age}'")
    return result
