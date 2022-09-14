import bpy
import bpy.types
import bpy.props


class HTA_PT_ShaderNode(bpy.types.Panel):
    bl_idname      = 'HTA_PT_ShaderNode'
    bl_label       = 'HTA Texture'
    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category    = 'Node'

    @classmethod
    def poll(self, context) -> bool:
        return context.area.ui_type == 'ShaderNodeTree' \
           and hasattr(context.active_node, 'hta') \
           and isinstance(context.active_node, bpy.types.ShaderNodeTexImage)

    def draw(self, context) -> None:
        self.layout.prop(context.active_node.hta, 'texture_type')


def register() -> None:
    bpy.utils.register_class(HTA_PT_ShaderNode)


def unregister() -> None:
    bpy.utils.unregister_class(HTA_PT_ShaderNode)
