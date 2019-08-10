# This Python file uses the following encoding: utf-8
#####################################################
#                  __       ___  __ ______________
#   ___ ___  ___ _/ /_____ / _ \/ // /_  __<  <  /
#  (_-</ _ \/ _ `/  '_/ -_) // / _  / / /  / // /
# /___/_//_/\_,_/_/\_\\__/____/_//_/ /_/  /_//_/
#
#####################################################
# Title:        snakeDHT11
# Version:      1.0
# Description:  Provides humidity and temperature readings for snake encloure
# Author:       Jonas Werner
#####################################################
import os
import glob
import time
import json
from influxdb import InfluxDBClient
from datetime import datetime
import sys, Adafruit_DHT
import redis



# Set environment variables
host            = os.environ['influxDBHost']
port            = os.environ['influxDBPort']
user            = os.environ['influxDBUser']
password        = os.environ['influxDBPass']
dbname          = os.environ['influxDBName']

redisHost  = os.environ['redisHost']
redisPort  = os.environ['redisPort']
redisPass  = os.environ['redisPass']


def influxDBconnect():
    influxDBConnection = InfluxDBClient(host, port, user, password, dbname)
    return influxDBConnection

def redisDBconnect():
    redisDBConnection = redis.Redis(host=redisHost, port=redisPort, password=redisPass)
    return redisDBConnection



def influxDBwrite(device, sensorName, sensorValue):

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    measurementData = [
        {
            "measurement": device,
            "tags": {
                "gateway": device,
                "location": "Tokyo"
            },
            "time": timestamp,
            "fields": {
                sensorName: sensorValue
            }
        }
    ]
    influxDBConnection.write_points(measurementData, time_precision='ms')



def readDht11():

    rawHum, rawTmp = Adafruit_DHT.read_retry(11, 19)

    formHum = int(rawHum)
    humval= str(formHum)
    formTmp = int(rawTmp)
    tempval = str(rawTmp)

    return humval, tempval


influxDBConnection = influxDBconnect()
redisDBConnection = redisDBconnect()

while True:

    hum, temp = readDht11()

    print("%s: %s   %s: %s" % ("coldZoneAirTemp", temp, "coldZoneAirHum", hum))
    # Sometimes the DHT11 sensor provides ridiculous spike values which we will ignore as they are invalid
    if 80 > float(temp) > 14:
        influxDBwrite("coldZoneAirTemp", "Temperature", temp)
        redisDBConnection.hmset("snakeTemp", {'temp':temp})
    # Sometimes the DHT11 sensor provides ridiculous spike values which we will ignore as they are invalid
    if 10 < int(hum) < 100:
        influxDBwrite("coldZoneAirHum", "Humidity", hum)
        redisDBConnection.hmset("snakeHum", {'hum':hum})
    time.sleep(5)
