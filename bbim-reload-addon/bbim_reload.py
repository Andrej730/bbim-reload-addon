bl_info = {
    "name": "BBIM reload",
    "author": "bdamay",
    "version": (0, 1),
    "blender": (4,0,0),
    "location": "File Menu",
    "description": "Reload bbim classes",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"
}

import bpy
import os, sys
import subprocess
import importlib


class BBIM_reload(bpy.types.Operator):
    bl_idname = "wm.bbim_reload"
    bl_label = "Reload BBIM classes"
    bl_description = "BlenderBIM reload "
    bl_options = {'REGISTER'}

    def execute(self, context):
        reregister_classes = {
            "blenderbim.bim.module.demo.ui": ("BIM_PT_demo", )
        }   
        print("reloading bbim recent files")
        for module_name, classes in reregister_classes.items():
            module = importlib.import_module(module_name)
            for class_name in classes:
                class_obj = getattr(module, class_name)
                bpy.utils.unregister_class(class_obj)

            importlib.reload(module)

            for class_name in classes:
                class_obj = getattr(module, class_name)
                bpy.utils.register_class(class_obj)

        return {'FINISHED'}


def menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("wm.bbim_reload", text="Reload_bbim", icon='PLUGIN')
    # layout.separator()
    # prefs = bpy.context.preferences
    # view = prefs.view
    # layout.prop(view, "use_save_prompt")


def register():
    bpy.utils.register_class(BBIM_reload)
    bpy.types.TOPBAR_MT_file.append(menu_draw)


def unregister():
    bpy.utils.unregister_class(BBIM_reload)
    bpy.types.TOPBAR_MT_file.remove(menu_draw)


if __name__ == "__main__":
    register()
