import os
import struct
from Types import Type, KeyManager


class VertexType:
    class VertexComponent:
        COORDINATE = 0x0
        NORMAL = 0x1
        COLOR = 0x2
        TEXTURE1 = 0x3
        TEXTURE2 = 0x4
        TEXTURE3 = 0x5
        TANGENT = 0x14
        BINORMAL = 0x15
        INFLUENCE = 0x16

    @classmethod
    def from_headers(cls, headers):
        header_type = list([i[0] for i in headers])
        header_size = list([i[1] for i in headers])

        skinned = header_type.index(0x16) if 0x16 in header_type else 0
        if skinned:
            del header_type[skinned]
            del header_size[skinned]
            skinned = True
        else:
            skinned = False

        binormal = header_type.index(0x15) if 0x15 in header_type else 0
        if binormal:
            del header_type[binormal]
            del header_size[binormal]
        else:
            binormal = False

        header_type = tuple(header_type)
        header_size = tuple(header_size)

        if header_type == (0,):
            return cls.XYZ, skinned
        if header_type == (0, 3,):
            return cls.XYZT1, skinned
        if header_type == (0, 2,) and header_size[0] == 16:
            return cls.XYZWC, skinned
        if header_type == (0, 2,):
            return cls.XYZC, skinned
        if header_type == (0, 2, 3,) and header_size[0] == 16:
            return cls.XYZWCT1, skinned
        if header_type == (0, 1, 2,):
            return cls.XYZNC, skinned
        if header_type == (0, 2, 3,):
            return cls.XYZCT1, skinned
        if header_type == (0, 1, 3,):
            return cls.XYZNT1, skinned
        if header_type == (0, 1, 2, 3):
            return cls.XYZNCT1, skinned
        if header_type == (0, 1, 2, 3, 4,):
            return cls.XYZNCT2, skinned
        if header_type == (0, 1, 3, 4,):
            return cls.XYZNT2, skinned
        if header_type == (0, 1, 3, 4, 5,):
            return cls.XYZNT3, skinned
        if header_type == (0, 2, 3) and header_size[2] == 12:
            return cls.XYZCT1_UVW, skinned
        if header_type == (0, 2, 3, 4) and header_size[2] == 12:
            return cls.XYZCT2_UVW, skinned
        if header_type == (0, 2, 3, 4):
            return cls.XYZCT2, skinned
        if header_type == (0, 1, 3, 0x14):
            return cls.XYZNT1T, skinned
        if header_type == (0, 1, 2, 3, 0x14):
            return cls.XYZNCT1T, skinned
        raise RuntimeError('Unknown Vertex Headers', header_type)


    class XYZ(Type.Struct):             # 0x00 @ 12
        position: Type.Float(3)

        def pack(self) -> bytes:
            return struct.pack('<3f', *self.position)

    class XYZT1(Type.Struct):           # 0x01 @ 20
        position: Type.Float(3)
        uv0: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f2f', *self.position, *self.uv0)

    class XYZC(Type.Struct):            # 0x02 @ 16
        position: Type.Float(3)
        color: Type.UInt8(4)

        def pack(self) -> bytes:
            return struct.pack('<3f4B', *self.position, *self.color)

    class XYZWC(Type.Struct):           # 0x03 @ 20
        position: Type.Float(4)
        color: Type.UInt8(4)

        def pack(self) -> bytes:
            return struct.pack('<4f4B', *self.position, *self.color)

    class XYZWCT1(Type.Struct):         # 0x04
        position: Type.Float(4)
        color: Type.UInt8(4)
        uv0: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f4B2F', *self.position, *self.color, *self.uv0)

    class XYZNC(Type.Struct):           # 0x05
        position: Type.Float(3)
        normal: Type.Float(3)
        color: Type.UInt8(4)

        def pack(self) -> bytes:
            return struct.pack('<3f3f4B', *self.position, *self.normal, *self.color)

    class XYZCT1(Type.Struct):          # 0x06
        position: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f4B2f', *self.position, *self.color, *self.uv0)

    class XYZNT1(Type.Struct):          # 0x07
        position: Type.Float(3)
        normal: Type.Float(3)
        uv0: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f3f2f', *self.position, *self.normal, *self.uv0)

    class XYZNCT1(Type.Struct):         # 0x08
        position: Type.Float(3)
        normal: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f3f4B2f', *self.position, *self.normal, *self.color, *self.uv0)

    class XYZNCT2(Type.Struct):         # 0x09
        position: Type.Float(3)
        normal: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(2)
        uv1: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f3f4B2f2f', *self.position, *self.normal, *self.color, *self.uv0, *self.uv1)

    class XYZNT2(Type.Struct):          # 0x0A
        position: Type.Float(3)
        normal: Type.Float(3)
        uv0: Type.Float(2)
        uv1: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f3f2f2f', *self.position, *self.normal, *self.uv0, *self.uv1)

    class XYZNT3(Type.Struct):          # 0x0B
        position: Type.Float(3)
        normal: Type.Float(3)
        uv0: Type.Float(2)
        uv1: Type.Float(2)
        uv2: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f3f2f2f2f', *self.position, *self.normal, *self.uv0, *self.uv1, *self.uv2)

    class XYZCT1_UVW(Type.Struct):      # 0x0C
        position: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(3)

        def pack(self) -> bytes:
            return struct.pack('<3f4f3f', *self.position, *self.color, *self.uv0)

    class XYZCT2_UVW(Type.Struct):      # 0x0D
        position: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(3)
        uv1: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f4B3f2f', *self.position, *self.color, *self.uv0, *self.uv1)

    class XYZCT2(Type.Struct):          # 0x0E
        position: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(2)
        uv1: Type.Float(2)

        def pack(self) -> bytes:
            return struct.pack('<3f4B2f2f', *self.position, *self.color, *self.uv0, *self.uv1)

    class XYZNT1T(Type.Struct):         # 0x0F
        position: Type.Float(3)
        normal: Type.Float(3)
        uv0: Type.Float(2)
        tangent: Type.Float(4)

        def pack(self) -> bytes:
            return struct.pack('<3f3f2f4f', *self.position, *self.normal, *self.uv0, *self.tangent)

    class XYZNCT1T(Type.Struct):        # 0x10
        position: Type.Float(3)
        normal: Type.Float(3)
        color: Type.UInt8(4)
        uv0: Type.Float(2)
        tangent: Type.Float(4)

        def pack(self) -> bytes:
            return struct.pack('<3f3f4B2f4f', *self.position, *self.normal, *self.color, *self.uv0, *self.tangent)

    class XYZNCT1_UV2_S1(Type.Struct):  # 0x11
        pass

    class STREAM_UV_S1(Type.Struct):    # 0x12
        pass

    class WATER_TEST(Type.Struct):      # 0x13
        pass

    class GRASS_TEST(Type.Struct):      # 0x14
        pass

    class IMPOSTORTEST(Type.Struct):    # 0x15
        pass

    class YNI(Type.Struct):             # 0x16
        pass

    class XYZT1I(Type.Struct):          # 0x17
        pass

    class INSTANCE(Type.Struct):        # 0x18
        pass

    map = {
        0: XYZ,
        1: XYZT1,
        2: XYZC,
        3: XYZWC,
        4: XYZWCT1,
        5: XYZNC,
        6: XYZCT1,
        7: XYZNT1,
        8: XYZNCT1,
        9: XYZNCT2,
        10: XYZNT2,
        11: XYZNT3,
        12: XYZCT1_UVW,
        13: XYZCT2_UVW,
        14: XYZCT2,
        15: XYZNT1T,
        16: XYZNCT1T,
        17: XYZNCT1_UV2_S1,
        18: STREAM_UV_S1,
        19: WATER_TEST,
        20: GRASS_TEST,
        21: IMPOSTORTEST,
        22: YNI,
        23: XYZT1I,
        24: INSTANCE,
    }

    SAM_PACK_TYPE = {
        'XYZ':          ((0, 12), ),
        'XYZT1':        ((0, 12), (3,  8), ),
        'XYZC':         ((0, 12), (2,  4), ),
        'XYZWC':        ((0, 16), (2,  4), ),
        'XYZWCT1':      ((0, 16), (2,  4), (3,  8), ),
        'XYZNC':        ((0, 12), (1, 12), (2,  4), ),
        'XYZCT1':       ((0, 12), (2,  4), (3,  8), ),
        'XYZNT1':       ((0, 12), (1, 12), (3,  8), ),
        'XYZNCT1':      ((0, 12), (1, 12), (2,  4), (3,  8)),
        'XYZNCT2':      ((0, 12), (1, 12), (2,  4), (3,  8), (4, 8),),
        'XYZNT2':       ((0, 12), (1, 12), (3,  8), (4,  4),),
        'XYZNT3':       ((0, 12), (1, 12), (3,  8), (4,  4), (5, 8), ),
        'XYZCT1_UVW':   ((0, 12), (2,  4), (3,  12), ),
        'XYZCT2_UVW':   ((0, 12), (2,  4), (3,  12), (4,  4), ),
        'XYZCT2':       ((0, 12), (2,  4), (3,  8), (4,  4), ),
        'XYZNT1T':      ((0, 12), (1, 12), (3,  8), (0x14, 16), ),
        'XYZNCT1T':     ((0, 12), (1, 12), (2,  4), (3,  8), (0x14, 16), ),
    }


