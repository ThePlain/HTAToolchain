import struct
import warnings
import functools
from typing import Any, List, Union, Sequence


def deprecated(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)
    return new_func


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
    class Base:
        @deprecated
        def __call__(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Any, int]:
            return self.load(buffer, structure=structure, *args, **kwargs)

        @deprecated
        def unpack(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Any, int]:
            return self.load(buffer, structure=structure, *args, **kwargs)

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Any, int]:
            raise NotImplementedError

    class Structure(Base):
        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Any, int]:
            padding = 0
            results = self.__class__()
            for key, type in self.__annotations__.items():
                value, size = type.load(buffer[padding:], *args, structure=self, **kwargs)
                setattr(results, key, value)
                padding += size
            return results, padding


        def dump(self, *args, value=None, **kwarg) -> bytes:
            if not value:
                value = self

            results = b''
            for key, type in self.__annotations__.items():
                value = getattr(value, key)
                results += type.dump(value)
            return results

    class Union(Base):
        def __init__(self, **types):
            self.__types = types

        def load(self, buffer: bytes, *args, structure=None, type=None, **kwargs) -> Sequence[Any, int]:
            provider = self.__types[type]
            results = self.__class__()
            for key, type in provider.__annotations__.items():
                value, size = type.load(buffer[padding:], *args, structure=self, **kwargs)
                setattr(results, key, value)
                padding += size
            return results, padding

        def dump(self, *args, value=None, type=None, **kwargs) -> bytes:
            if not value:
                value = self

            provider = self.__types[type]
            results = provider.dump(value)

            return results

        @deprecated
        def apply(self, structure):
            for key, type in structure.__annotations__.items():
                if isinstance(type, Type.Base):
                    value = getattr(structure, key)
                    setattr(self, key, value)

    class Byte(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[bytes, int]:
            return buffer[:self.count], self.count

        def dump(self, value, *args, **kwarg) -> bytes:
            return value[:self.count]

    class UInt8(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}B', buffer[:self.count * 1])

            if value == 1:
                return value[0], 1

            else:
                return value, self.count

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<B', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}B', *value)

            raise ValueError('passed unsupported value.')

    class Int8(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}b', buffer[:self.count * 1])

            if value == 1:
                return value[0], 1

            else:
                return value, self.count

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<b', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}b', *value)

            raise ValueError('passed unsupported value.')

    class UInt16(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}H', buffer[:self.count * 2])

            if value == 1:
                return value[0], 2

            else:
                return value, self.count * 2

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<H', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}H', *value)

            raise ValueError('passed unsupported value.')

    class Int16(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}h', buffer[:self.count * 2])

            if value == 1:
                return value[0], 2

            else:
                return value, self.count * 2

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<h', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}h', *value)

            raise ValueError('passed unsupported value.')

    class UInt32(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}I', buffer[:self.count * 4])

            if value == 1:
                return value[0], 4

            else:
                return value, self.count * 4

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<I', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}I', *value)

            raise ValueError('passed unsupported value.')

    class Int32(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}i', buffer[:self.count * 4])

            if value == 1:
                return value[0], 4

            else:
                return value, self.count * 4

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<i', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}i', *value)

            raise ValueError('passed unsupported value.')

    class UInt64(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}Q', buffer[:self.count * 8])

            if value == 1:
                return value[0], 8

            else:
                return value, self.count * 8

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<Q', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}Q', *value)

            raise ValueError('passed unsupported value.')

    class Int64(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[int, List[int]], int]:
            value = struct.unpack(f'<{self.count}q', buffer[:self.count * 8])

            if value == 1:
                return value[0], 8

            else:
                return value, self.count * 8

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, int):
                return struct.pack('<q', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}q', *value)

            raise ValueError('passed unsupported value.')

    class Float(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[Union[float, List[float]], int]:
            value = struct.unpack(f'<{self.count}f', buffer[:self.count * 4])

            if value == 1:
                return value[0], 4

            else:
                return value, self.count * 4

        def dump(self, value, *args, **kwarg) -> bytes:
            if isinstance(value, float):
                return struct.pack('<f', value)

            if isinstance(value, (list, tuple)) and len(value) == self.count:
                return struct.pack(f'<{self.count}f', *value)

            raise ValueError('passed unsupported value.')

    class CharArray(Base):
        __slots__ = ['count']

        def __init__(self, count=1):
            self.count = count

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[str, int]:
            results, = struct.unpack(f'<{self.count}s', buffer[:self.count])

            if b'\x00' in results:
                results = results[:results.index(b'\x00')]

            results = results.decode('cp1251')
            return results, self.count

        def dump(self, values: str) -> bytes:
            values = values.encode('cp1251')
            size = len(values)
            return struct.pack(f'<I{size}B', size, *values)

    class CharVector(Base):
        __slots__ = []

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[str, int]:
            count, = struct.unpack('<I', buffer[:4])
            results, = struct.unpack(f'<{count}s', buffer[4:count + 4])
            results = results.decode('cp1251')
            return results, count + 4

        def dump(self, values: str) -> bytes:
            values = values.encode('cp1251')
            size = len(values)
            return struct.pack(f'<I{size}B', size, *values)

    class Vector(Base):
        __slots__ = ['structure']

        def __init__(self, structure):
            self.structure = structure

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[List[Any], int]:
            results = list()
            padding = 4
            count, = struct.unpack('<I', buffer[:4])

            for _ in range(count):
                value, size = self.structure.load(buffer[padding:], *args, **kwargs)
                results.append(value)
                padding += size

            return results

        def dump(self, values: list) -> bytes:
            results = struct.pack('<I', len(values))

            for item in values:
                results += values.dump()

            return results

    class Array(Base):
        __slots__ = ['count', 'structure', 'count_ptr']

        def __init__(self, type, count: int = 1, count_ptr=None):
            self.count = count
            self.structure = type
            self.count_ptr = count_ptr

        def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Sequence[List[Any], int]:
            results = list()
            padding = 0

            count = self.count
            if self.count_ptr:
                if not structure:
                    raise ValueError('can\'t use dynamic attribute because structure not passed.')

                if not hasattr(structure, self.count_ptr):
                    raise AttributeError(f'unable to get "{self.count_ptr}" attribute from struct.')

                count = getattr(structure, self.count_ptr)

            for _ in range(count):
                value, size = self.structure.load(buffer[padding:], structure=structure, *args, **kwargs)
                results.append(value)
                padding += size

            return results, padding

        def dump(self, values: list) -> bytes:
            results = b''

            for item in values[:self.count]:
                results += item.dump()

            return results

    @deprecated
    class Struct(Structure): pass

    @deprecated
    class StructArray(Array): pass
    @deprecated
    class TypeArray(Array): pass

    @deprecated
    class StructVector(Vector): pass
    @deprecated
    class TypeVector(Vector): pass
