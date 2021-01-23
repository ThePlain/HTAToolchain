import unittest
from struct import pack, unpack

# pylint: disable=import-error
import htatype


class Test_Int32(unittest.TestCase):
    border = 2**32
    htatype = htatype.Int32
    strtype = 'i'

    def test_create_correct(self):
        _type = self.htatype()
        self.assertIsInstance(_type, (self.htatype, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = self.htatype(1)
        self.assertIsInstance(_type, (self.htatype, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = self.htatype(8)
        self.assertIsInstance(_type, (self.htatype, htatype.Base, ))
        self.assertEqual(_type.count, 8)

    def test_create_incorrect(self):
        with self.assertRaises(AssertionError):
            self.htatype('test')
            self.htatype([])
            self.htatype(None)

    def test_load_single_correct(self):
        _tst_value = pack(f'<{self.strtype}', 16)
        _type = self.htatype()
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, int)
        self.assertEqual(_res_value, 16)
        self.assertEqual(_res_size, _type.size)

    def test_load_single_smaller(self):
        _tst_value = b''
        _type = self.htatype(1, False)

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_load_array_correct(self):
        _tst_value = pack(f'<2{self.strtype}', 32, 64)
        _type = self.htatype(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, list)
        self.assertListEqual(_res_value, [32, 64])
        self.assertEqual(_res_size, _type.size)

    def test_load_array_bigger(self):
        _tst_value = pack(f'<3{self.strtype}', 32, 64, 92)
        _type = self.htatype(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertIsInstance(_res_value, list)
        self.assertListEqual(_res_value, [32, 64])
        self.assertEqual(_res_size, _type.size)

    def test_load_array_smaller(self):
        _tst_value = pack(f'<{self.strtype}', 32)
        _type = self.htatype(2)

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_dump_single_correct(self):
        _tst_value = pack(f'<{self.strtype}', 16)
        _type = self.htatype()
        _res_value = _type.dump(16)

        self.assertEqual(_res_value, _tst_value)

    def test_dump_single_bigger(self):
        _type = self.htatype()

        with self.assertRaises(ValueError):
            _res_value = _type.dump(self.border + 1)

    def test_dump_single_smaller(self):
        _type = self.htatype()

        with self.assertRaises(ValueError):
            _res_value = _type.dump(-self.border - 1)

    def test_dump_array_correct(self):
        _tst_value = pack(f'<2{self.strtype}', 16, 32)

        _type = self.htatype(2)
        _res_value = _type.dump([16, 32])

        self.assertEqual(_res_value, _tst_value)

    def test_dump_array_bigger(self):
        _tst_value = pack(f'<2{self.strtype}', 16, 32)

        _type = self.htatype(2)
        _res_value = _type.dump([16, 32, 56])

        self.assertEqual(_res_value, _tst_value)

    def test_dump_array_smaller(self):
        _type = self.htatype(2, False)
        with self.assertRaises(ValueError):
            _res_value = _type.dump([16,])

        _tst_value = pack(f'<2{self.strtype}', 16, 0)
        _type = self.htatype(2, True)
        _res_value = _type.dump([16,])
        self.assertEqual(_res_value, _tst_value)

    def test_dump_array_incorrect(self):
        _type = self.htatype(2)

        with self.assertRaises(ValueError):
            _type.dump([-self.border - 1, self.border + 1])
