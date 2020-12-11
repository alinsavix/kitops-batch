import bpy
from . import utils
from .ops import OBJECT_MT_display_presets

class KitOpsBatchPanel(bpy.types.Panel):
    """KIT OPS Batch Panel"""
    bl_label = "KIT OPS BATCH"
    bl_idname = "OBJECT_PT_kit_ops_batch"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'BATCH'

    def draw(self, context):
        wm = bpy.context.window_manager
        props = utils.get_props()
        kob_mode = props.kob_mode

        layout = self.layout
        row = layout.row(align=True)
        row.prop_enum(props, "kob_mode", "0")
        row.prop_enum(props, "kob_mode", "1")
        row.prop_enum(props, "kob_mode", "2")

        line_width = 35
        buttons_hight = 1.5
        labels_hight = 0.7

        if kob_mode == "0":
            col = layout.column()

            sub = col.column()
            utils.wrap_text(sub, "Step 1: Open render.blend scene from KIT OPS BATCH folder", line_width)
            sub.scale_y = labels_hight

            col.operator("kob.kob_open_render_file")
            col.label(text= "")

            sub = col.column()
            utils.wrap_text(sub, "Step 2: Import an INSERT from the KPACK you want to batch thumbnail", line_width)
            sub.scale_y = labels_hight

            sub = col.column()
            sub.operator("kob.load_insert")
            sub.scale_y = buttons_hight

            row = col.row()
            row.label(text= props.kpack_folder)
            row.alignment ='CENTER'

            sub = col.column()
            utils.wrap_text(sub, "Step 3: Position camera and adjust lighting", line_width)
            sub.scale_y = labels_hight

            col.prop(props, "auto_camera_pos")

            sub = col.row()
            sub.prop(props, "camera_padding")
            if not props.auto_camera_pos:
                sub.enabled = False
            
            sub = col.column()
            sub.operator("kob.align_camera_to_insert")
            sub.scale_y = buttons_hight
            col.label(text= "")

            utils.wrap_text(col, "Step 4: Test the thumbnail render", line_width)

            sub = col.column()
            sub.operator("kob.test_thumb_render")
            sub.scale_y = buttons_hight
            # utils.wrap_text(col, "Step 5: When satisfied, delete the imported INSERT", line_width)
            col.label(text= "")

            sub = col.column()
            utils.wrap_text(sub, "Step 5: Batch render the entire KPACK folder of INSERTS", line_width)
            sub.scale_y = labels_hight

            sub = col.column()
            sub.operator("kob.batch_render_thumbs")
            sub.scale_y = buttons_hight

            row = layout.row()
            row.label(text="")
            row.operator("kob.view_log")
            row.scale_x =0.5
            row.operator("kob.kob_help", text="?")

        elif kob_mode == "2":
            col = layout.column()
            sub = col.column()
            sub.label(text= "")
            utils.wrap_text(sub, "Step 1: Choose folder of transparent PNG images", line_width)
            sub.scale_y = labels_hight
            
            col.prop(props, "images_folder", text= "")
            col.label(text= "")

            sub = col.column()
            utils.wrap_text(sub, "Step 2: Choose decal template file", line_width)
            sub.scale_y = labels_hight

            col.prop(props, "decal_temp_file", text= "")
            col.label(text= "")

            sub = col.column()
            utils.wrap_text(sub, "Step 3: Convert all decals to KIT OPS INSERTS", line_width)
            sub.scale_y = labels_hight
            sub.label(text= "")

            sub = col.column()
            sub.operator("kob.batch_convert_img")
            sub.scale_y = buttons_hight

            sub = col.column()
            sub.label(text= "")
            sub.scale_y = 10
        
            row = col.row()
            row.label(text= "")
            row.operator("kob.view_log_images")
            sub = row.column()
            sub.operator("kob.help")
            sub.scale_x = 0.5
            row.scale_y = 1.5


