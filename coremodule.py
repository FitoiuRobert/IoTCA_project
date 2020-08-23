#! /usr/bin/env python3

import time
import random
import argparse
import logging
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--simulation',action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('--sleep',type=int, default=30, help='Sleep duration between temperature reading')
parser.add_argument('-f', '--fever-threshold', type=float, default=37,
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
MAX_END_FEVER: int = 10
SLEEP_DURATION: int = args.sleep


def read_temperature():
    if args.simulation:
        temperature = random.randrange(30, 42)
    else:
        sys.exit("ops I didn't knew how to implement this part")

    return temperature

def get_fever_event(temperature: float):
    global TEMP_UNDER_THRESHOLD
    global TEMP_OVER_THRESHOLD

    if temperature >= FEVER_THRESHOLD:
        TEMP_UNDER_THRESHOLD = 0
        TEMP_OVER_THRESHOLD += 1
        if TEMP_OVER_THRESHOLD == 1:
            return FEVER_START

    if temperature < FEVER_THRESHOLD:
        TEMP_UNDER_THRESHOLD += 1
        TEMP_OVER_THRESHOLD = 0
        if TEMP_UNDER_THRESHOLD == MAX_END_FEVER:
            TEMP_UNDER_THRESHOLD = 0
            return FEVER_END

    return None


def main():
    while True:
        temperature = read_temperature()
        fever_event = get_fever_event(temperature)

        log("temperature:{}".format(temperature))
        log("TEMP_UNDER_THRESHOLD:{}".format(TEMP_UNDER_THRESHOLD))
        log("TEMP_OVER_THRESHOLD:{}".format(TEMP_OVER_THRESHOLD))
        log("fever_event:{}".format(fever_event))

        time.sleep(SLEEP_DURATION)

if __name__ == "__main__":
    main()
