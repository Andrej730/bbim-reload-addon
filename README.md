# bbim-reload-addon
 A add-on to help reloading BlenderBIM modules while developping inside blender
 Based on a snippet by Andrej730 (see https://community.osarch.org/discussion/comment/19395#Comment_19395)

*bbim_reload_manual.py*: you need to open the file in the blender text editor 
replace ["blenderbim.bim.module.demo.ui"] by (a list) of module(s) you are working on, and execute the script within blender (this will reload all the classes that are registered in the module) 

*bbim_reload_recursive.py*: you also need to open the file in the blender editor. 
replace ["blenderbim.bim.module.demo"] by the module you are working on and execute (this will reload all the classes in module and parse also submodules if there's any) 

*bbim-reload-addon.py* is meant to work as the recursive one but you need to install it as an add-on in Blender.
It provides a panel with a text input where you can specify a comma separated list of bbim modules you want to reregister and you need to click on the button to actually do it. 

![image](https://github.com/bdamay/bbim-reload-addon/assets/16347726/fc9b8979-3d27-4449-8057-198522007ebb)

Beware as each entry is a starting point for recursive reload. (i experienced strange errors and behavior with the root module package of bbim, you may have a clue on a way it could be solved?). 



