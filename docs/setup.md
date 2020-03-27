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

Containers are ephemeral, and once spun down any content generated in the
container is destroyed.  This docker-compose setup injects the rpt source tree
into the container so that the container always has the latest copy and any
changes made via editing/debugging in the container are retained.

> Before we go further here, it's important to note that for Linux-based dev
setups, your distribution's version of docker may not be the latest.  If the
commands below don't work, be sure docker's version is >= 1.26.  For Ubuntu,
the following [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04) helped me. 
>
>You will also need docker-compose, which oddly enough doesn't come with the
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

If the above worked, **congrats** -- you now have a local copy of the source code
and a container setup to run it in.  You can tweak the code and re-run the
command above to test your changes.

# Microsoft VSCode

Once you have VSCode installed and before you load the project for
the first time, install the following extensions:

* Python (Microsoft)
* Remote - Containers (Microsift)

Next, start a development container on the local machine

```bash
docker-compose \
    --file docker/docker-compose.yaml \
    --file .devcontainer/docker-compose-extend.yaml \
    --env-file docker/docker-hosttype-${HOSTTYPE}.env \
    run rpt
```

Now, instead of opening the project directly from your local cloned workspace,
click the bottom-left-hand corner in the IDE and chose "Remote-Containers: 
Attach to Running Container".  From there, choose the option that has 'rpt'
in it.  This should start a new copy of VSCode that is now "inside" your
running development container.  

Once in the container, it will take a minute or to do to its initial setup.
You'll then want to open the folder '/usr/local/rpt' which is where the source
code is.  You will likley need to install/enable the Python module again in 
this copy of VSCode (beacuse it's in the container).  I also recommend saying
'yes' to all the prompts you'll get for installing a linter, the testing
libraries, etc.  

From here, you **should** be able to debug using the 'Local fake hardware'.
Most of the above I figured out from the following [documentation]
(https://code.visualstudio.com/docs/remote/containers)

# Extra Commands

## Download the docker documentation

In case you're on a plane and are too cheap for WiFi...

```bash
docker run -ti -p 4000:4000 docs/docker.github.io:latest
```
## Debug/attach 

If you are no fun and don't like the VSCode + Remote-Containers setup, you can
run VSCode locally and attach to your container.  You can get the container 
started and ready with the following:

```bash
docker-compose \
    --file docker/docker-compose.yaml \
    --env-file docker/docker-hosttype-${HOSTTYPE}.env \
    run  -p 3001:3001 -p 5000:5000 \
        --entrypoint '/bin/bash -c "cd /usr/local/rpt && python3 -m ptvsd --host 0.0.0.0 --port 3001 --wait -m src"' rpt
```
Once the avove is complete, you should be able to 'attach' to the container.

## Random terminal 

To get a terminal in one of your composed containers (e.g. rpt)

```bash
docker-compose \
    --file docker/docker-compose.yaml \
    --env-file docker/docker-hosttype-${HOSTTYPE}.env \
    run --entrypoint sh rpt
```

## Docker and MacOS

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