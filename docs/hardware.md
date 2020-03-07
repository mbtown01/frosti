# Hardware

I've taken an 'agile' approach to this project and focused on an MVP that
delivers a simple hardware/software combination.  *Once that works*, then
I'll focus on refinements.

![RPT board v3.0 rendering](images/board_v3.png)

The board integrates the following components:

* 24V AC to 5V DC power conversion to power everything from the HVAC
* RaspberryPi Zero W
* Three independent relays (cooling, heating, and fan)
* I2C header for 20x4 character-based LCD
* 5-way temminal block to host the 5-wire thermostat cable
* 4 buttons for user input on a break-away daughter board
* Integrated BME280 temperature sensor
* Integrated supercapacitor to handle power sags
* 2 multi-color LEDs for indicating any kind of state
* Several status LEDs for board features

## Power Header (J2)

The power jumper is the 2x2 header at the top-left.  It's designed to be used with two shunts.  Connecting the two *rows* will engage the supercapacitor circuitry.  Should that circuit not work as planned, a shunt across the first *column* will disconnect the supercapacitor circuit and power everything directly from the raw 24V -> 5V conversion.  And yes, somehow I silkscreen'd 'Power Jumper', should have been 'Power Header'.

## LCD w/ Optional MOSFET-driven Power Header (J1)

Only 4 pins are needed for a header to drive the LCD.  This header includes an optional 5th pin which represents power controlled be a MOSFET (T2).  I'm not sure if it's going to work as designed, so I've left the raw power pin here.  Pins from top-down are GND, *MOSFET-driven power*, 5V, SDA, SCL.

## Button Board and Header

The break-away board at the bottom contains the buttons, temperature sensor, and some multi-colored LED indicators.  This breaks away so it can be placed at the face of the thermostat, moving the sensor away from the heat of the main board components, exposing the LEDs, and getting the buttons closer to the user.  To make this board happen with as few pins on the header as possible, a GPIO extension chip (U1) is included.  Via i2c, we can now simply use the GPIO pins on U1 to read buttons and drive the LCDs.  The alternative was 10+ pins and the corresponding cabling... 

## Screw Terminal

The connecting screw terminal is near a hole in the board to allow the thermostat cable through.  Each pin is labeled below with the first letters for blue, green, yellow, white, red.  These are:

* Blue -- Common ground
* Green -- Return to power **fan**
* Yellow -- Return to power **A/C**
* White -- Return to power **heat**
* Red -- Thermostat 24V power input

## Credits

I'd like to thank  Rays Hobby for a
[great write-up on 24V AC to 5V DC power conversion](https://rayshobby.net/wordpress/24vac-to-5vdc-conversion/).  I personally run Ray's
[OpenSprinkler Pi (OSPi) platform](https://opensprinkler.com/product/opensprinkler-pi/) (with the 8-zone extender!) and was inspired to take a shot at my own board by reading his blog posts.
