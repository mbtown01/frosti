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


def get_simple_element(ser, elementName, attrName, command):
    element = None
    while element is None:
        try:
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
        except:
            print(sys.exc_info()[0])

    value = int(element.find(attrName).text, 16)
    multiplier = max(1, int(element.find("Multiplier").text, 16))
    divisor = max(1, int(element.find("Divisor").text, 16))
    return value * multiplier / float(divisor)


if not config.influxdb_enabled:
    raise RuntimeError('InfluxDB is not configured')

client = InfluxDBClient(host=config.influxdb_host, port=config.influxdb_port)
client.switch_database(config.influxdb_dbName)

payload = {
    'meterID': config.gogriddy_meterId,
    'memberID': config.gogriddy_meterId,
    'settlement_point': config.gogriddy_settlementPoint
}

r = requests.post(config.gogriddy_apiUrl, data=json.dumps(payload))
j = json.loads(r.text)

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

influxdb_entry = \
    f'electric_cost,price_date={j["now"]["date_local_tz"]},' + \
    f'future_date={j["forecast"][0]["date_local_tz"]} ' + \
    f'future_price={j["forecast"][0]["price_ckwh"]},' + \
    f'current_price={j["now"]["price_ckwh"]},' + \
    f'value_score={j["now"]["value_score"]},' + \
    f'future_value_score={j["forecast"][0]["value_score"]},' + \
    f'wstd_dev_ckwh={j["now"]["std_dev_ckwh"]},' + \
    f'future_wstd_dev_ckwh={j["forecast"][0]["std_dev_ckwh"]},' + \
    f'seconds_until_refresh={j["seconds_until_refresh"]},' + \
    f'demand={demand},' + \
    f'meter={meter}'

# print(influxdb_entry)
client.write_points(influxdb_entry, protocol=config.influxdb_protocol)
