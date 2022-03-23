import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import random
import yaml
import logging
import logging.config
from base import Base
from stats import Stats
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_stats(): 
    """ Gets new sale reports after the timestamp """ 
 
    session = DB_SESSION() 
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
  
    if stats:
        return stats.to_dict(), 200
    return {"message":"No stats found"}, 400


def populate_stats(): 
    """ Periodically update stats """ 
    logger.info("Start Periodic Processing") 
    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    session = DB_SESSION() 
    latest_stats = session.query(Stats).order_by(Stats.last_updated.desc()).first() 

    if latest_stats:
        latest_stats = latest_stats.to_dict()
    else:
        latest_stats = {
            "num_bs_readings": 1,
            "max_bs_reading": 0,
            "num_bc_readings": 1,
            "max_bc_reading": 0,
            "last_updated": last_updated
        }
    
    session.close()

    new_stats = latest_stats
    response = requests.get('http://localhost:8090/readings/blood-sugar', params={"timestamp": latest_stats["last_updated"]})

    if response and response.status_code == 200:
        if len(response.json()) != 0:
            logging.info(f'Return {len(response.json())} numbers of events')
            blood_sugar_result = []
            for report in response.json(): 
                blood_sugar_result.append(report)
                new_stats["max_bs_reading"] = max(new_stats["max_bs_reading"], report["blood_sugar"])
                logging.debug(f'Process blood sugar event with trace id: {report["trace_id"]}')

            new_stats["num_bs_readings"] = latest_stats["num_bs_readings"] + len(blood_sugar_result)

    else:
        logging.error(f'Blood sugar response failed with {response.status_code}')


    response = requests.get('http://localhost:8090/readings/blood-cholesterol', params={"timestamp": latest_stats["last_updated"]})

    if response and response.status_code == 200:
        if len(response.json()) != 0:
            logging.info(f'Return {len(response.json())} numbers of events')
            blood_cholesterol_result = []
            for report in response.json(): 
                blood_cholesterol_result.append(report)
                new_stats["max_bc_reading"] = max(new_stats["max_bc_reading"], report["blood_cholesterol"])
                logging.debug(f'Process blood cholesterol event with trace id: {report["trace_id"]}')

            new_stats["num_bc_readings"] = latest_stats["num_bc_readings"] + len(blood_cholesterol_result)

    else:
        logging.error(f'Blood cholesterol response failed with {response.status_code}')


    new_stats["last_updated"] = datetime.datetime.now()
    logging.debug(new_stats)
    session = DB_SESSION()

    stat = Stats(new_stats['num_bs_readings'],
                    new_stats['max_bs_reading'],
                    new_stats['num_bc_readings'],
                    new_stats['max_bc_reading'],
                    new_stats['last_updated'])

    session.add(stat)

    session.commit()
    session.close()

    logging.debug(f'Updated stat: {new_stats}')
    logging.info(f'End Periodic Processing')
    

def init_scheduler(): 
    sched = BackgroundScheduler(timezone="America/Vancouver", daemon=True) 
    sched.add_job(populate_stats,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='') 
CORS(app.app) 
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True) 

if __name__ == "__main__": 
    init_scheduler()
    app.run(port=8100, use_reloader=False)