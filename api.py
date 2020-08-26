#! /usr/bin/env python3

from flask import Flask, request, abort, jsonify
import database as db
import json

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

@app.route('/temperature', methods=['GET'])
def show_temperature():
    start_date = int(request.args.get('start'))
    end_date = int(request.args.get('end'))
    
    if not start_date or not end_date:
        abort(400)

    measurements = get_temp_measurements(start_date, end_date)
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "measurements" : measurements
    }

    return response


@app.route('/fever', methods=['GET'])
def show_fever():
    return 'fever'

@app.route('/')
def hello_world():
    return {}


def get_temp_measurements(start_date: int, end_date: int):
    conn = db.create_connection(db.DB_FILE)
    with conn:
        rows = db.get_all_rows(conn, db.TABLE_NAME)

    m = []
    for row in rows:
        timestamp = int(row[0])
        value = row[1]
        if timestamp < start_date or timestamp > end_date:
            continue
        m.append({"timestamp": timestamp, "value": value})

    return m


if __name__ == "__main__":
    print("Hello {}".format(__file__))
    app.run(debug=True, port=5051)
