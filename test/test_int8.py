import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Int8(unittest.TestCase):
    def test_create_single(self):
        _type = htatype.Int8()
        self.assertIsInstance(_type, (htatype.Int8, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Int8(1)
        self.assertIsInstance(_type, (htatype.Int8, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Int8(8)
        self.assertIsInstance(_type, (htatype.Int8, htatype.Base, ))
        self.assertEqual(_type.count, 8)

    def test_create_incorrect(self):
        with self.assertRaises(AssertionError):
            htatype.Int8('test')
            htatype.Int8([])
            htatype.Int8(None)

    def test_load_single_correct(self):
        _tst_value = pack('<b', 16)
        _type = htatype.Int8()
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, int)
        self.assertEqual(_res_value, 16)
        self.assertEqual(_res_size, 2)

    def test_load_single_smaller(self):
        _tst_value = b''
        _type = htatype.Int8()

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_load_single_bigger(self):
        _tst_value = pack('<bb', 255, -255)
        _type = htatype.Int8()

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_load_array_correct(self):
        _tst_value = pack('<bb', 32, 64)
        _type = htatype.Int8(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, list)
        self.assertListEqual(_res_value, [32, 64])
        self.assertEqual(_res_size, 2)

    def test_load_array_bigger(self):
        _tst_value = pack('<bbb', 32, 64, 92)
        _type = htatype.Int8(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, list)
        self.assertListEqual(_res_value, [32, 64])
        self.assertEqual(_res_size, 2)

    def test_load_array_smaller(self):
        _tst_value = pack('<b', 32)
        _type = htatype.Int8(2)

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_dump_single_correct(self):
        _tst_value = pack('<b', 16)
        _type = htatype.Int8()
        _res_value = _type.dump(16)

        self.assertEqual(_res_value, _tst_value)

        _tst_value = pack('<b', -16)
        _type = htatype.Int8()
        _res_value = _type.dump(-16)

        self.assertEqual(_res_value, _tst_value)

    def test_dump_single_bigger(self):
        _type = htatype.Int8()
        
        with self.assertRaises(ValueError):
            _res_value = _type.dump(512)

    def test_dump_single_smaller(self):
        _type = htatype.Int8()

        with self.assertRaises(ValueError):
            _res_value = _type.dump(-256)

    def test_dump_array_correct(self):
        _tst_value = pack('<bb', 16, 32)

        _type = htatype.Int8(2)
        _res_value = _type.dump([16, 32])

        self.assertEqual(_res_value, _tst_value)

    def test_dump_array_bigger(self):
        _tst_value = pack('<bb', 16, 32)

        _type = htatype.Int8(2)
        _res_value = _type.dump([16, 32, 56])

        self.assertEqual(_res_value, _tst_value)

    def test_dump_array_smaller(self):
        _type = htatype.Int8(2)

        with self.assertRaises(ValueError):
            _res_value = _type.dump([16,])

    def test_dump_array_incorrect(self):
        _type = htatype.Int8(2)

        with self.assertRaises(ValueError):
            _type.dump([256, -256])
