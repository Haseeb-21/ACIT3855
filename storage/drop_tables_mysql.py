import mysql.connector 
 
db_conn = mysql.connector.connect(host="aceit3855.westus.cloudapp.azure.com", user="root", 
password="Haseeb-2001", database="events") 
 
db_cursor = db_conn.cursor() 
 
db_cursor.execute(''' 
                  DROP TABLE blood_sugar, blood_cholesterol 
                  ''') 
 
db_conn.commit() 
db_conn.close() 
 
 