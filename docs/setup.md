# Developer Setup

Let's start with the code first...

```bash
git clone https://github.com/mbtown01/rpt.git
```

## Docker

We're using docker-compose to make the runtime and it's set of dependencies as portable as possible.  This includes not only python and the modules, but also
any libraries that need to be installed in support of python-land *plus* all
the services like postgres and grafana that run in support of the thermostat.

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
that.  On the raspberry pi you may also need to check out [another guide](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl)

Once you have the source pulled down and the latest version of docker, let's
make the first container orchestration to host the dev environment

```bash
./scripts/docker-compose.py build rpt
```

For convenience, we've wrapped docker-compose so that the appropriate flags and
environment are set before the real docker-compose is exec()'d.

The process above is essentially building out your development environment
with a base linux, python, and all the modules you'll need to
develop and run.  It will take some time to execute, especially if you're
running on a Raspberry Pi.

Once completed, we can test if it worked by running the thermostat simulator:

```bash
./scripts/docker-compose.py run --service-ports rpt-term
```

If the above worked, **congrats** -- you now have a local copy of the source
code and a container setup to run it in.  You can tweak the code and re-run the
command above to test your changes.

> *Fun fact -* Tell Docker to only use one core on your laptop!  That will
save you a ton of battery!

## Docker Hub

How do I push an image to dockerhub?

[https://ropenscilabs.github.io/r-docker-tutorial/04-Dockerhub.html](https://ropenscilabs.github.io/r-docker-tutorial/04-Dockerhub.html)

## Microsoft VSCode

Once you have VSCode installed and before you load the project for
the first time, install the following extensions:

* Python (Microsoft)
* Remote - Containers (Microsoft)

Next, start a development container on the local machine

```bash
./scripts/docker-compose.py run \
    --name rpt-dev --restart yes \
    rpt-daemon bash -c "while sleep 600; do /bin/false; done"
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
Most of the above I figured out from the following [documentation](
https://code.visualstudio.com/docs/remote/containers)

> I've had some issues recently where VSCode is trying to interpret the
locale and gets it wrong.  The sympton is when you start a debug session but
you get a bunch of errors about locale settings. [This bug
report](https://github.com/microsoft/vscode-remote-release/issues/2169)
explains the fix (spoiler alert: Turn off 'Detect Locale' in the integrated
terminal in VSCode settings)

### Debug/attach on RaspberryPi

The configuration above works well for a x64 workstation doing
terminal-based work.  However, when developing on the RaspberryPi, you're
going to want to still run the IDE on a big machine and then use the
'Remote-SSH' plugin to get to the Pi.  Once installed, click the
lower-left-hand corner quick menu and select 'Remote-SSH: Connect to
Host...' and choose the pi you're working on.  

Once there, you can clone the github repo, build (or pull) the  arm-based
rpi container, and you're off!  If you want to debug your code interactively
with VSCode, first open a local terminal and start python under the debugger

```bash
./scripts/docker-compose.py run --service-ports rpt-daemon-debug
```

Once the avove is complete, you should be able to choose the 'Python: Local
Attach' debug profile and start debugging.  'Local Attach' is configured in
.vscode/launch.json to run on the local host and has the source directory
mappings configured so the debugger can step line-by-line.  

## QEMU / Build Raspberry Pi Images on x64

I followed [these
instructions](https://matchboxdorry.gitbooks.io/matchboxblog/content/blogs/build_and_run_arm_images.html)
and magically built the rpt container for arm on my local x64 linux box.
Good in a pinch, but I think an RPi v4 is probably faster...

In summary, when the base image coming from an arm-based container, docker
seems to realize this and know that it needs emulation should you be
building on an non-arm platform.  It then looks for /usr/bin/qemu-arm-static
(which we inject in to the container).

To make this even easier, you can use the docker-compose wrapper and build for
arm from x86_64:

```bash
./scripts/docker-compose.py --arch arm build grafana
```

## Setup watchdog timer

This one seems the best and easiest to implement looks like the following:

[https://www.raspberrypi.org/forums/viewtopic.php?t=258042](https://www.raspberrypi.org/forums/viewtopic.php?t=258042)

This one has more info, but relies on the 'watchdog' service.  The link above relies on Systemd
[https://www.raspberrypi.org/forums/viewtopic.php?t=210974](https://www.raspberrypi.org/forums/viewtopic.php?t=210974)

## Install RPT as a service on the Raspberry Pi

I got the info for how to do this from [https://stackoverflow.com/questions/43671482/how-to-run-docker-compose-up-d-at-system-start-up](https://stackoverflow.com/questions/43671482/how-to-run-docker-compose-up-d-at-system-start-up).  In
summary, from your local repo

```bash
cp etc/rpt.service /etc/systemd/system
sudo systemctl enable rpt
```

### Random terminal

To get a terminal in one of your composed containers (e.g. rpt)

```bash
./scripts/docker-compose.py run --entrypoint sh rpt
```

### Docker and MacOS

On MacOS, docker runs in its own VM.  Using docker volumes creates space in
the VM and not on the local machine.  To inspect the volume contents, you
can get console on the VM with the following command:

```bash
screen ~/Library/Containers/com.docker.docker/Data/vms/0/tty
```

RPT uses a docker volume for storing the postgres database

```bash
docker volume inspect docker_postgres
```

To remove the local volumes and start over

```bash
docker-compose --file docker/docker-compose.yaml down --volumes
```
