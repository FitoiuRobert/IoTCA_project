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
    aggregation_type = request.args.get('aggregation_type')
    operator_type = request.args.get('operator_type')
    
    if not start_date or not end_date:
        abort(400)

    if ( aggregation_type and not operator_type ) or ( not aggregation_type and operator_type):
        abort(400)

    if aggregation_type:
        supported_aggregations = ['HOURLY', 'DAILY']
        supported_operators = ['AVERAGE', 'MEDIAN', 'MAX']
        if aggregation_type not in supported_aggregations:
            abort(400)
        if operator_type not in supported_operators:
            abort(400)
        measurements = get_aggregated_temp_measurements(start_date, end_date, aggregation_type, operator_type)
        response = {
            "start_date": start_date,
            "end_date": end_date,
            "aggregation_type": aggregation_type,
            "operator_type": operator_type,
            "measurements" : measurements
        }
    else:
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

    events = get_fever_events_measurements(start_date, end_date)
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


def apply_operation(aggregation_list: list, operator_type: str):
    aggregation_list = sorted(aggregation_list)
    value = 0.0
    if operator_type == 'AVERAGE':
        value = sum(aggregation_list) / len(aggregation_list)
    elif operator_type == 'MEDIAN':
        mid = int(len(aggregation_list) / 2)
        value = aggregation_list[mid]
    elif operator_type == 'MAX':
        value = max(aggregation_list)

    return round(value,1)


def get_aggregated_temp_measurements(start_date: int, end_date: int, aggregation_type: str, operator_type: str):
    conn = db.create_connection(db.DB_FILE)
    with conn:
        rows = db.get_all_rows(conn, db.TABLE_NAME)
        rows_iter = iter(rows)
    
    m = []
    while True:
        try:
            row = next(rows_iter)
            timestamp = int(row[0])
            value = row[1]

            start_timestamp = timestamp
            if aggregation_type == 'HOURLY':
                end_timestamp = timestamp + 36000
            elif aggregation_type == 'DAILY':
                end_timestamp = timestamp + (3600 * 24)

            aggregation_list = [ value ]
            while timestamp < end_timestamp:
                try:
                    row = next(rows_iter)
                    timestamp = int(row[0])
                    value = row[1]
                    aggregation_list.append(value)
                except StopIteration:
                    break

            value = apply_operation(aggregation_list, operator_type)
            m.append({"timestamp": start_timestamp, "value":value})

        except StopIteration:
            break

    return m


def get_fever_events_measurements(start_date: int, end_date: int):
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
    app.run(debug=True, port=5051)
