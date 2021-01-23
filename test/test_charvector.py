import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_CharVector(unittest.TestCase):
    def test_create(self):
        _type = htatype.CharVector()
        self.assertIsInstance(_type, (htatype.CharVector, htatype.Base, ))
