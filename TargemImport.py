import os
import sys
import math

import bpy
import bpy.props
import bpy.types
import bpy.utils
import bpy_extras.io_utils

from mathutils import Vector, Quaternion, Matrix

from . import TargemParser


def load_targem_mode(filepath, game_type):
    directory = os.path.dirname(filepath)
    parser = TargemParser.Parser()
    parser.unpack(game_type, filepath)

    scene = bpy.context.scene
    content = bpy.data
    
    r180 = math.radians(180)

    # Instantiate bone list
    for bone_cfg in parser.nodes:
        bone_ptr = content.objects.new(bone_cfg.name, None)
        scene.collection.objects.link(bone_ptr)

    # Apply bone configuration
    for bone_cfg in parser.nodes:
        parent_cfg = parser.nodes[bone_cfg.parent]

        bone_ptr = content.objects[bone_cfg.name]

        parent_ptr = None
        if parent_cfg and bone_cfg.name != parent_cfg.name:
            parent_ptr = content.objects[parent_cfg.name]
            bone_ptr.parent = parent_ptr

        x, z, y = bone_cfg.location
        bone_ptr.location = (x, y, z)


        x, y, z, w = bone_cfg.rotation
        bone_ptr.rotation_mode = 'QUATERNION'
        bone_ptr.rotation_quaternion = Quaternion((w, -x, -z, -y))

        bpy.context.view_layer.update()

    # Create collections
    for group_cfg in parser.groups:
        group_ptr = content.collections.new(group_cfg.name)
        scene.collection.children.link(group_ptr)

    # Create materials
    for skin_num, skin_cfg in enumerate(parser.materials):
        for material_num, material_cfg in enumerate(skin_cfg):
            # Get name by first texture
            material_name = f'Material{material_num}(Skin{skin_num})'
            if material_cfg.textures:
                material_name = material_cfg.textures[0].file

            if material_name in content.materials:
                continue
            else:
                material_ptr = content.materials.new(material_name)
                material_cfg.handle = material_ptr

            material_ptr.use_nodes = True
            node_tree = material_ptr.node_tree
            bsdf_ptr = node_tree.nodes["Principled BSDF"]

            for texture_cfg in material_cfg.textures:
                try:
                    content.images.load(os.path.join(directory, texture_cfg.file), check_existing=True)
                except Exception:
                    continue

                image_node = node_tree.nodes.new('ShaderNodeTexImage')
                if texture_cfg.type == 0:
                    image_node.image = content.images[texture_cfg.file]
                    node_tree.links.new(bsdf_ptr.inputs['Base Color'], image_node.outputs['Color'])
                    node_tree.links.new(bsdf_ptr.inputs['Specular'], image_node.outputs['Alpha'])

                if texture_cfg.type == 1:
                    image_node.image = content.images[texture_cfg.file]
                    content.images[texture_cfg.file].colorspace_settings.name = 'Non-Color'

                    bump_ptr = node_tree.nodes.new('ShaderNodeNormalMap')

                    node_tree.links.new(bump_ptr.inputs['Color'], image_node.outputs['Color'])
                    node_tree.links.new(bsdf_ptr.inputs['Normal'], bump_ptr.outputs['Normal'])

    # Create mesh
    for mesh_cfg in parser.meshes:
        print(f'Generater mesh: {mesh_cfg.name}')

        group_cfg = parser.groups[mesh_cfg.group]
        parent_cfg = parser.nodes[mesh_cfg.parent]

        vertexes = []
        for vertex in mesh_cfg.vertexes:
            x, z, y = vertex.position
            vertexes.append([x, y, z])

        indices = []
        for indice in mesh_cfg.indices:
            i2, i1, i0 = indice
            indices.append([i0, i1, i2])

        mesh_ptr = content.meshes.new(mesh_cfg.name)
        mesh_ptr.from_pydata(vertexes, [], indices)

        for face in mesh_ptr.polygons:
            face.use_smooth = True

        tokenset = list(mesh_cfg.struct_vertexes.__annotations__.keys())
        for face in mesh_ptr.polygons:
            for vid, lid in zip(face.vertices, face.loop_indices):
                for token in tokenset:
                    if token == 'normal':
                        x, z, y = mesh_cfg.vertexes[vid].normal
                        mesh_ptr.loops[lid].normal = (-x, -y, -z)

                    if token.startswith('uv'):
                        if token not in mesh_ptr.uv_layers:
                            mesh_ptr.uv_layers.new(name=token)
                        uv_layer = mesh_ptr.uv_layers[token]
                        x, y, *_ = getattr(mesh_cfg.vertexes[vid], token)
                        uv_layer.data[lid].uv = (x, 1 - y)

                    if token == 'color':
                        if 'color' not in mesh_ptr.vertex_colors:
                            mesh_ptr.vertex_colors.new(name='color')

                        a, r, g, b = mesh_cfg.vertexes[vid].color
                        color_layer = mesh_ptr.vertex_colors['color']
                        color_layer.data[lid].color = (r / 255, g / 255, b / 255, a / 255)

        node_ptr = content.objects.new(mesh_cfg.name, mesh_ptr)

        if mesh_cfg.type == 2:
            for vid, influence in enumerate(mesh_cfg.influences):
                for aid in range(influence.count_bone):
                    aligh_cfg = influence.influences[aid]
                    bone_cfg = parser.nodes[aligh_cfg.bone]

                    if bone_cfg.name not in node_ptr.vertex_groups:
                        node_ptr.vertex_groups.new(name=bone_cfg.name)

                    node_ptr.vertex_groups[bone_cfg.name].add([vid], aligh_cfg.weight, 'ADD')

            for bone_name in node_ptr.vertex_groups.keys():
                hook_ptr = node_ptr.modifiers.new(bone_name, 'HOOK')
                hook_ptr.vertex_group = bone_name
                hook_ptr.object = bpy.data.objects[bone_name]
                hook_ptr.strength = 0.75
                hook_ptr.falloff_type = 'CONSTANT'


        if parent_cfg:
            parent_ptr = bpy.data.objects[parent_cfg.name]

            if group_cfg:
                group_ptr = content.collections[group_cfg.name]
            else:
                group_ptr = scene.collection

            group_ptr.objects.link(node_ptr)

            node_ptr.matrix_basis = parent_ptr.matrix_basis.inverted()

            if parent_ptr.name not in group_ptr.objects:
                group_ptr.objects.link(parent_ptr)

            node_ptr.parent = parent_ptr

        else:
            scene.collection.objects.link(node_ptr)

        for skin_cfg in parser.materials:
            material_cfg = skin_cfg[mesh_cfg.material]
            if material_cfg:
                mesh_ptr.materials.append(material_cfg.handle)

    # Apply animation
    for animation in parser.animations:
        targets = []
        for frame, frame_cfg in enumerate(animation.keyframes):
            for bone, key in enumerate(frame_cfg):
                bone = getattr(key, 'bone', bone)
                bone_cfg = parser.nodes[bone]
                bone_ptr = content.objects[bone_cfg.name]

                targets.append(bone_ptr)

                x, z, y = key.location
                bone_ptr.location = (x, y, z)
                
                x, y, z, w = key.rotation
                bone_ptr.rotation_quaternion = Quaternion((w, -x, -z, -y))

                bone_ptr.keyframe_insert(data_path='location', frame=frame)
                bone_ptr.keyframe_insert(data_path='rotation_quaternion', frame=frame)
                bone_ptr.animation_data.action.name = f'{animation.name}({bone_cfg.name})'

        for bone_ptr in targets:
            action = bone_ptr.animation_data.action
            if action:
                non_linear = bone_ptr.animation_data.nla_tracks.new()
                non_linear.name = action.name
                non_linear.strips.new(action.name, action.frame_range[0], action)

                bone_ptr.animation_data.action = None

    # Generate mesh collision
    if parser.mesh_collision:
        vertexes = []
        for vertex in parser.mesh_collision.vertexes:
            x, z, y = vertex
            vertexes.append([x, y, z])

        indices = []
        for indice in parser.mesh_collision.indices:
            i2, i1, i0 = indice
            indices.append([i0, i1, i2])

        mesh_ptr = content.meshes.new('MeshCollision')
        mesh_ptr.from_pydata(vertexes, [], indices)

        node_ptr = bpy.data.objects.new('MeshCollision', mesh_ptr)
        node_ptr.display_type = 'WIRE'

        scene.collection.objects.link(node_ptr)

    # Generate Simple Colliders
    for collision_cfg in parser.simple_collisions:
        collision_ptr = bpy.data.objects.new(collision_cfg.name, None)

        x, z, y = collision_cfg.location
        collision_ptr.location = (x, y, z)

        x, y, z, w = collision_cfg.rotation
        collision_ptr.rotation_mode = 'QUATERNION'
        collision_ptr.rotation_quaternion = (w, -x, -z, -y)

        if collision_cfg.type == 0:
            x, z, y = collision_cfg.size
            collision_ptr.scale = (x, y, z)
            collision_ptr.empty_display_type = 'CUBE'
            collision_ptr.empty_display_size = 0.5

        if collision_cfg.type == 1:
            x, y, z = collision_cfg.size
            collision_ptr.scale = (x, x, x)
            collision_ptr.empty_display_type = 'SPHERE'
            collision_ptr.empty_display_type = 0.5

        bpy.context.scene.collection.objects.link(collision_ptr)

    return {'FINISHED'}

class ImportGAMFile(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'hta.gam_import_model'
    bl_label = 'Import GAM Targem Model'
    filename_ext = '.gam'

    game_type: bpy.props.EnumProperty(
        name='Game version',
        items={
            ('hta', 'Hard Truck Apocalypse', ''),
            ('113', 'Hard Truck Apocalypse: Rise of Clans', ''),
        },
        default='hta',
    )

    filter_glob: bpy.props.StringProperty(
        default='*.gam',
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return load_targem_mode(self.filepath, self.game_type)

class ImportSAMFile(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'hta.sam_import_model'
    bl_label = 'Import SAM Targem Model'
    filename_ext = '.sam'

    game_type: bpy.props.EnumProperty(
        name='Game version',
        items={
            ('hta', 'Hard Truck Apocalypse', ''),
            ('113', 'Hard Truck Apocalypse: Rise of Clans', ''),
        },
        default='hta',
    )

    filter_glob: bpy.props.StringProperty(
        default='*.sam',
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return load_targem_mode(self.filepath, self.game_type)