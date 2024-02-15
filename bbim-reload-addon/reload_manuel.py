
import bpy
import os, sys
import subprocess
import importlib
import inspect



def execute():
    
        
    reregister_modules = ["blenderbim.bim.module.demo.ui")
        
          
    
    for module_name, classes in reregister_classes.items():
        module = importlib.import_module(module_name)
        # retrieving registered classes with inspect
        classes = [c for c, o in ( ) if hasattr(bpy.types, c)]
        for class_name in classes:
            class_obj = getattr(module, class_name)
            bpy.utils.unregister_class(class_obj)

        importlib.reload(module)

        for class_name in classes:
            class_obj = getattr(module, class_name)
            bpy.utils.register_class(class_obj)

    return {'FINISHED'}



if __name__ == "__main__":
   execute()
