#FROM influxdb:latest
#FROM arm32v5/influxdb:latest
ARG HOSTTYPE_IMAGE_INFLUX
FROM ${HOSTTYPE_IMAGE_INFLUX}

LABEL maintainer="Mike Townsley mike@madllama.net"

ADD ./docker/influxdb/create_db.iql /docker-entrypoint-initdb.d/