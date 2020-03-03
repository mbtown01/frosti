

class GenericEnvironmentSensor:

    def __init__(self):
        self.__temperature = 72.0
        self.__pressure = 1015.0
        self.__humidity = 40.0

    @property
    def temperature(self):
        return self.__temperature

    @temperature.setter
    def temperature(self, value):
        self.__temperature = value

    @property
    def pressure(self):
        return 1015.0

    @pressure.setter
    def pressure(self, value):
        self.__pressure = value

    @property
    def humidity(self):
        return 40.0

    @humidity.setter
    def humidity(self, value):
        self.__humidity = value
