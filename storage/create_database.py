import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE blood_sugar
          (id INTEGER PRIMARY KEY ASC, 
           blood_sugar INTEGER NOT NULL,
           patient_age INTEGER NOT NULL,
           patient_name VARCHAR(250) NOT NULL,
           patient_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE blood_cholesterol
          (id INTEGER PRIMARY KEY ASC, 
           blood_cholesterol INTEGER NOT NULL,
           patient_age INTEGER NOT NULL,
           patient_name VARCHAR(250) NOT NULL,
           patient_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
