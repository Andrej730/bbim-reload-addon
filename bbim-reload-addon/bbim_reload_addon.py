bl_info = {
    "name": "BBIM reload",
    "author": "bdamay",
    "version": (0, 1),
    "blender": (4,0,2),
    "location": "File Menu",
    "description": "Reload bbim classes",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"
}

import bpy
import importlib
from datetime import datetime 
import inspect
import pkgutil


class BBIM_reload(bpy.types.Operator):
    bl_idname = "wm.bbim_reload"
    bl_label = "Reload BBIM classes"
    bl_description = "BlenderBIM reload "
    bl_options = {'REGISTER'}

    # here's the name of upper level module (demo here but it could be module ? )
    module = 'blenderbim.bim.module.demo'

    def execute(self, context):                             
        print('-'*60)
        print('Reregistering BBIM utility')
        self.reregister_modules_recursive(self.module)
        print('done')
        print('-'*60)
        return {'FINISHED'}


    def reregister_modules_recursive(self,module_name):
        """ 
            This function parses module_name recursively 
            And reregister all registered classes that it can find     
            TODO some errors occurs (even in demo - find why and skip problems ?)
        """
        print('Module ', module_name)
        try: 
            module = importlib.import_module(module_name)
            # retrieving registered classes with inspect
            classes = [c for c, o in inspect.getmembers(module, inspect.isclass)
                    if hasattr(bpy.types, c)]
            # reregistering classes        
            for class_name in classes:
                class_obj = getattr(module, class_name)
                bpy.utils.unregister_class(class_obj)
            importlib.reload(module)
            for class_name in classes:
                print('Reregistering Class', class_name)
                class_obj = getattr(module, class_name)
                bpy.utils.register_class(class_obj)

            # in case there are submodules reregister them  
            # i use pkgutil cause for some reason inspect module brings also bpy as a sub module 
            if '__path__' in dir(module): # seems __path__ doesn't exist on last level  
                modules = [module_name +'.'+ o.name 
                           for o in pkgutil.iter_modules(module.__path__)]
                print('module has summodules:')
                for module_name in modules:
                    reregister_modules_recursive(module_name)
        except Exception as e:        
            print('*** Some errors have occurred in ', module_name, e)


def menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("wm.bbim_reload", text="Reload_BBIM", icon='PLUGIN')


def register():
    bpy.utils.register_class(BBIM_reload)
    bpy.types.TOPBAR_MT_file.append(menu_draw)


def unregister():
    bpy.utils.unregister_class(BBIM_reload)
    bpy.types.TOPBAR_MT_file.remove(menu_draw)


if __name__ == "__main__":
    register()
