import unittest
import sys
from time import sleep

from src.power import GoGriddyPowerInterface


class Test_GoGriddyInterface(unittest.TestCase):

    def setup_method(self, method):
        pass

    def test_data(self):
        griddy = GoGriddyPowerInterface()
        data = griddy.getRawData()
        self.assertGreaterEqual(len(data.keys()), 0)

    def test_forecast(self):
        griddy = GoGriddyPowerInterface()
        griddy.getForecast()
