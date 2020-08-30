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


def create_db(conn, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="CREATE TABLE IF NOT EXISTS {} (timestamp TIMESTAMP, temperature NUMBER, event VARCHAR(30))".format(TABLE_NAME)
    cur.execute(statement)


def get_all_rows(conn, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="SELECT * FROM {}".format(table_name)
    cur.execute(statement)
    rows = cur.fetchall()

    return rows


def insert_row(conn, timestamp, temperature, event, table_name=TABLE_NAME):
    cur = conn.cursor()
    statement="INSERT INTO {} (timestamp, temperature, event) VALUES (?,?,?)".format(TABLE_NAME)
    cur.execute(statement, (timestamp, temperature, event))


if __name__ == "__main__":
    conn = create_connection(DB_FILE)
    with conn:
        create_db(conn, TABLE_NAME)
        # insert_row(conn,time.time(), 37.2, None, TABLE_NAME)
        rows = get_all_rows(conn, TABLE_NAME)

    for row in rows:
        print(row)