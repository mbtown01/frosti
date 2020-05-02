ARG HOSTTYPE_IMAGE
FROM ${HOSTTYPE_IMAGE}
LABEL maintainer="Mike Townsley mike@madllama.net"

COPY docker/qemu-arm-static /usr/bin/qemu-arm-static

ARG HOSTTYPE
ARG NODEJS_VERSION

# upgrade base packages
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
    python3 python3-pip python3-dev python3-smbus \
    vim i2c-tools git postgresql-client libpq-dev curl tzdata

# install all the requied modules
RUN python3 -m pip install pip && \
    python3 -m pip install \
        adafruit-blinka \
        adafruit-circuitpython-bmp280 \
        adafruit-circuitpython-bme280 \
        adafruit-circuitpython-charlcd \
        adafruit-circuitpython-mcp230xx \
        flask requests ptvsd psycopg2-binary \
        sqlalchemy sqlalchemy-utils smbus PyYAML pykwalify

# run anything pi-specific
RUN if [ ${HOSTTYPE:-none} = 'arm' ]; then \
        apt-get install -y python-rpi.gpio; \
        python3 -m pip install RPi.GPIO; \
    fi

# # https://github.com/nodejs/help/wiki/Installation
# RUN set -x && cd /tmp && curl --output distro.tar.gz \
#         https://nodejs.org/download/release/latest-v11.x/${NODEJS_VERSION}.tar.gz && \
#     mkdir /usr/local/lib/nodejs && \
#     tar xfvz distro.tar.gz -C /usr/local/lib/nodejs && \
#     echo "export PATH=/usr/local/lib/nodejs/${NODEJS_VERSION}/bin:$PATH" > /etc/profile.d/nodejs.sh

# RUN . /etc/profile && npm install -g @angular/cli

WORKDIR /usr/local/rpt