class FileHeaderItem(Type.Struct):
    tag: Type.UInt32()
    size: Type.UInt32()
    offset: Type.UInt64()


class ManagerHeader(KeyManager):
    bom: bytes

    @classmethod
    def unpack(cls, buffer):
        offset = 0
        item = cls()

        item.bom, size = Type.Byte(8)(buffer)
        offset += size

        content, size = Type.StructVector(FileHeaderItem)(buffer[offset:])
        offset += size

        for header in content:
            item.dict_int[header.tag] = header

        return item, offset

    def pack(self) -> (int, bytes):
        content = b''

        for item in self:
            content += struct.pack('<IIL', item.tag, item.size, item.offset)

        return None, content


class DraftMeta(Type.Struct):
    count_mesh: Type.UInt32()
    count_material: Type.UInt32()
    count_node: Type.UInt32()
    count_animation: Type.UInt32()


class ModelMeta(Type.Struct):
    count_triangle: Type.Int16()
    count_skin: Type.Int16()
    count_static: Type.Int16()
    count_animation: Type.Int16()
    count_material: Type.Int16()
    count_node: Type.Int16()
    size_cfg: Type.Int32()


class FileMeta(Type.Union):
    count_triangle: int = 0
    count_skin: int = 0
    count_static: int = 0
    count_animation: int = 0
    count_material: int = 0
    count_node: int = 0
    size_cfg: int = 0
    count_mesh: int = 0
    config: str = 'hta'

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer)
        if mode == 'sam':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        content, size = ModelMeta.unpack(buffer)
        item.apply(content)
        item.count_mesh = item.count_skin + item.count_static + item.count_triangle
        return item, size

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        content, size = DraftMeta.unpack(buffer)
        item.apply(content)
        return item, size

    def pack(self, mode) -> (int, bytes):
        if mode == 'sam':
            return self.pack_sam()

        if mode == 'gam':
            return self.pack_gam()

    def pack_sam(self) -> (int, bytes):
        content = struct.pack(
            '<4I',
            self.count_mesh,
            self.count_material,
            self.count_node,
            self.count_animation)

        return 0x0006, content

    def pack_gam(self) -> (int, bytes):
        content = struct.pack(
            '<6HI',
            self.count_triangle,
            self.count_skin,
            self.count_static,
            self.count_animation,
            self.count_material,
            self.count_node,
            self.size_cfg,
        )

        return 0x0001, content


