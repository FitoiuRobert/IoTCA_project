#! /usr/bin/env python3

import time
import random
import argparse
import logging as log
import sys
import database as db
from firebase import firebase
import plotly.graph_objs as go
import plotly.offline as ply


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--simulation',action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-l', '--log-path',help="Path to log")
parser.add_argument('--sleep',type=int, default=30, help='Sleep duration between temperature reading')
parser.add_argument('-f', '--fever-threshold', type=float, default=41,
                        help='Threshold temperature for fever events')
args = parser.parse_args()


if args.verbose:
    if args.log_path:
        log.basicConfig(filename=args.log_path, filemode='w', level=log.DEBUG)
    else:
        log.basicConfig(stream=sys.stdout, level=log.DEBUG)



FEVER_START: str = 'FEVER_START_EVENT'
FEVER_END: str = 'FEVER_END_EVENT'
FEVER_THRESHOLD: float = args.fever_threshold
TEMP_UNDER_THRESHOLD: int = 0
TEMP_OVER_THRESHOLD: int = 0
MAX_END_FEVER: int = 9
SLEEP_DURATION: int = args.sleep
X: int=[]
Y: int=[]

firebase=firebase.FirebaseApplication("https://iotproject-45a41.firebaseio.com/",None)


def read_temperature():
    if args.simulation:
        temperature = round(random.uniform(36, 42),2)
    else:
        sys.exit("ops I didn't knew how to implement this part")

    return temperature


def get_fever_event(temperature: float):
    global TEMP_UNDER_THRESHOLD
    global TEMP_OVER_THRESHOLD

    if TEMP_UNDER_THRESHOLD == MAX_END_FEVER:
            TEMP_UNDER_THRESHOLD = 0
            return FEVER_END
    elif temperature > FEVER_THRESHOLD:
        TEMP_OVER_THRESHOLD = 1
        TEMP_UNDER_THRESHOLD = 0
        return FEVER_START
    elif TEMP_OVER_THRESHOLD == 1:
        TEMP_UNDER_THRESHOLD +=1
    else: 
        TEMP_UNDER_THRESHOLD = TEMP_UNDER_THRESHOLD
    
    return None

def write_in_plotly(temp_under_threshold,temperature,time):
    global X
    global Y
    global data
    global fig
    if temp_under_threshold != MAX_END_FEVER:
        X.append(time)
        Y.append(temperature)
        data=[go.Scatter(
            x = X,
            y = Y,
            name = "Temperature by Time",
            line = dict(
                color = ("green"),
                width = 4,
                dash = 'dashdot'
            )
        )]
        layout = dict(
            title = "Temperature readings until Fever_End",
            xaxis = dict(title = "Time"),
            yaxis = dict(title = "Temperature")
        )
        fig = dict(data = data,layout = layout)
    if temp_under_threshold == MAX_END_FEVER:
        ply.plot(fig, filename='test.html')


def get_current_time():
    return int(time.time())


def send_to_firebase(event,time):
    if not event:
        return

    data = {
        'Time':time,
        'Event':event
            }
    result = firebase.post('iotproject-45a41/EVENTS',data)     


def main():
    conn = db.create_connection(db.DB_FILE)
    with conn:
        db.create_db(conn)

    while True:
        temperature = read_temperature()
        fever_event = get_fever_event(temperature)
        current_time = get_current_time()

        send_to_firebase(fever_event,current_time)
        write_in_plotly(TEMP_UNDER_THRESHOLD,temperature,current_time)
        with conn:
            db.insert_row(conn, current_time, temperature, fever_event, db.TABLE_NAME)

        log.debug("temperature:{}".format(temperature))
        log.debug("TEMP_UNDER_THRESHOLD:{}".format(TEMP_UNDER_THRESHOLD))
        log.debug("TEMP_OVER_THRESHOLD:{}".format(TEMP_OVER_THRESHOLD))
        log.debug("fever_event:{}".format(fever_event))

        time.sleep(SLEEP_DURATION)


if __name__ == "__main__":
    main()
