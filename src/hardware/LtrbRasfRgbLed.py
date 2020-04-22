from src.core.generics import GenericRgbLed
from adafruit_mcp230xx.mcp23017 import MCP23017


class LtrbRasfRgbLed(GenericRgbLed):
    """ Simple three-color RGB LED that can only be in 8 states """

    def __init__(
            self, mcp: MCP23017,
            redPin: int, greenPin: int, bluePin: int):

        self.__mcp = mcp
        self.__colorPinMap = {
            GenericRgbLed.Color.RED: mcp.get_pin(redPin),
            GenericRgbLed.Color.GREEN: mcp.get_pin(greenPin),
            GenericRgbLed.Color.BLUE: mcp.get_pin(bluePin),
        }

        for pin in self.__colorPinMap.values():
            pin.direction = Direction.OUTPUT

    def setColor(self, color: GenericRgbLed.Color):
        for pinColor, pin in self.__colorPinMap.items():
            pin.value = 1 if (color.value & pinColor.value) else 0
