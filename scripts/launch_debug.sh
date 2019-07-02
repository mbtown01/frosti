#!/bin/bash

set -x

RPT_HOME="$(readlink -f $(dirname $0)/../)"
source ${RPT_HOME}/scripts/setenv.sh

# Shutdown any previously running interpreters
ssh ${RPT_RUN_USER}@${RPT_RUN_HOSTNAME} killall python3

# Sync the project and execute
rsync -avz "${RPT_HOME}/src" "${RPT_RUN_USER}@${RPT_RUN_HOSTNAME}:rpt"
ssh ${RPT_RUN_USER}@${RPT_RUN_HOSTNAME} python3 -m ptvsd \
    --host ${RPT_RUN_IPADDR} --port ${RPT_RUN_PORT} --wait \
    "rpt/${RPT_RUN_ENTRYPOINT}"
