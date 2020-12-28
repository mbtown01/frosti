from os import path
import yaml
import argparse

from frosti.logging import log, setupLogging, handleException
from frosti.core import EventBus, ServiceProvider
from frosti.services import ApiDataBrokerService, \
    GoGriddyPriceCheckService, OrmManagementService, ThermostatService, \
    OrmStateCaptureService, UserInterfaceService, EnvironmentSamplingService, \
    RelayManagementService
from frosti.core.events import SettingsChangedEvent


class RootDriver(ServiceProvider):

    def __init__(self):
        super().__init__()

        parser = argparse.ArgumentParser(
            description='FROSTI main process')
        parser.add_argument(
            '--hardware', choices=['v5', 'auto'], default='auto',
            help='Pick the underlying hardware supporting operations')
        parser.add_argument(
            '--diagnostics', default=False, action='store_true',
            help='Run hardware diagnostics and exit')
        self.__args = parser.parse_args()

    def __detectHardware(self):
        from board import SDA, SCL
        from busio import I2C
        i2c = I2C(SCL, SDA)
        results = i2c.scan()

        # Hardware v5 the two 5024 chips at 0x28 and 0x29
        if 0x28 in results and 0x29 in results:
            return "v5"

        raise RuntimeError("We just don't support hardware older than v5")

    def __getYamlConfigData(self):
        localPath = path.realpath(__file__)

        searchOrder = (
            path.expanduser('~/.frosti.yaml'),
            '/etc/frosti.yaml',
            path.abspath(
                path.dirname(localPath) + '/../etc/frosti.yaml')
        )

        for fileName in searchOrder:
            if path.exists(fileName):
                log.info(f"Configuration coming from {fileName}")
                with open(fileName) as configFile:
                    return yaml.load(configFile, Loader=yaml.FullLoader)

        raise RuntimeError("Couldn't not find a frosti.yaml config file")

    def start(self):
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)
        setupLogging()

        self.__eventBus = EventBus()
        self.installService(EventBus, self.__eventBus)

        ormManagementService = OrmManagementService()
        ormManagementService.setServiceProvider(self)
        self.installService(
            OrmManagementService, ormManagementService)

        ormStateCaptureService = OrmStateCaptureService()
        ormStateCaptureService.setServiceProvider(self)
        self.installService(
            OrmStateCaptureService, ormStateCaptureService)

        # Put all the event handlers together
        configData = self.__getYamlConfigData()
        apiDataBrokerService = ApiDataBrokerService()
        apiDataBrokerService.setServiceProvider(self)
        apiDataBrokerService.setConfig(configData['config'])
        apiDataBrokerService.setPrograms(configData['programs'])
        apiDataBrokerService.setSchedules(configData['schedules'])

        thermostatService = ThermostatService()
        thermostatService.setServiceProvider(self)
        self.installService(ThermostatService, thermostatService)

        if self.__args.hardware == 'auto':
            self.__args.hardware = self.__detectHardware()
            log.info(f"Starting FROSTI on hardware {self.__args.hardware}")

        if self.__args.hardware == 'v5':
            from frosti.hardware.v5.UserInterfaceService \
                import UserInterfaceService as HardwareUserInterfaceService
            from frosti.hardware.v5.RelayManagementService \
                import RelayManagementService as HardwareRelayManagementService
            from frosti.hardware.v5.EnvironmentSamplingService \
                import EnvironmentSamplingService as \
                HardwareEnvironmentSamplingService

            service = HardwareRelayManagementService()
            service.setServiceProvider(self)
            self.installService(RelayManagementService, service)

            service = HardwareEnvironmentSamplingService()
            service.setServiceProvider(self)
            self.installService(EnvironmentSamplingService, service)

            service = HardwareUserInterfaceService()
            service.setServiceProvider(self)
            self.installService(UserInterfaceService, service)

        else:
            raise RuntimeError(
                f'Hardware option {self.__args.hardware} not supported')

        # Setup the power price handler after the other services have
        # been created so they get the first power events
        try:
            priceChecker = GoGriddyPriceCheckService()
            priceChecker.setServiceProvider(self)
        except ConnectionError:
            log.warning("Unable to reach GoGriddy")

        try:
            log.info('Entering into standard operation')
            self.__eventBus.fireEvent(SettingsChangedEvent())
            self.__eventBus.exec()
        finally:
            GPIO.cleanup()


if __name__ == '__main__':
    log.info('Starting thermostat main thread')

    try:
        rootDriver = RootDriver()
        rootDriver.start()
    except:
        handleException("Main entry point")
