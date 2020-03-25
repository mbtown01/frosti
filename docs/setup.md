# Developer Setup

Let's start with the code first...

```bash
git clone https://github.com/mbtown01/rpt.git
```

## Docker

We're using docker-compose to encapsulate the entire set of runtime
dependencies.  This includes not only python and the modules, but also any
libraries that need to be installed in support of python-land *plus* all
the services like influx and grafana that run in support of the thermostat.

Before we go further here, it's important to note that for Linux-based dev
setups, your distribution's version of docker may not be the latest.  If the
commands below don't work, be sure docker's version is >= 1.26.  For Ubuntu,
the following [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04) helped me.

You will also need docker-compose, which oddly enough doesn't come with the
Linux distribution (though it does seem to come w/ the Windows one?)  I would
checkout this [guide](https://docs.docker.com/compose/install/) on how to do
that.

Once you have the source pulled down and the latest version of docker, let's
make the first container orchestration to host the dev environment

```bash
docker-compose \
    --file docker/docker-compose.yaml \
    --env-file docker/docker-hosttype-${HOSTTYPE}.env \
    build rpt
```

The process above is essentially building out your development environment
with a base Ubuntu 18 image, python, and all the modules you'll need to
develop and run.  It will take some time to execute, especially if you're
running on a Raspberry Pi.

Once completed, we can test if it worked by running the thermostat simulator:

```bash
docker-compose \
    --file docker/docker-compose.yaml \
    --env-file docker/docker-hosttype-${HOSTTYPE}.env \
    run rpt
```

If the above worked, congrats -- you now have a local copy of the source code
and a container setup to run it in.  You can tweak the code and re-run the
command above to test your changes.

# Extra stuff

To get the documentation locally

```bash
docker run -ti -p 4000:4000 docs/docker.github.io:latest
```

For development, here are some useful docker commands

```bash
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
