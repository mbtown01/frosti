# rpt

RaspberryPi-powered Griddy-enabled thermostat

## Overview

RPT is yet-another RaspberryPi powered thermostat, with the added twist that GoGriddy customers can vary temperature targets based on the current cost of electricity.

### Running

Start the main process with python by calling `python -m src` from the rpt directory.

## For Developers

### Setup a development environment

### Creating a new RaspberryPi image

### Debugging

Though it's not impossible, it's far better to have a dedicated development machine and not work directly on the RaspberryPi.  It's a great little computer, but just doesn't have much horsepower to really host an IDE.

At start-up, RPT checks to see if `uname -a` contains the 'armv' architecture.  If detected, RPT starts in hardware mode and assumes it's attached to an RPT board.  Otherwise, it assumes it's in simulation mode and uses the terminal as a fake LCD, using keys 1-4 as proxies for the 4 buttons.
