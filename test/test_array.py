import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Array(unittest.TestCase):
    def test_create(self):
        _type = htatype.Array(htatype.Base())
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertIsInstance(_type.structure, htatype.Base)

        _type = htatype.Array(htatype.Base(), 1)
        self.assertIsInstance(_type, (htatype.Array, htatype.Base, ))
        self.assertIsInstance(_type.structure, htatype.Base)
        self.assertEqual(_type.count, 1)

        _type = htatype.Array(htatype.Base(), count_ptr='test')
        self.assertIsInstance(_type.structure, htatype.Base)
        self.assertEqual(_type.count_ptr, 'test')

    def test_load(self):
        _tst_value = b'\x00\x00\x00\x00'

        _type = htatype.Array(htatype.UInt8(), 4)
        _res_value, _res_size = _type.load(_tst_value)
        self.assertIsInstance(_res_value, list)
        self.assertEqual(len(_res_value), 4)
        self.assertListEqual(_res_value, [0, 0, 0, 0])

    def test_load_struct_array(self):
        class Define(htatype.Structure):
            attr1: htatype.UInt8()
            attr2: htatype.Int8()

        _tst_value = b'\x00\x00\x00\x00'

        _type = htatype.Array(Define(), 2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertEqual(_res_size, len(_tst_value))
        self.assertEqual(len(_res_value), 2)
        self.assertIsInstance(_res_value[0], Define)

    def test_dump_correct(self):
        _tst_value = b'\x00\x00\x00\x00'

        _type = htatype.Array(htatype.UInt8(), 4)
        self.assertEqual(_type.size, 4)

        _res_value = _type.dump([0, 0, 0, 0])

        self.assertEqual(_res_value, _tst_value)

        _res_value = _type.dump([0, 0])
        self.assertEqual(_res_value, _tst_value)

    def test_pointer_incorrect(self):
        _tst_value = b'\x00\x00\x00\x00'
        _type = htatype.Array(htatype.UInt8(), count_ptr='count')

        with self.assertRaises(AttributeError):
            _type.load(_tst_value)
