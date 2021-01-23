import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Array(unittest.TestCase):
    def test_create(self):
        _type = htatype.Array(htatype.Base)
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertEqual(_type.structure, htatype.Base)

        _type = htatype.Array(htatype.Base, 1)
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertEqual(_type.structure, htatype.Base)
        self.assertEqual(_type.count, 1)

        _type = htatype.Array(htatype.Base, count_ptr='test')
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertEqual(_type.structure, htatype.Base)
        self.assertEqual(_type.count_ptr, 'test')
