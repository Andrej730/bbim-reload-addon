bl_info = {
    "name": "BBIM reload",
    "author": "bdamay",
    "version": (0, 1),
    "blender": (4, 0, 2),
    "location": "Scene Panel ",
    "description": "Reload bbim classes",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development",
}

import bpy
import importlib
from datetime import datetime
import inspect
import pkgutil


from bpy.props import (
    StringProperty,
    PointerProperty,
)
from bpy.types import (
    PropertyGroup
)

class BBIM_OT_Reload(bpy.types.Operator):
    """ 
    Reload modules from starting point provided by the string property  module 
    """ 
    bl_idname = 'bbim.bbim_ot_reload'
    bl_label = "Reload Classes from modules"
    
    def reregister_modules_recursive(self, module_name: str) -> int:
        n_reloaded = 0

        print('Module', module_name)
        module = importlib.import_module(module_name)
        # retrieving registered classes with inspect
        class_names = [(n, c) for n, c in inspect.getmembers(module, inspect.isclass)]
        # reregistering classes
        classes_to_reload = []
        for cn, cl in class_names:
            if hasattr(cl, 'is_registered'):
                if cl.is_registered and module_name == cl.__module__:
                    classes_to_reload.append((cn, cl))

        importlib.reload(module)
        for cn, cl in classes_to_reload:
            bpy.utils.unregister_class(cl)
            cl = getattr(module, cn)
            bpy.utils.register_class(cl)
            print('- Registered Class', cn)
            n_reloaded += 1

        sub_modules=[]
        for n, sm in inspect.getmembers(module, inspect.ismodule):
            # We should avoid reparsing upper modules here. so check if sub module contains module name
            if module_name in sm.__name__:
                sub_modules.append(sm.__name__)

        for sub_module_name in sub_modules:
            n_reloaded+=self.reregister_modules_recursive(sub_module_name)

        return n_reloaded

    def execute(self, context):
        self.props = context.scene.BBIMReloadProperties            
        print("-" * 60)# i'm printing but might be better to do logging.
        print("Reregistering BBIM utility")
        n = self.reregister_modules_recursive(self.props.basename+'.'+self.props.module)
        print("done")
        print("-" * 60)
        self.report({"INFO"}, f"{n} classes were reloaded.")
        return {"FINISHED"}


class BBIMReloadProperties(PropertyGroup):
    # This property is a string, where we can list modules comma separated...
    # Starting with bbim  module
    basename: StringProperty(name="Basename", default="blenderbim.bim.module")
    module: StringProperty(name="Module", default="project.operator")


class BBIM_PT_Reload(bpy.types.Panel):
    bl_idname = 'BBIM_PT_Reload'
    bl_label = "Reload BBIM classes"
    bl_description = "BlenderBIM reload "
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        self.props = context.scene.BBIMReloadProperties

        scene = context.scene

        # Create a simple row.
        row = layout.row()
        row.prop(self.props, 'basename')
        row = layout.row()
        row.prop(self.props, 'module')
        row = layout.row()
        row.scale_y = 1.0
        row.operator("bbim.bbim_ot_reload")
     


def register():    

    bpy.utils.register_class(BBIMReloadProperties) 
    # Seems i have to register this class before using Pointer Property  -- ? 
    bpy.types.Scene.BBIMReloadProperties = bpy.props.PointerProperty(type=BBIMReloadProperties)
    bpy.utils.register_class(BBIM_OT_Reload)
    bpy.utils.register_class(BBIM_PT_Reload)


def unregister():
    bpy.utils.unregister_class(BBIM_PT_Reload)
    bpy.utils.unregister_class(BBIM_OT_Reload)
    bpy.utils.unregister_class(BBIMReloadProperties)
    del bpy.types.Scene.BBIMReloadProperties


if __name__ == "__main__":
    register()
