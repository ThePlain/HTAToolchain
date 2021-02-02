import os
import struct
from htatype import *


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
            return 0, skinned
        if header_type == (0, 3,):
            return 1, skinned
        if header_type == (0, 2,) and header_size[0] == 16:
            return 2, skinned
        if header_type == (0, 2,):
            return 3, skinned
        if header_type == (0, 2, 3,) and header_size[0] == 16:
            return 4, skinned
        if header_type == (0, 1, 2,):
            return 5, skinned
        if header_type == (0, 2, 3,):
            return 6, skinned
        if header_type == (0, 1, 3,):
            return 7, skinned
        if header_type == (0, 1, 2, 3):
            return 8, skinned
        if header_type == (0, 1, 2, 3, 4,):
            return 9, skinned
        if header_type == (0, 1, 3, 4,):
            return 10, skinned
        if header_type == (0, 1, 3, 4, 5,):
            return 11, skinned
        if header_type == (0, 2, 3) and header_size[2] == 12:
            return 12, skinned
        if header_type == (0, 2, 3, 4) and header_size[2] == 12:
            return 13, skinned
        if header_type == (0, 2, 3, 4):
            return 14, skinned
        if header_type == (0, 1, 3, 0x14):
            return 15, skinned
        if header_type == (0, 1, 2, 3, 0x14):
            return 16, skinned
        raise RuntimeError('Unknown Vertex Headers', header_type)

    class Vertex(Dynamic):
        class XYZ(Structure):             # 0x00 @ 12
            position: Float(3)

        class XYZT1(Structure):           # 0x01 @ 20
            position: Float(3)
            uv0: Float(2)

        class XYZC(Structure):            # 0x02 @ 16
            position: Float(3)
            color: UInt8(4)

        class XYZWC(Structure):           # 0x03 @ 20
            position: Float(4)
            color: UInt8(4)

        class XYZWCT1(Structure):         # 0x04
            position: Float(4)
            color: UInt8(4)
            uv0: Float(2)

        class XYZNC(Structure):           # 0x05
            position: Float(3)
            normal: Float(3)
            color: UInt8(4)

        class XYZCT1(Structure):          # 0x06
            position: Float(3)
            color: UInt8(4)
            uv0: Float(2)

        class XYZNT1(Structure):          # 0x07
            position: Float(3)
            normal: Float(3)
            uv0: Float(2)

        class XYZNCT1(Structure):         # 0x08
            position: Float(3)
            normal: Float(3)
            color: UInt8(4)
            uv0: Float(2)

        class XYZNCT2(Structure):         # 0x09
            position: Float(3)
            normal: Float(3)
            color: UInt8(4)
            uv0: Float(2)
            uv1: Float(2)

        class XYZNT2(Structure):          # 0x0A
            position: Float(3)
            normal: Float(3)
            uv0: Float(2)
            uv1: Float(2)

        class XYZNT3(Structure):          # 0x0B
            position: Float(3)
            normal: Float(3)
            uv0: Float(2)
            uv1: Float(2)
            uv2: Float(2)

        class XYZCT1_UVW(Structure):      # 0x0C
            position: Float(3)
            color: UInt8(4)
            uv0: Float(3)

        class XYZCT2_UVW(Structure):      # 0x0D
            position: Float(3)
            color: UInt8(4)
            uv0: Float(3)
            uv1: Float(2)

        class XYZCT2(Structure):          # 0x0E
            position: Float(3)
            color: UInt8(4)
            uv0: Float(2)
            uv1: Float(2)

        class XYZNT1T(Structure):         # 0x0F
            position: Float(3)
            normal: Float(3)
            uv0: Float(2)
            tangent: Float(4)

        class XYZNCT1T(Structure):        # 0x10
            position: Float(3)
            normal: Float(3)
            color: UInt8(4)
            uv0: Float(2)
            tangent: Float(4)

        _modes_ = {
            0: XYZ(),
            1: XYZT1(),
            2: XYZC(),
            3: XYZWC(),
            4: XYZWCT1(),
            5: XYZNC(),
            6: XYZCT1(),
            7: XYZNT1(),
            8: XYZNCT1(),
            9: XYZNCT2(),
            10: XYZNT2(),
            11: XYZNT3(),
            12: XYZCT1_UVW(),
            13: XYZCT2_UVW(),
            14: XYZCT2(),
            15: XYZNT1T(),
            16: XYZNCT1T(),
        }
        position: list = [0, 0, 0]
        normal: list = [0, 0, 0]
        color: list = [0, 0, 0, 0]
        uv0: list = [0, 0]
        uv1: list = [0, 0]
        uv2: list = [0, 0]
        tangent: list = [0, 0, 0, 0]


