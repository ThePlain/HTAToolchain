import bpy
import bpy.props


VERTEX_TYPE_PROP = {
    ('None', 'Preset', ''),
    ('XYZ', '(Position, )', ''),
    ('XYZT1', '(Position, UV, )', ''),
    ('XYZC', '(Position, Color, )', ''),
    ('XYZWC', '(Position, Color, )', ''),
    ('XYZWCT1', '(Position, Color, UV, )', ''),
    ('XYZNC', '(Position, Normal, Color, )', ''),
    ('XYZCT1', '(Position, Color, UV, )', ''),
    ('XYZNT1', '(Position, Normal, UV, )', ''),
    ('XYZNCT1', '(Position, Normal, Color, UV, )', ''),
    ('XYZNCT2', '(Position, Normal, Color, UV, UV, )', ''),
    ('XYZNT2', '(Position, Normal, UV, )', ''),
    ('XYZNT3', '(Position, Normal, UV, UV, UV, )', ''),
    ('XYZCT1_UVW', '(Position, Color, UVW, )', ''),
    ('XYZCT2_UVW', '(Position, Color, UVW, UV, )', ''),
    ('XYZCT2', '(Position, Color, UV, UV, )', ''),
    ('XYZNT1T', '(Position, Normal, UV, Tangent, )', ''),
    ('XYZNCT1T', '(Position, Normal, Color, UV, Tangent, )', ''),
}


class HTAConfig(bpy.types.AddonPreferences):
    bl_idname = __package__

    data_path: bpy.props.StringProperty(
        name='Game data folder',
        subtype='DIR_PATH',
    )

    game_type: bpy.props.EnumProperty(
        name='Default game version',
        items={
            ('hta', 'Hard Truck Apocalypse', ''),
            ('113', 'Hard Truck Apocalypse: Rise of Clans', ''),
        },
        default='hta',
        description='Default game version.'
    )

    vertex_type: bpy.props.EnumProperty(
        name='Mesh vertex type',
        items=VERTEX_TYPE_PROP,
        default='XYZNCT1T',
        description='Default vertex format for mesh'
    )

    animation_type: bpy.props.EnumProperty(
        name='Animation armature type',
        items={
            ('emptyes', 'Empty based armature', ''),
            ('armature', 'Native blender armature(In progress)', 'Currently unavailble'),
        },
        default='emptyes',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'game_type')
        layout.prop(self, 'data_path')
        layout.prop(self, 'vertex_type')
        layout.prop(self, 'animation_type')


class HTAObjectProperty(bpy.types.PropertyGroup):
    object_type: bpy.props.EnumProperty(
        name='Object Type',
        items={
            ('Mesh', 'Default', 'Default renderable mesh'),
            ('SColiider', 'Simple Collider', 'Primitive collider'),
            ('MColiider', 'Mesh Collider', 'Mesh based ob vertex data'),
        },
        default='Mesh',
    )

    vertex_type: bpy.props.EnumProperty(
        name='Mesh vertex type',
        items=VERTEX_TYPE_PROP,
        default='None',
        description='Vertex format for mesh'
    )


class HTAObjectPanel(bpy.types.Panel):
    bl_idname = 'hta.mesh_panel'
    bl_label = 'HTA Config'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        self.layout.prop(context.object.hta_config, 'object_type')
        self.layout.prop(context.object.hta_config, 'vertex_type')
