# bbim-reload-addon
 A add-on to help reloading BlenderBIM modules while developping inside blender
 Based on a snippet by Andrej730 (see https://community.osarch.org/discussion/comment/19395#Comment_19395)

with bbim_reload_manual.py you need to open the file in the blender text editor 
replace ["blenderbim.bim.module.demo.ui"] by (a list) of module(s) you are working on, and execute the script within blender (this will reload all the classes that are registered in the module) 

with bbim_reload_recursive.py you also need to open the file in the blender editor. 
replace ["blenderbim.bim.module.demo"] by the module you are working on and execute (this will reload all the classes in module and parse also submodules if there's any) 

bbim-reload-addon.py is meant to work as the recursive one but you need to install it as an add-on in Blender. It provides a bbim-reload entry in the file menu. 
But beware, the add-on is not working as i expect it actually it is stuck on demo module as you may get errors when speciying "blenderbim.bim.module" as the root module to inspect from. 
 
