import connexion 
from connexion import NoContent
from datetime import datetime
from flask_cors import CORS, cross_origin

import requests
import yaml
import json
import os
import logging
import logging.config

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

# Load logging config
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

site_root = os.path.realpath(os.path.dirname(__file__))
event_file = os.path.join(site_root, 'health.json')

# json functions
def to_json(file, payload):
    """
    Takes payload data and writes it to a JSON file. JSON file should be initialized with {"subs": []}
    :param: file: file path
    :type: str
    :param: payload: data to be written to the file
    :type: str
    """

    # Open file as write and dump JSON payload to file
    with open(file, mode='w') as json_file:
        json.dump(payload, json_file)

def clear_json(file):
    # Object to initialize file with
    init_data = {"data": []}
    with open(file, mode='w+') as f:
        # Seek beginning of file and rewrite the file
        f.seek(0)
        f.truncate()
        f.write(json.dumps(init_data))

def json_init():
    # Try block to check if file exists, or if file is corrupted
    try:
        with open(event_file) as json_file:
            data = json.load(json_file)
        print(f'json file successfully returned')
        return data
    except json.JSONDecodeError or TypeError:
        data = clear_json(event_file)
        print(f'json file cleared')
        return data
    except FileNotFoundError:
        data = {"data": []}
        with open(event_file, mode='w+') as f:
            f.write(json.dumps(data))
        print(f'json file initialized')
        return data

# Get data from database and return processed stats
def get_health():
    '''Returns stats data'''
    try:
        receiver = requests.get("http://aceit3855.westus.cloudapp.azure.com:8080/health", timeout=4)
        logger.info(f'receiver response is: {receiver.status_code}')
        r = receiver.status_code
    except:
        logger.info(f'service is unreachable')
        r = 400
    
    try:
        storage = requests.get("http://aceit3855.westus.cloudapp.azure.com:8090/health", timeout=4)
        logger.info(f'storage response is: {storage.status_code}')
        s = storage.status_code
    except:
        logger.info(f'service is unreachable')
        s = 400

    try:
        processing = requests.get("http://aceit3855.westus.cloudapp.azure.com:8100/health", timeout=4)
        logger.info(f'processing response is: {processing.status_code}')
        p = processing.status_code
    except:
        logger.info(f'service is unreachable')
        p = 400

    try:
        audit= requests.get("http://aceit3855.westus.cloudapp.azure.com:8110/health", timeout=4)
        logger.info(f'audit response is: {audit.status_code}')
        a = audit.status_code
    except:
        logger.info(f'service is unreachable')
        a = 400

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    status_codes = [r, s, p, a]

    for i in range(len(status_codes)):
        if status_codes[i] < 400:
            status_codes[i] = 'Running'
        else:
            status_codes[i] = 'Down'

    payload = {
        "receiver": status_codes[0],
        "storage": status_codes[1],
        "processing": status_codes[2],
        "audit": status_codes[3],
        "last_update": now
    }
    
    to_json(event_file, payload)
    logger.info(f'payload written to json file')
    logger.info(f'payload: \n{payload}')
    return payload, 200

def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(get_health,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()

# Run the app
app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yml', strict_validation=True, validate_responses=True) 
 
if __name__ == "__main__": 
    # run our standalone gevent server
    json_init()
    init_scheduler() 
    app.run(port=8120, use_reloader=False)