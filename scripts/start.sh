#!/bin/bash

if [[ $(uname -a) =~ "^Darwin" ]]; then 
    alias realpath=grealpath 
fi
RPT_HOME="$(realpath $(dirname $0)/../)"
cd ${RPT_HOME}

# Assert the environment is sane
# Run the containers
# Debug the containers

while (( "$#" )); do
  case "$1" in
    -b|--build)
        set -x
        exec docker-compose \
            --file docker/docker-compose.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            build rpt
    shift
    ;;
    -r|--run)
        set -x
        exec docker-compose \
            --file docker/docker-compose.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run rpt python3 -m src --hardware term
    shift
    ;;
    -v|--vscode)
        set -x
        exec docker-compose \
            --file docker/docker-compose.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run rpt bash -c "while sleep 600; do /bin/false; done"
    shift
    ;;
    -c|--console)
        set -x
        exec docker-compose \
            --file docker/docker-compose.yaml \
            --file .devcontainer/docker-compose-extend.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run --entrypoint /bin/bash rpt
    shift
    ;;
  esac
done