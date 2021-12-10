import imp
import os
from typing import DefaultDict, Text
import bpy
import shutil
import bpy.types
import bpy.props
import bpy_extras.io_utils
import bmesh
import mathutils
import math
import pathlib

from . import htaparser

imp.reload(htaparser)

#FIX: Fix item by index selection
#FIX: Renamed parser module
#FIX: bl_idname must contain only lowercase chars
#FIX: Apply smooth for imported meshes
#FIX: Fix for node or mesh name collision
#FIX: Fix type hint for keyset methods
#FIX: Fix Influence weight capture
#FIX: Fix animation parsing error
#FIX: Added new object type for skinned meshes
#FIX: Added sort for convex mesh
#FIX: Remove double convex mesh after export

#TODO: Export Selected
#TODO: Import vertex weight
#TODO: Export vertex weight
#TODO: Import JOINTS as native armature
#TODO: Export JOINTS as object
#TODO: Fix JOINTS transformations
#TODO: Can't save .sam format

#TODO: Import cannot set group variant for mesh
#TODO: Not export new meshes(Not added to group)
#TODO: Smooth for UVSeam


bl_info = {
    'name': 'Hard Truck Apocalypse Tools',
    'blender': (2, 93, 0),
    'category': 'Import-Export',
    'version': (3, 5, 106),
    'desctiption': 'Import-Export Hard Truck Apocalypse GAM and SAM files',
    'support': 'TESTING',
    'author': 'ThePlain (Alexander Fateev)',
}


GAME_VERSION = [
    ('HTA', 'Hard Truck Apocalypse', ''),
    ('113', 'Hard Truck Apocalypse: Rise of Clans', ''),
]

VERTEX_TYPE = [
    ('NONE', 'Not Used', ''),
    ('0',  'XYZ', ''),
    ('1',  'XYZT1', ''),
    ('2',  'XYZC', ''),
    ('3',  'XYZWC', ''),
    ('4',  'XYZWCT1', ''),
    ('5',  'XYZNC', ''),
    ('6',  'XYZCT1', ''),
    ('7',  'XYZNT1', ''),
    ('8',  'XYZNCT1', ''),
    ('9',  'XYZNCT2', ''),
    ('10', 'XYZNT2', ''),
    ('11', 'XYZNT3', ''),
    ('12', 'XYZCT1_UVW', ''),
    ('13', 'XYZCT2_UVW', ''),
    ('14', 'XYZCT2', ''),
    ('15', 'XYZNT1T', ''),
    ('16', 'XYZNCT1T', ''),
]

DRAW_MODE = [
    ('1', 'Animated', 'Mode for animated objects'),
    ('2', 'Skinned', 'Mode for skinned objects'),
    ('4', 'Static', 'Mode for static objects'),
]

OBJECT_TYPE = [
    ('DEFAULT', 'Default object', 'Default mesh or bone object'),
    ('COLLIDER', 'Simple collider', 'Simple cube or sphere collider'),
    ('CONVEX', 'Mesh collider', 'Mesh based collider'),
]

COLLIDER_TYPE = [
    ('NONE', 'Not Used', ''),
    ('0', 'Cube collider', ''),
    ('1', 'Sphere collider', ''),
    ('2', 'Cylinder collider', ''),
]

ANIM_DATA_MAP = {
    'location': 'location',
    'rotation_quaternion': 'rotation',
    'rotation_euler': 'rotation',
    'scale': 'scale',
}

MATRIX_ENTITY = [
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
]

MATRIX_SWITCH = mathutils.Matrix([
    [1.0, 0.0, 0.0, 0.0,],
    [0.0, 0.0, 1.0, 0.0,],
    [0.0, 1.0, 0.0, 0.0,],
    [0.0, 0.0, 0.0, 1.0,],
])

TEXTURE_TYPES = ('Diffuse', 'Bump', 'Lightmap', 'Cube', 'Detail')


def matrix_flatten(matrix: mathutils.Matrix) -> list:
    return list(sum(map(list, matrix), []))


