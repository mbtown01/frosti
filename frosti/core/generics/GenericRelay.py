from abc import ABC, abstractmethod

from frosti.core import ThermostatState


class GenericRelay(ABC):

    def __init__(self, function: ThermostatState):
        self.__function = function
        self.__isOpen = None

    @property
    def isOpen(self):
        """  True if open, False if closed, None if indeterminite """
        return self.__isOpen

    @property
    def function(self):
        """ Gets the ThermostatState function this relay handles """
        return self.__function

    @abstractmethod
    def openRelay(self):
        """ Open the relay, break circuit, disabling the function """
        self.__isOpen = True

    @abstractmethod
    def closeRelay(self):
        """ Close the relay, connect circuit, enabling the function """
        self.__isOpen = False
