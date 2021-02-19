import unittest

# pylint: disable=import-error
import htatype


class Test_Byte(unittest.TestCase):
    def test_create_correct(self):
        _type = htatype.Byte()
        self.assertIsInstance(_type, (htatype.Byte, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Byte(1)
        self.assertIsInstance(_type, (htatype.Byte, htatype.Base, ))
        self.assertEqual(_type.count, 1)

        _type = htatype.Byte(8)
        self.assertIsInstance(_type, (htatype.Byte, htatype.Base, ))
        self.assertEqual(_type.count, 8)

    def test_create_incorrect(self):
        with self.assertRaises(AssertionError):
            htatype.Byte('test')
            htatype.Byte([])
            htatype.Byte(None)

    def test_load_correct(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'

        _type = htatype.Byte(4)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertEqual(_res_value, _tst_value)
        self.assertEqual(_res_size, 4)

    def test_load_smaller(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'

        _type = htatype.Byte(8)

        with self.assertRaises(ValueError):
            _type.load(_tst_value)

    def test_load_bigger(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'

        _type = htatype.Byte(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertEqual(_res_value, b'\xDE\xAD')
        self.assertEqual(_res_size, 2)

    def test_dump_correct(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'

        _type = htatype.Byte(4)
        _res_value = _type.dump(_tst_value)

        self.assertEqual(_res_value, _tst_value)
        self.assertEqual(len(_res_value), _type.count)

    def test_dump_smaller(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'
        _type = htatype.Byte(8)
        _res_value = _type.dump(_tst_value)
        self.assertEqual(_res_value, b'\xDE\xAD\xBE\xEF\x00\x00\x00\x00')
        self.assertEqual(len(_res_value), 8)

        _tst_value = None
        _type = htatype.Byte(4)
        _res_value = _type.dump(_tst_value)
        self.assertEqual(_res_value, b'\x00\x00\x00\x00')

    def test_dump_bigger(self):
        _tst_value = b'\xDE\xAD\xBE\xEF'

        _type = htatype.Byte(2)
        _res_value, _res_size = _type.load(_tst_value)

        self.assertEqual(_res_value, b'\xDE\xAD')
        self.assertEqual(len(_res_value), _type.count)
