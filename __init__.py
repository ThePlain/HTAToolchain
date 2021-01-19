import bpy
import bpy.props
import bpy.types
import bpy.utils
import bpy_extras.io_utils

from . import TargemImport
from . import TargemInterface


bl_info = {
    "name": "Targem Files Toolchain",
    "blender": (2, 80, 0),
    "category": 'Import-Export',
    "version": (1, 1, 17),
    "desctiption": "Import Targem files",
    "support": 'TESTING',
    "author": 'ThePlain (Alexander Fateev)',
}

def menu_func_import(self, context):
    self.layout.operator(
        TargemImport.ImportGAMFile.bl_idname,
        text=TargemImport.ImportGAMFile.bl_label
    )
    self.layout.operator(
        TargemImport.ImportSAMFile.bl_idname,
        text=TargemImport.ImportSAMFile.bl_label
    )

def register():
    bpy.utils.register_class(TargemInterface.HTAConfig)
    bpy.utils.register_class(TargemInterface.HTAObjectProperty)
    bpy.utils.register_class(TargemInterface.HTAObjectPanel)

    bpy.utils.register_class(TargemImport.ImportGAMFile)
    bpy.utils.register_class(TargemImport.ImportSAMFile)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    bpy.types.Object.hta_config = bpy.props.PointerProperty(type=TargemInterface.HTAObjectProperty)

def unregister():
    bpy.utils.unregister_class(TargemInterface.HTAConfig)
    bpy.utils.unregister_class(TargemInterface.HTAObjectProperty)
    bpy.utils.unregister_class(TargemInterface.HTAObjectPanel)

    bpy.utils.unregister_class(TargemImport.ImportGAMFile)
    bpy.utils.unregister_class(TargemImport.ImportSAMFile)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