class Headers(Structure, KeyManager):
    _container_ = ('items', 'tag')
    _headers_ = {
    # Header tag table for different file version
    #   Name             GAM     SAM
        'META':         (0x0001, 0x0006),
        'BONES':        (0x0002, 0x0003),
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
    }

    class Header(Structure):
        tag: UInt32()
        size: UInt32()
        offset: UInt64()

    bom: Byte(8)
    items: Vector(Header())

    def find(self, name: str, mode: str):
        assert isinstance(name, str)
        assert isinstance(mode, str)

        assign = self._headers_.get(name, None)
        assert assign is not None
        
        if mode == 'gam':
            tag = assign[0]
        
        if mode == 'sam':
            tag = assign[1]

        return self._container_ptr_.get(tag, None)


class Meta(Dynamic):
    class MetaSAM(Structure):
        count_mesh: UInt32()
        count_material: UInt32()
        count_node: UInt32()
        count_animation: UInt32()

    class MetaGAM(Structure):
        count_triangle: Int16()
        count_skin: Int16()
        count_static: Int16()
        count_animation: Int16()
        count_material: Int16()
        count_node: Int16()
        size_cfg: Int32()

    _modes_ = {'sam': MetaSAM(), 'gam': MetaGAM(), }

    count_triangle: int = 0
    count_skin: int = 0
    count_static: int = 0
    count_mesh: int = 0
    count_animation: int = 0
    count_material: int = 0
    count_node: int = 0
    size_cfg: int = 0


class Bones(Dynamic, KeyManager):
    class BoneSAM(Structure):
        name: CharArray(40)
        parent: Int16()
        location: Float(3)
        rotation: Float(4)
        scale: Float(3)

    class BoneGAM(Structure):
        name: CharArray(40)
        parent: Int32()
        location: Float(3)
        rotation: Float(4)
        inverse: Float(16)

    _container_ = (None, 'name')
    _modes_ = {'sam': BoneSAM(), 'gam': BoneGAM(), }

    name: str = ''
    parent: int = -1
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0, 1]
    scale: list = [1, 1, 1]
    inverse: list = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


class InfluenceItem(Dynamic):
    class InfluenceItemSAM(Structure):
        bone: Int16()
        weight: Float()

    class InfluenceItemGAM(Structure):
        bone: UInt16()
        weight: Float()
        offset: Float(3)
        normal: Float(3)

    _modes_ = {'sam': InfluenceItemSAM(), 'gam': InfluenceItemGAM(), }

    bone: int = 0
    weight: float = 0
    offset: list = [0, 0, 0]
    normal: list = [0, 0, 0]


class Influence(Dynamic):
    class InfluenceSAM(Dynamic):
        count: UInt32()
        items: Array(InfluenceItem, count_ptr='count')

    class InfluenceGAM():
        count: UInt16()
        items: Array(InfluenceItem, 4)

    _modes_ = {'sam': InfluenceSAM(), 'gam': InfluenceGAM()}

    count: int = 0
    items: list = []


