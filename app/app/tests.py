from django.test import TestCase

from app.calc import add, subtract


class CalcTests(TestCase):
    # test functions MUST ALWAYS BEGIN WITH the wortd 'test'
    def test_add_numbers(self):
        """Test that two numbers are added together"""
        self.assertEqual(add(3, 8), 11)

    def test_subtract_numbers(self):
        """Test that values are subtracted and returned"""
        self.assertEqual(subtract(5, 11), 6)
