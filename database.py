#! /usr/bin/env python3

import sqlite3
import os
import sys
import time


__db_file_name="TEMPERATURE.db"
__path_to_db=os.path.dirname(os.path.abspath(__file__))
DB_FILE=os.path.join(__path_to_db, __db_file_name)
TABLE_NAME="TEMPERATURE"


def create_connection(DB_FILE, read_only=False):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except Exception as e:
        print("ERROR: ", e, file=sys.stderr)

    return conn


def get_all_rows(conn, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="SELECT * FROM {}".format(table_name)
    cur.execute(statement)
    rows = cur.fetchall()

    return rows


def create_db(conn, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="CREATE TABLE IF NOT EXISTS {} (timestamp TIMESTAMP, temperature NUMBER, event VARCHAR(30))".format(TABLE_NAME)
    cur.execute(statement)

def insert_row(conn, timestamp, temperature, event, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="INSERT INTO {} (timestamp, temperature, event) VALUES (?,?,?)".format(TABLE_NAME)
    cur.execute(statement, (timestamp, temperature, event))


if __name__ == "__main__":
    test_db_file = 'test.db'
    test_db_table = 'test'


    conn = create_connection("test.db")
    with conn:
        create_db(conn, test_db_table)
        insert_row(conn,time.time(), 37.2, None, test_db_table)
        rows = get_all_rows(conn, test_db_table)

    print("Hello {}".format(__file__))