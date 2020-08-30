#! /usr/bin/env python3

from flask import Flask, request, abort, jsonify
import database as db
import json

FEVER_START: str = 'FEVER_START_EVENT'
FEVER_END: str = 'FEVER_END_EVENT'

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route('/temperature', methods=['GET'])
def show_raw_temperature():
    start_date = int(request.args.get('start'))
    end_date = int(request.args.get('end'))
    
    if not start_date or not end_date:
        abort(400)

    measurements = get_raw_temp_measurements(start_date, end_date)
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "measurements" : measurements
    }

    return response


@app.route('/fever', methods=['GET'])
def show_fever():
    start_date = int(request.args.get('start'))
    end_date = int(request.args.get('end'))
    
    if not start_date or not end_date:
        abort(400)

    events = get_fever_events(start_date, end_date)
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "events" : events
    }

    return response


def get_raw_temp_measurements(start_date: int, end_date: int):
    conn = db.create_connection(db.DB_FILE)
    with conn:
        rows = db.get_all_rows(conn, db.TABLE_NAME)

    m = []
    for row in rows:
        timestamp = int(row[0])
        value = row[1]
        if timestamp > end_date:
            break # we asume that the data is sorted inside db as it should be
        if timestamp < start_date:
            continue # we asume that the data is sorted inside db as it should be
        m.append({"timestamp": timestamp, "value": value})

    return m


def get_fever_events(start_date: int, end_date: int):
    conn = db.create_connection(db.DB_FILE)
    with conn:
        rows = db.get_all_rows(conn, db.TABLE_NAME)
    
    events_list = []
    event_dict = {}
    for row in rows:
        timestamp = int(row[0])
        value = row[1]
        event = row[2]
        if timestamp > end_date:
            break # we asume that the data is sorted inside db as it should be
        if timestamp < start_date :
            continue # we asume that the data is sorted inside db as it should be
        if event == FEVER_START and not event_dict:
            event_dict = {
                "event_start": timestamp,
                "event_stop": 0,
                "measurements": [
                    {
                        "timestamp": timestamp,
                        "value": value
                    }
                ]
            }

        elif event == FEVER_START and event_dict:
            event_dict['event_stop'] = timestamp
            event_dict['measurements'].append({"timestamp":timestamp, "value": value})

        elif event == FEVER_END:
            if event_dict['event_stop'] == 0:
                event_dict['event_stop'] = timestamp
            event_dict['measurements'].append({"timestamp":timestamp, "value": value})
            events_list.append(event_dict)
            event_dict = {}

        elif event_dict:
            event_dict['measurements'].append({"timestamp":timestamp, "value": value})

    return events_list


if __name__ == "__main__":
    print("Hello {}".format(__file__))
    app.run(debug=True, port=5051)
