from src.core import ServiceConsumer, ServiceProvider, EventBus
from src.core.generics import GenericEnvironmentSensor
from src.core.events import SensorDataChangedEvent


class EnvironmentSamplingService(ServiceConsumer):
    """ Holds a GenericEnvironmentSensor and at a specified frequency
    takes a sampling and fires a SensorDataChangedEvent """

    def __init__(self, sensor: GenericEnvironmentSensor):
        self.__sensor = sensor

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)
        self.__sampleSensorsInvoker = eventBus.installTimer(
            frequency=5.0, handler=self.__sampleSensors)
        self.__sampleSensors()

    def __sampleSensors(self):
        eventBus = self._getService(EventBus)
        eventBus.fireEvent(SensorDataChangedEvent(
            temperature=self.__sensor.temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))
