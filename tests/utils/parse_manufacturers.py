import json
import os
import unittest

from netengine.utils import parse_manufacturers

__all__ = ['TestParseManufacturers']


class TestParseManufacturers(unittest.TestCase):
    def test_parse_manufacturers(self):
        parse_manufacturers()
        open("manufacturers.py")
        os.remove("manufacturers.py")
