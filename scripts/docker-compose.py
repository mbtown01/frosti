#!/usr/bin/env python3

from os import environ, execve, path
from sys import argv
from subprocess import check_output


ALL_HOSTTYPES = {
    'x86_64': 'x86_64',
    'armv7l': 'arm',
    'armv6l': 'arm'
}

ENV_BY_HOSTTYPE = {
    'x86_64': {
        'HOSTTYPE': 'x86_64',
        'HOSTTYPE_IMAGE_RPT': 'ubuntu:19.10',
        'HOSTTYPE_IMAGE_GRAFANA': 'grafana/grafana:latest',
        'HOSTTYPE_IMAGE_POSTGRES': 'postgres:12.2',
        'NODEJS_VERSION': 'node-v11.15.0-linux-x64'
    },
    'arm': {
        'HOSTTYPE': 'arm',
        'HOSTTYPE_IMAGE_RPT': 'balenalib/rpi-raspbian:buster-20200408',
        'HOSTTYPE_IMAGE_GRAFANA':
            'unibaktr/grafana:v5.4.2@sha256:7aa34a3729674298da67b8197e'
            '64d120225e34c5829b87a9f28dc179c66a9ff2',
        'HOSTTYPE_IMAGE_POSTGRES': 'arm32v6/postgres:12.2-alpine',
        'NODEJS_VERSION': 'node-v11.15.0-linux-armv6l'
    }
}

ENV_BY_OSNAME = {
    'Darwin': {
        'POSTGRES_DATA': '/private/var/lib/postgresql/data'
    },
    'Linux': {
        'POSTGRES_DATA': '/var/lib/postgresql/data'
    }
}
osName = check_output(['uname', '-s']).decode('UTF-8').rstrip()
osEnv = ENV_BY_OSNAME.get(osName)
if osEnv is None:
    raise Exception(f"OS {osName} is not supported")

uname = check_output(['uname', '-m']).decode('UTF-8').rstrip()
hosttype = ALL_HOSTTYPES.get(uname)
if hosttype is None:
    raise Exception(f"Host with uname {uname} is not supported")

postgresData = ENV_BY_OSNAME[osName]['POSTGRES_DATA']
if not path.isdir(postgresData):
    raise Exception(
        f"Directory {postgresData} must exist and be "
        "writable by docker user")

environment = environ.copy()
for key, value in ENV_BY_HOSTTYPE[hosttype].items():
    environment[key] = value
for key, value in ENV_BY_OSNAME[osName].items():
    environment[key] = value

timezone = check_output(
    ['readlink', '/etc/localtime']).decode('UTF-8').rstrip()
environment['TZ'] = \
    timezone[(timezone.find("/zoneinfo/")+10):]

arguments = [
    '/usr/local/bin/docker-compose',
    '--file', 'docker/docker-compose.yaml'] + argv[1:]
execve(arguments[0], arguments, environment)
