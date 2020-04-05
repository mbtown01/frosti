ARG HOSTTYPE_IMAGE
FROM ${HOSTTYPE_IMAGE}
LABEL maintainer="Mike Townsley mike@madllama.net"

COPY docker/qemu-arm-static /usr/bin/qemu-arm-static

ARG HOSTTYPE

# upgrade base packages
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip && \
    apt-get install -y python3.7 python3.7-dev python3-smbus && \
    apt-get install -y vim i2c-tools git postgresql-client

# install all the requied modules
RUN python3.7 -m pip install pip && \
    python3.7 -m pip install \
        adafruit-blinka \
        adafruit-circuitpython-bmp280 \
        adafruit-circuitpython-bme280 \
        adafruit-circuitpython-charlcd \
        adafruit-circuitpython-mcp230xx \
        flask requests ptvsd psycopg2-binary \
        sqlalchemy sqlalchemy-utils

# run anything pi-specific
RUN if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        apt-get install -y python-rpi.gpio; \
        python3.7 -m pip install RPi.GPIO; \
    fi

WORKDIR /usr/local/rpt