class DraftBone(Type.Struct):
    name: Type.CharArray(40)
    parent: Type.Int16()
    location: Type.Float(3)
    rotation: Type.Float(4)
    scale: Type.Float(3)


class ModelBone(Type.Struct):
    name: Type.CharArray(40)
    parent: Type.Int32()
    location: Type.Float(3)
    rotation: Type.Float(4)
    inverse: Type.Float(16)


class FileBone(Type.Union):
    name: str = ''
    parent: int = -1
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0, 1]
    scale: list = [1, 1, 1]
    inverse: list = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


class ManagerBone(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        content = None
        offset = 0
        item = cls()

        if mode == 'gam':
            content, offset = Type.StructArray(info.count_node, ModelBone)(buffer)
        if mode == 'sam':
            content, offset = Type.StructArray(info.count_node, DraftBone)(buffer)

        if not content:
            return item, 0

        for num, bone in enumerate(content):
            if not bone.name:
                bone.name = f'Bone{num}'

            item.dict_str[bone.name] = bone
            item.dict_int[num] = bone

        return item, offset

    def pack(self, mode) -> (int, bytes):
        if mode == 'sam':
            return self.pack_sam()
        if mode == 'gam':
            return self.pack_gam()

    def pack_sam(self) -> (int, bytes):
        content = b''

        for item in self:
            content += item.encode('cp1251').rjust(b'\x00', 40)
            content += struct.pack(
                '<h3f4f3f',
                item.parent,
                *item.location,
                *item.rotation,
                *item.scale,
            )

        return 0x0003, content

    def pack_gam(self) -> (int, bytes):
        content = b''

        for item in self:
            content += item.encode('cp1251').rjust(b'\x00', 40)
            content += struct.pack(
                '<i3f4f16f',
                *item.location,
                *item.rotation,
                *item.inverse,
            )

        return 0x0002, content

class DraftInfluenceItem(Type.Struct):
    bone: Type.Int16()
    weight: Type.Float()


class ModelInfluenceItem(Type.Struct):
    bone: Type.UInt16()
    weight: Type.Float()
    offset: Type.Float(3)
    normal: Type.Float(3)


# Custom struct with methods equal Type.Struct
class DraftInfluence:
    count_bone: int = 0
    influences = None

    @classmethod
    def unpack(cls, buffer):
        offset = 0
        item = cls()

        item.count_bone, size = Type.UInt32()(buffer)
        offset += size

        item.influences, size = Type.StructArray(item.count_bone, DraftInfluenceItem)(buffer[offset:])
        offset += size

        return item, offset


class ModelInfluence(Type.Struct):
    count_bone: Type.UInt16()
    influences: Type.StructArray(4, ModelInfluenceItem)


class FileInfluence(Type.Union):
    count_bone: int = 0
    influences: list = None

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer)
        if mode == 'sam':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        content, size = ModelInfluence.unpack(buffer)
        item.apply(content)
        return item, size

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        content, size = DraftInfluence.unpack(buffer)
        item.apply(content)
        return item, size

    def pack(self, mode) -> bytes:
        content = struct.pack('<H', len(self.count_bone))

        if mode == 'sam':
            for influence in self.influences:
                content += struct.pack('<Hf', influence.bone, influence.weight)

        if mode == 'gam':
            if len(self.influences) > 4:
                raise ValueError('GAM not support more that 4 bone per vertex')

            for influence in self.influences:
                content += struct.pack(
                    '<Hf3f3f',
                    influence.bone,
                    influence.weight,
                    *influence.offset,
                    *influence.normal,
                )

            align = 4 - len(self.influences)
            if align > 0:
                content += b'\x00' * 30 * align

        return content


class DraftMesh(Type.Struct):
    type: Type.UInt32()
    material: Type.Int16()
    count_vertexes: Type.UInt32()
    count_indices: Type.UInt32()
    parent: Type.Int16()


class ModelMesh(Type.Struct):
    name: Type.CharArray(40)
    type: Type.Int32()
    parent: Type.Int32()
    group: Type.Int32()
    material: Type.Int32()
    size_vertexes: Type.UInt32()
    type_vertexes: Type.UInt32()
    count_vertexes: Type.UInt32()
    count_indices: Type.UInt32()


