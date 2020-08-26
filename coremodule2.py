#! /usr/bin/env python3

import time
import random
import argparse
import logging
import sys
from firebase import firebase
import plotly.graph_objs as go
import plotly.offline as ply

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--simulation',action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('--sleep',type=int, default=30, help='Sleep duration between temperature reading')
parser.add_argument('-f', '--fever-threshold', type=float, default=41,
                        help='Threshold temperature for fever events')
args = parser.parse_args()


log = logging.debug
if args.verbose:
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')


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

def current_time():
     return round(time.time(),1)



def write_in_firebase(event,time):
      if not event:
         return 
      data = {
        'Time':time,
        'Event':event
             }
      result = firebase.post('iotproject-45a41/EVENTS',data)     


def main():
    while True:
        temperature = read_temperature()
        current_t=current_time()
        fever_event = get_fever_event(temperature)
        write_in_firebase(fever_event,current_t)
        write_in_plotly(TEMP_UNDER_THRESHOLD,temperature,current_t)
        log("temperature:{}".format(temperature))
        log("TEMP_UNDER_THRESHOLD:{}".format(TEMP_UNDER_THRESHOLD))
        log("TEMP_OVER_THRESHOLD:{}".format(TEMP_OVER_THRESHOLD))
        log("fever_event:{}".format(fever_event))

        time.sleep(SLEEP_DURATION)

if __name__ == "__main__":
    main()
