# Developer Setup

RPT is based on python3.   I personally use pip3 for bringing in packages.
Depending on your development platform, you may have several ways of installing
both python and your own packages.

## Containerization Strategy

We're using containers to encapsulate the entire runtime into a docker-compose
configuration so all run-time dependencies are clear.  It also makes it much
easier to do development off the RaspberryPi -- the local environment is
almost a perfect match

For influx, need to create and permission the database.  This may include
changing/setting admin userid/password.  Need to be careful so we don't stomp
already existing data should it exist.

So that we don't have to fork and create a custom container for influxdb, could
create a setup/initialize script in rpt that tests if the db is there and if not
creates it on first touch.  Think that's already in the RPT code.

At development time, modifications to the grafana configuration should be
captured in source control somehow.  That is a different way of running the
container than a production version.  At dev time, a local directory needs
inserted.  At production time, a clean volume needs to be populated with the
context from git.  MAY be able to do this with one configuration.

## Docker

To get the documentation locally

```bash
docker run -ti -p 4000:4000 docs/docker.github.io:latest
```

For development, here are some useful docker commands

```bash
# Build and run the services
docker-compose --file docker/docker-compose.yaml build rpt
docker-compose --file docker/docker-compose.yaml run rpt

# After a build, debug the rpt server
docker-compose --file docker/docker-compose.yaml run \
    -p 3001:3001 -p 5000:5000 \
    --entrypoint '/bin/bash -c "cd /usr/local/rpt && python3 -m ptvsd --host 0.0.0.0 --port 3001 --wait -m src"' rpt

```

To get a terminal in one of your composed containers (e.g. rpt)

```bash
docker-compose --file docker/docker-compose.yaml run --entrypoint sh rpt
```

On MacOS, docker runs in its own VM.  Using docker volumes creates space in
the VM and not on the local machine.  To inspect the volume contents, you
can get console on the VM with the following command:

```bash
screen ~/Library/Containers/com.docker.docker/Data/vms/0/tty
```

RPT uses a docker volume for storing the influx database

```bash
docker volume inspect docker_influxdb
```

To remove the local volumes and start over

```bash
docker-compose --file docker/docker-compose.yaml down --volumes
```

## On the RaspberryPi

This was what I had to do the first time I got the Raspberry Pi docker
environment setup.  It's unclear whether it's at ALL necessary and that you
can't simply just apt-get install docker and docker-compose and be done with it.
Need to test again...

```bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
sudo apt-get install libffi-dev libssl-dev
sudo apt-get install -y python python-pip
sudo pip install docker-compose
```

The first time I tried this, the docker installation process had issues with
conflicting versions of python v2.7.  I had to do the following two commands
in addition to the ones above to make things work:

```bash
sudo cp -r /usr/local/lib/python2.7/dist-packages/backports/ssl_match_hostname /usr/lib/python2.7/dist-packages/backports/
sudo cp -r /usr/local/lib/python2.7/dist-packages/backports/shutil_get_terminal_size /usr/lib/python2.7/dist-packages/backports/

```

```bash
sudo apt install python3 wiringpi python3-pip i2c-tools python3-smbus
```

## Required modules

```bash
pip3 install --user adafruit-circuitpython-bme280
pip3 install --user adafruit-blinka adafruit-circuitpython-charlcd
pip3 install --user flask influxdb requests pytest pytest-cov
pip3 install --user --upgrade ptvsd
```

## Setup a development environment

## Creating a new RaspberryPi image

## Debugging

Though it's not impossible, it's far better to have a dedicated development
machine and not work directly on the RaspberryPi.  It's a great little computer,
but just doesn't have much horsepower to really host an IDE.

At start-up, RPT checks to see if `uname -a` contains the 'armv' architecture.
If detected, RPT starts in hardware mode and assumes it's attached to an RPT
board.  Otherwise, it assumes it's in simulation mode and uses the terminal as a
fake LCD, using keys 1-4 as proxies for the 4 buttons.