class HTAConfing(bpy.types.AddonPreferences):
    bl_idname = __package__

    game_path: bpy.props.StringProperty(
        name='Game path', 
        subtype='DIR_PATH',
    )
    game_version: bpy.props.EnumProperty(
        name='Game Version',
        default='HTA',
        items=GAME_VERSION
    )
    vertex_type: bpy.props.EnumProperty(
        name='VertexType',
        default='15',
        items=VERTEX_TYPE
    )
    collider_type: bpy.props.EnumProperty(
        name='ColliderType',
        default='0',
        items=COLLIDER_TYPE
    )
    shader_name: bpy.props.StringProperty(
        name='Shader name',
        default='bumpdiffuse_envalphagloss_spec'
    )
    model_sign: bpy.props.StringProperty(
        name='Model sign',
        default=''
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'game_path')
        layout.prop(self, 'game_version')
        layout.prop(self, 'vertex_type')
        layout.prop(self, 'collider_type')
        layout.prop(self, 'shader_name')
        layout.prop(self, 'model_sign')


bpy.utils.register_class(HTAConfing)
preferences = bpy.context.preferences.addons[__package__].preferences


def search_file(name: str) -> str:
    if not preferences.game_path:
        return None

    for root, _, files in os.walk(preferences.game_path):
        if name in files:
            return os.path.join(root, name)

    return None


def HTAObject_update(self, context):
    preferences = bpy.context.preferences.addons[__package__].preferences

    if context.object:
        if self.object_type == 'DEFAULT':
            context.object.display_type = 'TEXTURED'

            self.vertex_type = preferences.vertex_type
            self.collider_type = 'NONE'

        elif self.object_type == 'CONVEX':
            context.object.display_type = 'WIRE'

            self.vertex_type = 'XYZ'
            self.collider_type = 'NONE'

        elif self.object_type == 'COLLIDER':
            self.vertex_type = 'NONE'
            self.collider_type = preferences.collider_type


class HTAObject(bpy.types.PropertyGroup):
    draw_mode: bpy.props.EnumProperty(
        name='Draw mode',
        default='4',
        items=DRAW_MODE,
        update=HTAObject_update
    )

    object_type: bpy.props.EnumProperty(
        name='Object type',
        default='DEFAULT',
        items=OBJECT_TYPE,
        update=HTAObject_update
    )

    vertex_type: bpy.props.EnumProperty(
        name='Vertex type',
        default=preferences.vertex_type,
        items=VERTEX_TYPE
    )

    collider_type: bpy.props.EnumProperty(
        name='Collider type',
        default=preferences.collider_type,
        items=COLLIDER_TYPE
    )

    variant: bpy.props.IntProperty(
        name='Variant Num',
        default=0,
    )

    bound_used: bpy.props.BoolProperty(
        name='Rotaion Limit',
        default=False,
    )

    bound_min_x: bpy.props.FloatProperty(
        name='Min X',
        default=0
    )

    bound_min_y: bpy.props.FloatProperty(
        name='Min Y',
        default=0
    )

    bound_min_z: bpy.props.FloatProperty(
        name='Min Z',
        default=0
    )

    bound_max_x: bpy.props.FloatProperty(
        name='Max X',
        default=0
    )

    bound_max_y: bpy.props.FloatProperty(
        name='Max Y',
        default=0
    )

    bound_max_z: bpy.props.FloatProperty(
        name='Max Z',
        default=0
    )


class HTAObjectPanel(bpy.types.Panel):
    bl_idname = f'{__package__}.objectpanel'.lower()
    bl_label = 'HTA Object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        layout.prop(context.object.htatools, 'draw_mode')
        layout.prop(context.object.htatools, 'object_type')
        layout.prop(context.object.htatools, 'vertex_type')
        layout.prop(context.object.htatools, 'collider_type')
        layout.prop(context.object.htatools, 'variant')

        layout.prop(context.object.htatools, 'bound_used')

        col = layout.column()
        row = col.split(align=True)
        row.prop(context.object.htatools, 'bound_min_x')
        row.prop(context.object.htatools, 'bound_min_y')
        row.prop(context.object.htatools, 'bound_min_z')

        col = layout.column()
        row = col.split(align=True)
        row.prop(context.object.htatools, 'bound_max_x')
        row.prop(context.object.htatools, 'bound_max_y')
        row.prop(context.object.htatools, 'bound_max_z')


