---
layout: page
title: Developer Setup
permalink: /setup/
---

## Getting Started

```bash
git clone https://github.com/mbtown01/frosti.git
```

You'll need to install docker and docker-compose.

> Before we go further here, it's important to note that for Linux-based dev
> setups, your distribution's version of docker may not be the latest. If the
> commands below don't work, be sure docker's version is >= 1.26. For Ubuntu,
> the following [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04) helped me.
>
> You will also need docker-compose, which oddly enough doesn't come with the
> Linux distribution (though it does seem to come w/ the Windows one?) I would
> checkout this [guide](https://docs.docker.com/compose/install/) on how to do
> that. On the raspberry pi you may also need to check out [another guide](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl)

Even though the Raspberry Pi is our target platform, almost all development
starts on x86 systems. For this guide, I'll refer to `${ARCH}` which can
be either `x86_64` or `arm` depending on the context.

Once you have the source pulled down and the latest version of docker, let's
bring up the development environment for the first time:

```bash
docker volume create grafana-data
docker volume create postgres-data
docker-compose --file docker/docker-compose-${ARCH}.yaml up -d rpt-dev
```

> _Fun fact -_ You can build and push your arm images from x86_64!

The process above is is pulling down the latest docker images for the project
and running them locally. Later on we'll discuss how to build those images
locally.

Once completed, we can test if it worked by running the thermostat simulator
from a terminal inside the dev environment:

```bash
docker exec -ti rpt-dev bash
python3 -m src --hardware term
```

If the above worked, **congrats** -- you now have a local copy of the source
code and a container setup to run it in. You can tweak the code and re-run the
command above to test your changes.

> _Fun fact -_ Tell Docker to only use one core on your laptop! That will
> save you a ton of battery!

## Microsoft VSCode

Once you have VSCode installed and before you load the project for
the first time, install the following extensions:

- Python (Microsoft)
- Remote - Containers (Microsoft)

Next, start a development container on the local machine as we did above:

```bash
docker-compose --file docker/docker-compose-${ARCH}.yaml up -d rpt-dev
```

Now, instead of opening the project directly from your local cloned workspace,
click the bottom-left-hand corner in the IDE and chose "Remote-Containers:
Attach to Running Container". From there, choose 'rpt-dev'. This should start
a new copy of VSCode that is now "inside" your running development container.

Once in the container, it will take a minute or to do to its initial setup.
You'll then want to open the folder '/usr/local/rpt' which is where the source
code is. You will likley need to install/enable the Python module again in
this copy of VSCode (beacuse it's in the container). I also recommend saying
'yes' to all the prompts you'll get for installing a linter, the testing
libraries, etc.

From here, you **should** be able to debug using the 'Local fake hardware'.
Most of the above I figured out from the following [documentation](https://code.visualstudio.com/docs/remote/containers)

> I've had some issues recently where VSCode is trying to interpret the
> locale and gets it wrong. The sympton is when you start a debug session but
> you get a bunch of errors about locale settings. [This bug
> report](https://github.com/microsoft/vscode-remote-release/issues/2169)
> explains the fix (spoiler alert: Turn off 'Detect Locale' in the integrated
> terminal in VSCode settings)

### Debug/attach on RaspberryPi

The configuration above works well for a x64 workstation doing
terminal-based work. However, when developing on the RaspberryPi, you're
going to want to still run the IDE on a big machine and then use the
'Remote-SSH' plugin to get to the Pi. Once installed, click the
lower-left-hand corner quick menu and select 'Remote-SSH: Connect to
Host...' and choose the pi you're working on.

Once there, you can clone the github repo, build (or pull) the arm-based
rpi container, and you're off! If you want to debug your code interactively
with VSCode, first open a local terminal and start python under the debugger:

```bash
docker-compose --file docker/docker-compose-arm.yaml up rpt-debug
```

Once the above is complete, you should be able to choose the 'Python: Local
Attach' debug profile and start debugging. 'Local Attach' is configured in
.vscode/launch.json to run on the local host and has the source directory
mappings configured so the debugger can step line-by-line.

## Building images locally

By and large, the only changes at development time are in the code, which do
not require the container images to be re-built. However, sometimes there is
a need to update the images. When that time comes, we rely on regular
`docker build` (and not `docker-compose`):

```bash
# Build grafana on x86_64 (starting on the repository root)
docker build --tag mbtowns/grafana:x86_64-latest -f docker/grafana/Dockerfile.x86_64 docker/

# Build the x86 development environment
docker build --build-arg RPT_DEV=true--no-cache -f docker/rpt/Dockerfile.x86_64 docker/
```

## QEMU / Build Raspberry Pi Images on x64

I followed [these
instructions](https://matchboxdorry.gitbooks.io/matchboxblog/content/blogs/build_and_run_arm_images.html)
and magically built the rpt container for arm on my local x64 linux box.
Good in a pinch, but I think an RPi v4 is probably faster...

In summary, when the base image coming from an arm-based container, docker
seems to realize this and know that it needs emulation should you be
building on an non-arm platform. It then looks for /usr/bin/qemu-arm-static
(which we inject in to the container).

In summary, on `x86_64` platforms you can simply refer to the `arm` Dockerfile
and docker-compose files and it should simply work. This is much faster than
building on the Raspberry Pi Zero, though a Raspberry Pi v4 makes it much
faster.
