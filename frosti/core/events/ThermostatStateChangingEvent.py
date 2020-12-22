from .. import ThermostatState, Event


class ThermostatStateChangingEvent(Event):
    def __init__(self, value: ThermostatState):
        super().__init__('ThermostatStateChangingEvent', {'state': value})

    @property
    def state(self):
        """ Returns the new state of the thermostat """
        return self._data['state']
