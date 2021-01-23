import struct
from typing import Any, List, Union, Tuple


class KeyManager:
    __slots__ = ['dict', 'provider', 'name_ptr']

    def __init__(self, provider, name_ptr=None):
        self.dict = dict()
        self.name_ptr = name_ptr
        self.provider = provider

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.dict[key]
        if isinstance(key, int):
            key = list(self.dict)[key]
            return self.dict[key]
        raise TypeError('unsupported key type.')

    def __setitem__(self, key, item):
        self.dict[key] = item

    def __delitem__(self, key):
        del self.dict[key]

    def new(self, name):
        assert self.provider
        self.dict[name] = self.provider()

    def load(self, buffer: bytes, *args, **kwargs):
        raise NotImplementedError

    def dump(self) -> Tuple[bytes, int]:
        raise NotImplementedError


class Base:
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Any, int]:
        raise NotImplementedError


class Structure(Base):
    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Any, int]:
        padding = 0
        results = self.__class__()
        # pylint: disable=no-member
        for key, type in self.__annotations__.items():
            value, size = type.load(buffer[padding:], *args, structure=self, **kwargs)
            setattr(results, key, value)
            padding += size
        return results, padding

    # pylint: disable=unused-argument
    def dump(self, *args, value=None, **kwarg) -> bytes:
        if not value:
            value = self

        results = b''
        # pylint: disable=no-member
        for key, type in self.__annotations__.items():
            value = getattr(value, key)
            results += type.dump(value)
        return results


class Dynamic(Base):
    def __init__(self, **types):
        self.__types = types

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, type=None, **kwargs) -> Tuple[Any, int]:
        provider = self.__types[type]
        results = self.__class__()
        for key, type in provider.__annotations__.items():
            value, size = type.load(buffer[padding:], *args, structure=self, **kwargs)
            setattr(results, key, value)
            padding += size
        return results, padding

    # pylint: disable=unused-argument
    def dump(self, *args, value=None, type=None, **kwargs) -> bytes:
        if not value:
            value = self

        provider = self.__types[type]
        results = provider.dump(value)

        return results


class Byte(Base):
    __slots__ = ['count', 'aligment']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[bytes, int]:
        if len(buffer) < self.count:
            raise ValueError('presented data smaller that required.')

        return buffer[:self.count], self.count

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            return b'\x00' * self.count

        if len(value) > self.count:
            return value[:self.count]

        if self.aligment and len(value) < self.count:
            value += b'\x00' * (self.count - len(value))

        return value


class UInt8(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.count:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}B', buffer[:self.count])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}B', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class Int8(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}b', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}b', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class UInt16(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 2

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}H', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}H', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class Int16(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 2

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}h', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}h', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class UInt32(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 4

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}I', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}I', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class Int32(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 4

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}i', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}i', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class UInt64(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 8

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}Q', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}Q', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class Int64(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 8

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}q', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}q', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class Float(Base):
    __slots__ = ['count', 'aligment', 'size']

    def __init__(self, count=1, aligment=True):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)

        self.count = count
        self.aligment = aligment
        self.size = count * 4

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Union[int, List[int]], int]:
        if len(buffer) < self.size:
            raise ValueError('presented data smaller that required.')

        value = struct.unpack(f'<{self.count}f', buffer[:self.size])

        if self.count == 1:
            return value[0], self.size

        else:
            return list(value), self.size

    # pylint: disable=unused-argument
    def dump(self, value, *args, **kwarg) -> bytes:
        if value is None:
            value = []

        if not isinstance(value, list):
            value = [value, ]

        if len(value) < self.count:
            if self.aligment:
                value += [0, ] * (self.count - len(value))

            else:
                raise ValueError('presented data smaller that required')

        if len(value) > self.count:
            value = value[:self.count]

        try:
            return struct.pack(f'<{self.count}f', *value)

        except struct.error as error:
            raise ValueError(error)

        raise ValueError('passed unsupported value.')


class CharArray(Base):
    __slots__ = ['count']

    def __init__(self, count=1):
        self.count = count

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[str, int]:
        results, = struct.unpack(f'<{self.count}s', buffer[:self.count])

        if b'\x00' in results:
            results = results[:results.index(b'\x00')]

        results = results.decode('cp1251')
        return results, self.count

    # pylint: disable=unused-argument
    def dump(self, values: str) -> bytes:
        values = values.encode('cp1251')
        size = len(values)
        return struct.pack(f'<I{size}B', size, *values)


class CharVector(Base):
    __slots__ = []

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[str, int]:
        count, = struct.unpack('<I', buffer[:4])
        results, = struct.unpack(f'<{count}s', buffer[4:count + 4])
        results = results.decode('cp1251')
        return results, count + 4

    # pylint: disable=unused-argument
    def dump(self, values: str) -> bytes:
        values = values.encode('cp1251')
        size = len(values)
        return struct.pack(f'<I{size}B', size, *values)


class Vector(Base):
    __slots__ = ['structure']

    def __init__(self, structure):
        self.structure = structure

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[List[Any], int]:
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
            results += self.structure.dump(item)

        return results


class Array(Base):
    __slots__ = ['count', 'structure', 'count_ptr']

    def __init__(self, structure, count: int = 1, count_ptr=None):
        self.count = count
        self.structure = structure
        self.count_ptr = count_ptr

    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[List[Any], int]:
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
            results += self.structure.dump(item)

        return results
