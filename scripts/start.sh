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
        docker-compose \
            --file docker/docker-compose.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            build rpt
    shift
    ;;
    -s|--start)
        docker-compose \
            --file docker/docker-compose.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run rpt
    shift
    ;;
    -v|--vscode)
        docker-compose \
            --file docker/docker-compose.yaml \
    	    --file .devcontainer/docker-compose-extend.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run rpt
    shift
    ;;
    -c|--console)
        docker-compose \
            --file docker/docker-compose.yaml \
            --file .devcontainer/docker-compose-extend.yaml \
            --env-file docker/docker-hosttype-${HOSTTYPE}.env \
            run --entrypoint /bin/bash rpt
    shift
    ;;
  esac
done