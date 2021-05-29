from __future__ import annotations
import io
import struct


__version__ = '2.3.1'


class IOWrapper:
    def __init__(self, stream: io.FileIO) -> None:
        self.stream = stream
        self._offset = 0

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value: int):
        self._offset = value
        self.stream.seek(self._offset)

    def read(self, count: int = 0):
        result = self.stream.read(count)
        self.offset += count
        return result

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)

        buffer = self.stream.read(size)
        result = struct.unpack(fmt, buffer)

        self.offset += size

        if len(result) == 1:
            return result[0]

        else:
            return list(result)

    def iter_unpack(self, fmt: str, count: int):
        for _ in range(count):
            yield self.unpack(fmt)

    def pack(self, fmt: str, *args):
        self.stream.write(struct.pack(fmt, *args))

    def write(self, data: bytes):
        self.stream.write(data)


TAG_MAP = {
    'INFO':         (0x0001, 0x0006),
    'NODES':        (0x0002, 0x0003),
    'MESHES':       (0x0004, 0x0001),
    'ANIMATIONS':   (0x0008, 0x0004),
    'MATERIALS':    (0x000F, 0x0008),
    'CONVEX':       (0x0010, 0x0005),
    'COLLISIONS':   (0x0020, 0x0007),
    'HIER_GEOM':    (0x0040, 0x000A),
    'BOUNDS':       (0x0080, 0x000B),
    'GROUPS':       (0x00F0, 0x0009),
    'TAG':          (0xF001, 0xF001),
    'VERSION':      (0xF002, 0xF002),
    'PARSER':       (0xF003, 0xF003),
    'SIGN':         (0xF004, 0xF004),
}


class Header():
    tag: int = 0
    size: int = 0
    offset: int = 0

class Headers:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.bom: bytes = b'\x65\x63\x62\x6E\x74\x2C\x74\x00'
        self.items: dict = dict()

    def load(self, stream: IOWrapper):
        stream.offset = 0
        self.bom = stream.read(8)

        count = stream.unpack('<I')
        for tag, size, offset in stream.iter_unpack('<IIQ', count):
            self.items[tag] = Header()
            self.items[tag].tag = tag
            self.items[tag].size = size
            self.items[tag].offset = offset

    def dump(self, stream: IOWrapper):
        stream.offset = 0
        stream.write(self.bom)
        stream.pack('<I', len(self.items))
        for item in self.items.values():
            stream.pack('<IIQ', item.tag, item.size, item.offset)

    def get_tag(self, name: str) -> int:
        gam, sam = TAG_MAP.get(name)

        if self.parser.file == 'GAM':
            return gam

        if self.parser.file == 'SAM':
            return sam

    def set_tag(self, name: str, stream: IOWrapper) -> bool:
        tag = self.get_tag(name)
        header = self.items.get(tag, None)

        if not header:
            return False

        stream.offset = header.offset

        return True

    def has(self, name: str) -> bool:
        tag = self.get_tag(name)
        return tag in self.items

    def gen(self, tag, size):
        self.items[tag] = Header()
        self.items[tag].tag = tag
        self.items[tag].size = size

    def recalculate(self):
        self.items = dict()

        tag = self.get_tag('INFO')
        self.gen(tag, self.parser.info.size)

        tag = self.get_tag('NODES')
        self.gen(tag, self.parser.nodes.size)

        tag = self.get_tag('MESHES')
        self.gen(tag, self.parser.meshes.size)

        if self.parser.animations.used or self.parser.file == 'GAM':
            tag = self.get_tag('ANIMATIONS')
            self.gen(tag, self.parser.animations.size)

        tag = self.get_tag('MATERIALS')
        self.gen(tag, self.parser.skins.size)

        if self.parser.convex.used:
            tag = self.get_tag('CONVEX')
            self.gen(tag, self.parser.convex.size)

        if self.parser.collisions.used:
            tag = self.get_tag('COLLISIONS')
            self.gen(tag, self.parser.collisions.size)

        if self.parser.hier_geoms.used:
            tag = self.get_tag('HIER_GEOM')
            self.gen(tag, self.parser.hier_geoms.size)

        if self.parser.bounds.used:
            tag = self.get_tag('BOUNDS')
            self.gen(tag, self.parser.bounds.size)

        tag = self.get_tag('GROUPS')
        self.gen(tag, self.parser.groups.size)

        tag = self.get_tag('TAG')
        self.gen(tag, 30)

        tag = self.get_tag('VERSION')
        self.gen(tag, 4)

        tag = self.get_tag('PARSER')
        self.gen(tag, 64)

        tag = self.get_tag('SIGN')
        self.gen(tag, 64)

        offset = 12 + len(self.items) * 16

        for header in self.items.values():
            header.offset = offset
            offset += header.size


class Info:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.triangle: int = 0
        self.skinned: int = 0
        self.static: int = 0
        self.animations: int = 0
        self.materials: int = 0
        self.nodes: int = 0
        self.config: int = 0

    @property
    def meshes(self):
        return self.triangle + self.skinned + self.static

    @property
    def size(self):
        return 16

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('INFO', stream):
            print('Cant find: "Info" - skipped!')
            return

        if self.parser.file == 'GAM':
            self.triangle = stream.unpack('<h')
            self.skinned = stream.unpack('<h')
            self.static = stream.unpack('<h')
            self.animations = stream.unpack('<h')
            self.materials = stream.unpack('<h')
            self.nodes = stream.unpack('<h')
            self.config = stream.unpack('<i')

        if self.parser.file == 'SAM':
            self.triangle = stream.unpack('<I')
            self.materials = stream.unpack('<I')
            self.nodes = stream.unpack('<I')
            self.config = stream.unpack('<I')

    def dump(self, stream: IOWrapper):
        if self.parser.file == 'GAM':
            stream.pack('<h', self.triangle)
            stream.pack('<h', self.skinned)
            stream.pack('<h', self.static)
            stream.pack('<h', self.animations)
            stream.pack('<h', self.materials)
            stream.pack('<h', self.nodes)
            stream.pack('<i', self.config)

        if self.parser.file == 'SAM':
            stream.pack('<I', self.meshes)
            stream.pack('<I', self.materials)
            stream.pack('<I', self.nodes)
            stream.pack('<I', self.config)


