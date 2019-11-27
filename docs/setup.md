# Developer Setup

RPT is based on python3.   I personally use pip3 for bringing in packages.  Depending on your development platform, you may have several ways of installing both python and your own packages. 

## Containerization Strategy

Containers are the way to go for development and  deployment.  On first run, volumes are created for influx and grafana and default installations need to occur.  

For influx, need to create and permission the database.  This may include changing/setting admin userid/password.  Need to be careful so we don't stomp already existing data should it exist. 

So that we don't have to fork and create a custom container for influxdb, could create a setup/initialize script in rpt that tests if the db is there and if not creates it on first touch.  Think that's already in the RPT code.

At development time, modifications to the grafana configuration should be captured in source control somehow.  That is a different way of running the container than a production version.  At dev time, a local directory needs inserted.  At production time, a clean volume needs to be populated with the context from git.  MAY be able to do this with one configuration.

# Docker

To get the documentation locally
```
docker run -ti -p 4000:4000 docs/docker.github.io:latest
```

For development, here are some useful docker commands
```
# Build and run the services
docker-compose --file docker/docker-compose.yaml run --build rpt

# After a build, debug the rpt server
docker-compose --file docker/docker-compose.yaml run -p 3001:3001 -p 5000:5000 \
    --entrypoint '/bin/bash -c "cd /usr/local/rpt && python3 -m ptvsd --host 0.0.0.0 --port 3001 --wait -m src"' rpt

```

To get a terminal in one of your composed containers (e.g. rpt)
```
docker-compose --file docker/docker-compose.yaml exec rpt sh
```

On MacOS, get connected to the VM hosting docker
```
screen ~/Library/Containers/com.docker.docker/Data/vms/0/tty
```

RPT uses a docker volume for storing the influx database
```
docker volume inspect docker_influxdb
```

To remove the local volumes and start over
```
docker-compose --file docker/docker-compose.yaml down --volumes
```

# On the RaspberryPi

```
sudo apt install python3 wiringpi python3-pip i2c-tools python3-smbus
```

# Required modules
```
pip3 install --user adafruit-circuitpython-bme280
pip3 install --user adafruit-blinka adafruit-circuitpython-charlcd
pip3 install --user flask influxdb requests pytest pytest-cov
pip3 install --user --upgrade ptvsd
```

## Setup a development environment

## Creating a new RaspberryPi image

## Debugging

Though it's not impossible, it's far better to have a dedicated development machine and not work directly on the RaspberryPi.  It's a great little computer, but just doesn't have much horsepower to really host an IDE.

At start-up, RPT checks to see if `uname -a` contains the 'armv' architecture.  If detected, RPT starts in hardware mode and assumes it's attached to an RPT board.  Otherwise, it assumes it's in simulation mode and uses the terminal as a fake LCD, using keys 1-4 as proxies for the 4 buttons.