class FileMesh(Type.Union):
    name: str = 'Mesh'
    type: int = 0
    parent: int = -1
    group: int = -1
    material: int = -1
    type_vertexes: int = -1
    size_vertexes: int = -1
    count_vertexes: int = -1
    count_indices: int = -1

    struct_vertexes = None
    vertex_headers: list = None
    vertexes: list = None
    influences: list = None
    indices: list = None
    animation: bool = False

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer, mode)
        if mode == 'sam':
            return cls.unpack_sam(buffer, mode)

    @classmethod
    def unpack_gam(cls, buffer, mode):
        offset = 0
        item = cls()

        content, size = ModelMesh.unpack(buffer)
        item.apply(content)
        offset += size

        item.struct_vertexes = VertexType.map[item.type_vertexes]

        content, size = Type.StructArray(item.count_vertexes, item.struct_vertexes)(buffer[offset:])
        item.vertexes = content
        offset += size

        if item.type == 1:
            content, size = Type.StructArray(item.count_vertexes, item.struct_vertexes)(buffer[offset:])
            item.vertexes = content
            offset += size

        if item.type == 2:
            content, size = Type.StructArray(item.count_vertexes, ModelInfluence)(buffer[offset:], mode)
            item.influences = content
            offset += size

        item.indices, size = Type.TypeArray(item.count_indices, Type.UInt16(3))(buffer[offset:])
        offset += size

        return item, offset

    @classmethod
    def unpack_sam(cls, buffer, mode):
        offset = 0
        item = cls()

        content, size = DraftMesh.unpack(buffer)
        item.apply(content)
        offset += size

        content, size = Type.TypeVector(Type.Int32(2))(buffer[offset:])
        item.vertex_headers = content
        offset += size

        item.struct_vertexes, self.animation = VertexType.from_headers(item.vertex_headers)

        item.vertexes = []
        for _ in range(item.count_vertexes):
            item.vertexes.append(item.struct_vertexes())

        for vtype, _ in item.vertex_headers:
            if vtype == 0:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('position'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].position = content[vid]
                offset += size

            if vtype == 1:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('normal'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].normal = content[vid]
                offset += size

            if vtype == 2:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('color'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].color = content[vid]
                offset += size

            if vtype == 3:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('uv0'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].uv0 = content[vid]
                offset += size

            if vtype == 4:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('uv1'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].uv1 = content[vid]
                offset += size

            if vtype == 5:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('uv2'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].uv2 = content[vid]
                offset += size

            if vtype == 0x14:
                content, size = Type.TypeArray(item.count_vertexes, item.struct_vertexes.type('tangent'))(buffer[offset:])
                for vid in range(item.count_vertexes):
                    item.vertexes[vid].tangent = content[vid]
                offset += size

#        content, size = Type.StructArray(item.count_vertexes, item.struct_vertexes)(buffer[offset:])
#        item.vertexes = content
#        offset += size

        if self.animation:
            content, size = Type.StructArray(item.count_vertexes, DraftInfluence)(buffer[offset:])
            item.influences = content
            offset += size

        content, size = Type.TypeArray(item.count_indices, Type.UInt16(3))(buffer[offset:])
        item.indices = content
        offset += size

        return item, offset

    def pack(self, mode) -> (int, bytes):
        if mode == 'sam':
            return self.pack_sam()
        if mode == 'gam':
            return self.pack_gam()

    def pack_sam(self) -> (int, bytes):
        content = b''

        content += struct.pack(
            '<IhIIh',
            item.type,
            item.material,
            item.count_vertexes,
            item.count_indices,
            item.parent,
        )

        vertex_header = VertexType.SAM_PACK_TYPE
        content += struct.pack(f'<{len(vertex_header) * 2}i', *sum(vertex_header, ()))

        if item.animation:
            content += struct.pack('<ii', 0x16, 0)

        vcount = item.vertex_count
        for vtype, vsize in vertex_header:
            if vtype == 0:
                elems = int(vsize / 4)
                content += struct.pack(f'<{vcount * elems}f', *sum([v.position for v in item.vertexes], []))
            if vtype == 1:
                content += struct.pack(f'<{vcount * 3}f', *sum([v.normal for v in item.vertexes], []))
            if vtype == 2:
                content += struct.pack(f'<{vcount * 4}B', *sum([v.color for v in item.vertexes], []))
            if vtype == 3:
                elems = int(vsize / 4)
                content += struct.pack(f'<{vcount * elems}f', *sum([v.uv0 for v in item.vertexes], []))
            if vtype == 4:
                content += struct.pack(f'<{vcount * 2}f', *sum([v.uv1 for v in item.vertexes], []))
            if vtype == 5:
                content += struct.pack(f'<{vcount * 2}f', *sum([v.uv2 for v in item.vertexes], []))
            if vtype == 0x14:
                content += struct.pack(f'<{vcount * 4}f', *sum([v.tangent for v in item.vertexes], []))

        if item.animation:
            for influence in self.influences:
                content += influence.pack('sam')

        icount = item.count_indices
        content += struct.pack(f'<{icount * 3}H', *sum(item.indices, []))

        return content

    def pack_gam(self) -> (int, bytes):
        content = b''

        content += item.name.encode('cp1251').rjust(b'\x00', 40)
        content += struct.pack(
            '<4i4I',
            item.type,
            item.parent,
            item.group,
            item.material,
            item.size_vertexes,
            item.type_vertexes,
            item.count_vertexes,
            item.count_indices,
        )

        for vert in item.vertexes:
            content += vert.pack()

        if item.animation:
            for influence in self.influences:
                content += influence.pack('gam')

        return content