class Meshes(Dynamic, KeyManager):
    class MeshSAM(Structure):
        type: UInt32()
        material: Int16()
        count_vertexes: UInt32()
        count_indices: UInt32()
        parent: Int16()
        headers: Vector(Int32(2))
        vertexes: Array(VertexType.Vertex(), count_ptr='count_vertexes')
        influences: Array(Influence(), count_ptr='count_vertexes')
        indices: Array(UInt16(), count_ptr='count_indices')

        def filter(self, name, type, buffer: bytes, *args, structure=None, **kwargs):
            # TODO: Process SAM loading
            return type.load(buffer, *args, structure=structure, **kwargs)

    class MeshGAM(Structure):
        name: CharArray(40)
        type: Int32()
        parent: Int32()
        group: Int32()
        material: Int32()
        size_vertexes: UInt32()
        type_vertexes: UInt32()
        count_vertexes: UInt32()
        count_indices: UInt32()
        vertexes: Array(VertexType.Vertex(), count_ptr='count_vertexes')
        doubles: Array(VertexType.Vertex(), count_ptr='count_vertexes')
        influences: Array(Influence(), count_ptr='count_vertexes')
        indices: Array(UInt16(), count_ptr='count_indices')

        def filter(self, name, type, buffer: bytes, *args, structure=None, **kwargs):
            if name == 'vertexes':
                kwargs['mode'] = self.type

            if name == 'doubles' and structure.type != 1:
                return [], 0

            if name == 'influences' and structure.type != 2:
                return [], 0

            return type.load(buffer, *args, structure=structure, **kwargs)

    _modes_ = {'sam': MeshSAM(), 'gam': MeshGAM(), }
    _container_ = (None, 'name')

    name: str = ''
    type: int = 0
    parent: int = -1
    group: int = 0
    material: int = 9
    size_vertexes: int = 0
    type_vertexes: int = 0
    count_vertexes: int = 0
    count_indices: int = 0
    vertexes: list = []
    doubles: list = []
    influences: list = []
    indices: list = []


class AnimationChange(Dynamic):
    class AnimationChangeSAM(Structure):
        type: UInt32()
        index: Int16()
        parent: Int16()

    class AnimationChangeGAM(Structure):
        index: Int16()
        type: UInt32()
        parent: Int16()

    _modes_ = {'sam': AnimationChangeSAM, 'gam': AnimationChangeGAM, }
    index: int = 0
    parent: int = -1
    type: int = 0


class AnimationKey(Dynamic):
    class AnimationKeySAM(Structure):
        location: Float(3)
        rotation: Float(4)
        scale: Float(3)

    class AnimationKeyGAM(Structure):
        bone: Int16()
        location: Float(3)
        rotation: Float(4)

    _modes_ = {'sam': AnimationKeySAM, 'gam': AnimationKeyGAM, }
    bone: int = 0
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0, 1]
    scale: list = [1, 1, 1]


class Animations(Dynamic, KeyManager):
    class AnimationSAM(Structure):
        name: CharArray(25)
        count_frame: UInt32()
        fps: UInt32()
        next: Int32()
        count_change: UInt32()
        changes: Array(AnimationChange(), count_ptr='count_change')
        keys: Array(AnimationKey(), count_ptr='count_key')

    class AnimationGAM(Structure):
        name: CharArray(25)
        count_frame: UInt16()
        fps: UInt16()
        next: Int16()
        count_change: UInt16()
        count_key: UInt16()
        action: Int32()
        changes: Array(AnimationChange(), count_ptr='count_change')
        keys: Array(AnimationKey(), count_ptr='count_key')

    _modes_ = {'sam': AnimationSAM, 'gam': AnimationGAM, }
    name: str = ''
    fps: int = 0
    next: int = 0
    action: int = 0
    count_frame: int = 0
    count_change: int = 0
    count_key: int = 0
    count_action: int = 0

    def __pre_init__(self, info={}, **kwargs):
        if info.get('mode', None) == 'sam':
            self.count_key = info.get('count_node', 0)


class Texture(Structure):
    file: CharArray(40)
    uv: UInt32()
    type: UInt32()


class Materials(Dynamic):
    class MaterialSAM(Structure):
        diffuse: Float(4)
        ambient: Float(4)
        specular: Float(4)
        emmisive: Float(4)
        power: Float()
        count_texture: UInt32()
        shader: CharVector()
        textures: Array(Texture(), count_ptr='count_texture')

    class MaterialGAM(Structure):
        diffuse: Float(4)
        ambient: Float(4)
        emmisive: Float(4)
        specular: Float(4)
        power: Float()
        count_texture: UInt32()
        shader: CharArray(100)
        textures: Array(Texture(), count_ptr='count_texture')

    _modes_ = {'sam': MaterialSAM, 'gam': MaterialGAM, }
    diffuse: list = [0.7, 0.7, 0.7, 0.7]
    ambient: list = [0.7, 0.7, 0.7, 0.7]
    emmisive: list = [0.7, 0.7, 0.7, 0.7]
    specular: list = [0.7, 0.7, 0.7, 0.7]
    power: float = 0
    count_texture: int = 0
    shader: str = ''
    texures: list = []

