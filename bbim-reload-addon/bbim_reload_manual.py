import bpy
import importlib
import inspect

reregister_modules = ["blenderbim.bim.module.demo.ui"]


for module_name in reregister_modules:
    module = importlib.import_module(module_name)
    # retrieving registered classes with inspect
    classes = [n for n, c in inspect.getmembers(module, inspect.isclass) 
               if hasattr(c, 'is_registered') and c.is_registered]
    print(classes)
    
    for class_obj in classes:
        class_obj = getattr(module, class_name)
        bpy.utils.unregister_class(class_obj)

    importlib.reload(module)

    for class_obj in classes:
        class_obj = getattr(module, class_name)
        bpy.utils.register_class(class_obj)