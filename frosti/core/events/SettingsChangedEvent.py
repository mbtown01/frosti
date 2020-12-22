from frosti.core import Event


class SettingsChangedEvent(Event):
    """ Fired when any property of ThermostatSerivce changes """

    def __init__(self):
        super().__init__('SettingsChangedEvent')
