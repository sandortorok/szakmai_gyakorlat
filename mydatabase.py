import mysql.connector
import threading
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

class SensorDB:
    def __init__(self):
        self.lock = threading.Lock()
        self.lock.acquire()
        self.mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="Sanyi",
            password="sakkiraly11",
            database="AmmoniaDB"
        )
        self.lock.release()
    def updateAmmoniaLevel(self, id, val):
        self.lock.acquire()
        mycursor = self.mydb.cursor()
        mycursor.execute("UPDATE sensors SET ammonia_level = {} WHERE sensor_id = {}".format(val, id))
        self.mydb.commit()
        self.lock.release()
    def updateHorn(self, id, val):
        self.lock.acquire()
        mycursor = self.mydb.cursor()
        mycursor.execute("UPDATE sensors SET horn = {} WHERE sensor_id = {}".format(val, id))
        self.mydb.commit()
        self.lock.release()
    def GetElementByID(self, id):
        self.lock.acquire()
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM sensors WHERE sensor_id = {}".format(id))
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def getTheFirstX(self, x):
        self.lock.acquire()
        self.mydb.commit()
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM sensors WHERE sensor_id <= {}".format(x))
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def yearlyAverage(self):
        self.lock.acquire()
        mycursor = self.mydb.cursor()
        mycursor.execute(
            """SELECT sum(ammonia_value)/count(ammonia_value) as mean,
                STR_TO_DATE(concat(YEAR(date),'-',MONTH(date), '-',1), '%Y-%m-%d') as month,
                sensor_id 
            FROM sensor_records 
            GROUP BY month, sensor_id 
            ORDER BY date, sensor_id""")
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def monthlyAverage(self, how_old):
        self.lock.acquire()
        Q = """SELECT sensor_id, STR_TO_DATE(concat(YEAR(date),'-',MONTH(date), '-',1), '%Y-%m-%d') as month, 
                    sum(ammonia_value)/count(ammonia_value) as mean 
                FROM sensor_records 
                WHERE year(date) = year(DATE(NOW())) - {}
                GROUP BY month, sensor_id 
                ORDER BY month, sensor_id""".format(how_old)
        mycursor = self.mydb.cursor()
        mycursor.execute(Q)
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def dailyAverage(self, how_old):
        self.lock.acquire()
        Q = """SELECT sensor_id, STR_TO_DATE(concat(YEAR(date),'-',MONTH(date), '-',DAY(date)), '%Y-%m-%d') as daily, 
            sum(ammonia_value)/count(ammonia_value) as mean, 
            YEARWEEK(date) as week
        FROM sensor_records 
        WHERE YEARWEEK(date) = YEARWEEK(DATE(NOW())) - {}
        GROUP BY daily, sensor_id
        ORDER BY daily, sensor_id""".format(how_old)
        mycursor = self.mydb.cursor()
        mycursor.execute(Q)
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def weeklyAverage(self, how_old):
        self.lock.acquire()
        Q =  """SELECT sensor_id, 
                    YEARWEEK(date) as week,
                    sum(ammonia_value)/count(ammonia_value) as mean,
                    DATE_FORMAT(date,'%Y%m') AS yearmonth
                FROM sensor_records 
                WHERE DATE_FORMAT(date,'%Y%m') = DATE_FORMAT(DATE(NOW())- INTERVAL {} MONTH,'%Y%m') 
                GROUP BY week, sensor_id 
                ORDER BY week, sensor_id""".format(how_old)
        mycursor = self.mydb.cursor()
        mycursor.execute(Q)
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def hourlyAverage(self, date):
        self.lock.acquire()
        Q =  """SELECT sensor_id,
		DATE_FORMAT(date, '%Y-%m-%d-%H') as formatted_date,
            sum(ammonia_value)/count(ammonia_value) as mean
        FROM sensor_records
        WHERE DATE_FORMAT(date, '%Y-%m-%d') = {}
        GROUP BY formatted_date, sensor_id
        ORDER BY formatted_date, sensor_id""".format(date)
        mycursor = self.mydb.cursor()
        mycursor.execute(Q)
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def getSensorNumbers(self):
        self.lock.acquire()
        Q =  """select distinct sensor_id
                from sensor_records"""
        mycursor = self.mydb.cursor()
        mycursor.execute(Q)
        myresult = mycursor.fetchall()
        self.lock.release()
        return myresult
    def insert_sensor_record(self, id, val):
        self.lock.acquire()
        mycursor = self.mydb.cursor()
        mycursor.execute("""INSERT INTO sensor_records (sensor_id, date, ammonia_value)
            VALUES ({}, CURRENT_TIMESTAMP, {});
            """.format(id, val))
        self.mydb.commit()
        self.lock.release()
    # def insert_random(self):
    #     mycursor = self.mydb.cursor()
    #     for i in range(0,1000000):
    #         mycursor.execute("""INSERT INTO sensor_records (sensor_id, date, ammonia_value)
    #             VALUES (4, CURRENT_TIMESTAMP - INTERVAL FLOOR(RAND() * 365 * 24 * 60 *60) SECOND, FLOOR( RAND() * (20)));
    #             """)
    #     self.mydb.commit()