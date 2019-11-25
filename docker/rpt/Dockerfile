FROM ubuntu:18.04
LABEL maintainer="Mike Townsley mike@madllama.net"

RUN apt-get update && \
    apt-get install -y i2c-tools python3 python3-pip python3-smbus

# install all the requied modules
RUN pip3 install \
    adafruit-blinka \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-charlcd \
    flask influxdb requests \
    ptvsd

ADD ./src/ /rpt/src
ADD ./etc/thermostat.json /etc/thermostat.json

ENTRYPOINT cd /rpt && python3 -m src