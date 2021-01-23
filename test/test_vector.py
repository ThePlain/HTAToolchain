import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Vector(unittest.TestCase):
    def test_create(self):
        _type = htatype.Vector(htatype.Base)
        self.assertIsInstance(_type, (htatype.Vector, htatype.Base, ))
        self.assertEqual(_type.structure, htatype.Base)
