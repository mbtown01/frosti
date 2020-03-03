from src.core import ThermostatState


class GenericRelay:

    def __init__(self, function: ThermostatState):
        self.__function = function
        self.__isOpen = None
        self.__callbackList = []

    @property
    def isOpen(self):
        """  True if open, False if closed, None if indeterminite """
        return self.__isOpen

    @property
    def function(self):
        """ Gets the ThermostatState function this relay handles """
        return self.__function

    def addCallback(self, callback):
        """ Provide a callback in the form of callback(relay: GenericRelay) to
        notify when the relay is opening or closing """
        self.__callbackList.append(callback)

    def openRelay(self):
        """ Open the relay, break circuit, disabling the function """
        for callback in self.__callbackList:
            callback(self)
        self._openRelay()
        self.__isOpen = True

    def closeRelay(self):
        """ Close the relay, connect circuit, enabling the function """
        for callback in self.__callbackList:
            callback(self)
        self._closeRelay()
        self.__isOpen = False

    def _openRelay(self):
        pass

    def _closeRelay(self):
        pass
