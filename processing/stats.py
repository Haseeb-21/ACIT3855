from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 
class Stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    num_bs_readings = Column(Integer, nullable=False)  
    max_bs_reading = Column(Integer, nullable=True) 
    num_bc_readings = Column(Integer, nullable=False)
    max_bc_reading = Column(Integer, nullable=True) 
    last_updated = Column(DateTime, nullable=False) 
 
    def __init__(self, num_bs_readings, max_bs_reading, num_bc_readings, max_bc_reading, last_updated): 
        """ Initializes a processing statistics objet """ 
        self.num_bs_readings = num_bs_readings  
        self.max_bs_reading = max_bs_reading 
        self.num_bc_readings = num_bc_readings
        self.max_bc_reading = max_bc_reading 
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['num_bs_readings'] = self.num_bs_readings  
        dict['max_bs_reading'] = self.max_bs_reading 
        dict['num_bc_readings'] = self.num_bc_readings
        dict['max_bc_reading'] = self.max_bc_reading 
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ") 
 
        return dict