class ManagerMesh(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        item = cls()
        content, size = Type.StructArray(info.count_mesh, FileMesh)(buffer, mode)

        for num, mesh in enumerate(content):
            item.dict_int[num] = mesh
            item.dict_str[mesh.name or f'Mesh{num}'] = mesh

        return item, size

    def pack(self, mode) -> bytes:
        content = b''

        for item in self:
            content += item.pack(mode)

        if mode == 'sam':
            return 0x0004, content

        if mode == 'gam':
            return 0x0001, content


class DraftChange(Type.Struct):
    type: Type.UInt32()
    index: Type.Int16()
    parent: Type.Int16()


class ModelChange(Type.Struct):
    index: Type.Int16()
    type: Type.UInt32()
    parent: Type.Int16()


class DraftKey(Type.Struct):
    location: Type.Float(3)
    rotation: Type.Float(4)
    scale: Type.Float(3)


class ModelKey(Type.Struct):
    bone: Type.Int16()
    location: Type.Float(3)
    rotation: Type.Float(4)


class DraftAnimation(Type.Struct):
    name: Type.CharArray(25)
    frames: Type.UInt32()
    fps: Type.UInt32()
    next: Type.Int32()
    changes: Type.UInt32()


class ModelAnimation(Type.Struct):
    name: Type.CharArray(25)
    frames: Type.UInt16()
    fps: Type.UInt16()
    next: Type.Int16()
    changes: Type.UInt16()
    keycount: Type.UInt16()
    action: Type.Int32()


class FileAnimation(Type.Union):
    name: str = ''
    frames: int = 0
    fps: int = 30
    next: int = 0
    changes: int = 0
    keycount: int = 0
    action: int = 0

    modifies: list = None
    keyframes: list = None

    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        if mode == 'gam':
            return cls.unpack_gam(buffer, info)
        if mode == 'sam':
            return cls.unpack_sam(buffer, info)

    @classmethod
    def unpack_gam(cls, buffer, info: FileMeta):
        item = cls()
        offset = 0

        content, size = ModelAnimation.unpack(buffer)
        item.apply(content)
        offset += size

        content, size = Type.StructArray(item.changes, ModelChange)(buffer[offset:])
        item.modifies = content
        offset += size

        content, size = Type.TypeArray(
            item.frames,
            Type.StructArray(item.keycount, ModelKey),
        )(buffer[offset:])
        item.keyframes = content
        offset += size

        return item, offset

    @classmethod
    def unpack_sam(cls, buffer, info: FileMeta):
        item = cls()
        offset = 0

        content, size = DraftAnimation.unpack(buffer)
        item.apply(content)
        offset += size

        content, size = Type.StructArray(item.changes, DraftChange)(buffer[offset:])
        item.changes = content
        offset += size

        content, size = Type.TypeArray(
            item.frames,
            Type.StructArray(info.count_node, DraftKey),
        )(buffer[offset:])
        item.keyframes = content
        offset += size

        return item, offset

    def pack(self, mode) -> bytes:
        if mode == 'sam':
            return self.pack_sam()

        if mode == 'gam':
            return self.pack_gam()

    def pack_sam(self) -> bytes:
        content = self.name.encode('cp1251').rjust(25)
        content += struct.pack(
            '<IIiI',
            self.frames,
            self.fps,
            self.next,
            self.changes,
        )
        for item in self.modifies:
            content += struct.pack(
                '<Ihh',
                item.type,
                item.index,
                item.parent,
            )
        for item in self.keyframes:
            content += struct.pack(
                '<3f4f3f',
                *item.position,
                *item.rotaiton,
                *item.scale,
            )
        return content

    def pack_gam(self) -> bytes:
        content = self.name.encode('cp1251').rjust(b'\x00', 25)
        content += struct.pack(
            '<HHhHHi',
            self.frames,
            self.fps,
            self.next,
            self.changes,
            self.keycount,
            self.action,
        )
        for item in self.modifies:
            content += struct.pack(
                '<hIh',
                item.index,
                item.type,
                item.parent,
            )
        for item in self.keyframes:
            content += struct.pack(
                '<h3f4f',
                item.bone,
                *item.location,
                *item.rotation,
            )

        return content


class ManagerAnimation(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        content = None
        offset = 0
        item = cls()

        content, offset = Type.StructArray(info.count_animation, FileAnimation)(buffer, mode, info)

        if not content:
            return item, 0

        for num, animation in enumerate(content):
            item.dict_str[animation.name or f'Animation{num}'] = animation
            item.dict_int[num] = animation

        return item, offset

    def pack(self, mode) -> (int, bytes):
        if mode == 'gam':
            return self.pack_gam(mode)
        if mode == 'sam':
            return self.pack_sam(mode)

    def pack_gam(self, mode) -> (int, bytes):
        content = b''
        for item in self:
            content += item.pack(mode)
        return 0x0008, content

    def pack_sam(self, mode) -> (int, bytes):
        content = b''
        for item in self:
            content += item.pack(mode)
        return 0x0004, content


class DraftTexture(Type.Struct):
    file: Type.CharArray(40)
    uv: Type.UInt32()
    type: Type.UInt32()


class ModelTexture(Type.Struct):
    file: Type.CharArray(40)
    uv: Type.UInt32()
    type: Type.UInt32()


class FileTexture(Type.Union):
    type: int = 0
    uv: int = 0
    file: str = ''

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer)
        if mode == 'sam':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        content, size = ModelTexture.unpack(buffer)
        item.apply(content)
        return item, size

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        content, size = DraftTexture.unpack(buffer)
        item.apply(content)
        return item, size

    def pack(self, mode) -> bytes:
        content = self.file.encode('cp1251').rjust(b'\x00', 40)
        content += struct.pack('<II', self.uv, self.type)
        return content


class DraftMaterial(Type.Struct):
    diffuse: Type.Float(4)
    ambient: Type.Float(4)
    specular: Type.Float(4)
    emmisive: Type.Float(4)
    power: Type.Float()
    tex_count: Type.UInt32()
    shader: Type.CharVector()


class ModelMaterial(Type.Struct):
    diffuse: Type.Float(4)
    ambient: Type.Float(4)
    emmisive: Type.Float(4)
    specular: Type.Float(4)
    power: Type.Float()
    tex_count: Type.UInt32()
    shader: Type.CharArray(100)


class FileMaterial(Type.Union):
    diffuse: list = None
    ambient: list = None
    specular: list = None
    emmisive: list = None
    power: float = 0
    tex_count: int = 0
    shader: str = ''
    textures: list = None
    shader_id: int = 0
    handle = None

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer, mode)
        if mode == 'sam':
            return cls.unpack_sam(buffer, mode)

    @classmethod
    def unpack_gam(cls, buffer, mode):
        item = cls()
        offset = 0

        content, size = ModelMaterial.unpack(buffer)
        item.apply(content)
        offset += size

        item.textures, size = Type.StructArray(item.tex_count, ModelTexture)(buffer[offset:], mode)
        offset += size

        return item, offset

    @classmethod
    def unpack_sam(cls, buffer, mode):
        item = cls()
        offset = 0

        content, size = DraftMaterial.unpack(buffer)
        item.apply(content)
        offset += size

        item.textures, size = Type.StructArray(item.tex_count, DraftTexture)(buffer[offset:], mode)
        offset += size

        return item, offset

    def pack(self, mode) -> bytes:
        content = b''

        if mode == 'sam':
            content = self.pack_sam()

        if mode == 'gam':
            content = self.pack_gam()

        for tex in self.textures:
            content += texture.pack(mode)

        return content

    def pack_sam(self):
        content = struct.pack(
            '<4f4f4f4ffI',
            *self.diffuse,
            *self.ambient,
            *self.specular,
            *self.emmisive,
            self.power,
            self.tex_count
        )
        shader = self.shader.encode('cp1251')
        content += struct.pack('<I', len(shader)) + shader
        return content

    def pack_gam(self):
        content = struct.pack(
            '<4f4f4f4ffI',
            *self.diffuse,
            *self.ambient,
            *self.emmisive,
            *self.specular,
            self.power,
            self.tex_count
        )
        content += self.shader.encode('cp1251').rjust(b'\x00', 100)
        return content

