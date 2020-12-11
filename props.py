import bpy
from mathutils import Matrix
from .utils import get_props
import os

def get_ca_pa(self):
    return self.get("camera_padding", 0.0)
    
def set_ca_pa(self, value):
    old_value = self.get("camera_padding", 0.0)
    self["camera_padding"] = value

    diff = self["camera_padding"] - old_value
    loc = Matrix.Translation((0.0, 0.0, diff))
    bpy.context.scene.camera.matrix_basis @= loc
    print("finished")

def mode_update(self, context):
    # reset the log_file_created property
    props = get_props()
    props.log_file_created = False


class KOBPreferences(bpy.types.AddonPreferences):
    """The addon preferences"""
    bl_idname = __package__

    use_suffix: bpy.props.BoolProperty(
        name= "Auto adjust maps using suffix",
        description= "Use image texture name suffix to adjust material",
        default= False
    )

    color_suffix: bpy.props.StringProperty(
        name= "Color",
        description= "Color map suffix",
        default= "c"
    )

    metallic_suffix: bpy.props.StringProperty(
        name= "Metallic",
        description= "Metallic map suffix",
        default= "m"
    )

    specular_suffix: bpy.props.StringProperty(
        name= "Specular",
        description= "Specular map suffix",
        default= "s"
    )

    roughness_suffix: bpy.props.StringProperty(
        name= "Roughness",
        description= "Roughness map suffix",
        default= "r"
    )

    normal_suffix: bpy.props.StringProperty(
        name= "Normal",
        description= "Normal map suffix",
        default= "n"
    )

    bump_suffix: bpy.props.StringProperty(
        name= "Bump",
        description= "Bump map suffix",
        default= "b"
    )

    blend_export_enabled: bpy.props.BoolProperty(
        name= "Enable blend export secret mode",
        description= "Adds a new button in OBJ tab to export blend file objects to external blends",
        default= False
        )

    obj_default_scale: bpy.props.FloatProperty(
        name= "Exported OBJ default scale",
        description= "Default value for exported OBJs scale",
        default= 1,
        min= 0
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_suffix")
        layout.label(text= "OBJ texture map name suffix:")
        row = layout.row()
        col = row.column()
        col.prop(self, "color_suffix")
        col.prop(self, "metallic_suffix")
        col.prop(self, "specular_suffix")

        col = row.column()
        col.prop(self, "normal_suffix")
        col.prop(self, "roughness_suffix")
        col.prop(self, "bump_suffix")

        if not self.use_suffix:
            row.enabled = False

        col = layout.column()
        col.prop(self, "obj_default_scale")
        col.prop(self, "blend_export_enabled")


class KOBProps(bpy.types.PropertyGroup):
    kob_mode: bpy.props.EnumProperty(
        items=[
            ("0", "Thumbnails", "Thumbnails", '', 0),
            ("1", "OBJ", "OBJ", '', 1),
            ("2", "Decals", "Decals", 2)
        ],
        default='0',
        update= mode_update
    )

    kpack_folder: bpy.props.StringProperty(
        default=""
    )

    log_file_created: bpy.props.BoolProperty(
        default= False
    )

    batch_render_enabled: bpy.props.BoolProperty(
        default= False
    )

    auto_camera_pos: bpy.props.BoolProperty(
        name= "Auto camera position",
        description= "Enable camera auto alignment to insert",
        default= True
    )

    camera_padding: bpy.props.FloatProperty(
        name= "Camera padding",
        default= 0.0,
        min= -1.0,
        max= 1.0,
        get= get_ca_pa,
        set= set_ca_pa
    )

    obj_folder: bpy.props.StringProperty(
        name= "OBJ files folder",
        subtype= 'DIR_PATH'
    )

    create_insert: bpy.props.BoolProperty(
        name= "Create KIT OPS INSERT",
        default= True
    )

    center_n_set: bpy.props.BoolProperty(
        name= "Center XY and set on ground",
        default= True
    )

    clear_split_normals: bpy.props.BoolProperty(
        name= "Clear custom split normals",
        default= True
    )

    convert_mode: bpy.props.EnumProperty(
        items=[
            ("0", "Collections", "Collections", '', 0),
            ("1", "Objects", "Objects", '', 1)
        ],
        default='1'
    )

    override_material: bpy.props.PointerProperty(
        type= bpy.types.Material,
        name= "Material Override"
    )

    images_folder: bpy.props.StringProperty(
        name= "PNG Images Folder",
        description= "Transparent PNG Images Folder",
        subtype= 'DIR_PATH'
    )

    decal_temp_file: bpy.props.StringProperty(
        name= "Decals Template File",
        subtype= 'FILE_PATH',
        default= os.path.join(os.path.dirname(os.path.realpath(__file__)), "decaltemplates", "")
    )

    # some properties for the object export
    use_edges: bpy.props.BoolProperty(name= "Lines", default= False)
    use_smooth_groups: bpy.props.BoolProperty(name= "Smooth Groups", default= False)
    use_split_objects: bpy.props.BoolProperty(name= "Split by Object", default= False)
    use_split_groups: bpy.props.BoolProperty(name= "Split by Group", default= False)
    use_groups_as_vgroups: bpy.props.BoolProperty(name= "Poly Groups", default= False)
    use_image_search: bpy.props.BoolProperty(name= "Image Search", default= False)
    split_mode: bpy.props.EnumProperty(
        items=[
            ("ON", "Split", "Split geometry, omits unused verts"),
            ("OFF", "Keep Vert Order", "Keep vertex order from file")
        ],
        default='ON'
    )
    global_clight_size: bpy.props.FloatProperty(name= "Clamp Size", default= 0.0)
    axis_forward: bpy.props.EnumProperty(
        name= "Forward",
        items=[
            ("X", "X Forward", ""),
            ("Y", "Y Forward", ""),
            ("Z", "Z Forward", ""),
            ("-X", "-X Forward", ""),
            ("-Y", "-Y Forward", ""),
            ("-Z", "-Z Forward", "")
        ],
        default='Z'
    )
    axis_up: bpy.props.EnumProperty(
        name= "Up",
        items=[
            ("X", "X Up", ""),
            ("Y", "Y Up", ""),
            ("Z", "Z Up", ""),
            ("-X", "-X Up", ""),
            ("-Y", "-Y Up", ""),
            ("-Z", "-Z Up", "")
        ],
        default='X'
    )


classes = (
    KOBPreferences,
    KOBProps
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.kob = bpy.props.PointerProperty(type=KOBProps)
    bpy.types.Object.keep_object = bpy.props.BoolProperty(default= False)
    bpy.types.Collection.keep_collection = bpy.props.BoolProperty(default= False)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.kob
    del bpy.types.Object.keep_object
    del bpy.types.Collection.keep_collection
