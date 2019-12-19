#FROM arm32v5/debian:latest
ARG ARCH
FROM ${ARCH}/debian:latest
LABEL maintainer="Mike Townsley mike@madllama.net"

RUN apt-get update && \
    apt-get install -y i2c-tools python3 python3-pip python3-smbus python-rpi.gpio

# install all the requied modules
RUN pip3 install \
    adafruit-blinka \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-charlcd \
    flask influxdb requests \
    ptvsd RPi.GPIO

ADD ./etc/thermostat.json /etc/thermostat.json

ENTRYPOINT cd /usr/local/rpt && python3 -m src
