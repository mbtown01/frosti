"""
These classes implement a bone-head simple IOC container pattern, where
there is a set of components that need services (ServiceConsumers) and
somewhere there is a component that provides them (ServiceProvider).
"""


class ServiceProvider:
    """ Provies services to ServiceConsumer instances """

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
    """ Consumes services provided by a ServiceProvider """

    def __init__(self):
        self.__serviceProvider = None

    def setServiceProvider(self, provider: ServiceProvider):
        """ Associates this instance with a service provider.  Only after
        this method is called can this instance successfully obtain
        service instances by calling _getService() """
        self.__serviceProvider = provider

    def _getService(self, service: type):
        """ Get a service provided by this consumers ServiceProvider
        instance.  Cannot be called before setServiceProvider() establishes
        the provider instance """
        if self.__serviceProvider is None:
            raise RuntimeError(
                "getService() called but no service provider set")

        return self.__serviceProvider.getService(service)
