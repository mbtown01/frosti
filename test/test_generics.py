import unittest

from src.generics import GenericButton, GenericScreen


class Test_Generics(unittest.TestCase):

    def setup_method(self, method):
        pass

    def test_row_update_middle(self):
        row = GenericScreen.Row(20)
        row.update(5, 'test')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(5, updates[0][0])
        self.assertEqual('test', updates[0][1])

    def test_row_update_leading(self):
        row = GenericScreen.Row(20)
        row.update(0, 'easy_update')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('easy_update', updates[0][1])

    def test_row_update_too_long(self):
        row = GenericScreen.Row(20)
        row.update(0, '0123456789012345678901234567890123456789')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('01234567890123456789', updates[0][1])

    def test_row_update_neg_offset(self):
        row = GenericScreen.Row(20)
        row.update(-5, '0123456789')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('56789', updates[0][1])

    def test_row_update_two_updates(self):
        row = GenericScreen.Row(20)
        row.update(0, '01234567890123456789')
        updates = row.commit()
        row.update(0, '01234012340123401234')
        updates = row.commit()

        self.assertEqual(2, len(updates))
        self.assertEqual(5, updates[0][0])
        self.assertEqual('01234', updates[0][1])
        self.assertEqual(15, updates[1][0])
        self.assertEqual('01234', updates[1][1])

    def test_row_update_two_updates_no_finalize(self):
        row = GenericScreen.Row(20)
        row.update(0, '01234567890123456789')
        row.update(0, '01234012340123401234')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('01234012340123401234', updates[0][1])

    def test_screen_simple(self):
        screen = GenericScreen(20, 2)
        screen.update(0, 0, "01234567890123456789")
        screen.update(1, 0, "01234567890123456789")
        screen.commit()

        self.assertEqual(
            "01234567890123456789\n01234567890123456789", screen.text)

    def test_screen_too_many_rows(self):
        screen = GenericScreen(20, 2)
        with self.assertRaises(RuntimeError):
            screen.update(2, 4, 'this should throw')