class Node:
    name: str = ''
    parent: int = -1
    location: list = [0, 0, 0]
    rotation: list = [1, 0, 0, 0]
    scale: list = [1, 1, 1]
    matrix: list = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


class Nodes:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: dict = dict()

    def __getitem__(self, key: str):
        return self.items.get(key, None)

    def __setitem__(self, key: str, value: Group):
        self.items[key] = value

    def __iter__(self):
        return iter(self.items.values())

    def index(self, key: str):
        if key not in self.items:
            return -1

        return list(self.items.keys()).index(key)

    def by_index(self, key: int):
        if len(self.items) <= key < 0:
            return None

        return list(self.items.values())[key]

    def recalculate(self):
        self.parser.info.nodes = len(self.items)

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('NODES', stream):
            print('Cant find: "Nodes" - skipped!')
            return

        for num in range(self.parser.info.nodes):
            node = Node()
            node.name = stream.unpack('<40s')

            if b'\x00' in node.name:
                node.name = node.name[:node.name.index(b'\x00')]

            node.name = node.name.decode('cp1251')

            if not node.name:
                node.name = f'Node.{num:0>3}'

            if self.parser.file == 'GAM':
                node.parent = stream.unpack('<i')

            if self.parser.file == 'SAM':
                node.parent = stream.unpack('<h')

            node.location = stream.unpack('<3f')
            node.rotation = stream.unpack('<4f')

            if self.parser.file == 'GAM':
                node.matrix = stream.unpack('<16f')

            if self.parser.file == 'SAM':
                node.scale = stream.unpack('<3f')

            self.items[node.name] = node

    def dump(self, stream: IOWrapper):
        for node in self.items.values():
            stream.pack('<40s', node.name.encode('cp1251'))

            if self.parser.file == 'GAM':
                stream.pack('<i', node.parent)

            if self.parser.file == 'SAM':
                stream.pack('<h', node.parent)

            stream.pack('<3f', *node.location)
            stream.pack('<4f', *node.rotation)

            if self.parser.file == 'GAM':
                stream.pack('<16f', *node.matrix)

            if self.parser.file == 'SAM':
                stream.pack('<3f', *node.scale)

    @property
    def size(self):
        if self.parser.file == 'GAM':
            return 136 * len(self.items)

        if self.parser.file == 'SAM':
            return 82 * len(self.items)

