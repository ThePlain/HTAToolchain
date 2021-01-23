import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Float(unittest.TestCase):
    def test_create(self):
        _type = htatype.Float()
        self.assertIsInstance(_type, (htatype.Float, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Float(1)
        self.assertIsInstance(_type, (htatype.Float, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Float(8)
        self.assertIsInstance(_type, (htatype.Float, htatype.Base, ))
        self.assertEqual(_type.count, 8)
