import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_CharArray(unittest.TestCase):
    def test_create(self):
        _type = htatype.CharArray()
        self.assertIsInstance(_type, (htatype.CharArray, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.CharArray(1)
        self.assertIsInstance(_type, (htatype.CharArray, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.CharArray(8)
        self.assertIsInstance(_type, (htatype.CharArray, htatype.Base, ))
        self.assertEqual(_type.count, 8)
