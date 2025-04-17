# pyright: reportInvalidTypeForm=false

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
import collections
import inspect
from typing import TYPE_CHECKING, Any


class BBIM_OT_Reload(bpy.types.Operator):
    bl_idname = "bbim_reload.reload"
    bl_label = "BBIM Reload"
    bl_description = "Reload provided modules and reregister Blender classes if those modules have them."

    def reregister_modules_recursive(self, module_name: str) -> tuple[int, int]:
        """
        :return: A tuple of number of reloaded modules and classes.
        """
        # Start with 1 counting the current module.
        n_modules_reloaded = 1
        n_classes_reloaded = 0

        print("Module", module_name)
        module = importlib.import_module(module_name)
        # retrieving registered classes with inspect
        class_names = [(n, c) for n, c in inspect.getmembers(module, inspect.isclass)]
        # reregistering classes
        classes_dependencies = collections.defaultdict(set[type])
        classes_to_reload: list[tuple[str, type[Any]]] = []
        for cn, cl in class_names:
            if hasattr(cl, "is_registered"):
                if cl.is_registered and module_name == cl.__module__:
                    classes_to_reload.append((cn, cl))

                    # Figure out class dependencies - when one prop group is using another,
                    # so the latter should be reregistered first.
                    for property in cl.__annotations__.values():
                        # Skin usual annotations unrelated to Blender.
                        if type(property).__name__ != "_PropertyDeferred":
                            continue
                        if property.function.__name__ != "CollectionProperty":
                            continue
                        dependency = property.keywords["type"]
                        if dependency.__module__ != module_name:
                            continue
                        classes_dependencies[cl].add(dependency)

        importlib.reload(module)
        classes_to_reload = sorted(classes_to_reload, key=lambda x: len(classes_dependencies[x[1]]))
        while classes_to_reload:
            resolved_dependencies = set()
            for cl_data in classes_to_reload[:]:
                cn, cl = cl_data
                if classes_dependencies[cl]:
                    continue
                # Save dependency before we reload it.
                resolved_dependencies.add(cl)

                bpy.utils.unregister_class(cl)
                cl = getattr(module, cn)
                bpy.utils.register_class(cl)
                print("- Registered Class", cn)
                n_classes_reloaded += 1
                classes_to_reload.remove(cl_data)

            for dependencies in classes_dependencies.values():
                if not dependencies:
                    continue
                dependencies.difference_update(resolved_dependencies)

            # Just to be safe but this shouldn't occur.
            if not resolved_dependencies:
                classes_str = ", ".join([cn for cn, cl in classes_to_reload])
                raise Exception(
                    f"Failed to reload all available classes in the module. Classes left to reload: {classes_str}"
                )

        sub_modules: list[str] = []
        for n, sm in inspect.getmembers(module, inspect.ismodule):
            # We should avoid reparsing upper modules here. so check if sub module contains module name
            if sm.__name__.startswith(f"{module_name}."):
                sub_modules.append(sm.__name__)

        for sub_module_name in sub_modules:
            n_modules_reloaded_, n_classes_reloaded_ = self.reregister_modules_recursive(sub_module_name)
            n_modules_reloaded += n_modules_reloaded_
            n_classes_reloaded = n_classes_reloaded_

        return n_modules_reloaded, n_classes_reloaded

    def execute(self, context):
        prefs = get_preferences(context)
        print("-" * 60)  # i'm printing but might be better to do logging.
        print("Reregistering BBIM utility")

        n_classes = 0
        n_modules = 0
        for module in prefs.modules:
            if not module.is_active:
                continue
            module_name = module.name.strip()
            n_modules_, n_classes_ = self.reregister_modules_recursive(module_name)
            n_modules += n_modules_
            n_classes += n_classes_

        print("done")
        print("-" * 60)
        self.report({"INFO"}, f"{n_modules} modules and {n_classes} classes were reloaded.")
        return {"FINISHED"}


