class ServiceProvider:

    def __init__(self):
        self.__services = {}

    def installService(self, service: type, instance):
        """ Adds a service to this provider """
        if not isinstance(instance, service):
            raise RuntimeError("Service mismatch")
        self.__services[service] = instance

    def getService(self, service: type):
        """ Gets a previously installed service from this provider """
        return self.__services[service]


class ServiceConsumer:

    def __init__(self):
        self.__serviceProvider = None

    def setServiceProvider(self, provider: ServiceProvider):
        self.__serviceProvider = provider

    def _getService(self, service: type):
        if self.__serviceProvider is None:
            raise RuntimeError(
                "getService() called but no service provider set")

        return self.__serviceProvider.getService(service)
