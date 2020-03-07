#FROM arm32v5/debian:latest
#FROM ubuntu:18.04
ARG HOSTTYPE_IMAGE_RPT
FROM ${HOSTTYPE_IMAGE_RPT}

LABEL maintainer="Mike Townsley mike@madllama.net"

RUN apt-get update && \
    apt-get install -y i2c-tools python3 python3-pip python3-smbus
RUN if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        apt-get install -y python-rpi.gpio; \
    fi

# install all the requied modules
RUN pip3 install \
    adafruit-blinka \
    adafruit-circuitpython-bmp280 \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-charlcd \
    flask influxdb requests \
    ptvsd
RUN if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        pip3 install RPi.GPIO; \
    fi

ADD ./etc/thermostat.json /etc/thermostat.json

ENTRYPOINT cd /usr/local/rpt && python3 -m src --sim
