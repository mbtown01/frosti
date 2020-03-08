#!/bin/bash

if [[ $(uname -a) =~ "^Darwin" ]]; then 
    alias realpath=grealpath 
fi
RPT_HOME="$(realpath $(dirname $0)/../)"

# Assert the environment is sane
# Run the containers
# Debug the containers

build() {
    cd ${RPT_HOME}
    docker-compose \
        --file docker/docker-compose.yaml \
        --env-file docker/docker-hosttype-${HOSTTYPE}.env \
        build rpt
}

start() {
    cd ${RPT_HOME}
    docker-compose \
        --file docker/docker-compose.yaml \
        --env-file docker/docker-hosttype-${HOSTTYPE}.env \
        run rpt
}

develop() {
    cd ${RPT_HOME}
    docker-compose \
        --file docker/docker-compose.yaml \
	    --file .devcontainer/docker-compose-extend.yaml \
        --env-file docker/docker-hosttype-${HOSTTYPE}.env \
        run rpt
}

develop-console() {
    cd ${RPT_HOME}
    docker-compose \
        --file docker/docker-compose.yaml \
	    --file .devcontainer/docker-compose-extend.yaml \
        --env-file docker/docker-hosttype-${HOSTTYPE}.env \
        run --entrypoint /bin/bash rpt
}

develop-console