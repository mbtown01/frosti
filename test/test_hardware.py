import unittest

from src.hardware import HardwareDriver


class Test_Hardware(unittest.TestCase):

    def setup_method(self, method):
        pass

    def test_row(self):
        row = HardwareDriver.Screen.Row(20)
        row.update(5, 'test')
        updates = row.finalizeUpdates()

        self.assertEqual(1, len(updates))
