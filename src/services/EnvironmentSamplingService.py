from src.core import ServiceConsumer, ServiceProvider, EventBus
from src.core.generics import GenericEnvironmentSensor
from src.core.events import SensorDataChangedEvent
from src.services import ConfigService, SettingsChangedEvent


class EnvironmentSamplingService(ServiceConsumer):
    """ Holds a GenericEnvironmentSensor and at a specified frequency
    takes a sampling and fires a SensorDataChangedEvent """

    def __init__(self, sensor: GenericEnvironmentSensor):
        self.__sensor = sensor

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__delta = \
            config.value('thermostat').value('sampling_freq', 5.0)

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            SettingsChangedEvent, self.__settingsChanged)
        self.__sampleSensorsInvoker = eventBus.installTimer(
            frequency=5.0, handler=self.__sampleSensors)
        self.__sampleSensors()

    def __settingsChanged(self, event: SettingsChangedEvent):
        """ If any settings have changed, wait the full time before getting
        another reading from the sensors.  This prevents a user quickly
        changing settings from causing the thermostat to change states """
        self.__sampleSensorsInvoker.reset()

    def __sampleSensors(self):
        eventBus = self._getService(EventBus)
        eventBus.fireEvent(SensorDataChangedEvent(
            temperature=self.__sensor.temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))
