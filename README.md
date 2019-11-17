# rpt

RaspberryPi-powered Griddy-enabled thermostat

## Overview

RPT is yet another Python-based, Raspberry Pi powered thermostat, with the added twist that [GoGriddy](https://www.gogriddy.com/) customers can vary temperature targets based on the current cost of electricity.

![RPT board v1.0 rendering](docs/images/board_v1.jpeg)

## Features

* Simple user interface at the thermostat for setting temperature targets
* Simple web interface (hosted by the thermostat) for configuring from remote
* RESTful API for getting current environmental data as well as changing settings

## More Topics

* [Movations](docs/motivation.md) for yet another thermostat
* [Design](docs/design.md) overview
* [Gettings started](docs/setup.md) with rpt
  * This is currently targeted for developers

## Credits

I'd like to thank Ray at Rays Hobby for a [great write-up on 24V AC to 5V DC power conversion](https://rayshobby.net/wordpress/24vac-to-5vdc-conversion/).  I personally run Ray's [OpenSprinkler Pi (OSPi) platform](https://opensprinkler.com/product/opensprinkler-pi/) (with the 8-zone extender!) and was inspired to take a shot at my own board by reading his blog posts.