#FROM arm32v5/debian:latest
#FROM ubuntu:18.04
ARG HOSTTYPE_IMAGE
FROM ${HOSTTYPE_IMAGE}
LABEL maintainer="Mike Townsley mike@madllama.net"

ARG HOSTTYPE

RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get install -y python3.7 python3.7-dev \
        python3-smbus i2c-tools git \
        language-pack-en-base locales && \
    dpkg-reconfigure --frontend noninteractive locales 
RUN if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        apt-get install -y python-rpi.gpio; \
    fi

# install all the requied modules
RUN python3.7 -m pip install pip && \
    python3.7 -m pip install \
        adafruit-blinka \
        adafruit-circuitpython-bmp280 \
        adafruit-circuitpython-bme280 \
        adafruit-circuitpython-charlcd \
        flask influxdb requests \
        ptvsd
RUN echo FRD ${HOSTTYPE} BAR; if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        pip3 install RPi.GPIO; \
    fi

ENTRYPOINT cd /usr/local/rpt && python3 -m src --sim