class Vertex:
    location: list = None
    normal: list = None
    color: list = None
    uv0: list = None
    uv1: list = None
    uv2: list = None
    tangent: list = None
    binormal: list = None

    @staticmethod
    def toXYZ(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])

    @staticmethod
    def toXYZT1(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.uv = list(data[3:5])

    @staticmethod
    def toXYZC(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.color = list(data[3:7])

    @staticmethod
    def toXYZWC(vertex: Vertex, data: list):
        vertex.location = list(data[0:4])
        vertex.color = list(data[4:8])

    @staticmethod
    def toXYZWCT1(vertex: Vertex, data: list):
        vertex.location = list(data[0:4])
        vertex.color = list(data[4:8])
        vertex.uv0 = list(data[8:10])

    @staticmethod
    def toXYZNC(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.color = list(data[6:10])

    @staticmethod
    def toXYZCT1(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.color = list(data[3:7])
        vertex.uv0 = list(data[7:9])

    @staticmethod
    def toXYZNT1(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.uv0 = list(data[6:8])

    @staticmethod
    def toXYZNCT1(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.color = list(data[6:10])
        vertex.uv0 = list(data[10:12])

    @staticmethod
    def toXYZNCT2(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.color = list(data[6:10])
        vertex.uv0 = list(data[10:12])
        vertex.uv1 = list(data[12:14])

    @staticmethod
    def toXYZNT2(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.uv0 = list(data[6:8])
        vertex.uv1 = list(data[8:10])

    @staticmethod
    def toXYZNT3(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.uv0 = list(data[6:8])
        vertex.uv1 = list(data[8:10])
        vertex.uv2 = list(data[10:12])

    @staticmethod
    def toXYZCT1_UVW(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.color = list(data[3:7])
        vertex.uv0 = list(data[7:10])

    @staticmethod
    def toXYZCT2_UVW(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.color = list(data[3:7])
        vertex.uv0 = list(data[7:10])
        vertex.uv1 = list(data[10:12])

    @staticmethod
    def toXYZCT2(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.color = list(data[3:7])
        vertex.uv0 = list(data[7:9])
        vertex.uv1 = list(data[9:11])

    @staticmethod
    def toXYZNT1T(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.uv0 = list(data[6:8])
        vertex.tangent = list(data[8:12])

    @staticmethod
    def toXYZNCT1T(vertex: Vertex, data: list):
        vertex.location = list(data[0:3])
        vertex.normal = list(data[3:6])
        vertex.color = list(data[6:10])
        vertex.uv0 = list(data[10:12])
        vertex.tangent = list(data[12:16])

    @staticmethod
    def fromXYZ(vertex: Vertex):
        return [*vertex.location]

    @staticmethod
    def fromXYZT1(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.uv,
        ]

    @staticmethod
    def fromXYZC(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
        ]

    @staticmethod
    def fromXYZWC(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
        ]

    @staticmethod
    def fromXYZWCT1(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
            *vertex.uv0,
        ]

    @staticmethod
    def fromXYZNC(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.color,
        ]

    @staticmethod
    def fromXYZCT1(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
            *vertex.uv0,
        ]

    @staticmethod
    def fromXYZNT1(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.uv0,
        ]

    @staticmethod
    def fromXYZNCT1(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.color,
            *vertex.uv0,
        ]

    @staticmethod
    def fromXYZNCT2(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.color,
            *vertex.uv0,
            *vertex.uv1,
        ]

    @staticmethod
    def fromXYZNT2(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.uv0,
            *vertex.uv1,
        ]

    @staticmethod
    def fromXYZNT3(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.uv0,
            *vertex.uv1,
            *vertex.uv2,
        ]

    @staticmethod
    def fromXYZCT1_UVW(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
            *vertex.uv0,
        ]

    @staticmethod
    def fromXYZCT2_UVW(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
            *vertex.uv0,
            *vertex.uv1,
        ]

    @staticmethod
    def fromXYZCT2(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.color,
            *vertex.uv0,
            *vertex.uv1,
        ]

    @staticmethod
    def fromXYZNT1T(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.uv0,
            *vertex.tangent,
        ]

    @staticmethod
    def fromXYZNCT1T(vertex: Vertex):
        return [
            *vertex.location,
            *vertex.normal,
            *vertex.color,
            *vertex.uv0,
            *vertex.tangent,
        ]


GAM_DATA2VERTEX = {
     0: ('<3f',              Vertex.toXYZ),
     1: ('<3f 2f',           Vertex.toXYZT1),
     2: ('<3f 4B',           Vertex.toXYZC),
     3: ('<4f 4B',           Vertex.toXYZWC),
     4: ('<4f 4B 2f',        Vertex.toXYZWCT1),
     5: ('<3f 3f 4B',        Vertex.toXYZNC),
     6: ('<3f 4B 2f',        Vertex.toXYZCT1),
     7: ('<3f 3f 2f',        Vertex.toXYZNT1),
     8: ('<3f 3f 4B 2f',     Vertex.toXYZNCT1),
     9: ('<3f 3f 4B 2f 2f',  Vertex.toXYZNCT2),
    10: ('<3f 3f 2f 2f',     Vertex.toXYZNT2),
    11: ('<3f 3f 2f 2f 2f',  Vertex.toXYZNT3),
    12: ('<3f 4B 3f',        Vertex.toXYZCT1_UVW),
    13: ('<3f 4B 3f 2f',     Vertex.toXYZCT2_UVW),
    14: ('<3f 4B 2f 2f',     Vertex.toXYZCT2),
    15: ('<3f 3f 2f 4f',     Vertex.toXYZNT1T),
    16: ('<3f 3f 4B 2f 4f',  Vertex.toXYZNCT1T),
}

GAM_VERTEX2DATA = {
     0: ('<3f',              Vertex.fromXYZ),
     1: ('<3f 2f',           Vertex.fromXYZT1),
     2: ('<3f 4B',           Vertex.fromXYZC),
     3: ('<4f 4B',           Vertex.fromXYZWC),
     4: ('<4f 4B 2f',        Vertex.fromXYZWCT1),
     5: ('<3f 3f 4B',        Vertex.fromXYZNC),
     6: ('<3f 4B 2f',        Vertex.fromXYZCT1),
     7: ('<3f 3f 2f',        Vertex.fromXYZNT1),
     8: ('<3f 3f 4B 2f',     Vertex.fromXYZNCT1),
     9: ('<3f 3f 4B 2f 2f',  Vertex.fromXYZNCT2),
    10: ('<3f 3f 2f 2f',     Vertex.fromXYZNT2),
    11: ('<3f 3f 2f 2f 2f',  Vertex.fromXYZNT3),
    12: ('<3f 4B 3f',        Vertex.fromXYZCT1_UVW),
    13: ('<3f 4B 3f 2f',     Vertex.fromXYZCT2_UVW),
    14: ('<3f 4B 2f 2f',     Vertex.fromXYZCT2),
    15: ('<3f 3f 2f 4f',     Vertex.fromXYZNT1T),
    16: ('<3f 3f 4B 2f 4f',  Vertex.fromXYZNCT1T),
}


class Influence:
    node: int = 0
    weight: float = 0
    offset: list = [0, 0, 0]
    normal: list = [0, 0, 0]


class InfluenceGroup:
    count: int = 0
    items: list = []

    def __init__(self) -> None:
        self.items = list()

    def get(self, num):
        if num >= len(self.items):
            return Influence
        return self.items[num]


class Mesh:
    parser: Parser = None
    name: str = None
    type: int = 4
    parent: int = -1
    group: int = 0
    material: int = 0
    vertex_size: int = 0
    vertex_type: int = 0
    vertex_count: int = 0
    indices_count: int = 0
    header_count: int = 0
    headers: dict = dict()
    vertices: list = list()
    doubles: list = list()
    influences: list = list()
    indices: list = list()

    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.headers = dict()
        self.vertices = list()
        self.doubles = list()
        self.influences = list()
        self.indices = list()

    @property
    def size(self):
        if self.parser.file == 'GAM':
            size = 72 + self.vertex_size * self.vertex_count + self.indices_count * 6

            if self.type == 1:
                size += self.vertex_size * self.vertex_count

            if self.type == 2:
                size += 122 * self.vertex_count

            return size

        if self.parser.file == 'SAM':
            size = 20 + self.vertex_size * self.vertex_count + self.indices_count * 6 + len(self.headers) * 8

            if self.type == 2:
                for group in self.influences:
                    size += 2 + len(group.items) * 6

            return size

    def recalculate(self):
        self.vertex_size = 0

        if self.type == 1:
            self.parser.info.triangle += 1

        if self.type == 2:
            self.parser.info.skinned += 1

        if self.type == 4:
            self.parser.info.static += 1

        vert = self.vertices[0]

        if vert.location:
            self.headers[0] = 12
            self.vertex_size += 12

        if vert.normal:
            self.headers[1] = 12
            self.vertex_size += 12

        if vert.color:
            self.headers[2] = 4
            self.vertex_size += 4

        if vert.uv0:
            self.headers[3] = len(vert.uv0) * 4
            self.vertex_size += len(vert.uv0) * 4

        if vert.uv1:
            self.headers[4] = len(vert.uv1) * 4
            self.vertex_size += len(vert.uv1) * 4

        if vert.uv2:
            self.headers[5] = len(vert.uv2) * 4
            self.vertex_size += len(vert.uv2) * 4

        if vert.tangent:
            self.headers[20] = 16
            self.vertex_size += 16

        if vert.binormal:
            self.headers[21] = 12
            self.vertex_size += 12

        if self.influences:
            self.headers[22] = -1
            self.type = 2

        self.header_count = len(self.headers)
        self.vertex_count = len(self.vertices)
        self.indices_count = len(self.indices)
        v, _ = GAM_VERTEX2DATA[self.vertex_type]
        self.vertex_size = struct.calcsize(v)

        for influence in self.influences:
            influence.count = len(influence.items)


class Meshes:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: dict = dict()
        self.bvh_min: list = [0, 0, 0]
        self.bvh_max: list = [0, 0, 0]

    def __getitem__(self, key: str):
        return self.items.get(key, None)

    def __setitem__(self, key: str, value: Group):
        self.items[key] = value

    def __iter__(self):
        return iter(self.items.values())

    def index(self, key: str):
        if key not in self.items:
            return -1

        return list(self.items.keys()).index(key)

    def by_index(self, key: int):
        if len(self.items) <= key < 0:
            return None

        return list(self.items.values())[key]

    def recalculate(self):
        self.parser.info.triangle = 0
        self.parser.info.static = 0
        self.parser.info.skinned = 0

        for mesh in self.items.values():
            mesh.recalculate()

    @property
    def size(self):
        size = 24
        for mesh in self.items.values():
            size += mesh.size
        return size

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('MESHES', stream):
            print('Cant find: "Meshes" - skipped!')
            return

        if self.parser.file == 'GAM':
            for num in range(self.parser.info.meshes):
                mesh = Mesh(self.parser)

                mesh.name = stream.unpack('<40s')

                if b'\x00' in mesh.name:
                    mesh.name = mesh.name[:mesh.name.index(b'\x00')]

                mesh.name = mesh.name.decode('cp1251')

                if not mesh.name:
                    mesh.name = f'Mesh.{num:0>3}'

                mesh.type = stream.unpack('<i')
                mesh.parent = stream.unpack('<i')
                mesh.group = stream.unpack('<i')
                mesh.material = stream.unpack('<i')
                mesh.vertex_size = stream.unpack('<I')
                mesh.vertex_type = stream.unpack('<I')
                mesh.vertex_count = stream.unpack('<I')
                mesh.indices_count = stream.unpack('<I')

                struct, method = GAM_DATA2VERTEX.get(mesh.vertex_type)

                for data in stream.iter_unpack(struct, mesh.vertex_count):
                    vertex = Vertex()
                    method(vertex, data)
                    mesh.vertices.append(vertex)

                if mesh.type == 1:
                    for data in stream.iter_unpack(struct, mesh.vertex_count):
                        vertex = Vertex()
                        method(vertex, data)
                        mesh.doubles.append(vertex)

                if mesh.type == 2:
                    for count in stream.iter_unpack('<H', mesh.vertex_count):
                        group = InfluenceGroup()
                        group.count = count

                        for _ in range(4):
                            influence = Influence()
                            influence.node = stream.unpack('<H')
                            influence.offset = stream.unpack('<3f')
                            influence.normal = stream.unpack('<3f')

                            group.items.append(influence)

                        mesh.influences.append(group)

                for indices in stream.iter_unpack('<3H', mesh.indices_count):
                    mesh.indices.append(indices)

                self.items[mesh.name] = mesh

        if self.parser.file == 'SAM':
            for num in range(self.parser.info.meshes):
                mesh = Mesh(self.parser)

                mesh.name = f'Mesh.{num:0>3}'
                mesh.type = stream.unpack('<I')
                mesh.material = stream.unpack('<h')
                mesh.vertex_count = stream.unpack('<I')
                mesh.indices_count = stream.unpack('<I')
                mesh.parent = stream.unpack('<h')
                mesh.header_count = stream.unpack('<I')

                for key, size in stream.iter_unpack('<2I'):
                    mesh.headers[key] = size

                for _ in range(mesh.vertex_count):
                    self.vertexes.append(Vertex)

                for element_type, element_size in mesh.headers.items():
                    for vertex in mesh.vertices:
                        if element_type == 0:
                            vertex.position = stream.unpack('<3f')

                        if element_type == 1:
                            vertex.normal = stream.unpack('<3f')

                        if element_type == 2:
                            vertex.color = stream.unpack('<4B')

                        if element_type == 3:
                            count = int(element_size / 4)
                            vertex.uv0 = stream.unpack(f'<{count}f')

                        if element_type == 4:
                            count = int(element_size / 4)
                            vertex.uv1 = stream.unpack(f'<{count}f')

                        if element_type == 5:
                            count = int(element_size / 4)
                            vertex.uv2 = stream.unpack(f'<{count}f')

                        if element_type == 20:
                            vertex.tangent = stream.unpack('<4f')

                        if element_type == 21:
                            vertex.binormal = stream.unpack('<3f')

                        if element_type == 22:
                            group = InfluenceGroup()
                            group.count = stream.unpack('<I')
                            for _ in range(group.count):
                                influence = Influence()
                                influence.node = stream.unpack('<h')
                                influence.weight = stream.unpack('<f')

                for indices in stream.iter_unpack('<3h'):
                    mesh.indices.append(indices)

                self.items[mesh.name] = mesh

        self.bvh_min = stream.unpack('<3f')
        self.bvh_max = stream.unpack('<3f')

    def dump(self, stream: IOWrapper):
        for mesh in self.items.values():
            if self.parser.file == 'GAM':
                stream.pack('<40s', mesh.name.encode('cp1251'))
                stream.pack('<i', mesh.type)
                stream.pack('<i', mesh.parent)
                stream.pack('<i', mesh.group)
                stream.pack('<i', mesh.material)
                stream.pack('<I', mesh.vertex_size)
                stream.pack('<I', mesh.vertex_type)
                stream.pack('<I', mesh.vertex_count)
                stream.pack('<I', mesh.indices_count)

                struct, method = GAM_VERTEX2DATA.get(mesh.vertex_type)

                for vertex in mesh.vertices:
                    stream.pack(struct, *method(vertex))

                if mesh.type == 1:
                    for vertex in mesh.vertices:
                        stream.pack(struct, *method(vertex))

                if mesh.type == 2:
                    for group in mesh.influences:
                        stream.pack('<h', group.count)
                        for num in range(4):
                            influence = group.get(num)
                            stream.pack('<h', influence.node)
                            stream.pack('<f', influence.weight)
                            stream.pack('<3f', *influence.offset)
                            stream.pack('<3f', *influence.normal)

                for indices in mesh.indices:
                    stream.pack('<3H', *indices)

            if self.parser.file == 'SAM':
                stream.pack('<I', mesh.type)
                stream.pack('<h', mesh.material)
                stream.pack('<I', mesh.vertex_count)
                stream.pack('<I', mesh.indices_count)
                stream.pack('<h', mesh.parent)
                stream.pack('<I', mesh.header_count)

                for tag, size in mesh.headers.items():
                    stream.pack('<2I', tag, size)

                for element_type, element_size in mesh.headers.items():
                    for vertex in mesh.vertices:
                        if element_type == 0:
                            stream.pack('<3f', *vertex.location)

                        if element_type == 1:
                            stream.pack('<3f', *vertex.normal)

                        if element_type == 2:
                            stream.pack('<4B', *vertex.color)

                        if element_type == 3:
                            count = int(element_size / 4)
                            stream.pack(f'<{count}f', *vertex.uv0)

                        if element_type == 4:
                            count = int(element_size / 4)
                            stream.pack(f'<{count}f', *vertex.uv1)

                        if element_type == 5:
                            count = int(element_size / 4)
                            stream.pack(f'<{count}f', *vertex.uv2)

                        if element_type == 20:
                            stream.pack('<4f', *vertex.tangent)

                        if element_type == 21:
                            stream.pack('<3f', *vertex.binormal)

                        if element_type == 22:
                            for group in mesh.influences:
                                stream.pack('<I', group.count)

                                for influence in group.items:
                                    stream.pack('<h', influence.node)
                                    stream.pack('<f', influence.weight)

                for indices in mesh.indices:
                    stream.pack('<3H', *indices)

        stream.pack('<3f', *self.bvh_min)
        stream.pack('<3f', *self.bvh_max)


class Key:
    node: int = 0
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0]
    scale: list = [1, 1, 1]


class Change:
    type: int = 0
    current: int = 0
    new: int = 0


class Animation:
    parser: Parser = None
    name: str = None
    frame_count: int = 0
    change_count: int = 0
    key_count: int = 0
    fps: int = 0
    next: int = 0
    action: int = 0
    changes: list = list()
    frames: list = list()

    def __init__(self, parser: Parser):
        self.parser = parser
        self.changes = list()
        self.frames = list()

    @property
    def size(self):
        if self.parser.file == 'GAM':
            size = 39 + len(self.changes) * 8
            
            for frame in self.frames:
                size += self.key_count * 30

            return size

        if self.parser.file == 'SAM':
            size = 41 + len(self.changes) * 8
            
            for frame in self.frames:
                size += self.key_count * 40

            return size

class Animations:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: dict = dict()

    def __getitem__(self, key: str):
        return self.items.get(key, None)

    def __setitem__(self, key: str, value: Group):
        self.items[key] = value

    def __contains__(self, key: str):
        return key in self.items

    def __iter__(self):
        return iter(self.items.values())

    def index(self, key: str):
        if key not in self.items:
            return -1

        return list(self.items.keys()).index(key)

    def by_index(self, key: int):
        if len(self.items) <= key < 0:
            return None

        return list(self.items.values())[key]

    def recalculate(self):
        self.parser.info.animations = len(self.items)
        for animation in self.items.values():
            animation.frame_count = len(animation.frames)
            animation.change_count = len(animation.changes)
            animation.key_count = len(animation.frames[0])

    @property
    def used(self):
        return bool(self.items)

    @property
    def size(self):
        size = 0

        for animation in self.items.values():
            size += animation.size

        return size

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('ANIMATIONS', stream):
            print('Cant find: "Animations" - skipped!')
            return

        count = self.parser.info.animations
        for num in range(count):
            if self.parser.file == 'GAM':
                animation: Animation = Animation(self.parser)

                animation.name = stream.unpack('<25s')

                if b'\x00' in animation.name:
                    animation.name = animation.name[:animation.name.index(b'\x00')]

                animation.name = animation.name.decode('cp1251')

                if not animation.name:
                    animation.name = f'Animation.{num:0>3}'

                animation.frame_count = stream.unpack('<H')
                animation.fps = stream.unpack('<H')
                animation.next = stream.unpack('<h')
                animation.change_count = stream.unpack('<H')
                animation.key_count = stream.unpack('<H')
                animation.action = stream.unpack('<i')
                
                for _ in range(animation.change_count):
                    change: Change = Change()
                    change.current = stream.unpack('<h')
                    change.type = stream.unpack('<I')
                    change.new = stream.unpack('<h')

                    animation.changes.append(change)

                for _ in range(animation.frame_count):
                    keys = dict()

                    for _ in range(animation.key_count):
                        key = Key()
                        key.node = stream.unpack('<h')
                        key.location = stream.unpack('<3f')
                        key.rotation = stream.unpack('<4f')

                        keys[key.node] = key

                    animation.frames.append(keys)

                self.items[animation.name] = animation

            if self.parser.file == 'SAM':
                animation: Animation = Animation(self.parser)

                animation.name = stream.unpack('<25s')

                if b'\x00' in animation.name:
                    animation.name = animation.name[:animation.name.index(b'\x00')]

                animation.name = animation.name.decode('cp1251')

                if not animation.name:
                    animation.name = f'Animation.{num:0>3}'

                animation.frame_count = stream.unpack('<I')
                animation.fps = stream.unpack('<I')
                animation.next = stream.unpack('<i')
                animation.change_count = stream.unpack('<I')
                animation.key_count = self.parser.info.nodes

                for _ in range(animation.change_count):
                    change: Change = Change()
                    change.type = stream.unpack('<I')
                    change.current = stream.unpack('<h')
                    change.new = stream.unpack('<h')

                    animation.changes.append(change)

                for _ in range(animation.frame_count):
                    keys = dict()

                    for num in range(animation.key_count):
                        key = Key()
                        key.node = num
                        key.location = stream.unpack('<3f')
                        key.rotation = stream.unpack('<4f')
                        key.scale = stream.unpack('<3f')

                        keys[key.node] = key

                    animation.frames = keys
                self.items[animation.name] = animation

    def dump(self, stream: IOWrapper):
        for animation in self.items.values():
            if self.parser.file == 'GAM':
                stream.pack('<25s', animation.name.encode('cp1251'))
                stream.pack('<H', animation.frame_count)
                stream.pack('<H', animation.fps)
                stream.pack('<h', animation.next)
                stream.pack('<H', animation.change_count)
                stream.pack('<H', animation.key_count)
                stream.pack('<i', animation.action)

                for change in animation.changes:
                    stream.pack('<h', change.current)
                    stream.pack('<I', change.type)
                    stream.pack('<h', change.new)

                for frame in animation.frames:
                    for key in frame:
                        stream.pack('<h', key.node)
                        stream.pack('<3f', *key.location)
                        stream.pack('<4f', *key.rotation)

            if self.parser.file == 'SAM':
                stream.pack('<25s', animation.name.enncode('cp1251'))
                stream.pack('<I', animation.frame_count)
                stream.pack('<I', animation.fps)
                stream.pack('<i', animation.next)
                stream.pack('<I', animation.change_count)

                for change in animation.changes:
                    stream.pack('<I', change.type)
                    stream.pack('<h', change.current)
                    stream.pack('<h', change.new)

                for frame in animation.frames:
                    for num in animation.key_count:
                        key = frame.get(num, Key)
                        stream.pack('<3f', *key.location)
                        stream.pack('<4f', *key.rotation)
                        stream.pack('<3f', *key.scale)

class Texture:
    filename: str = None
    uv: int = 0
    type: int = 0


class Material:
    parser: Parser = None
    name: str = ''
    diffuse: list = [1, 1, 1, 1]
    ambient: list = [1, 1, 1, 1]
    specular: list = [1, 1, 1, 1]
    emmisive: list = [1, 1, 1, 1]
    power: float = 1.0
    texture_count: int = 0
    shader: str = ''
    textures: list = list()

    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.textures = list()

    def recalculate(self):
        self.texture_count = len(self.textures)

    @property
    def size(self):
        if self.parser.file == 'GAM':
            return 172 + len(self.textures) * 48

        if self.parser.file == 'SAM':
            return 77 + len(self.shader) + len(self.textures) * 48


class Skins:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: dict = dict()

    def __getitem__(self, key: str):
        return self.items.get(key, None)

    def __setitem__(self, key: str, value: Group):
        self.items[key] = value

    def __iter__(self):
        return iter(self.items.values())

    def index(self, key: str):
        if key not in self.items:
            return -1

        return list(self.items.keys()).index(key)

    def recalculate(self):
        self.parser.info.materials = len(self.items[0])

        for skin in self.items.values():
            for material in skin.values():
                material.texture_count = len(material.textures)

    @property
    def size(self):
        size = 4

        for skin in self.items.values():
            for material in skin.values():
                size += material.size

        return size

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('MATERIALS', stream):
            print('Cant find: "Skins" - skipped!')
            return

        count = stream.unpack('<I')
        for skin_num in range(count):
            skin = dict()
            for num in range(self.parser.info.materials):
                material: Material = Material(self.parser)
                material.name = f'Material.{skin_num:0>2}.{num:0>2}'

                material.diffuse = stream.unpack('<4f')
                material.ambient = stream.unpack('<4f')
                material.specular = stream.unpack('<4f')
                material.emmisive = stream.unpack('<4f')
                material.power = stream.unpack('<f')
                material.texture_count = stream.unpack('<I')

                if self.parser.file == 'GAM':
                    material.shader = stream.unpack('<100s')

                if self.parser.file == 'SAM':
                    size = stream.unpack('<I')
                    material.shader = stream.unpack(f'<{size}s')

                if b'\x00' in material.shader:
                    material.shader = material.shader[:material.shader.index(b'\x00')]

                material.shader = material.shader.decode('cp1251')

                for _ in range(material.texture_count):
                    texture = Texture()
                    texture.filename = stream.unpack('<40s')

                    if b'\x00' in texture.filename:
                        texture.filename = texture.filename[:texture.filename.index(b'\x00')]

                    texture.filename = texture.filename.decode('cp1251')

                    texture.uv = stream.unpack('<I')
                    texture.type = stream.unpack('<I')

                    material.textures.append(texture)

                skin[material.name] = material

            self.items[skin_num] = skin

    def set_skin(self, num: int, material: Material):
        if num not in self.items:
            self.items[num] = dict()

        if material.name in self.items[num]:
            return

        self.items[num][material.name] = material

    def dump(self, stream: IOWrapper):
        stream.pack('<I', len(self.items))
        for skin in self.items.values():
            for material in skin.values():
                stream.pack('<4f', *material.diffuse)
                stream.pack('<4f', *material.ambient)
                stream.pack('<4f', *material.specular)
                stream.pack('<4f', *material.emmisive)
                stream.pack('<f', material.power)
                stream.pack('<I', material.texture_count)

                if self.parser.file == 'GAM':
                    stream.pack('<100s', material.shader.encode('cp1251'))

                if self.parser.file == 'SAM':
                    size = len(material.shader) + 1
                    stream.pack('<I', size)
                    stream.pack(f'<{size}s', material.shader.encode('cp1251'))

                for texture in material.textures:
                    stream.pack('<40s', texture.filename.encode('cp1251'))
                    stream.pack('<I', texture.uv)
                    stream.pack('<I', texture.type)


class Convex:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.verticles_count: int = 0
        self.indices_count: int = 0
        self.vertices: list = list()
        self.indices: list = list()

    def recalculate(self):
        self.verticles_count = len(self.vertices)
        self.indices_count = len(self.indices)

    @property
    def used(self):
        return self.verticles_count > 0

    @property
    def size(self):
        return 8 + len(self.vertices) * 12 + len(self.indices) * 6

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('CONVEX', stream):
            print('Cant find: "Convex" - skipped!')
            return

        self.verticles_count = stream.unpack('<I')
        self.indices_count = stream.unpack('<I')

        for vert in stream.iter_unpack('<3f', self.verticles_count):
            self.vertices.append(vert)

        for indices in stream.iter_unpack('<3h', self.indices_count):
            self.indices.append(indices)

    def dump(self, stream: IOWrapper):
        if not self.parser.headers.has('CONVEX'):
            return

        stream.pack('<I', self.verticles_count)
        stream.pack('<I', self.indices_count)

        for vert in self.vertices:
            stream.pack('<3f', *vert)

        for indices in self.indices:
            stream.pack('<3H', *indices)


class Collision:
    name: str = None
    type: int = 0
    location: list = [0, 0, 0]
    rotation: list = [1, 0, 0, 0]
    scale: list = [1, 1, 1]
    gametype: int = 0


class Collisions:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: list = list()

    def __iter__(self):
        return iter(self.items)

    def recalculate(self):
        pass

    @property
    def used(self):
        return bool(self.items)

    @property
    def size(self):
        if self.parser.mode == 'HTA':
            return 4 + len(self.items) * 44

        if self.parser.mode == '113':
            return 4 + len(self.items) * 48

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('COLLISIONS', stream):
            print('Cant find: "Collisions" - skipped!')
            return

        count = stream.unpack('<I')
        for num in range(count):
            collision: Collision = Collision()
            collision.name = f'Collider.{num:0>3}'
            collision.type = stream.unpack('<I')
            collision.location = stream.unpack('<3f')
            collision.rotation = stream.unpack('<4f')
            collision.scale = stream.unpack('<3f')

            if self.parser.mode == '113':
                collision.gametype = stream.unpack('<I')

            self.items.append(collision)

    def dump(self, stream: IOWrapper):
        if not self.parser.headers.has('COLLISIONS'):
            return

        stream.pack('<I', len(self.items))
        for collision in self.items:
            stream.pack('<I', collision.type)
            stream.pack('<3f', *collision.location)
            stream.pack('<4f', *collision.rotation)
            stream.pack('<3f', *collision.scale)

            if self.parser.mode == '113':
                stream.pack('<I', collision.gametype)

class HierGeom:
    type: int = 0
    location: list = [0, 0, 0]
    rotation: list = [1, 0, 0, 0]
    scale: list = [1, 1, 1]
    gametype: int = 0
    node: int = 0


class HierGeoms:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: list = list()

    def __iter__(self):
        return iter(self.items)

    def recalculate(self):
        pass

    @property
    def used(self):
        return bool(self.items)

    @property
    def size(self):
        if self.parser.mode == 'HTA':
            return len(self.items) * 48

        if self.parser.mode == '113':
            return len(self.items) * 52

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('HIER_GEOM', stream):
            print('Cant find: "HierGeoms" - skipped!')
            return

        count = stream.unpack('<I')
        for _ in range(count):
            item: HierGeom = HierGeom()
            item.type = stream.unpack('<I')
            item.location = stream.unpack('<3f')
            item.rotation = stream.unpack('<4f')
            item.scale = stream.unpack('<3f')

            if self.parser.mode == '113':
                item.gametype = stream.unpack('<I')

            item.node = stream.unpack('<I')

            self.items.append(item)

    def dump(self, stream: IOWrapper):
        if not self.parser.headers.has('HIER_GEOM'):
            return

        stream.pack('<I', len(self.items))
        for collision in self.items:
            stream.pack('<I', collision.type)
            stream.pack('<3f', *collision.location)
            stream.pack('<4f', *collision.rotation)
            stream.pack('<3f', *collision.scale)

            if self.parser.mode == '113':
                stream.pack('<I', collision.gametype)

            stream.pack('<I', collision.node)


class Bound:
    node: int = 0
    min_rotaiton: list = [0, 0, 0]
    max_rotaiton: list = [0, 0, 0]

class Bounds:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: list = list()

    def __iter__(self):
        return iter(self.items)

    @property
    def used(self):
        return bool(self.items)

    @property
    def size(self):
        return 4 + len(self.items) * 28

    def recalculate(self):
        pass

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('BOUNDS', stream):
            print('Cant find: "Bounds" - skipped!')
            return

        count = stream.unpack('<I')
        for _ in range(count):
            bound: Bound = Bound()
            bound.node = stream.unpack('<I')
            bound.min_rotaiton = stream.unpack('<3f')
            bound.max_rotaiton = stream.unpack('<3f')
            self.items.append(bound)
    
    def dump(self, stream: IOWrapper):
        if not self.parser.headers.has('BOUNDS'):
            return

        stream.pack('<I', len(self.items))
        for bound in self.items:
            stream.pack('<I', bound.node)
            stream.pack('<3f', *bound.min_rotation)
            stream.pack('<3f', *bound.max_rotation)


class Group:
    parser: Parser = None
    name: str = None
    min: int = 1
    max: int = 1
    nodes: list = list()
    variants: dict = dict()

    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.nodes = list()
        self.variants = dict()

    def add_variant(self, variant: int, node: int):
        if variant not in self.variants:
            self.variants[variant] = list()

        self.variants[variant].append(node)

    def get_variant(self, node: int):
        for key, variant in self.variants.items():
            if node in variant:
                return key
        return 0

    @property
    def size(self):
        if self.parser.file == 'GAM':
            size = 36 + len(self.nodes) * 4

            for variant in self.variants.values():
                size += 4 + len(variant) * 4

            return size

        if self.parser.file == 'SAM':
            size = 32

            for variant in self.variants.values():
                size += 4 + len(variant) * 4

            return size

class Groups:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.items: dict = dict()

    def __getitem__(self, key: str):
        return self.items.get(key, None)

    def __setitem__(self, key: str, value: Group):
        self.items[key] = value

    def __iter__(self):
        return iter(self.items.values())

    def index(self, key: str):
        if key not in self.items:
            return -1

        return list(self.items.keys()).index(key)

    def by_index(self, key: int):
        if len(self.items) <= key < 0:
            return None

        return list(self.items.values())[key]

    @property
    def size(self):
        size = 4

        for group in self.items.values():
            size += group.size

        return size

    def recalculate(self):
        self.parser.info.config = len(self.parser.groups.items)
        for group in self.items.values():
            group.max = len(group.variants)

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('GROUPS', stream):
            print('Cant find: "Groups" - skipped!')
            return

        count = stream.unpack('<I')
        for num in range(count):
            group: Group = Group(self.parser)
            group.name = stream.unpack('<20s')

            if b'\x00' in group.name:
                group.name = group.name[:group.name.index(b'\x00')]

            group.name = group.name.decode('cp1251')

            if not group.name:
                group.name = f'Group.{num:0>3}'

            group.min = stream.unpack('<I')
            group.max = stream.unpack('<I')

            if self.parser.file == 'GAM':
                count = stream.unpack('<I')
                group.nodes = stream.unpack(f'<{count}I')

                if not isinstance(group.nodes, list):
                    group.nodes = [group.nodes]

            count = stream.unpack('<I')
            for num in range(count):
                count = stream.unpack('<I')
                variant = stream.unpack(f'<{count}I')

                if not isinstance(variant, list):
                    variant = [variant, ]

                group.variants[num] = variant

            self.items[group.name] = group

    def dump(self, stream: IOWrapper):
        stream.pack('<I', len(self.items))
        for group in self.items.values():
            stream.pack('<20s', group.name.encode('cp1251'))
            stream.pack('<I', group.min)
            stream.pack('<I', group.max)

            if self.parser.file == 'GAM':
                stream.pack(f'<I{len(group.nodes)}I', len(group.nodes), *group.nodes)

            stream.pack('<I', len(group.variants))
            for num in range(len(group.variants)):
                variant = group.variants[num]

                if self.parser.file == 'GAM':
                    variant = list([group.nodes.index(uid) for uid in group.variants[num]])

                stream.pack(f'<I{len(variant)}I', len(variant), *variant)

class Version:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser

    def dump(self, stream: IOWrapper):
        if self.parser.file == 'GAM':
            stream.pack('<30s', b'IVR')
            stream.pack('<I', 1)

        if self.parser.file == 'SAM':
            stream.pack('<30s', b'DFT')
            stream.pack('<I', 2)

class Generator:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.value: str =  f'HTAParser: {__version__}'

    def dump(self, stream: IOWrapper):
        stream.pack('<64s', self.value.encode('cp1251'))


class Sign:
    def __init__(self, parser: Parser) -> None:
        self.parser: Parser = parser
        self.value: str = ''

    def load(self, stream: IOWrapper):
        if not self.parser.headers.set_tag('SIGN', stream):
            print('Cant find: "Sign" - skipped!')
            return

        self.value = stream.unpack('<64s')

        if b'\x00' in self.value:
            self.value = self.value[:self.value.index(b'\x00')]

        self.value = self.value.decode('cp1251')

    def dump(self, stream: IOWrapper):
        if not self.value:
            self.value = 'Unsigned'

        stream.pack('<64s', self.value.encode('cp1251'))


class Parser:
    def __init__(self) -> None:
        self.mode = 'HTA'
        self.file = 'GAM'

        self.headers = Headers(self)
        self.info = Info(self)
        self.nodes = Nodes(self)
        self.meshes = Meshes(self)
        self.animations = Animations(self)
        self.skins = Skins(self)
        self.convex = Convex(self)
        self.collisions = Collisions(self)
        self.hier_geoms = HierGeoms(self)
        self.bounds = Bounds(self)
        self.groups = Groups(self)
        self.version = Version(self)
        self.generator = Generator(self)
        self.sign = Sign(self)

    def load(self, stream: io.FileIO):
        with IOWrapper(stream) as target:
            self.headers.load(target)
            self.info.load(target)
            self.nodes.load(target)
            self.meshes.load(target)
            self.animations.load(target)
            self.skins.load(target)
            self.convex.load(target)
            self.collisions.load(target)
            self.hier_geoms.load(target)
            self.bounds.load(target)
            self.groups.load(target)
            self.sign.load(target)

    def dump(self, stream: io.FileIO):
        self.nodes.recalculate()
        self.meshes.recalculate()
        self.animations.recalculate()
        self.skins.recalculate()
        self.convex.recalculate()
        self.collisions.recalculate()
        self.hier_geoms.recalculate()
        self.bounds.recalculate()
        self.groups.recalculate()
        self.headers.recalculate()

        with IOWrapper(stream) as target:
            self.headers.dump(target)
            self.info.dump(target)
            self.nodes.dump(target)
            self.meshes.dump(target)
            self.animations.dump(target)
            self.skins.dump(target)
            self.convex.dump(target)
            self.collisions.dump(target)
            self.hier_geoms.dump(target)
            self.bounds.dump(target)
            self.groups.dump(target)
            self.version.dump(target)
            self.generator.dump(target)
            self.sign.dump(target)
