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
from flask_cors import CORS, cross_origin


MAX_EVENTS = 10
EVENT_FILE = "events.json"

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_blood_sugar_reading(index): 
    """ Get blood sugar reading in history """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving blood sugar at index %d" % index) 
    try: 
        i = 0
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 

            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
            
            if msg['type'] == 'blood_sugar' and i == index:
                #print(msg['payload'], 200)
                return msg['payload'], 200
            i+=1
            
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find blood sugar at index %d" % index) 
    return { "message": "Not Found"}, 404


def get_blood_cholesterol_reading(index): 
    """ Get blood cholesterol reading in history """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving blood cholesterol at index %d" % index) 
    try: 
        i = 0
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str) 
 
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
            #print("hello", i, msg['payload'])
            if msg['type'] == 'blood_cholesterol' and i == index:
                return msg['payload'], 200
            i+=1
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find blood cholesterol at index %d" % index) 
    print()
    return { "message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='') 
CORS(app.app) 
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True) 

if __name__ == "__main__": 
    app.run(port=8110)