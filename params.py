import bpy
import bpy.types
import bpy.props

from . import consts


class HTA_PG_ShaderNode(bpy.types.PropertyGroup):
    def get_texture_type(self) -> int:
        value = bpy.context.active_node.label

        if value in consts.TEXTURE_TYPES:
            # Add one because enum contain additional type UNKNOWN for bad names
            return consts.TEXTURE_TYPES.index(value) + 1

        else:
            return 0

    def set_texture_type(self, value: int) -> None:
        # Sub one because enum contain additional type UNKNOWN for bad names
        value = consts.TEXTURE_TYPES[value - 1]

        bpy.context.active_node.name = value
        bpy.context.active_node.label = value

    texture_type: bpy.props.EnumProperty(
        name='Shader sampler',
        description='Select texture sampler for shader.',
        items=consts.TEXTURE_ENUM,
        get=get_texture_type,
        set=set_texture_type,)


def register() -> None:
    bpy.utils.register_class(HTA_PG_ShaderNode)
    bpy.types.ShaderNode.hta = bpy.props.PointerProperty(type=HTA_PG_ShaderNode)


def unregister() -> None:
    bpy.utils.unregister_class(HTA_PG_ShaderNode)
