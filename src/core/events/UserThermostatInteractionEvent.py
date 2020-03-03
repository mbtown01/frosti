from enum import Enum

from src.core import Event

class UserThermostatInteractionEvent(Event):
    MODE_NEXT = 1
    COMFORT_RAISE = 2
    COMFORT_LOWER = 3

    def __init__(self, interaction: int):
        super().__init__(
            name='UserThermostatInteractionEvent',
            data={'interaction': interaction})

    @property
    def interaction(self):
        return super().data['interaction']
