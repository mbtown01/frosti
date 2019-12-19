# Hardware

I've taken an 'agile' approach to this project and focused on an MVP that
delivers a simple hardware/software combination.  *Once that works*, then
I'll focus on refinements. 

![RPT board v1.0 rendering](images/board_v1.png)

The board integrates the following components:
* 24V AC to 5V DC power conversion to power everything from the HVAC
* RaspberryPi Zero W
* Three independent relays (cooling, heating, and fan)
* 20x4 character-based LCD
* 5-way temminal block to host the 5-wire thermostat cable
* 4 buttons for user input
* 2 I2C headers for the temperature sensor (BMP280) and the LCD

This is board v1.0, and there are many things that absolutely need to be
changed.  I intend on writing an entire article on what I learned by running
this board for a period of time and what will go into v2.0.

## Credits

I'd like to thank Ray at Rays Hobby for a 
[great write-up on 24V AC to 5V DC power conversion](https://rayshobby.net/wordpress/24vac-to-5vdc-conversion/).  I personally run Ray's 
[OpenSprinkler Pi (OSPi) platform](https://opensprinkler.com/product/opensprinkler-pi/)
(with the 8-zone extender!) and was inspired to take a shot at my own board by 
reading his blog posts.