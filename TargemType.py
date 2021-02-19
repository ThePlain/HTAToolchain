import struct


class KeyManager:
    def __init__(self):
        self.dict_str = dict()
        self.dict_int = dict()

    def __iter__(self):
        return iter(self.dict_int.values())

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.dict_str.get(key, None)
        if isinstance(key, int):
            return self.dict_int.get(key, None)
        return None


class Type:
    class Struct:
        @classmethod
        def unpack(cls, buffer, *args, **kwargs):
            pad = 0
            item = cls()
            # pylint: disable=no-member
            for key, var_type in cls.__annotations__.items():
                value, size = var_type(buffer[pad:], *args, **kwargs)
                setattr(item, key, value)
                pad += size
            return item, pad

        @classmethod
        def type(cls, key):
            return cls.__annotations__.get(key, None)

    class Union:
        def apply(self, structure):
            for key in structure.__annotations__:
                value = getattr(structure, key)
                setattr(self, key, value)

    @staticmethod
    def Byte(size=1):
        def Byte(buffer, *args, **kwargs):
            if size == 1:
                return buffer[0], 1
            else:
                return buffer[0:size], size
        return Byte

    @staticmethod
    def UInt8(size=1):
        def UInt8(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<B', buffer[:1])[0], 1
            else:
                return struct.unpack(f'<{size}b', buffer[:size]), size
        return UInt8

    @staticmethod
    def Int8(size=1):
        def Int8(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<b', buffer[:1])[0], 1
            else:
                return struct.unpack(f'<{size}b', buffer[:size]), size
        return Int8

    @staticmethod
    def UInt16(size=1):
        def UInt16(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<H', buffer[:2])[0], 2
            else:
                _size = size * 2
                return struct.unpack(f'<{size}H', buffer[:_size]), _size
        return UInt16

    @staticmethod
    def Int16(size=1):
        def Int16(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<h', buffer[:2])[0], 2
            else:
                _size = size * 2
                return struct.unpack(f'<{size}h', buffer[:_size]), _size
        return Int16

    @staticmethod
    def UInt32(size=1):
        def UInt32(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<I', buffer[:4])[0], 4
            else:
                _size = size * 4
                return struct.unpack(f'<{size}I', buffer[:_size]), _size
        return UInt32

    @staticmethod
    def Int32(size=1):
        def Int32(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<i', buffer[:4])[0], 4
            else:
                _size = size * 4
                return struct.unpack(f'<{size}i', buffer[:_size]), _size
        return Int32

    @staticmethod
    def UInt64(size=1):
        def UInt64(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<Q', buffer[:8])[0], 8
            else:
                _size = size * 8
                return struct.unpack(f'<{size}Q', buffer[:_size]), _size
        return UInt64

    @staticmethod
    def Int64(size=1):
        def Int64(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<q', buffer[:8])[0], 8
            else:
                _size = size * 8
                return struct.unpack(f'<{size}q', buffer[:_size]), _size
        return Int64

    @staticmethod
    def Float(size=1):
        def Float(buffer, *args, **kwargs):
            if size == 1:
                return struct.unpack('<f', buffer[:4])[0], 4
            else:
                _size = size * 4
                return struct.unpack(f'<{size}f', buffer[:_size]), _size
        return Float

    @staticmethod
    def String(size=1):
        def String(buffer, *args, **kwargs):
            return struct.unpack(f'<{size}s', buffer[:size])[0], size
        return String

    @staticmethod
    def CString(size=1):
        def CString(buffer, *args, **kwargs):
            value = struct.unpack(f'<{size}s', buffer[:size])[0]
            if b'\x00' in value:
                value = value[:value.index(b'\x00')]
            return value.decode('cp1251'), size
        return CString

    @staticmethod
    def PString():
        def PString(buffer, *args, **kwargs):
            count = struct.unpack('<I', buffer[:4])[0]
            value = struct.unpack(f'<{count}s', buffer[4:4+count])[0]
            return value.decode('cp1251'), 4 + count
        return PString

    @staticmethod
    def Vector(fmt, size):
        def Vector(buffer, *args, **kwargs):
            count = struct.unpack('<I', buffer[:4])[0]
            _size = size * count
            return struct.unpack(f'<{count}{fmt}', buffer[4:4 + _size]), 4 + _size
        return Vector

    @staticmethod
    def TypeVector(var_type):
        def TypeVector(buffer, *args, **kwargs):
            count = struct.unpack('<I', buffer[:4])[0]
            result = []
            pad = 4
            for _ in range(count):
                value, size = var_type(buffer[pad:], *args, **kwargs)
                result.append(value)
                pad += size
            return result, pad
        return TypeVector

    @staticmethod
    def FixedTypeVector(count, var_type):
        def FixedTypeVector(buffer, *args, **kwargs):
            result = []
            pad = 0
            for _ in range(count):
                value, size = var_type(buffer[pad:], *args, **kwargs)
                result.append(value)
                pad += size
            return result, pad
        return FixedTypeVector

    @staticmethod
    def StructVector(structure):
        def StructVector(buffer, *args, **kwargs):
            count = struct.unpack('<I', buffer[:4])[0]
            result = []
            pad = 4
            for _ in range(count):
                value, size = structure.unpack(buffer[pad:], *args, **kwargs)
                result.append(value)
                pad += size
            return result, pad
        return StructVector

    @staticmethod
    def FixedStructVector(count, structure):
        def FixedStructVector(buffer, *args, **kwargs):
            result = []
            pad = 0
            for _ in range(count):
                value, size = structure.unpack(buffer[pad:], *args, **kwargs)
                result.append(value)
                pad += size
            return result, pad
        return FixedStructVector
