
class Interface:
    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name


class Display(Interface):
    def __init__(self, name):
        super().__init__(name)


class Hardware(Interface):
    def __init__(self, name):
        super().__init__(name)

    # Returns temperature in degF
    def getTemperature(self):
        raise NotImplementedError()

    # Returns pressure in hPa
    def getPressure(self):
        raise NotImplementedError()

    # Returns humidity in relative %
    def getHumidity(self):
        raise NotImplementedError()

    # Set the underlying hardware heating mode
    def setModeHeat(self):
        raise NotImplementedError()

    # Set the underlying hardware to cooling
    def setModeCool(self):
        raise NotImplementedError()

    # Set the underlying hardware to fan only operation
    def setModeFan(self):
        raise NotImplementedError()