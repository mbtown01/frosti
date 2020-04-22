from src.core import EventBusMember, ServiceProvider
from src.core.generics import GenericEnvironmentSensor
from src.core.events import SensorDataChangedEvent


class EnvironmentSamplingService(EventBusMember):
    """ Holds a GenericEnvironmentSensor and at a specified frequency
    takes a sampling and fires a SensorDataChangedEvent """

    def __init__(self, sensor: GenericEnvironmentSensor):
        self.__sensor = sensor

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self.__sampleSensorsInvoker = self._installTimerHandler(
            frequency=5.0, handlers=self.__sampleSensors)

    def __sampleSensors(self):
        super()._fireEvent(SensorDataChangedEvent(
            temperature=self.__sensor.temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))
