## Members
Baciu Dragos Marian, Fitou Robert Claudiu
<br>
- Github repository: https://github.com/FitoiuRobert/IoTCA_project#table-of-contents

<br><br>


## Table of Contents
1. [ Quickstart ](#quickstart)
2. [ Project setup](#proj-setup)
3. [ Database ](#database)
4. [ Core module ](#coremodule)
5. [ Web API ](#api)
<br><br>


<a name="quickstart"></a>

## Quckstart
```sh
$ . venv.sh
$ pip3 install requirements.txt
$ ./fix_firebase_modules.sh # ONLY RUN THIS LINE IF YOU ARE USING python3.7 AND ABOVE
$ ./coremodule.py -s -f <FIREBASE_URL>
$ ./api.py
```
<br><br>


<a name="proj-setup"></a>
## Project setup

- __coremodule.py__ - Core module of the project, which is responsible for reading temperature (from senor or
    generates random values) and storing it to database, writes events in Firebase and graphs temperature data
    using Plotly.
- __api.py__ - Web API running on local host on port 5051 with endpoints for fever and temperature.
- __database.py__ - Sqlite3 databse module which is used by both __coremodule.py__ and __api.py__ .
- __fix_firebase_modules.sh__ - Fixes some issues related to Firebase module. Only needed to run if you are using
    python3.7 and above because "async" became a keyword in python3.7.
- __venv.sh__ - Installs `virtualenv` python module and activates the virtual environment.
- __requirements.txt__ - pip3 requirements file
<br><br>


<a name="database"></a>
## database.py

Database table layout:<br>
| timestamp|temperature|event|
|----------|:---------:|----:|
|1591124008896|37.4|FEVER_FEVER_START|
|1591124009161|35.2|None|
|...|...|...|
|1591124009161|36.8|FEVER_FEVER_END|

<br>Creates a database file named `TEMPERATURE.db` in the same directory with database.py
<br>To view the databse file content you can use: http://inloop.github.io/sqlite-viewer/
<br>The following values can be modified customized inside database.py:
- `__db_file_name`: name of the database file
- `TABLE_NAME`: name of the table that is going to be used by sqlite3 module
<br><br>

<a name="coremodule"></a>

## coremodule.py
__Usage__
```text
$ ./coremodule.py  --help
usage: coremodule.py [-h] -f FIREBASE_URL [-s] [-v] [-l LOG_PATH] [--sleep SLEEP] [-t FEVER_THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  -f FIREBASE_URL, --firebase-url FIREBASE_URL
                        Firebase storage URL
  -s, --simulation      Runs in simulation mode, generating random temperature values instead of reading from sensor
  -v, --verbose         Prints debug messages
  -l LOG_PATH, --log-path LOG_PATH
                        Path to to log. Only valid if 'verbose' is specified
  --sleep SLEEP         Sleep duration between temperature reading
  -t FEVER_THRESHOLD, --fever-threshold FEVER_THRESHOLD
                        Threshold temperature for fever events
```
__Firebase__
- Writes events in Firebase. Receives the events and the current time and while it is an event will be writen along with the current time, in firebase . ***Replace `FIREBASE_URL` with your own url***.
<img src=".img/firebase.png" width="30%" height="30%" alt="Firebase">
<br>

__Plotly__

- Graphs temperatures using Plotly. It receive temperature and time and draw an dashed graph using them.Generated plotly file is called **test.html**.<br>
<img src=".img/plotly.png" width="30%" height="30%" alt="Plotly">

<br><br>


<a name="api"></a>

## api.py

Falsk API which uses the data from database having 2 endpoints:<br>

__temperature__:
<br>`http://localhost:5051/temperature?start=<timestamp>&end=<timestamp>`
<br>`http://localhost:5051/temperature?start=<timestamp>&end=<timestamp>&aggregation=<aggregation_type>&operator=<operator_type>`
<br>Where the values for the second requests are:

- __aggregation_type__: `HOURLY`, `DAILY` 
- __operator_type__: `AVERAGE`, `MEDIAN`, `MAX`

__fever__:
<br>`http://localhost:5051/fever?start=<timestamp>&end=<timestamp>`
<br><br>Any other request will return "Bad request 400" response.