class HTAMaterial(bpy.types.PropertyGroup):
    shader_name: bpy.props.StringProperty(
        name='Shader name',
        default=preferences.shader_name
    )


class HTAMaterialPanel(bpy.types.Panel):
    bl_idname = f'{__package__}.materialpanel'.lower()
    bl_label = 'HTA Material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        return (context.material is not None)

    def draw(self, context):
        layout = self.layout
        layout.prop(context.material.htatools, 'shader_name')


class HTAImport(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = f'{__package__}.modelimport'.lower()
    bl_label = 'HTA Model Import (.gam/.sam)'

    filename_ext = ".gam"
    filter_glob: bpy.props.StringProperty(
        default="*.gam;*.sam",
        options={'HIDDEN'}
    )

    game_version: bpy.props.EnumProperty(
        name='Game Version',
        default=preferences.game_version,
        items=GAME_VERSION,
    )

    imp_textures: bpy.props.BoolProperty(
        name='Import Textures',
        default=True,
    )

    imp_animation: bpy.props.BoolProperty(
        name='Import Animations',
        default=True,
    )

    imp_convex: bpy.props.BoolProperty(
        name='Import Convex Collider',
        default=True,
    )

    imp_collisions: bpy.props.BoolProperty(
        name='Import Simple Colliders',
        default=True,
    )

    imp_hier: bpy.props.BoolProperty(
        name='Import Hier Geoms',
        default=True,
    )

    use_tex2mtl_name: bpy.props.BoolProperty(
        name='Cast texture to material name',
        default=True,
    )

    def execute(self, context):
        provider = htaparser.Parser()
        provider.t2m_name = True
        provider.mode = self.game_version
        provider.file = self.filepath[-3:].upper()

        filename = os.path.basename(self.filepath)
        provider.model_name, _ = os.path.splitext(filename)

        model_directory = os.path.dirname(self.filepath)

        print(f'Load file: "{provider.file}" at mode: "{provider.mode}"')
        scene = bpy.context.scene

        with open(self.filepath, 'rb') as stream:
            provider.load(stream)

        print('Import: Materials')
        for skin in provider.skins:
            for item in skin.values():
                mtl = bpy.data.materials.new(item.name)
                mtl.use_nodes = True
                mtl.htatools.shader_name = item.shader

                root = mtl.node_tree.nodes["Principled BSDF"]

                for tex_item in item.textures:
                    if tex_item.filename not in bpy.data.images:
                        filepath = os.path.join(model_directory, tex_item.filename)

                        if not os.path.isfile(filepath):
                            filepath = search_file(tex_item.filename)

                        if not filepath:
                            continue

                        if self.imp_textures:
                            bpy.data.images.load(filepath, check_existing=True)

                    node = mtl.node_tree.nodes.new('ShaderNodeTexImage')
                    node.name = TEXTURE_TYPES[tex_item.type]

                    if tex_item.filename in bpy.data.images:
                        node.image = bpy.data.images[tex_item.filename]

                    if node.name == 'Diffuse':
                        mtl.node_tree.links.new(root.inputs['Base Color'], node.outputs['Color'])
                        mtl.node_tree.links.new(root.inputs['Alpha'], node.outputs['Alpha'])

                    if node.name == 'Bump':
                        filter = mtl.node_tree.nodes.new('ShaderNodeNormalMap')

                        mtl.node_tree.links.new(root.inputs['Normal'], filter.outputs['Normal'])
                        mtl.node_tree.links.new(root.inputs['Specular'], node.outputs['Alpha'])
                        mtl.node_tree.links.new(filter.inputs['Color'], node.outputs['Color'])

                        bpy.data.images[tex_item.filename].colorspace_settings.name = 'Non-Color'


        if self.imp_collisions:
            print('Import: Collisions')
            for item in provider.collisions:
                obj = bpy.data.objects.new(item.name, None)

                x, y, z = item.location
                obj.location = [x, z, y]

                x, y, z, w = item.rotation
                obj.rotation_mode = 'QUATERNION'
                obj.rotation_quaternion = [w, -x, -z, -y]

                obj.empty_display_size = 0.5
                obj.htatools.collider_type = str(item.type)
                obj.htatools.object_type = 'COLLIDER'

                x, y, z = item.scale
                if item.type == 0:
                    obj.empty_display_type = 'CUBE'
                    obj.scale = [x, z, y]

                elif item.type == 1:
                    obj.empty_display_type = 'SPHERE'
                    obj.scale = [x, x, x]

                elif item.type == 2:
                    obj.scale = [x, z, y]

                scene.collection.objects.link(obj)

        if self.imp_convex:
            print('Import: Convex')
            if provider.convex.used:
                data = bpy.data.meshes.new('Convex')
                vertices = [[x, z, y] for x, y, z in provider.convex.vertices]
                indices = [[i2, i1, i0] for i0, i1, i2 in provider.convex.indices]
                data.from_pydata(vertices, [], indices)

                obj = bpy.data.objects.new('Convex', data)
                obj.htatools.object_type = 'CONVEX'
                obj.display_type = 'WIRE'

                scene.collection.objects.link(obj)

        print('Import: Meshes')
        for item in provider.meshes:
            mesh = bpy.data.meshes.new(item.name)

            obj_item = provider.nodes.by_index(item.parent)
            inverse = mathutils.Matrix([
                obj_item.matrix[0:4],
                obj_item.matrix[4:8],
                obj_item.matrix[8:12],
                obj_item.matrix[12:16]
            ]).transposed()

            vertices = []
            for vert in item.vertices:
                x, y, z, *w = vert.location
                location = mathutils.Vector([x, y, z, w or 1.0])

                x, y, z, w = inverse @ location
                vertices.append([x, z, y])

            indices = [[i2, i1, i0] for i0, i1, i2 in item.indices]

            mesh.from_pydata(vertices, [], indices)

            for face in mesh.polygons:
                for vert_id, loop_id in zip(face.vertices, face.loop_indices):
                    vert = item.vertices[vert_id]
                    if vert.normal:
                        normal = mathutils.Vector([*vert.normal, 0.0])
                        x, y, z, _ = inverse @ normal
                        mesh.loops[loop_id].normal = [x, z, y]

                    if vert.uv0:
                        x, y, *_ = vert.uv0
                        if 'uv0' not in mesh.uv_layers:
                            mesh.uv_layers.new(name='uv0')
                        layer = mesh.uv_layers['uv0']
                        layer.data[loop_id].uv = [x, 1 - y]

                    if vert.uv1:
                        x, y, *_ = vert.uv1
                        if 'uv1' not in mesh.uv_layers:
                            mesh.uv_layers.new(name='uv1')
                        layer = mesh.uv_layers['uv1']
                        layer.data[loop_id].uv = [x, 1 - y]

                    if vert.uv2:
                        x, y, *_ = vert.uv2
                        if 'uv2' not in mesh.uv_layers:
                            mesh.uv_layers.new(name='uv2')
                        layer = mesh.uv_layers['uv2']
                        layer.data[loop_id].uv = [x, 1 - y]

                    if vert.color:
                        if 'color' not in mesh.vertex_colors:
                            mesh.vertex_colors.new(name='color')
                        layer = mesh.vertex_colors['color']
                        r, g, b, a = [v / 255 for v in vert.color]
                        layer.data[loop_id].color = [r, g, b, a]

            for f in mesh.polygons:
                f.use_smooth = True

            obj = bpy.data.objects.new(obj_item.name, mesh)
            obj.htatools.draw_mode = str(item.type)
            obj.htatools.vertex_type = str(item.vertex_type)

            group = provider.groups.by_index(item.group)
            obj.htatools.variant = group.get_variant(provider.meshes.index(item.name))

            x, y, z = obj_item.location
            obj.location = [x, z, y]

            x, y, z, w = obj_item.rotation
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = [w, -x, -z, -y]

            x, y, z = obj_item.scale
            obj.scale = [x, z, y]

            scene.collection.objects.link(obj)

            if item.material >= 0:
                for skin in provider.skins.items:
                    mtl_item = provider.skins.by_index(skin, item.material)
                    mtl = bpy.data.materials[mtl_item.name]
                    mesh.materials.append(mtl)

        print('Import: Loadpoints')
        for item in provider.nodes:
            if item.name in bpy.data.objects:
                continue

            obj = bpy.data.objects.new(item.name, None)

            x, y, z = item.location
            obj.location = [x, z, y]

            x, y, z, w = item.rotation
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = [w, -x, -z, -y]

            x, y, z = item.scale
            obj.scale = [x, z, y]

            obj.show_name = True
            obj.empty_display_size = 0.5

            scene.collection.objects.link(obj)

        print('Load BoneBounds')
        for bound in provider.bounds:
            item = provider.nodes.by_index(bound.node)
            obj = bpy.data.objects[item.name]

            obj.htatools.bound_used = True
            x, y, z = bound.min_rotaiton
            obj.htatools.bound_min_x = -math.degrees(x)
            obj.htatools.bound_min_y = -math.degrees(z)
            obj.htatools.bound_min_z = -math.degrees(y)

            x, y, z = bound.max_rotaiton
            obj.htatools.bound_max_x = -math.degrees(x)
            obj.htatools.bound_max_y = -math.degrees(z)
            obj.htatools.bound_max_z = -math.degrees(y)

        print('Relink: Parents')
        for item in provider.nodes:
            if item.parent < 0:
                continue

            parent_item = provider.nodes.by_index(item.parent)

            obj = bpy.data.objects[item.name]
            obj.parent = bpy.data.objects[parent_item.name]

        print('Relink: Collections')
        for item in provider.groups:

            if item.name not in bpy.data.collections:
                if item.name == 'Main':
                    continue

                collection = bpy.data.collections.new(item.name)
                scene.collection.children.link(collection)

            else:
                collection = bpy.data.collections[item.name]

            for node_num in item.nodes:
                mesh_item = provider.meshes.by_index(node_num)
                node_item = provider.nodes.by_index(mesh_item.parent)

                collection.objects.link(bpy.data.objects[node_item.name])

        if self.imp_animation:
            print('Import: Animations')
            for animation in provider.animations:
                targets = []
                for num, frame in enumerate(animation.frames):
                    for key in frame.values():
                        item = provider.nodes.by_index(key.node)
                        node = bpy.data.objects[item.name]
                        targets.append(node)

                        x, y, z = key.location
                        node.location = [x, z, y]

                        x, y, z, w = key.rotation
                        node.rotation_quaternion = [w, -x, -z, -y]

                        x, y, z = key.scale
                        node.scale = [x, z, y]

                        node.keyframe_insert(data_path='location', frame=num)
                        node.keyframe_insert(data_path='rotation_quaternion', frame=num)
                        node.keyframe_insert(data_path='scale', frame=num)

                        node.animation_data.action.name = f'{animation.name}({node.name})'

                for node in targets:
                    action = node.animation_data.action

                    if action:
                        nla = node.animation_data.nla_tracks.new()
                        nla.name = action.name

                        if '(' in nla.name:
                            nla.name = nla.name[:nla.name.index('(')]

                        nla.strips.new(animation.name, action.frame_range[0], action)
                        node.animation_data.action = None

        return {'FINISHED'}


class HTAExport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = f'{__package__}.modelexport'.lower()
    bl_label = 'HTA Model Export (.gam/.sam)'

    filename_ext = ".gam"
    filter_glob: bpy.props.StringProperty(
        default="*.gam;*.sam",
        options={'HIDDEN'}
    )

    game_version: bpy.props.EnumProperty(
        name='Game Version',
        default=preferences.game_version,
        items=GAME_VERSION,
    )

    export_images: bpy.props.BoolProperty(
        name='Export Textures',
        default=False,
    )

    make_backup: bpy.props.BoolProperty(
        name='Create File Backup',
        default=False,
    )

    def execute(self, context):
        if self.make_backup and os.path.isfile(self.filepath):
            shutil.copy(self.filepath, self.filepath + '.bak')

        model_directory = os.path.dirname(self.filepath)

        provider = htaparser.Parser()
        provider.mode = self.game_version
        provider.file = self.filepath[-3:].upper()

        for item in bpy.data.objects:
            if item.type != 'MESH' and item.htatools.object_type == 'CONVEX':
                continue
            if item.htatools.object_type != 'DEFAULT':
                continue

            provider.nodes[item.name] = htaparser.Node()
            provider.nodes[item.name].name = item.name

            x, y, z = item.location
            provider.nodes[item.name].location = [x, z, y]

            if item.rotation_mode == 'QUATERNION':
                w, x, y, z = item.rotation_quaternion

            if item.rotation_mode == 'XYZ':
                w, x, y, z = item.rotation_euler.to_quaternion().normalized()

            provider.nodes[item.name].rotation = [-x, -z, -y, w]

            x, y, z = item.scale
            provider.nodes[item.name].scale = [x, z, y]

            if item.htatools.draw_mode == '4':
                provider.nodes[item.name].matrix = matrix_flatten(item.matrix_world.inverted().transposed())

            node_index = provider.nodes.index(item.name)

            group_name = 'Main'

            if item.users_collection[0] is not bpy.context.scene.collection:
                group_name = item.users_collection[0].name

            group = provider.groups[group_name]
            if not group:
                group = htaparser.Group(provider)
                group.name = group_name
                provider.groups[group_name] = group

            if item.htatools.bound_used:
                bound = htaparser.Bound()
                bound.node = node_index

                x = -math.radians(item.htatools.bound_min_x)
                y = -math.radians(item.htatools.bound_min_z)
                z = -math.radians(item.htatools.bound_min_y)
                bound.min_rotation = [x, z, y]

                x = -math.radians(item.htatools.bound_max_x)
                y = -math.radians(item.htatools.bound_max_z)
                z = -math.radians(item.htatools.bound_max_y)
                bound.max_rotation = [x, z, y]

                provider.bounds.items.append(bound)

            if item.animation_data and item.animation_data.nla_tracks:
                tracks = item.animation_data.nla_tracks
                for track in tracks:
                    for strip in track.strips:
                        action = strip.action

                        if track.name not in provider.animations:
                            anim = htaparser.Animation(provider)
                            anim.name = track.name
                            provider.animations[track.name] = anim
                            anim.fps = 60
                            anim.frame_count = int(strip.frame_end)

                            for _ in range(anim.frame_count):
                                anim.frames.append(list())

                        anim = provider.animations[track.name]

                        for frame in range(anim.frame_count):
                            key = htaparser.Key()
                            key.location = []
                            key.rotation = []
                            key.scale = []
                            key.node = node_index

                            for curve in action.fcurves:
                                path = ANIM_DATA_MAP.get(curve.data_path)
                                value = getattr(key, path)
                                value.append(curve.evaluate(frame))

                            x, y, z = key.location or [0, 0, 0]
                            key.location = [x, z, y]

                            if len(key.rotation) == 4:
                                rot = mathutils.Quaternion(key.rotation or [1, 0, 0, 0])
                                rot.normalize()
                                w, x, y, z = rot
                                key.rotation = [-x, -z, -y, w]

                            elif len(key.rotation) == 3:
                                rot = mathutils.Euler(key.rotation or [0, 0, 0], 'XYZ')
                                w, x, y, z = rot.to_quaternion().normalized()
                                key.rotation = [-x, -z, -y, w]

                            x, y, z = key.scale or [1, 1, 1]
                            key.scale = [x, z, y]

                            anim.frames[frame].append(key)

        for item in bpy.data.objects:
            if item.type != 'MESH' and item.htatools.object_type == 'CONVEX':
                continue
            if item.htatools.object_type != 'DEFAULT':
                continue

            if item.parent:
                provider.nodes[item.name].parent = provider.nodes.index(item.parent.name)

        for item in bpy.data.objects:
            if item.type != 'MESH' and item.htatools.object_type == 'CONVEX':
                continue

            group_name = 'Main'
            if item.users_collection[0] is not bpy.context.scene.collection:
                group_name = item.users_collection[0].name

            if item.htatools.object_type == 'COLLIDER':
                collision = htaparser.Collision()
                x, y, z = item.location
                collision.location = [x, z, y]


                if item.rotation_mode == 'QUATERNION':
                    w, x, y, z = item.rotation_quaternion

                if item.rotation_mode == 'XYZ':
                    w, x, y, z = item.rotation_euler.to_quaternion().normalized()

                collision.rotation = [-x, -z, -y, w]

                collision.type = int(item.htatools.collider_type)
                x, y, z = item.scale
                if collision.type == 0:
                    collision.scale = [x, z, y]

                elif collision.type == 1:
                    collision.scale = [x, x, x]

                elif collision.type == 2:
                    collision.scale = [x, z, y]

                provider.collisions.items.append(collision)

            if item.htatools.object_type == 'CONVEX':
                data = item.data.copy()

                bm = bmesh.new()
                bm.from_mesh(data)
                bmesh.ops.triangulate(bm, faces=bm.faces[:])
                bm.to_mesh(data)
                bm.free()

                verts = dict()

                for face in data.polygons:
                    vertexes = [face.vertices[0], face.vertices[1], face.vertices[2],]
                    provider.convex.indices.append(vertexes[::-1])

                    for loop_id, vert_id in zip(face.loop_indices, vertexes):
                        if vert_id in verts:
                            continue

                        px, py, pz = data.vertices[vert_id].co
                        verts[vert_id] = [px, pz, py]

                order = list(verts.keys())
                order.sort()
                for vert_id in order:
                    provider.convex.vertices.append(verts[vert_id])

                bpy.data.meshes.remove(data)

            if item.type == 'MESH' and item.htatools.object_type == 'DEFAULT':
                for num, material in enumerate(item.data.materials):
                    mtl = htaparser.Material(provider)
                    mtl.name = material.name
                    mtl.shader = material.htatools.shader_name

                    for type_num, type_name in enumerate(TEXTURE_TYPES):
                        if type_name in material.node_tree.nodes:
                            pointer = material.node_tree.nodes[type_name]

                            if self.export_images and not pointer.image.name.endswith('tga'):
                                pointer.image.name = pointer.image.name.replace('.dds', '.tga')

                            texture = htaparser.Texture()
                            texture.filename = pointer.image.name
                            texture.type = type_num

                            texture.uv = 0
                            if pointer.inputs and pointer.inputs[0].links:
                                uvnode = pointer.inputs[0].links[0].from_node
                                texture.uv = item.data.uv_layers.keys().index(uvnode.uv_map)

                            if self.export_images:
                                tex_path = os.path.join(model_directory, pointer.image.name)

                                if pointer.image.file_format != 'TARGA':
                                    pointer.image.file_format = 'TARGA'

                                pointer.image.filepath_raw = tex_path
                                pointer.image.save()

                            mtl.textures.append(texture)

                    provider.skins.set_skin(num, mtl)


                mesh = htaparser.Mesh(provider)
                mesh.name = item.data.name
                mesh.type = int(item.htatools.draw_mode)

                mesh.parent = provider.nodes.index(item.name)
                mesh.group = provider.groups.index(group_name)

                skins = list(provider.skins[0].keys())

                if item.data.materials and item.data.materials[0].name in skins:
                    material_index = list(provider.skins[0].keys()).index(item.data.materials[0].name)

                else:
                    material_index = -1

                mesh.material = material_index
                mesh.vertex_type = int(item.htatools.vertex_type)

                data = item.data.copy()

                bm = bmesh.new()
                bm.from_mesh(data)
                bmesh.ops.triangulate(bm, faces=bm.faces[:])
                seams = [edge for edge in bm.edges if edge.seam or not edge.smooth]
                bmesh.ops.split_edges(bm, edges=seams)
                bm.to_mesh(data)
                bm.free()

                data.calc_tangents()

                verts = dict()
                local = dict()

                uv_layers = data.uv_layers
                uv_names = list(data.uv_layers.keys())

                for face in data.polygons:
                    vertexes = [face.vertices[0], face.vertices[1], face.vertices[2],]
                    mesh.indices.append(vertexes[::-1])

                    for loop_id, vert_id in zip(face.loop_indices, vertexes):
                        if vert_id in verts:
                            continue

                        vert = data.vertices[vert_id]

                        _data = htaparser.Vertex()

                        tx, ty, tz = data.loops[loop_id].tangent
                        tw = data.loops[loop_id].bitangent_sign
                        _data.tangent = [tx, tz, ty, tw]

                        if len(uv_names) >= 1:
                            layer = uv_layers[uv_names[0]]
                            ux, uy = layer.data[loop_id].uv
                            _data.uv0 = [ux, 1 - uy]

                        if len(uv_names) >= 2:
                            layer = uv_layers[uv_names[1]]
                            ux, uy = layer.data[loop_id].uv
                            _data.uv1 = [ux, 1 - uy]

                        if len(uv_names) >= 3:
                            layer = uv_layers[uv_names[2]]
                            ux, uy = layer.data[loop_id].uv
                            _data.uv2 = [ux, 1 - uy]

                        if 'color' in data.vertex_colors:
                            layer = data.vertex_colors['color']
                            color = list(layer.data[loop_id].color)
                            r, g, b, a = [int(v * 255) for v in color]
                            _data.color = [r, g, b, a]

                        px, py, pz = vert.co
                        nx, ny, nz = data.loops[loop_id].normal

                        _data.location = [px, pz, py]
                        _data.normal = [nx, nz, ny]

                        local[vert_id] = _data.copy

                        if mesh.type == 4:
                            px, py, pz = item.matrix_world @ vert.co
                            nx, ny, nz, _ = item.matrix_world @ mathutils.Vector([nx, ny, nz, 0.0])

                            _data.location = [px, pz, py]
                            _data.normal = [nx, nz, ny]

                        verts[vert_id] = _data

                        provider.meshes.bvh_min[0] = min(provider.meshes.bvh_min[0], px)
                        provider.meshes.bvh_min[1] = min(provider.meshes.bvh_min[1], pz)
                        provider.meshes.bvh_min[2] = min(provider.meshes.bvh_min[2], py)

                        provider.meshes.bvh_max[0] = max(provider.meshes.bvh_max[0], px)
                        provider.meshes.bvh_max[1] = max(provider.meshes.bvh_max[1], pz)
                        provider.meshes.bvh_max[2] = max(provider.meshes.bvh_max[2], py)

                order = list(verts.keys())
                order.sort()
                for vert_id in order:
                    mesh.vertices.append(verts[vert_id])

                order = list(local.keys())
                order.sort()
                for vert_id in order:
                    mesh.doubles.append(local[vert_id])

                bpy.data.meshes.remove(data)
                provider.meshes.items[mesh.name] = mesh

                group = provider.groups[group_name]
                mesh_index = provider.meshes.index(mesh.name)
                group.nodes.append(mesh_index)
                group.add_variant(item.htatools.variant, mesh_index)

        version = '%i.%i.%i' % bl_info['version']
        provider.generator.value += f' HTATools: {version}'
        provider.sign.value = preferences.model_sign

        with open(self.filepath, 'wb') as stream:
            provider.dump(stream)

        del provider

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(HTAImport.bl_idname, text=HTAImport.bl_label)


def menu_func_export(self, context):
    self.layout.operator(HTAExport.bl_idname, text=HTAExport.bl_label)


def register():
    bpy.utils.register_class(HTAObject)
    bpy.types.Object.htatools = bpy.props.PointerProperty(type=HTAObject)
    bpy.utils.register_class(HTAObjectPanel)

    bpy.utils.register_class(HTAMaterial)
    bpy.types.Material.htatools = bpy.props.PointerProperty(type=HTAMaterial)
    bpy.utils.register_class(HTAMaterialPanel)

    bpy.utils.register_class(HTAImport)
    bpy.utils.register_class(HTAExport)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(HTAObject)
    bpy.utils.unregister_class(HTAObjectPanel)

    bpy.utils.unregister_class(HTAMaterial)
    bpy.utils.unregister_class(HTAMaterialPanel)

    bpy.utils.unregister_class(HTAImport)
    bpy.utils.unregister_class(HTAExport)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
