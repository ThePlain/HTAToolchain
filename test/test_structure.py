import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Structure(unittest.TestCase):
    def test_create(self):
        class BadDefine(htatype.Structure):
            pass

        with self.assertRaises(TypeError):
            _type = BadDefine()

        class Define(htatype.Structure):
            attr0: htatype.UInt8()

        _type = Define()
        self.assertIsInstance(_type, htatype.Structure)
        self.assertEqual(_type.size, 1)

        _type = Define(4)
        self.assertIsInstance(_type, htatype.Structure)
        self.assertEqual(_type.size, 4)

    def test_dynamic_point_array(self):
        class Define(htatype.Structure):
            count: htatype.UInt8()
            values: htatype.Array(htatype.UInt8(), count_ptr='count')

        _tst_value = b'\x04\x00\x00\x00\x00'
        _type = Define()
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, Define)
        self.assertEqual(_res_value.count, 4)
        self.assertListEqual(_res_value.values, [0, 0, 0, 0])
        self.assertEqual(_res_size, len(_tst_value))

        _tst_value = b'\x04\x00\x00\x00\x00\x04\x00\x00\x00\x00'
        _type = Define(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, list)
        self.assertIsInstance(_res_value[0], Define)
        self.assertEqual(_res_value[0].count, 4)
        self.assertListEqual(_res_value[0].values, [0, 0, 0, 0])
        self.assertEqual(_res_size, len(_tst_value))

    def test_nested_simple(self):
        class Nested(htatype.Structure):
            attr0: htatype.UInt8()

        class Parent(htatype.Structure):
            attr0: htatype.UInt8()
            nested: Nested()

        _tst_value = b'\x00\x01'
        _type = Parent()

        _res_value, _res_size = _type.load(_tst_value)
        self.assertIsInstance(_res_value, Parent)
        self.assertIsInstance(_res_value.nested, Nested)
        self.assertEqual(_res_value.attr0, 0)
        self.assertEqual(_res_value.nested.attr0, 1)
        self.assertEqual(_res_size, len(_tst_value))

    def test_nested_pointed_arrays(self):
        class Nested(htatype.Structure):
            count: htatype.UInt8()
            attr0: htatype.Array(htatype.UInt8(), count_ptr='count')

        class Parent(htatype.Structure):
            count: htatype.UInt8()
            attr0: htatype.Array(htatype.UInt8(), count_ptr='count')
            nested: Nested()

        _tst_value = b'\x02\x01\x02\x03\x03\x04\x05'
        _type = Parent()
        self.assertEqual(_type.size, 2)

        _res_value, _res_size = _type.load(_tst_value)
        self.assertIsInstance(_res_value, Parent)
        self.assertIsInstance(_res_value.nested, Nested)
        self.assertListEqual(_res_value.attr0, [1, 2])
        self.assertListEqual(_res_value.nested.attr0, [3, 4, 5])
        self.assertEqual(_res_size, len(_tst_value))
