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
    
    def reregister_modules_recursive(self, module_name):
        """
        This function parses module_name recursively
        And reregister all registered classes that it can find
        TODO some errors occurs (even in demo - actually print error and skip problems...)
        """
        print("Module ", module_name)
        try:
            module = importlib.import_module(module_name)
            # retrieving registered classes with inspect
            classes = [
                c
                for c, o in inspect.getmembers(module, inspect.isclass)
                if hasattr(bpy.types, c)
            ]
            # reregistering classes
            for class_name in classes:
                class_obj = getattr(module, class_name)
                bpy.utils.unregister_class(class_obj)
            importlib.reload(module)
            for class_name in classes:
                print("Reregistering Class", class_name)
                class_obj = getattr(module, class_name)
                bpy.utils.register_class(class_obj)

            # in case there are submodules reregister them
            # i use pkgutil cause for some reason inspect module brings also bpy as a sub module
            if "__path__" in dir(module):  # seems __path__ doesn't exist on last level
                modules = [
                    module_name + "." + o.name
                    for o in pkgutil.iter_modules(module.__path__)
                ]
                print("module has summodules:")
                for module_name in modules:
                    self.reregister_modules_recursive(module_name)

        except Exception as e:
            print("*** Some errors have occurred in ", module_name, e)

    def execute(self, context):
        self.props = context.scene.BBIMReloadProperties            
        print("-" * 60)# i'm printing but might be better to do logging.
        print("Reregistering BBIM utility")
        _modules = self.props.module
        print(_modules)
        for _module in _modules.split(','):
            _full_path = 'blenderbim.bim.module.' + _module
            self.reregister_modules_recursive(_full_path)
        print("done")
        print("-" * 60)
        return {"FINISHED"}


class BBIMReloadProperties(PropertyGroup):
    # This property is a string, where we can list modules comma separated...
    # Starting with bbim demo module 
    module: StringProperty(name="Modules", default="demo")


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
