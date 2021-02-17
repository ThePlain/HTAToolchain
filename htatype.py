import struct
from typing import Any, List, Union, Tuple


class Base:
    size = 0

    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Any, int]:
        raise NotImplementedError


class Runtime(Base):
    def __init__(self, callback):
        self.callback = callback

    def load(self, buffer: bytes, *args, structure=None, **kwargs):
        return self.callback(buffer, *args, structure=structure, **kwargs), 0


class Structure(Base):
    def pre_load(self, buffer: bytes, *args, structure=None, **kwargs):
        pass

    def post_load(self, buffer: bytes, *args, structure=None, **kwargs):
        pass

    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Any, int]:
        instance = self.__class__()
        instance.pre_load(buffer, *args, structure=instance, **kwargs)
        padding = 0
        for key, type in self.__annotations__.items():
            if not isinstance(type, Base):
                continue

            value, size = instance.load_filter(key, type, buffer[padding:], *args, structure=instance, **kwargs)
            setattr(instance, key, value)
            padding += size
        instance.post_load(buffer, *args, structure=instance, **kwargs)
        return instance, padding

    def load_filter(self, name, type, buffer: bytes, *args, structure=None, **kwargs):
        return type.load(buffer, *args, structure=structure, **kwargs)


class KeyManager:
    _container_ = (None, None)
    _container_ptr_ = None

    def __getitem__(self, key):
        if self._container_[1] is not None:
            return self._container_ptr_.get(key)
        return self._container_ptr_[key] or None

    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[Any, int]:
        value, padding = super().load(buffer, *args, structure=structure, **kwargs)

        container, key = self._container_
        if container:
            instance = value
            items = getattr(value, container)

        else:
            instance = self.__class__()
            items = value

        if key:
            instance._container_ptr_ = dict()
            for item in items:
                instance._container_ptr_[getattr(item, key)] = item

        else:
            instance._container_ptr_ = items

        return instance, padding

class Dynamic(Base):
    _modes_ = dict()

    def pre_load(self, buffer: bytes, *args, structure=None, **kwargs):
        pass

    def post_load(self, buffer: bytes, *args, structure=None, **kwargs):
        pass

    def __init__(self, **types):
        self._modes_.update(types)

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, mode=None, **kwargs) -> Tuple[Any, int]:
        provider = self._modes_[mode]
        results = self.__class__()

        results.pre_load(buffer, *args, structure=structure, mode=mode, **kwargs)

        value, padding = provider.load(buffer, *args, structure=structure, mode=mode, **kwargs)
        for key in provider.__annotations__:
            setattr(results, key, getattr(value, key, getattr(results, key, None)))

        results.post_load(buffer, *args, structure=structure, mode=mode, **kwargs)

        return results, padding

    # pylint: disable=unused-argument
    def dump(self, *args, value=None, mode=None, **kwargs) -> bytes:
        if not value:
            value = self

        provider = self._modes_[mode]
        results = provider.dump(value)

        return results


class Byte(Base):
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
    def __init__(self, structure):
        self.structure = structure

    # pylint: disable=unused-argument
    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[List[Any], int]:
        results = list()
        padding = 4
        count, = struct.unpack('<I', buffer[:4])

        for num in range(count):
            kwargs['num'] = num

            value, size = self.structure.load(buffer[padding:], *args, structure=structure, **kwargs)
            results.append(value)
            padding += size

        return results, padding

    def dump(self, values: list) -> bytes:
        results = struct.pack('<I', len(values))

        for item in values:
            results += self.structure.dump(item)

        return results


class Array(Base):
    def __init__(self, structure, count: int = 0, aligment=True, count_ptr=None):
        assert isinstance(count, int)
        assert isinstance(aligment, bool)
        assert not count_ptr or isinstance(count_ptr, str)

        self.count = count
        self.structure = structure
        self.count_ptr = count_ptr
        self.aligment = aligment
        self.size = self.count * self.structure.size

    def load(self, buffer: bytes, *args, structure=None, **kwargs) -> Tuple[List[Any], int]:
        results = list()
        padding = 0

        count = self.count or kwargs.get('count', 0) or kwargs.get(self.count_ptr, 0)
        if self.count_ptr:
            if not structure:
                raise AttributeError(f'structure not present.')

            if not hasattr(structure, self.count_ptr):
                raise AttributeError(f'unable to get "{self.count_ptr}" attribute from struct.')

            count = getattr(structure, self.count_ptr)

        for num in range(count):
            kwargs['num'] = num

            value, size = self.structure.load(buffer[padding:], *args, structure=structure, **kwargs)
            results.append(value)
            padding += size

        return results, padding

    def dump(self, values: list) -> bytes:
        results = b''

        for item in values[:self.count]:
            results += self.structure.dump(item)

        if self.aligment:
            results = results.rjust(self.size, b'\x00')

        return results

__all__ = [
    'Runtime',
    'KeyManager',
    'Structure',
    'Dynamic',
    'Byte',
    'UInt8',
    'Int8',
    'UInt16',
    'Int16',
    'UInt32',
    'Int32',
    'UInt64',
    'Int64',
    'Float',
    'CharArray',
    'CharVector',
    'Vector',
    'Array',
]
