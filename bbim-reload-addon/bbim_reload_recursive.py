import bpy
import importlib
import inspect
import pkgutil

reregister_modules = ["blenderbim.bim.module.demo"]

def reregister_modules_recursive(module_name):
    print('Module ', module_name)
    module = importlib.import_module(module_name)
    # retrieving registered classes with inspect
    classes = []
    for n, c in inspect.getmembers(module, inspect.isclass): 
        if hasattr(c, 'is_registered') and c.is_registered:
            print(c, c.is_registered)
            classes.append(c) 

    # reregistering classes        
    for c in classes:            
        try:
            print('unregistering Class', c)
            bpy.utils.unregister_class(c)
            print('Reregistering Class', c)
            bpy.utils.register_class(c)
        except:
            print('**some errors have occurred in classe ', c, e)
                
    importlib.reload(module)

#        if '__path__' in dir(module): # seems __path__ doesn't exist on last level  
#            modules = [module_name +'.'+ o.name for o in pkgutil.iter_modules(module.__path__)]
#            print('module has summodules:')

    sub_modules=[]
    for n, sm in inspect.getmembers(module, inspect.ismodule): 
        # We should avoid reparsing upper modules here. so check if sub module is a real submodule 
        if module_name in sm.__name__:                           
            sub_modules.append(sm.__name__) 
    for module_name in sub_modules:      
        print('reregistering sub module ', sm.__name__)      
        reregister_modules_recursive(module_name)
            


for module_name in reregister_modules:                   
    print('-'*60)
    print('Reregistering utility')
    
    reregister_modules_recursive(module_name)
    print('done')
    print('-'*60)
    