def update_btn_remove_module(self: "Module", context: bpy.types.Context) -> None:
    prefs = get_preferences(context)
    i = next(i for i, module in enumerate(prefs.modules) if module == self)
    prefs.modules.remove(i)


class Module(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Python Module to Reload",
        description="Note that all it's submodules will be reloaded too, recursively.",
        default="bonsai.bim.module",
    )
    btn_remove_module: bpy.props.BoolProperty(name="Remove Selected Module", update=update_btn_remove_module)
    is_active: bpy.props.BoolProperty(
        name="Is Module Active",
        description="If module is not active, it will be skipped from the reload",
        default=True,
    )

    if TYPE_CHECKING:
        name: str
        btn_remove_module: bool
        is_active: bool


def update_btn_reload_bbim_reload(self: "BBIMReloadPreferences", context: bpy.types.Context) -> None:
    preferences = get_preferences(context)
    saved_modules = [dict(m) for m in preferences.modules]
    bpy.ops.preferences.addon_disable(module=__name__)
    bpy.ops.preferences.addon_enable(module=__name__)

    # Collection prop is reset after addon reload.
    # EGet new preferences, previous instance is broken after reload.
    new_preferences = get_preferences(context)
    for module_dict in saved_modules:
        module = new_preferences.modules.add()
        for key, value in module_dict.items():
            setattr(module, key, value)


def update_btn_add_new_module(self: "BBIMReloadPreferences", context: bpy.types.Context) -> None:
    set_name = self.modules[-1].name.strip() if self.modules else ""
    module = self.modules.add()
    # Duplicate name from last module if it's available.
    if set_name:
        module.name = set_name
    del self["btn_add_new_module"]


class BBIMReloadPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Using update callbacks as operators are more cumbersome.
    modules: bpy.props.CollectionProperty(type=Module)
    btn_reload_bbim_reload: bpy.props.BoolProperty(
        name="Reload BBIM Reload Addon Itself", update=update_btn_reload_bbim_reload
    )
    btn_add_new_module: bpy.props.BoolProperty(name="Add new module entry.", update=update_btn_add_new_module)
    # basename: bpy.props.StringProperty(name="Basename", default="bonsai.bim.module")
    # module: bpy.props.StringProperty(
    #     name="Module", description="Comma separated list of modules to reload", default="project.operator"
    # )

    if TYPE_CHECKING:
        modules: bpy.types.bpy_prop_collection_idprop[Module]
        btn_add_new_module: bool
        btn_reload_bbim_reload: bool


class BBIM_PT_Reload(bpy.types.Panel):
    bl_idname = "BBIM_PT_Reload"
    bl_label = "Reload BBIM classes"
    bl_description = "Bonsai reload "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        assert layout
        prefs = get_preferences(context)

        row = layout.row()
        left_row = row.row()
        left_row.alignment = "LEFT"
        left_row.operator(BBIM_OT_Reload.bl_idname, text="Reload", icon="FILE_REFRESH")

        right_row = row.row(align=True)
        right_row.alignment = "RIGHT"
        right_row.prop(prefs, "btn_add_new_module", text="", icon="ADD")
        right_row.prop(prefs, "btn_reload_bbim_reload", text="", icon="TOOL_SETTINGS")

        if prefs.modules:
            layout.label(text="Modules to Reload:")
        for module in prefs.modules:
            row = layout.row(align=True)
            row.prop(module, "name", text="")
            icon = "RADIOBUT_ON" if module.is_active else "RADIOBUT_OFF"
            row.prop(module, "is_active", text="", icon=icon, invert_checkbox=True)
            row.prop(module, "btn_remove_module", text="", icon="X")


def get_preferences(context: bpy.types.Context) -> "BBIMReloadPreferences":
    assert context.preferences
    addon_prefs = context.preferences.addons[__name__].preferences
    assert isinstance(addon_prefs, BBIMReloadPreferences)
    return addon_prefs


classes = (
    Module,
    BBIMReloadPreferences,
    BBIM_OT_Reload,
    BBIM_PT_Reload,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