class ConvertOBJtoBlendPanel(bpy.types.Panel):
    """KIT OPS Batch Panel"""
    bl_label = "Convert OBJ to .blend"
    bl_idname = "OBJECT_PT_convert_to_blend"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'BATCH'

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        return props.kob_mode == "1"

    def draw(self, context):
        layout = self.layout
        line_width = 35
        buttons_hight = 1.5
        labels_hight = 0.7
        props = utils.get_props()

        col = layout.column()
        sub = col.column()
        utils.wrap_text(sub, "Step1: Use the import settings to properly import your OBJ. \
            Set it's scale and orientation. These import settings will now be used for batch operations.", line_width)
        sub.scale_y = labels_hight

        col.label(text= "")
        utils.wrap_text(col, "Step 2: Choose folder to import", line_width)
        col.prop(props, "obj_folder", text= "")
        col = layout.column()

        row = col.row(align= True)
        row.menu(OBJECT_MT_display_presets.__name__, text=OBJECT_MT_display_presets.bl_label)
        row.operator("kob.obj_display_preset_add", text= "", icon= 'ADD')
        op = row.operator("kob.obj_display_preset_add", text= "", icon= "REMOVE").remove_active = True

        col = layout.column()

        col = layout.column()
        utils.wrap_text(col, "Step 3: Configure import *", line_width)
        col.prop(props, "create_insert")
        col.prop(props, "center_n_set")
        col.prop(props, "clear_split_normals")
        col.label(text= "Material Override:")
        col.prop(props, "override_material", text= "")
        col = layout.column()

        col = layout.column()
        sub = col.column()
        utils.wrap_text(sub, "Step 4: Convert all OBJ files to .blend files based on settings.", line_width)
        sub.scale_y = labels_hight
        sub = col.column()
        sub.operator("kob.batch_convert_blend")
        sub.scale_y = buttons_hight

class ConvertBlendToOBJPanel(bpy.types.Panel):
    """KIT OPS Batch Panel"""
    bl_label = "Export .blend to OBJ"
    bl_idname = "OBJECT_PT_convert_to_obj"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'BATCH'

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        return props.kob_mode == "1"

    def draw(self, context):
        layout = self.layout
        line_width = 35
        buttons_hight = 1.5
        labels_hight = 0.7
        props = utils.get_props()

        col = layout.column()
        sub = col.column()
        utils.wrap_text(sub, "Convert each Blender objects or collections in this scene to a separate OBJ.", line_width)
        sub.scale_y = labels_hight
        col = layout.column()
        
        col = layout.column()
        row = col.row(align=True)
        row.prop_enum(props, "convert_mode", "0")
        row.prop_enum(props, "convert_mode", "1")

        col = layout.column()
        sub = col.column()
        sub.operator("kob.batch_convert_obj")
        sub.scale_y = buttons_hight

        col = layout.column()
        row = col.row()
        row.label(text="")
        row.operator("kob.help")
        # row.scale_y = buttons_hight


class ExportToBlendPanel(bpy.types.Panel):
    """KIT OPS Batch Panel"""
    bl_label = "EXPERIMENTAL"
    bl_idname = "OBJECT_PT_export_to_blend"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'BATCH'

    @classmethod
    def poll(cls, context):
        props = utils.get_props()
        prefs = bpy.context.preferences.addons['kitops-batch'].preferences
        return props.kob_mode == "1" and prefs.blend_export_enabled

    def draw(self, context):
        layout = self.layout
        line_width = 35
        buttons_hight = 1.5
        labels_hight = 0.7
        props = utils.get_props()

        col = layout.column()
        sub = col.column()
        utils.wrap_text(sub, "Convert each Blender object in this scene to an external blend file.", line_width)
        sub.scale_y = labels_hight
        col = layout.column()

        col = layout.column()
        col.operator("kob.batch_export_blend")
        col.scale_y = buttons_hight


class OBJExportSettingsPanel(bpy.types.Panel):
    """OBJ file export settings"""
    bl_label = "* OBJ Import Settings"
    bl_idname = "OBJECT_PT_obj_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category= 'BATCH'
    bl_parent_id = "OBJECT_PT_convert_to_blend"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        props = utils.get_props()
        col = layout.column()

        col.prop(props, "use_image_search")
        col.prop(props, "use_smooth_groups")
        col.prop(props, "use_edges")
        col.prop(props, "global_clight_size")
        col.prop(props, "axis_forward")
        col.prop(props, "axis_up")

        row = col.row(align= True)
        row.prop(props, "split_mode", expand=True)

        if props.split_mode == 'ON':
            col.prop(props, "use_split_objects", text="Split by Object")
            col.prop(props, "use_split_groups", text="Split by Group")
        else:
            col.prop(props, "use_groups_as_vgroups")


classes = (
    KitOpsBatchPanel,
    ConvertOBJtoBlendPanel,
    ConvertBlendToOBJPanel,
    ExportToBlendPanel,
    OBJExportSettingsPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)