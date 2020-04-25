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