class ModelSkin(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        if mode == 'gam':
            return cls.unpack_gam(buffer, mode, info)
        if mode == 'sam':
            return cls.unpack_sam(buffer, mode, info)

    @classmethod
    def unpack_gam(cls, buffer, mode, info: FileMeta):
        item = cls()

        content, size = Type.StructArray(info.count_material, FileMaterial)(buffer, mode)
        for num, skin in enumerate(content):
            item.dict_int[num] = skin

        return item, size

    @classmethod
    def unpack_sam(cls, buffer, mode, info: FileMeta):
        item = cls()

        content, size = Type.StructArray(info.count_material, FileMaterial)(buffer, mode)
        for num, skin in enumerate(content):
            item.dict_int[num] = skin

        return item, size

    def pack(self, mode) -> (bytes):
        content = b''
        for item in self:
            content += item.pack(mode)
        return content


class ManagerMaterial(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode, info: FileMeta):
        if mode == 'gam':
            return cls.unpack_gam(buffer, mode, info)
        if mode == 'sam':
            return cls.unpack_sam(buffer, mode, info)

    @classmethod
    def unpack_gam(cls, buffer, mode, info: FileMeta):
        item = cls()

        content, size = Type.StructVector(ModelSkin)(buffer, mode, info)
        for num, mat in enumerate(content):
            item.dict_int[num] = mat

        return item, size

    @classmethod
    def unpack_sam(cls, buffer, mode, info: FileMeta):
        item = cls()

        content, size = Type.StructVector(ModelSkin)(buffer, mode, info)
        for num, mat in enumerate(content):
            item.dict_int[num] = mat

        return item, size

    def pack(self, mode) -> (int, bytes):
        content = struct.pack('<I', len(self.dict_int))
        for item in self:
            content += item.pack(mode)
        if mode == 'sam':
            return 0x0008, content
        if mode == 'gam':
            return 0x000F, content

class ModelCollision:
    count_vertexes: float = 0
    count_indices: float = 0
    vertexes: list = None
    indices: list = None

    @classmethod
    def unpack(cls, buffer, mode):
        if mode == 'gam':
            return cls.unpack_gam(buffer)
        if mode == 'sam':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        offset = 0

        item.count_vertexes, size = Type.UInt32()(buffer[offset:])
        offset += size

        item.count_indices, size = Type.UInt32()(buffer[offset:])
        offset += size

        item.vertexes, size = Type.TypeArray(item.count_vertexes, Type.Float(3))(buffer[offset:])
        offset += size

        item.indices, size = Type.TypeArray(item.count_indices, Type.UInt16(3))(buffer[offset:])
        offset += size

        return item, offset

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        offset = 0

        item.count_vertexes, size = Type.UInt32()(buffer[offset:])
        offset += size

        item.count_indices, size = Type.UInt32()(buffer[offset:])
        offset += size

        item.vertexes, size = Type.TypeArray(item.count_vertexes, Type.Float(3))(buffer[offset:])
        offset += size

        item.indices, size = Type.TypeArray(item.count_indices, Type.UInt16(3))(buffer[offset:])
        offset += size

        return item, offset

    def pack(self, mode) -> (int, bytes):
        content = struct.pack(
            '<II', self.count_vertexes, self.count_indices
        )
        icount = len(self.vertexes) * 3
        content += struct.pack(f'<{icount}f', *sum(self.vertexes, []))
        content += struct.pack(f'<{icount}h', *sum(self.indices, []))

        if mode == 'gam':
            return 0x0010, content
        if mode == 'sam':
            return 0x0005, content


class ModelSimpleCollider(Type.Struct):
    type: Type.UInt32()
    location: Type.Float(3)
    rotation: Type.Float(4)
    size: Type.Float(3)


class DraftSimpleCollider(Type.Struct):
    type: Type.UInt32()
    location: Type.Float(3)
    rotation: Type.Float(4)
    size: Type.Float(3)
    gametype: Type.UInt32()


class FileSimpleCollider(Type.Union):
    name: str = ''
    type: int = 0
    location: list = None
    rotation: list = None
    size: list = None
    gametype: int = 0

    @classmethod
    def unpack(cls, buffer, info: FileMeta):
        if info.config == 'hta':
            return cls.unpack_gam(buffer)
        if info.config == '113':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        content, size = ModelSimpleCollider.unpack(buffer)
        item.apply(content)
        return item, size

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        content, size = DraftSimpleCollider.unpack(buffer)
        item.apply(content)
        return item, size

    def pack(self, info: FileMeta) -> bytes:
        if info.config == 'hta':
            return self.pack_hta()
        if info.config == '113':
            return self.pack_113()

    def pack_hta(self) -> bytes:
        return struct.pack(
            '<I3f4f3f',
            self.type,
            *self.location,
            *self.rotation,
            *self.size,
        )

    def pack_113(self) -> bytes:
        return struct.pack(
            '<I3f4f3fI',
            self.type,
            *self.location,
            *self.rotation,
            *self.size,
            self.gametype,
        )


class ManagerSimpleCollider(KeyManager):
    @classmethod
    def unpack(cls, buffer, info: FileMeta):
        item = cls()
        content, size = Type.StructVector(FileSimpleCollider)(buffer, info)
        for num, collider in enumerate(content):
            collider.name = f'Collider{num}'
            item.dict_int[num] = collider
            item.dict_str[collider.name] = collider
        return item, size

    def pack(self, mode) -> (int, bytes):
        content = struct.pack('<I', len(self.dict_int))
        for item in self:
            content += item.pack(mode)
        if mode == 'gam':
            return 0x0020, content
        if mode == 'sam':
            return 0x0007, content


class ModelHierGeom(ModelSimpleCollider):
    bone: Type.UInt32()


class DraftHierGeom(DraftSimpleCollider):
    bone: Type.UInt32()


class FileHierGeom(Type.Union):
    type: int = 0
    location: list = None
    rotation: list = None
    size: list = None
    gametype: int = 0

    @classmethod
    def unpack(cls, buffer, info: FileMeta):
        if info.config == 'hta':
            return cls.unpack_gam(buffer)
        if info.config == '113':
            return cls.unpack_sam(buffer)

    @classmethod
    def unpack_gam(cls, buffer):
        item = cls()
        content, size = ModelHierGeom.unpack(buffer)
        item.apply(content)
        return item, size

    @classmethod
    def unpack_sam(cls, buffer):
        item = cls()
        content, size = DraftHierGeom.unpack(buffer)
        item.apply(content)
        return item, size

    def pack(self, info: FileMeta) -> bytes:
        if info.config == 'hta':
            return self.pack_hta()
        if info.config == '113':
            return self.pack_113()

    def pack_hta(self) -> bytes:
        return struct.pack(
            '<I3f4f3fI',
            self.type,
            *self.location,
            *self.rotation,
            *self.size,
            self.bone,
        )

    def pack_113(self) -> bytes:
        return struct.pack(
            '<I3f4f3fII',
            self.type,
            *self.location,
            *self.rotation,
            *self.size,
            self.gametype,
            self.bone,
        )


class ManagerHierGeom(KeyManager):
    @classmethod
    def unpack(cls, buffer, info: FileMeta):
        item = cls()
        content, size = Type.StructVector(FileHierGeom)(buffer, info)
        for num, collider in enumerate(content):
            item.dict_int[num] = collider
        return item, size

    def pack(self, mode) -> (int, bytes):
        content = struct.pack('<I', len(self.dict_int))
        for item in self:
            content += item.pack(mode)
        if mode == 'gam':
            return 0x0040, content
        if mode == 'sam':
            return 0x000A, content


class FileBoneBounds(Type.Struct):
    bone: Type.UInt32()
    min_rotation: Type.Float(3)
    max_rotation: Type.Float(3)


class ManagerBoneBounds(KeyManager):
    @classmethod
    def unpack(cls, buffer):
        item = cls()
        content, size = Type.StructVector(FileBoneBounds)(buffer)
        for num, bound in enumerate(content):
            item.dict_int[num] = bound
        return item, size

    def pack(self, mode) -> (int, bytes):
        content = struct.pack('<I', self.count)

        for item in self:
            content += struct.pack('<I3f3F', item.bone, *item.min, *item.max)

        if mode == 'sam':
            return 0x000B, content

        if mode == 'gam':
            return 0x0080, content


class ModelGroup(Type.Struct):
    name: Type.CharArray(20)
    min: Type.UInt32()
    max: Type.UInt32()
    nodes: Type.TypeVector(Type.UInt32())
    variants: Type.TypeVector(Type.TypeVector(Type.UInt32()))


class DraftGroup(Type.Struct):
    name: Type.CharArray(20)
    min: Type.UInt32()
    max: Type.UInt32()
    variants: Type.TypeVector(Type.UInt32())


class FileGroup(Type.Union):
    name: str = ''
    min: int = 0
    max: int = 0
    nodes: list = None
    variants: list = None

    @classmethod
    def unpack(cls, buffer, mode):
        item = cls()
        size = 0
        if mode == 'sam':
            content, size = DraftGroup.unpack(buffer)
            item.apply(content)
        if mode == 'gam':
            content, size = ModelGroup.unpack(buffer)
            item.apply(content)
        return item, size

    def pack(self, mode) -> bytes:
        content = self.name.encode('cp1251').rjust(b'\x00', 20)
        content += struct.pack('<II', self.min, self.max)

        if mode == 'gam':
            content += struct.pack(f'<I{len(self.nodes)}I', len(self.nodes), *self.nodes)
            content += struct.pack(f'<I{len(self.nodes)}I', len(self.nodes), *self.nodes)

        content += struct.pack(f'<I', len(self.variants))
        for var in self.variants:
            content += struct.pack(f'<I{len(var)}I', len(var), *var)

        return content


class ManagerGroup(KeyManager):
    @classmethod
    def unpack(cls, buffer, mode):
        item = cls()
        content, size = Type.StructVector(FileGroup)(buffer, mode)
        for num, group in enumerate(content):
            item.dict_str[group.name] = group
            item.dict_int[num] = group
        return item, size

    def pack(self, mode) -> (int, bytes):
        content = b''
        for item in self:
            content += item.pack(mode)
        if mode == 'gam':
            return 0x00F0, content
        if mode == 'sam':
            return 0x0009, content


class Parser:
    headers: ManagerHeader
    info: FileMeta
    nodes: ManagerBone
    meshes: ManagerMesh
    animations: ManagerAnimation
    materials: ManagerMaterial
    mesh_collision: ModelCollision
    simple_collisions: ManagerSimpleCollider
    hier_geom: ManagerHierGeom
    groups: ManagerGroup

    def __init__(self):
        self.headers = ManagerHeader()
        self.info = FileMeta()
        self.nodes = ManagerBone()
        self.meshes = ManagerMesh()
        self.animations = ManagerAnimation()
        self.materials = ManagerMaterial()
        self.mesh_collision = None
        self.simple_collisions = ManagerSimpleCollider()
        self.hier_geom = ManagerHierGeom()
        self.groups = ManagerGroup()

    def unpack(self, mode, filepath):
        assert isinstance(mode, str)
        assert mode in ('hta', '113')

        filename, ext = os.path.splitext(filepath)
        with open(filepath, 'rb') as file_pointer:
            content = file_pointer.read()
            if ext == '.gam':
                self.unpack_gam(content, mode)
            if ext == '.sam':
                self.unpack_sam(content, mode)

    def unpack_gam(self, buffer, mode):
        offset = 0

        self.headers, size = ManagerHeader.unpack(buffer)
        offset += size

        for header in self.headers:
            if header.tag == 0x0001:
                self.info, size = FileMeta.unpack(buffer[header.offset:], 'gam')
                self.info.config = mode
            if header.tag == 0x0002:
                self.nodes, size = ManagerBone.unpack(buffer[header.offset:], 'gam', self.info)
            if header.tag == 0x0004:
                self.meshes, size = ManagerMesh.unpack(buffer[header.offset:], 'gam', self.info)
            if header.tag == 0x0008:
                self.animations, size = ManagerAnimation.unpack(buffer[header.offset:], 'gam', self.info)
            if header.tag == 0x000F:
                self.materials, size = ManagerMaterial.unpack(buffer[header.offset:], 'gam', self.info)
            if header.tag == 0x0010:
                self.mesh_collisions, size = ModelCollision.unpack(buffer[header.offset:], 'gam')
            if header.tag == 0x0020:
                self.simple_collisions, size = ManagerSimpleCollider.unpack(buffer[header.offset:], self.info)
            if header.tag == 0x0040:
                self.hier_geom, size = ManagerHierGeom.unpack(buffer[header.offset:], self.info)
            if header.tag == 0x0080:
                self.bone_bound, size = ManagerBoneBounds.unpack(buffer[header.offset:])
            if header.tag == 0x00F0:
                self.groups, size = ManagerGroup.unpack(buffer[header.offset:], 'gam')

    def unpack_sam(self, buffer, mode):
        offset = 0

        self.headers, size = ManagerHeader.unpack(buffer)
        offset += size

        header = self.headers[0x0006]
        if header:
            self.info, size = FileMeta.unpack(buffer[header.offset:], 'sam')
            self.info.config = mode

        header = self.headers[0x0003]
        if header:
            self.nodes, size = ManagerBone.unpack(buffer[header.offset:], 'sam', self.info)

        header = self.headers[0x0001]
        if header:
            self.meshes, size = ManagerMesh.unpack(buffer[header.offset:], 'sam', self.info)

        header = self.headers[0x0004]
        if header:
            self.animations, size = ManagerAnimation.unpack(buffer[header.offset:], 'sam', self.info)

        header = self.headers[0x0008]
        if header:
            self.materials, size = ManagerMaterial.unpack(buffer[header.offset:], 'sam', self.info)

        header = self.headers[0x000C]
        if header:
            pass # self.masks

        header = self.headers[0x0005]
        if header:
            self.mesh_collision, size = ModelCollision.unpack_sam(buffer[header.offset:])

        header = self.headers[0x0007]
        if header:
            self.simple_collisions, size = ManagerSimpleCollider.unpack(buffer[header.offset:], self.info)

        header = self.headers[0x000A]
        if header:
            self.hier_geom, size = ManagerHierGeom.unpack(buffer[header.offset:], self.info)

        header = self.headers[0x000B]
        if header:
            self.bone_bound, size = ManagerBoneBounds.unpack(buffer[header.offset:])

        header = self.headers[0x0009]
        if header:
            self.groups, size = ManagerGroup.unpack(buffer[header.offset:], 'sam')

        print('Model info:')
        print(f'  Node count: {len(self.nodes.dict_int)}')
        print(f'  Mesh count: {len(self.meshes.dict_int)}')
        print(f'  Animation count: {len(self.animations.dict_int)}')
        print(f'  Materials count: {len(self.materials.dict_int)}')
