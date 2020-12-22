from .ServiceProvider import ServiceProvider


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
