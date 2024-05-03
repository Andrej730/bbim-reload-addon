import bpy
import importlib
import inspect

reregister_modules = ["blenderbim.bim.module.demo"]

def reregister_modules_recursive(module_name, level=0):
    print(f"{'-'*level}Module {module_name}")
    level += 1
    module = importlib.import_module(module_name)
    # retrieving registered classes with inspect
    class_names = [n for n, c in inspect.getmembers(module, inspect.isclass)] 
    # reregistering classes        
    for cn in class_names:          
        cl = getattr(module, cn) 
        if hasattr(cl, 'is_registered'):
            if  cl.is_registered and module_name == cl.__module__: 
#                print('unregistering Class', cn)
                bpy.utils.unregister_class(cl)
#                print('reloading ', module)
                importlib.reload(module)
                print('-' * level, 'Reregistering Class', cn)
                cl = getattr(module, cn)
                bpy.utils.register_class(cl)

    sub_modules=[]
    for n, sm in inspect.getmembers(module, inspect.ismodule): 
        # We should avoid reparsing upper modules here. so check if sub module contains module name 
        if module_name in sm.__name__:                           
            sub_modules.append(sm.__name__) 
            
    for module_name in sub_modules:          
        self.reregister_modules_recursive(module_name)
            


for module_name in reregister_modules:                   
    print('-'*60)
    print('Reregistering utility')
    reregister_modules_recursive(module_name)
    print('done')
    print('-'*60)
    
