#FROM influxdb:latest
#FROM arm32v5/influxdb:latest
ARG HOSTTYPE_IMAGE
FROM ${HOSTTYPE_IMAGE}
LABEL maintainer="Mike Townsley mike@madllama.net"

ADD ./docker/influxdb/create_db.iql /docker-entrypoint-initdb.d/
