import bpy
from bpy_extras.io_utils import ImportHelper
from bl_operators.presets import AddPresetBase
from .  import utils
import os
import sys

class OBJECT_OT_load_insert(bpy.types.Operator, ImportHelper):
    """Load INSERT"""
    bl_idname = "kob.load_insert"
    bl_label = "Load INSERT"
    bl_options = {'UNDO'}

    # filter to display only blend files in the file browser
    filter_glob: bpy.props.StringProperty(
        default= "*.blend",
        options= {'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if hasattr(bpy.context.window_manager, "kitops") and bpy.context.window_manager.kitops.pro:
            # if kit ops pro is installed and activated
            props = utils.get_props()
            props.kpack_folder = os.path.dirname(self.filepath)

            utils.append_all_objects(self, self.filepath)
            props.batch_render_enabled = False
            props.log_file_created = False
        else:
            self.report({'ERROR'}, "Please make sure KIT OPS Pro is installed and activated")
        return {'FINISHED'}
    

class OBJECT_OT_test_thumb_render(bpy.types.Operator):
    """Test thumb render"""
    bl_idname = "kob.test_thumb_render"
    bl_label = "Test Thumb Render"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        kpack_folder = props.kpack_folder
        return kpack_folder != ""

    def execute(self, context):
        props = utils.get_props()
        kpack_folder = props.kpack_folder

        utils.prepare_render()
        utils.render_inserts(False)
        utils.create_log_file(kpack_folder)

        props.batch_render_enabled = True
        print ("Thumb Tested")
        return {'FINISHED'}

class OBJECT_OT_batch_render_thumbs(bpy.types.Operator):
    """Batch render thumbs"""
    bl_idname = "kob.batch_render_thumbs"
    bl_label = "Batch Render Thumbs"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        return props.batch_render_enabled

    def execute(self, context):
        props = utils.get_props()
        kpack_folder = props.kpack_folder

        blend_files = utils.get_blends(kpack_folder)

        # cleaning up the viewport before batch rendering
        utils.clean_all_imported()

        for blend in blend_files:
            utils.append_all_objects(self, blend)
            utils.write_log_entry(kpack_folder, blend)
            utils.render_inserts(True, blend)
            utils.clean_all_imported()

        props.log_file_created = True
        utils.purge_orphan_data()
        print ("Batch render thumbs")
        return {'FINISHED'}

class OBJECT_OT_view_log(bpy.types.Operator):
    """View Log"""
    bl_idname = "kob.view_log"
    bl_label = "View Log"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        return props.log_file_created

    def execute(self, context):
        props = utils.get_props()
        kpack_folder = props.kpack_folder

        utils.open_log_file(kpack_folder)
        print ("view log")
        return {'FINISHED'}

class OBJECT_OT_kob_help(bpy.types.Operator):
    """Open the docs page in browser"""
    bl_idname = "kob.kob_help"
    bl_label = "Help"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.wm.url_open(url="https://docs.google.com/document/d/1J0gDERPU3SZCRsqoASGu4qlgz9lJMDto64ChnmwQJcE/edit")
        return {'FINISHED'}

class OBJECT_OT_open_render_blend(bpy.types.Operator):
    """Open render.blend file from KIT OPS BATCH folder"""
    bl_idname = "kob.kob_open_render_file"
    bl_label = "Open render.blend"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        render_blend = utils.get_render_blend(self)
        if render_blend:
            bpy.ops.wm.open_mainfile(filepath= render_blend)
        print ("Render.blend opened")
        return {'FINISHED'}

class OBJECT_OT_align_cam_to_insert(bpy.types.Operator):
    """Align active camera to INSERT"""
    bl_idname = "kob.align_camera_to_insert"
    bl_label = "Align Camera to INSERT"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        kpack_folder = props.kpack_folder
        return bool(bpy.context.scene.camera) and (kpack_folder != "")# making sure the scene has an active camera

    def execute(self, context):
        utils.align_camera_to_insert()
        bpy.context.scene.camera.select_set(True)
        bpy.ops.view3d.view_camera()
        
        print ("Camera aligned to insert")
        return {'FINISHED'} 

# ____________________________________________________
class OBJECT_MT_display_presets(bpy.types.Menu):
    # the object import presets menu
    bl_label = "OBJ Import Presets"
    preset_subdir = "obj_batch_import/import_scene.obj"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset

class AddPresetObjectDisplay(AddPresetBase, bpy.types.Operator):
    # The add/remove preset operator
    '''Import OBJ Display Preset'''
    bl_idname = "kob.obj_display_preset_add"
    bl_label = "Add Object Display Preset"
    preset_menu = "OBJECT_MT_display_presets"

    # variable used for all preset values
    preset_defines = [
        "op = bpy.context.window_manager.kob"
    ]

    # properties to store in the preset
    preset_values = [
        "op.use_edges",
        "op.use_smooth_groups",
        "op.use_split_objects",
        "op.use_split_groups",
        "op.use_groups_as_vgroups",
        "op.use_image_search",
        "op.split_mode",
        "op.global_clight_size",
        "op.axis_forward",
        "op.axis_up"
    ]

    # where to store the preset
    preset_subdir = "obj_batch_import/import_scene.obj"
# ____________________________________________________


class OBJECT_OT_batch_convert_to_blend(bpy.types.Operator):
    """Batch convert to blend files"""
    bl_idname = "kob.batch_convert_blend"
    bl_label = "Batch Convert to .blend"
    # bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        obj_folder = bpy.path.abspath(props.obj_folder)
        return os.path.exists(obj_folder)

    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)

    # def draw(self, context):
    #     layout = self.layout
    #     col = layout.column()
    #     row = col.row(align= True)
    #     row.menu(OBJECT_MT_display_presets.__name__, text=OBJECT_MT_display_presets.bl_label)
    #     row.operator("kob.obj_display_preset_add", text= "", icon= 'ZOOM_IN')
    #     op = row.operator("kob.obj_display_preset_add", text= "", icon= "ZOOM_OUT")
    #     op.remove_active = True
    #     # col.prop(self, "use_edges")


    def execute(self, context):
        props = utils.get_props()
        objs_folder = bpy.path.abspath(props.obj_folder)
        create_insert = props.create_insert
        center_n_set = props.center_n_set
        clear_split_normals = props.clear_split_normals
        prefs = bpy.context.preferences.addons['kitops-batch'].preferences

        # flag all existing objects to keep them when cleanup is performed
        for ob in bpy.data.objects:
            ob.keep_object = True

        new_scene = utils.copy_scene()
        new_scene.name = "Export"

        # import the objs
        objs = utils.get_objs(objs_folder)
        if objs:
            # imported_objects = []
            # if the directory contains OBJ files
            for ob in objs:
                imported_objects = utils.import_obj(ob)

                # apply transforms, assign origin to center bottom and reset transforms
                for ob in imported_objects:
                    print(ob.name)
                    ob.scale *= prefs.obj_default_scale
                    bpy.context.view_layer.update()
                    utils.apply_transforms(ob)
                    bpy.context.view_layer.update()
                    utils.origin_to_bottom(ob, center_n_set)
                    bpy.context.view_layer.update()
                    utils.reset_transforms(ob, center_n_set)
                    bpy.context.view_layer.update()
                    utils.clear_custom_split_normals(ob, clear_split_normals)

                    blend = utils.create_blend(objs_folder, ob, new_scene, self, create_insert)

            # after exporting all objs delete the scene and perform a cleanup
            bpy.data.scenes.remove(new_scene)
            utils.purge_orphan_data()
        else:
            self.report(type= {'ERROR'}, message="No OBJ files found")

        print ("Batch converted to blends")
        return {'FINISHED'}


class OBJECT_OT_batch_convert_to_obj(bpy.types.Operator):
    """Batch convert to OBJ files"""
    bl_idname = "kob.batch_convert_obj"
    bl_label = "Batch Convert to OBJ"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = utils.get_props()
        if bpy.data.is_saved:
            export_dir = utils.obj_export_path()

            # create a list of items to export (either collections or objects)
            if props.convert_mode == '1':
                export_list = bpy.context.scene.objects
            else:
                export_list = bpy.context.scene.collection.children

            if export_list:
                # if the export list is not empty
                for item in export_list:
                    utils.export_to_obj(item, export_dir)

            print ("Batch converted to OBJs")
        else:
            self.report(type= {'ERROR'}, message= "Please save current blend file first")
        return {'FINISHED'}

class OBJECT_OT_batch_convert_images(bpy.types.Operator):
    """Batch convert Images to INSERTS"""
    bl_idname = "kob.batch_convert_img"
    bl_label = "Batch Convert"
    # bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        temp_file_exists = os.path.isfile(props.decal_temp_file)
        return props.images_folder and temp_file_exists

    def execute(self, context):
        props = utils.get_props()
        images_folder = props.images_folder
        decal_temp_file = props.decal_temp_file
        decal_mat_name = "Batch DECAL"
        decal_object_name = "Batch DECAL"
        images = utils.get_pngs(images_folder)

        # create a new export scene
        new_scene = utils.copy_scene()
        new_scene.name = "Export"

        # load the decals material from the blend file
        utils.load_decal_mat(decal_temp_file, decal_mat_name)
        utils.load_decal_mod(decal_temp_file, decal_object_name)
        decal_template_ob = bpy.data.objects.get(decal_object_name)
        decal_modifiers = decal_template_ob.modifiers

        decal_objects = []
        for img in images:
            image_path = os.path.join(images_folder, img)
            bpy.data.images.load(image_path, check_existing= True)
            image = bpy.data.images.get(img)
            img_size = image.size
            decal_ob = utils.create_decal(img, img_size, decal_mat_name)
            utils.add_modifiers(decal_ob, decal_modifiers)
            decal_objects.append(decal_ob)

        # create log file
        utils.create_log_file(images_folder)

        for ob in decal_objects:
            # deactivating some cycles visibility options
            ob.cycles_visibility.glossy = False
            ob.cycles_visibility.shadow = False
            ob.cycles_visibility.diffuse = False
            
            blend = utils.create_blend(images_folder, ob, new_scene, self)
            utils.write_log_entry(images_folder, blend)

        # after exporting all objs delete the scene and perform a cleanup
        bpy.data.scenes.remove(new_scene)
        utils.purge_orphan_data()

        # set the property to True to enable the view log button
        props.log_file_created = True

        print("Batch converted images")
        return {'FINISHED'} 

class OBJECT_OT_help(bpy.types.Operator):
    """USER MANUAL"""
    bl_idname = "kob.help"
    bl_label = "?"

    def execute(self, context):
        bpy.ops.wm.url_open(url= "https://docs.google.com/document/d/1J0gDERPU3SZCRsqoASGu4qlgz9lJMDto64ChnmwQJcE/edit")
        return {'FINISHED'}

class OBJECT_OT_view_log_images(bpy.types.Operator):
    """View Log for Converted Images"""
    bl_idname = "kob.view_log_images"
    bl_label = "View Log"

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        return props.log_file_created

    def execute(self, context):
        props = utils.get_props()
        images_folder = bpy.path.abspath(props.images_folder)

        utils.open_log_file(images_folder)

        print("Log file opened")
        return {'FINISHED'}


class OBJECT_OT_batch_export_blend(bpy.types.Operator):
    """Batch export scene objects to blend files"""
    bl_idname = "kob.batch_export_blend"
    bl_label = "Batch Export Blend"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print("exporting to blend...")
        props = utils.get_props()
        objs_folder = bpy.path.abspath(props.obj_folder)
        create_insert = props.create_insert
        center_n_set = props.center_n_set
        clear_split_normals = props.clear_split_normals
        prefs = bpy.context.preferences.addons['kitops-batch'].preferences

        

        if bpy.data.is_saved:
            filepath = bpy.data.filepath
            directory = os.path.dirname(filepath)

            original_scene_name = context.scene.name
            new_scene = utils.copy_scene()
            new_scene.name = "Export"

            # this function works only for mesh objects with no parents
            to_export = [ob for ob in bpy.data.scenes[original_scene_name].objects if ob.type == 'MESH' and not ob.parent]

            for ob in to_export:
                print(ob.name)
                children = list(ob.children)
                objects_group = [ob] + children
                for ob_ in objects_group:
                    bpy.context.collection.objects.link(ob_)
                    utils.apply_transforms(ob_)
                    bpy.context.view_layer.update()
                    utils.origin_to_bottom(ob_, center_n_set)
                    bpy.context.view_layer.update()
                    utils.reset_transforms(ob_, center_n_set)
                    bpy.context.view_layer.update()
                    utils.clear_custom_split_normals(ob_, clear_split_normals)
                
                blend = utils.create_blend(directory, ob, new_scene, self, create_insert= create_insert, children= children)
            bpy.data.scenes.remove(new_scene)

        else:
            self.report(type= {'ERROR'}, message= "Please save current blend file first")
            return {'FINISHED'}

        return {'FINISHED'}

classes = (
    OBJECT_OT_load_insert,
    OBJECT_OT_test_thumb_render,
    OBJECT_OT_batch_render_thumbs,
    OBJECT_OT_view_log,
    OBJECT_OT_kob_help,
    OBJECT_OT_open_render_blend,
    OBJECT_OT_align_cam_to_insert,
    OBJECT_MT_display_presets,
    AddPresetObjectDisplay,
    OBJECT_OT_batch_convert_to_blend,
    OBJECT_OT_batch_convert_to_obj,
    OBJECT_OT_batch_convert_images,
    OBJECT_OT_help,
    OBJECT_OT_view_log_images,
    OBJECT_OT_batch_export_blend
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
