ARG HOSTTYPE_IMAGE
FROM ${HOSTTYPE_IMAGE}
LABEL maintainer="Mike Townsley mike@madllama.net"

COPY docker/qemu-arm-static /usr/bin/qemu-arm-static

ARG GRAFANA_VERSION

# upgrade base packages
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y adduser libfontconfig1 wget

RUN cd /tmp && \
    wget https://dl.grafana.com/oss/release/${GRAFANA_VERSION} && \
    dpkg -i ${GRAFANA_VERSION}

# RUN . /etc/profile && npm install -g @angular/cli

WORKDIR /usr/share/grafana
