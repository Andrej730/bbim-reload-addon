import bpy
import importlib
import inspect
import pkgutil

reregister_modules = ["blenderbim.bim.module"]

def reregister_modules_recursive(module_name):
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
            modules = [module_name +'.'+ o.name for o in pkgutil.iter_modules(module.__path__)]
            print('module has summodules:')
            for module_name in modules:
                reregister_modules_recursive(module_name)
    except Exception as e:        
        print('**some errors have occurred in ', module_name, e)

for module_name in reregister_modules:                   
    print('-'*60)
    print('Reregistering utility')
    
    reregister_modules_recursive(module_name)
    print('done')
    print('-'*60)
    
