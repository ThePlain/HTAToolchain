import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Vector(unittest.TestCase):
    def test_create(self):
        _type = htatype.Vector(htatype.Base())
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertIsInstance(_type.structure, htatype.Base)

    def test_load(self):
        _tst_value = b'\x04\x00\x00\x00\x00\x00\x00\x00'

        _type = htatype.Vector(htatype.UInt8())
        _res_value, _res_size = _type.load(_tst_value)
        self.assertIsInstance(_res_value, list)
        self.assertEqual(len(_res_value), 4)
        self.assertListEqual(_res_value, [0, 0, 0, 0])

    def test_load_struct_vector(self):
        class Define(htatype.Structure):
            attr1: htatype.UInt8()
            attr2: htatype.Int8()

        _tst_value = b'\x02\x00\x00\x00\x00\x00\x00\x00'

        _type = htatype.Vector(Define())
        _res_value, _res_size = _type.load(_tst_value)

        self.assertEqual(_res_size, len(_tst_value))
        self.assertIsInstance(_res_value, list)
        self.assertEqual(len(_res_value), 2)
        self.assertIsInstance(_res_value[0], Define)

    def test_dump_correct(self):
        _type = htatype.Vector(htatype.UInt8())

        _tst_value = b'\x04\x00\x00\x00\x00\x00\x00\x00'
        _res_value = _type.dump([0, 0, 0, 0])
        self.assertEqual(_res_value, _tst_value)

        _tst_value = b'\x02\x00\x00\x00\x00\x00'
        _res_value = _type.dump([0, 0])
        self.assertEqual(_res_value, _tst_value)

    def test_dump_bad_value(self):
        _type = htatype.Vector(htatype.UInt8())

        with self.assertRaises(ValueError):
            _type.dump([-1, 256])

    def test_load_bigger_buffer(self):
        _tst_value = b'\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        _type = htatype.Vector(htatype.UInt8())
        _res_value, _res_size = _type.load(_tst_value)
        self.assertIsInstance(_res_value, list)
        self.assertEqual(len(_res_value), 4)
        self.assertListEqual(_res_value, [0, 0, 0, 0])

    def test_load_smaller_buffer(self):
        _tst_value = b'\x04\x00\x00\x00\x00\x00'

        _type = htatype.Vector(htatype.UInt8())
        with self.assertRaises(ValueError):
            _type.load(_tst_value)
