import mysql.connector 
 
db_conn = mysql.connector.connect(host="aceit3855.westus.cloudapp.azure.com", user="root", 
password="Haseeb-2001", database="events") 
 
db_cursor = db_conn.cursor() 
 
db_cursor.execute(''' 
          CREATE TABLE blood_sugar 
          (id INT NOT NULL AUTO_INCREMENT,  
           blood_sugar INTEGER NOT NULL, 
           patient_age INTEGER NOT NULL, 
           patient_name VARCHAR(250) NOT NULL,
           patient_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL, 
           CONSTRAINT blood_sugar_pk PRIMARY KEY (id)) 
          ''') 
 
db_cursor.execute(''' 
          CREATE TABLE blood_cholesterol 
          (id INT NOT NULL AUTO_INCREMENT,  
           blood_cholesterol INTEGER NOT NULL,
           patient_age INTEGER NOT NULL,
           patient_name VARCHAR(250) NOT NULL,  
           patient_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL, 
           CONSTRAINT heart_cholesterol_pk PRIMARY KEY (id)) 
          ''') 
 
db_conn.commit() 
db_conn.close() 