from sqlite3 import InterfaceError
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class BloodSugar(Base):
    """ Blood Sugar """

    __tablename__ = "blood_sugar"

    id = Column(Integer, primary_key=True)
    blood_sugar = Column(Integer, nullable=False)
    patient_age = Column(Integer, nullable=False)
    patient_name = Column(String(250), nullable=False)
    patient_number = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)

    def __init__(self, blood_sugar, patient_age, patient_name, patient_number, timestamp, trace_id):
        """ Initializes a blood sugar reading """
        self.blood_sugar = blood_sugar
        self.patient_age = patient_age
        self.patient_name = patient_name
        self.patient_number = patient_number
        self.timestamp = timestamp
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a blood sugar reading """
        dict = {}
        dict['id'] = self.id
        dict['blood_sugar'] = self.blood_sugar
        dict['patient_age'] = self.patient_age
        dict['patient_name'] = self.patient_name
        dict['patient_number'] = self.patient_number
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
