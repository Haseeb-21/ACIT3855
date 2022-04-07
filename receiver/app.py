import connexion 
from connexion import NoContent 
import datetime
import os
import json
import yaml
from json.decoder import JSONDecodeError
import random
import uuid
import logging
import logging.config
import requests
from pykafka import KafkaClient

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

MAX_EVENTS = 10
EVENT_FILE = "events.json"


def report_blood_sugar(body):
    """ Reports blood sugar reading """
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    headers= {'Content-type': 'application/json'}
    #response = requests.post('http://localhost:8090/readings/blood-sugar', data=json.dumps(body), headers=headers)

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}') 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
    producer = topic.get_sync_producer() 
    reading = body
    msg = { "type": "blood_sugar",  
            "datetime" :    
                datetime.datetime.now().strftime( 
            "%Y-%m-%dT%H:%M:%S"),  
            "payload": reading } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Received event blood_sugar request with a trace id of {trace_id}")
    logger.info(f"Returned event blood_sugar response (Id: {trace_id}) with status 201")#{response.status_code}")

    return 201 #response.status_code


def report_blood_cholesterol(body):
    """ Reports blood cholesterol reading """
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    headers= {'Content-type': 'application/json'}
    #response = requests.post('http://localhost:8090/readings/blood-cholesterol', data=json.dumps(body), headers=headers)

    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}') 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
    producer = topic.get_sync_producer() 
    reading = body
    msg = { "type": "blood_cholesterol",  
            "datetime" :    
                datetime.datetime.now().strftime( 
            "%Y-%m-%dT%H:%M:%S"),  
            "payload": reading } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Received event blood_cholesterol request with a trace id of {trace_id}")
    logger.info(f"Returned event blood_cholesterol response (Id: {trace_id}) with status 201")# {response.status_code}")

    return 201 #response.status_code

def health():
    """ Returns health of receiver service """
    msg = f"Running"
    code = 200
    return msg, code

app = connexion.FlaskApp(__name__, specification_dir='') 
app.add_api("openapi.yml", strict_validation=True, validate_responses=True) 

if __name__ == "__main__": 
    app.run(port=8080)