#TODO: Vector Manager
class Skin(Structure):
    count_skins: int = 0
    materials: Array(Materials(), count_ptr='count_skin')

    def __pre_init__(self, info={}, **kwargs):
        self.count_skins = info.get('')


class MeshCollision(Structure):
    count_vertices: UInt32()
    count_indices: UInt32()
    vertices: Array(Float(3), count_ptr='count_vertices')
    indices: Array(UInt16(3), count_ptr='count_indices')


class Collisions(Dynamic, KeyManager):
    class SimpleColliderHTA(Structure):
        type: UInt32()
        location: Float(3)
        rotation: Float(4)
        size: Float(3)

    class SimpleCollider113(Structure):
        type: UInt32()
        location: Float(3)
        rotation: Float(4)
        size: Float(3)
        gametype: UInt32()

    _modes_ = {'hta': SimpleColliderHTA, '113':SimpleCollider113, }
    type: int = 0
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0, 1]
    size: list = [1, 1, 1]
    gametype: int = 0


class HierGeoms(Dynamic, KeyManager):
    class SimpleColliderHTA(Structure):
        type: UInt32()
        location: Float(3)
        rotation: Float(4)
        size: Float(3)
        bone: UInt32()

    class SimpleCollider113(Structure):
        type: UInt32()
        location: Float(3)
        rotation: Float(4)
        size: Float(3)
        gametype: UInt32()
        bone: UInt32()

    _modes_ = {'hta': SimpleColliderHTA, '113':SimpleCollider113, }
    type: int = 0
    location: list = [0, 0, 0]
    rotation: list = [0, 0, 0, 1]
    size: list = [1, 1, 1]
    gametype: int = 0
    bone: int = -1


#TODO: Vector Manager
class BoneBounds(Structure, KeyManager):
    bone: UInt32()
    min_rotation: Float(3)
    max_rotation: Float(3)


class Groups(Dynamic, Structure):
    class GroupGAM(Structure):
        name: CharArray(20)
        min: UInt32()
        max: UInt32()
        nodes: Vector(UInt32())
        variants: Vector(Vector(UInt32()))

    class GroupSAM(Structure):
        name: CharArray(20)
        min: UInt32()
        max: UInt32()
        variants: Vector(UInt32())

    _container_ = (None, 'name')
    _modes_ = {'gam': GroupGAM, 'sam': GroupSAM}
    name: str = ''
    min: int = 0
    max: int = 0
    nodes: list = []
    variants: list = []


class Parser:
    def __init__(self):
        self.headers = Headers()
        self.meta = Meta()
        self.bones = Bones()
        self.meshes = Meshes()
        self.animations = Animations()
        self.materials = Materials()
        self.mesh_collision = MeshCollision()
        self.collisions = Collisions()
        self.hier_geoms = HierGeoms()
        self.bounds = BoneBounds()
        self.groups = Groups()

    def load(self, version: str, fullpath: str):
        assert isinstance(version, str) and version in ('113', 'hta')
        assert isinstance(fullpath, str)

        filename, ext = os.path.splitext(fullpath)
        mode = ext[1:]

        content = None
        with open(fullpath, 'rb') as stream:
            content = stream.read()

        self.headers.load(content, mode=mode, version=version)

        state: Headers.Header = None

        state = self.headers.find('META', mode)
        if state is not None:
            self.meta.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('BONES', mode)
        if state is not None:
            self.bones.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('MESHES', mode)
        if state is not None:
            self.meshes.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('ANIMATIONS', mode)
        if state is not None:
            self.animations.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('MATERIALS', mode)
        if state is not None:
            self.materials.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('CONVEX', mode)
        if state is not None:
            self.mesh_collision.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('COLLISIONS', mode)
        if state is not None:
            self.collisions.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('HIER_GEOM', mode)
        if state is not None:
            self.hier_geoms.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('BOUNDS', mode)
        if state is not None:
            self.bounds.load(content[state.offset:state.offset + state.size], mode=mode, version=version)

        state = self.headers.find('GROUPS', mode)
        if state is not None:
            self.groups.load(content[state.offset:state.offset + state.size], mode=mode, version=version)
