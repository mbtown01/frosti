#!/usr/bin/python3

import requests
import json
import sys

from time import sleep
from xml.etree import ElementTree

# pylint: disable=import-error
from influxdb import InfluxDBClient
import serial
from os.path import dirname
sys.path.append(dirname(__file__)+'/../')
from src.config import config
# pylint: enable=import-error

if not config.resolve("influxdb", "enabled", False):
    raise RuntimeError('InfluxDB is not configured')

client = InfluxDBClient(
    host=config.resolve("influxdb", "host"),
    port=config.resolve("influxdb", "port")
)
client.switch_database(config.resolve("influxdb", "dbName"))

r = requests.get('http://pi-rpt-h3:5000/api/status', )
j = json.loads(r.text)

cool = 0
if 'COOLING' == j['state']:
    cool = 1
heat = 0
if 'HEATING' == j['state']:
    heat = 1

influxdb_entry = \
    f'rpt_status,unit=h3,state={j["state"]} ' + \
    f'temperature={j["sensors"]["temperature"]},' + \
    f'pressure={j["sensors"]["pressure"]},' + \
    f'humidity={j["sensors"]["humidity"]},' + \
    f'cool={cool},' + \
    f'heat={heat}'

# print(influxdb_entry)

client.write_points(
    influxdb_entry, protocol=config.resolve("influxdb", "protocol"))
