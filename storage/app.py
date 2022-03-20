from multiprocessing.spawn import import_main_path
from time import time
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from blood_sugar import BloodSugar
from blood_cholesterol import BloodCholesterol
import datetime
import random
import yaml
import logging
import logging.config
import requests
import mysql.connector
import pymysql 
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread  

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    user = app_config['datastore']['user']
    pwd = app_config['datastore']['password']
    hostname = app_config['datastore']['hostname']
    port = app_config['datastore']['port']
    db = app_config['datastore']['db']

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{pwd}@{hostname}:{port}/{db}')

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"Connecting to DB. Hostname: {hostname}, port:{port}")
def report_blood_sugar(body):
    """ Reports blood sugar reading """

    session = DB_SESSION()

    logger.debug(f"Stored event blood_sugar request with a trace id of {body['trace_id']}")

    blood_sugar = BloodSugar(body['blood_sugar'],
                       body['patient_age'],
                       body['patient_name'],
                       body['patient_number'],
                       body['timestamp'],
                       body['trace_id'])

    session.add(blood_sugar)

    session.commit()
    session.close()

    return NoContent, 201

def get_blood_sugar_readings(timestamp): 
    """ Gets new blood sugar readings after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") 
   
 
    readings = session.query(BloodSugar).filter(BloodSugar.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for Blood Sugar readings after %s returns %d results" %  
                (timestamp, len(results_list))) 
 
    return results_list, 200

def report_blood_cholesterol(body):
    """ Reports blood cholesterol reading """
    session = DB_SESSION()

    logger.debug(f"Stored event blood_cholesterol request with a trace id of {body['trace_id']}")

    blood_cholesterol = BloodCholesterol(body['blood_cholesterol'],
                       body['patient_age'],
                       body['patient_name'],
                       body['patient_number'],
                       body['timestamp'],
                       body['trace_id'])

    session.add(blood_cholesterol)

    session.commit()
    session.close()

    return NoContent, 201

def get_blood_cholesterol_readings(timestamp): 
    """ Gets new blood cholesterol readings after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") 
    
    readings = session.query(BloodCholesterol).filter(BloodCholesterol.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for Blood Cholesterol readings after %s returns %d results" %  
                (timestamp, len(results_list))) 
 
    return results_list, 200

def process_messages(): 
    """ Process event messages """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
     
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST) 
 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
 
        payload = msg["payload"] 
 
        if msg["type"] == "blood_sugar": # Change this to your event type 
            # Store the event1 (i.e., the payload) to the DB 
            session = DB_SESSION()

            logger.debug(f"Stored event blood_sugar request with a trace id of {payload['trace_id']}")

            blood_sugar = BloodSugar(payload['blood_sugar'],
                            payload['patient_age'],
                            payload['patient_name'],
                            payload['patient_number'],
                            payload['timestamp'],
                            payload['trace_id'])

            session.add(blood_sugar)

            session.commit()
            session.close()
            

        elif msg["type"] == "blood_cholesterol": # Change this to your event type 
            # Store the event2 (i.e., the payload) to the DB 
            session = DB_SESSION()

            logger.debug(f"Stored event blood_cholesterol request with a trace id of {payload['trace_id']}")

            blood_cholesterol = BloodCholesterol(payload['blood_cholesterol'],
                            payload['patient_age'],
                            payload['patient_name'],
                            payload['patient_number'],
                            payload['timestamp'],
                            payload['trace_id'])

            session.add(blood_cholesterol)

            session.commit()
            session.close()

 
        # Commit the new message as being read 
        consumer.commit_offsets() 

app = connexion.FlaskApp(__name__, specification_dir='') 
app.add_api("openapi.yml", strict_validation=True, validate_responses=True) 

if __name__ == "__main__": 
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    app.run(port=8090)