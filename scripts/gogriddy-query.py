#!/usr/bin/python3

import os
import configparser
import requests
import json
from time import sleep
from xml.etree import ElementTree

# pylint: disable=import-error
from influxdb import InfluxDBClient
import serial
# pylint: enable=import-error


def get_simple_element(ser, elementName, attrName, command):
    ser.write(command)
    ser.flush()

    sleep(1)
    xml_text = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<data>\n"
    for line in ser.readlines():
        xml_text += str(line)
    xml_text += "</data>"

    parser = ElementTree.XMLParser(encoding="utf-8")
    root = ElementTree.fromstring(xml_text, parser=parser)
    element = root.find(elementName)
    value = int(element.find(attrName).text, 16)
    multiplier = max(1, int(element.find("Multiplier").text, 16))
    divisor = max(1, int(element.find("Divisor").text, 16))
    value = value * multiplier / float(divisor)

    return value

dir_name = os.path.dirname(os.path.realpath(__file__))
conf = dir_name + '/../etc/gogriddy-config.conf'

config = configparser.ConfigParser()
config.read(conf)

meterID = config.get('default', 'meterID')
memberID = config.get('default', 'memberID')
settlement_point = config.get('default', 'settlement_point')
api_url = config.get('default', 'api_url')
influxdb_protocol = config.get('influxdb', 'protocol')
influxdb_host = config.get('influxdb', 'host')
influxdb_port = config.get('influxdb', 'port')
influxdb_dbname = config.get('influxdb', 'dbname')

client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
client.switch_database(influxdb_dbname)

payload = {
    'meterID': meterID, 'memberID': memberID,
    'settlement_point': settlement_point
}

r = requests.post(api_url, data=json.dumps(payload))
j = json.loads(r.text)

price_date = j["now"]["date_local_tz"]
current_price = j["now"]["price_ckwh"]
value_score = j["now"]["value_score"]
wstd_dev_ckwh = j["now"]["std_dev_ckwh"]
seconds_until_refresh = j["seconds_until_refresh"]
future_date = j["forecast"][0]["date_local_tz"]
future_price = j["forecast"][0]["price_ckwh"]
future_wstd_dev_ckwh = j["forecast"][0]["std_dev_ckwh"]
future_value_score = j["forecast"][0]["value_score"]

influxdb_entry = \
    f'electric_cost,price_date={price_date},future_date={future_date} ' + \
    f'future_price={future_price},current_price={current_price},' + \
    f'value_score={value_score},future_value_score={future_value_score},' + \
    f'wstd_dev_ckwh={wstd_dev_ckwh},' + \
    f'future_wstd_dev_ckwh={future_wstd_dev_ckwh},' + \
    f'seconds_until_refresh={seconds_until_refresh}'

# Connect and reuse the serial interface until complete
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Request that the device synchronize and not send update fragments and
# then clear out any pending lines in the input buffer
ser.write(b"<Command><Name>initialize</Name></Command>")
ser.readlines()

# Issue the command to request demand/meter and then store for later
demand = get_simple_element(
    ser, "InstantaneousDemand", "Demand",
    b"<Command><Name>get_instantaneous_demand</Name>" +
    b"<Refresh>Y</Refresh></Command>")
meter = get_simple_element(
    ser, "CurrentSummationDelivered", "SummationDelivered",
    b"<Command><Name>get_current_summation_delivered</Name>" +
    b"<Refresh>Y</Refresh></Command>")
ser.close()

influxdb_entry += f',demand={demand},meter={meter}'

print(influxdb_entry)
client.write_points(influxdb_entry, protocol=influxdb_protocol)
