from src.core import Event


class SensorDataChangedEvent(Event):
    def __init__(self, temperature: float, pressure: float, humidity: float):
        super().__init__(data={
            'temperature': temperature,
            'pressure': pressure,
            'humidity': humidity
        })

    @property
    def temperature(self):
        return float(self._data['temperature'])

    @property
    def pressure(self):
        return float(self._data['pressure'])

    @property
    def humidity(self):
        return float(self._data['humidity'])
