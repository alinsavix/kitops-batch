import bpy
import os
import webbrowser
import textwrap
from mathutils import Matrix, Vector
import sys
import bmesh
import numpy as np

def get_props():
    """Get addon properties"""
    return bpy.context.window_manager.kob

def shade_flat(ob):
    """Flat shading the faces of an object"""
    if ob.type == 'MESH':
        mesh = ob.data

    for f in mesh.polygons:
        f.use_smooth = False
    
def append_all_objects(operator, blend_file_path):
    """Append all objects from blend file"""

    # assign "tmp" id to all existing objects before appending
    # for ob in bpy.data.objects:
    #     ob.kitops.id = "tmp"

    # with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
    #     data_to.objects = data_from.objects

    # for ob in data_to.objects:
    #     if ob is not None:
    #         bpy.context.collection.objects.link(ob)
    #         ob.kob_insert_object = True
    # return data_to.objects
    
    # assign a keep property to use it later for deleting imported objects
    for ob in bpy.data.objects:
        ob.keep_object = True
    
    for col in bpy.data.collections:
        col.keep_collection = True

    # import using the insert operator from KIT OPS
    kitops_pref = bpy.context.preferences.addons['kitops'].preferences
    kitops_pref.mode = 'SMART'

    # deselect everything, it's necessary to prevent the
    # need for mouse input upon insert import
    for ob in bpy.data.objects:
        ob.select_set(False)

    if "Floor" in [ob.name for ob in bpy.data.objects]:
        # assign the ground plane as a target object to insert main object
        target_obj = bpy.data.objects['Floor']

        # flat shading the floor object
        shade_flat(target_obj)

        # importing the insert
        bpy.ops.ko.add_insert('INVOKE_DEFAULT', location= blend_file_path)

        for ob in bpy.data.objects:
            if ob.kitops.insert:
                ob.kitops.insert_target = target_obj
    else:
        operator.report({'WARNING'}, "Please make sure the render file has a Floor object")

    print("insert imported")

def get_kpack_name(path):
    """Get kpack folder name from folder path"""
    if path != "":
        abs_path = bpy.path.abspath(path)
        norm_path = os.path.normpath(abs_path)
        kpack_name = norm_path.split(os.sep)[-1]
    else:
        kpack_name = ""
    return kpack_name

def check_kitops_pro():
    """Check if kitops pro is installed"""
    if hasattr(bpy.context.window_manager, "kitops"):
        return bpy.context.window_manager.kitops.pro
    else:
        return False

def select_insert_objects():
    """Select only insert objects"""
    for ob in bpy.data.objects:
        if ob.kitops.insert:
            ob.select_set(True)
        else:
            ob.select_set(False)

def get_blends(path):
    """Get all blend files in the directory"""
    blend_files = [f for f in os.listdir(path) if os.path.splitext(f)[1] == ".blend"]
    blend_files_paths = [os.path.join(path, b) for b in blend_files]
    return blend_files_paths

def clean_all_imported():
    """Remove all imported objects and collections"""
    # for ob in bpy.data.objects:
    #     if ob.kitops.insert:
    #         bpy.data.objects.remove(ob, do_unlink= True)
    for ob in bpy.data.objects:
        if not ob.keep_object:
            bpy.data.objects.remove(ob, do_unlink= True)

    for col in bpy.data.collections:
        if not col.keep_collection:
            bpy.data.collections.remove(col)

def prepare_render():
    """Prepare render settings"""
    bpy.context.scene.render.image_settings.file_format='PNG'

def align_camera_to_insert():
    """Select insert objects and align active camera to it"""
    select_insert_objects()
    if bpy.context.scene.camera:
        bpy.ops.view3d.camera_to_view_selected()
    
    # moving camera in local z direction according
    # to camera padding value if "auto_camera_pos" enabled
    props = get_props()
    camera_padding = props.camera_padding
    if props.auto_camera_pos:
        loc = Matrix.Translation((0.0, 0.0, camera_padding))
        bpy.context.scene.camera.matrix_basis @= loc

def render_inserts(is_exported, blend_path=None):
    """"Render and export images"""
    props = get_props()
    
    if props.auto_camera_pos:
        align_camera_to_insert()

    if blend_path:
        bpy.context.scene.render.filepath = os.path.splitext(blend_path)[0]+".png"

    if is_exported:
        bpy.ops.render.render(write_still= is_exported)
    else:
        # making sure rendering window opens up when runing a test render
        bpy.ops.render.render('INVOKE_DEFAULT', write_still= is_exported)

def open_log_file(kpack_folder_path):
    """Open the log file in the defult text editor"""
    kpack_name = get_kpack_name(kpack_folder_path)
    log_file_path = os.path.join(kpack_folder_path, kpack_name + ".txt")

    webbrowser.open(log_file_path)

def write_log_entry(kpack_folder_path, blend_file_path):
    """Add a log entry to the text log file"""
    kpack_name = get_kpack_name(kpack_folder_path)

    abs_path = bpy.path.abspath(kpack_folder_path)
    log_file_path = os.path.join(abs_path, kpack_name + ".txt")

    with open(log_file_path, 'a') as log:
        log.write(f"{blend_file_path}\n")

def create_log_file(kpack_folder_path):
    """Create a new empty log file"""
    kpack_name = get_kpack_name(kpack_folder_path)
    abs_path = bpy.path.abspath(kpack_folder_path)
    # norm_path = os.path.normpath(abs_path)
    log_file_path = os.path.join(abs_path, kpack_name + ".txt")

    with open(log_file_path, 'w') as log:
        log.write("")
    
def wrap_text(col, text, width):
    wrapp = textwrap.TextWrapper(width=width)
    wrapped_text = wrapp.wrap(text=text) 
    for line in wrapped_text:
        row = col.row(align= True)
        row.alignment = 'EXPAND'
        row.label(text= line)

def get_render_blend(operator):
    """Get render.blend file path from the addon folder"""
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    render_blend = os.path.join(dir_path, "render.blend")
    if os.path.exists(render_blend):
        return render_blend
    else:
        operator.report({'ERROR'}, "render.blend does not exist, make sure KIT OPS BATCH installed correctly")

def enable_render_window():
    """Temporarily enable rendering in a new window if it's already disabled by the user"""
    pass

def purge_orphan_data():
    """Purge all unused data blocks"""
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

    for lib in bpy.data.libraries:
        # clearing library users, preparing to purge it
        lib.user_clear()

    bpy.ops.outliner.orphans_purge()

def get_objs(dir_path):
    """Get a list of all OBJ files in a directory"""
    objs = [f for f in os.listdir(dir_path) if f[-3:].lower()=="obj"]
    # print (*objs)
    return objs

def import_obj(path):
    """Import obj file to the scene"""
    props = get_props()
    obj_folder = bpy.path.abspath(props.obj_folder)
    file_path = os.path.join(obj_folder, path)

    bpy.ops.import_scene.obj(
        filepath= file_path,
        use_edges= props.use_edges,
        use_smooth_groups= props.use_smooth_groups,
        use_split_objects= props.use_split_objects,
        use_split_groups= props.use_split_groups,
        use_groups_as_vgroups= props.use_groups_as_vgroups,
        use_image_search= props.use_image_search,
        split_mode= props.split_mode,
        global_clight_size= props.global_clight_size,
        axis_forward= props.axis_forward,
        axis_up= props.axis_up
    )

    # not the best way to get a list of the imported objects but I can't think of another way
    imported_objs = bpy.context.selected_objects

    return imported_objs

def copy_scene():
    """Create a copy of the current scene"""
    new_scene = bpy.context.scene.copy()

    # unlink all existing objects from the newly created scene
    for col in new_scene.collection.children:
        new_scene.collection.children.unlink(col)

    for ob in new_scene.collection.objects:
        new_scene.collection.objects.unlink(ob)

    # set the new scene as active
    bpy.context.window.scene = new_scene

    return new_scene

def get_principled_node(material):
    """Get the principled node that is connected to material output"""
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            if node.outputs['BSDF'].links[0].to_socket.name == 'Surface':
                return node
        else:
            print("Unable to find a a valid principled node")
            return None

def lcs(S,T):
    """Find longest common substring of two strings"""
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])

    if list(lcs_set):
        return list(lcs_set)[0]
    else:
        return None

def get_base_image_name(material):
    """Get common image name from all image texture nodes"""
    # create a list of unique images names
    names = []
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and hasattr(node.image, "name"):
            image_name = node.image.name.split(".")[0]
            if image_name not in names:
                names.append(image_name)

    # get the common image name from names list
    if len(names) > 1:
        common_names = []
        for i, n in enumerate(names):
            if i != 0:
                # compare name with first name in the list
                common_string = lcs(names[0], names[i])
                if common_string:
                    common_names.append(common_string)
        if len(set(common_names)) == 1:
            base_name = list(set(common_names))[0]
            return base_name
    else:
        print("Unable to identify base texture name")
        return None

def get_addon_prefs():
    """Create a list of the addon preference properties"""
    prefs = bpy.context.preferences.addons['kitops-batch'].preferences
    suffix_list = {
        'COLOR' : prefs.color_suffix,
        'METALLIC' : prefs.metallic_suffix,
        'SPECULAR' : prefs.specular_suffix,
        'ROUGHNESS' : prefs.roughness_suffix,
        'NORMAL' : prefs.normal_suffix,
        'BUMP' : prefs.bump_suffix
    }
    return prefs.use_suffix, suffix_list

def identify_texture_type(node, image_base_name, suffix_list):
    """Identify the image texture map type according to base name
    and predefined suffixes in the addon preferences"""
    image_name = node.image.name.split(".")[0]
    for key in suffix_list:
        if image_name.replace(image_base_name, "") == suffix_list[key]:
            texture_type = key
            return texture_type
    print("Unable to identify a texture type")
    return None

def reconnect_node(material, node, texture_type, principled_node):
    """Reconnect node to proper output according to map/texture type"""
    tree = material.node_tree
    links = node.outputs['Color'].links
    pos_x, pos_y = node.location

    # if the node is connected already to a node
    if links: 
            link = links[0]
            tree.links.remove(link)

    if texture_type == 'COLOR':
        tree.links.new(principled_node.inputs['Base Color'], node.outputs['Color'])
            
    elif texture_type == 'METALLIC':
        tree.links.new(principled_node.inputs['Metallic'], node.outputs['Color'])
        
    elif texture_type == 'SPECULAR':
        tree.links.new(principled_node.inputs['Specular'], node.outputs['Color'])

    elif texture_type == 'ROUGHNESS':
        tree.links.new(principled_node.inputs['Roughness'], node.outputs['Color'])

    elif texture_type == 'NORMAL':
        # create a new normal map node
        normal_node = tree.nodes.new('ShaderNodeNormalMap')
        normal_node.location = Vector((pos_x + 300, pos_y))

        tree.links.new(principled_node.inputs['Normal'], normal_node.outputs['Normal'])
        tree.links.new(normal_node.inputs['Color'], node.outputs['Color'])

    elif texture_type == 'BUMP':
        # create a new bump node
        bump_node = tree.nodes.new('ShaderNodeBump')
        bump_node.inputs['Strength'].default_value = 0.05
        bump_node.location = Vector((pos_x + 300, pos_y))

        tree.links.new(principled_node.inputs['Normal'], bump_node.outputs['Normal'])
        tree.links.new(bump_node.inputs['Height'], node.outputs['Color'])

    else:
        print("Unrecognized map/texture type")

def fix_map_nodes(material, suffix_list):
    """Fix texure map nodes according to their naming convention from preferences"""
    # this process runs only if enabled from preferences
    principled_node = get_principled_node(material)
    base_name = get_base_image_name(material)
    if base_name:
        image_texture_nodes = [node for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
        for node in image_texture_nodes:
            texture_type = identify_texture_type(node, base_name, suffix_list)
            reconnect_node(material, node, texture_type, principled_node)


def create_blend(dir_path, ob, scene, operator, create_insert= True, children= []):
    """Save objects to a new blend file in dir_path"""
    props = get_props()
    use_suffix, suffix_list = get_addon_prefs()
    # create_insert = props.create_insert

    blend_name = f"{ob.name}.blend"
    abs_path = bpy.path.abspath(dir_path)
    norm_path = os.path.normpath(abs_path)
    filepath = os.path.join(norm_path, blend_name)

    if props.override_material:
        ob.data.materials.clear()
        ob.active_material = props.override_material
    
    if use_suffix:
        # reconnect texture map nodes according to their type
        for slot in ob.material_slots:
            fix_map_nodes(slot.material, suffix_list)
        

    if create_insert:
        # use save_insert() from KITOPS modules
        if 'kitops.addon.utility.smart' in sys.modules:
            # assign object as main object
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            ob.kitops.main = True

            # add object children to export list
            all_objects = [ob] + children

            # save to external blend file with INSERT properties
            sys.modules['kitops.addon.utility.smart'].save_insert(path= filepath, objects= all_objects)
            ob.select_set(False)
        else:
            operator.report(type= {'ERROR'}, message= "Please make sure KITOPS is installed and activated")
    else:
        data_blocks = {scene}
        bpy.data.libraries.write(filepath, data_blocks)

    # remove the object after exported
    for ob_ in [ob] + children:
        bpy.data.objects.remove(ob_, do_unlink= True)

    # clear all unused meshes and materials
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
            
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    return filepath


def origin_to_bottom(ob, activate= True):
    """Assign the origin to the bottom center of object bound box"""
    if activate:
        matrix= Matrix()
        me = ob.data
        mw = ob.matrix_world
        local_verts = [matrix @ Vector(v[:]) for v in ob.bound_box]
        o = sum(local_verts, Vector()) / 8
        o.z = min(v.z for v in local_verts)
        o = matrix.inverted() @ o
        me.transform(Matrix.Translation(-o))

        mw.translation = mw @ o

def apply_transforms(ob, activate= True):
    """Apply transforms for object"""
    if activate:
        # transform the mesh using the matrix world
        ob.data.transform(ob.matrix_world)
        # reset matrix to identity
        ob.matrix_world = Matrix()

def reset_transforms(ob, activate= True):
    """Reset all transforms of object"""
    if activate:
        ob.matrix_basis = Matrix()

def clear_custom_split_normals(ob, activate= True):
    """Clear custom split normals of object"""
    if activate:
        bpy.context.view_layer.objects.active = ob
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        print ("Custom split normals cleared")

def obj_export_path():
    """Determine the OBJ export path"""
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    print ("OBJ Export directory is:", directory)
    return directory

def deselect_all():
    """Deselect all"""
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    print ("deselect all!")

def export_to_obj(item, directory):
    """Export item to obj, item could be a single object or a collection of objects"""
    deselect_all()
    filepath = os.path.join(directory, f"{item.name}.obj")

    # select object to export
    if hasattr(item, 'type'):
        # if the item is a mesh object
        if item.type == 'MESH':
            item.select_set(True)
            bpy.ops.export_scene.obj(filepath= filepath, check_existing= False, use_selection= True)
            deselect_all()
    elif hasattr(item, 'objects'):
        # if the item is a collection
        export_objects = [ob for ob in item.objects if ob.type == 'MESH']
        if export_objects:
            for ob in export_objects:
                ob.select_set(True)
            bpy.ops.export_scene.obj(filepath= filepath, check_existing= False, use_selection= True)
            deselect_all()
    else:
        print(f"{item.name} is not a mesh or a collection, export aborted")

def load_decal_mat(blend_file, material_name):
    '''Get the dacal material from the decal template blend file'''
    blend_path = bpy.path.abspath(blend_file)
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        try:
            data_to.materials = [material_name]
        except:
            print("Cannot find Batch DECAL material")

def load_decal_mod(blend_file, object_name):
    """Get the list of modifiers from a decal template object"""
    blend_path = bpy.path.abspath(blend_file)
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        try:
            data_to.objects = [object_name]
        except:
            print("Cannot find Batch DECAL object template")

def add_modifiers(ob, modifiers: list):
    """Add all modifiers in the list to the object"""
    for mod in modifiers:
        ob.modifiers.new(name= mod.name, type= mod.type)
        mod = ob.modifiers.get(mod.name)
        if mod.type == 'DISPLACE':
            mod.direction = 'Z'
            mod.mid_level = 0.995
        if mod.type == 'SUBSURF':
            mod.subdivision_type = 'SIMPLE'
            mod.render_levels = 3
            mod.levels = 3
            mod.quality = 3
        if mod.type == 'SHRINKWRAP':
            mod.wrap_method = 'PROJECT'
            mod.wrap_mode = 'ON_SURFACE'
            mod.cull_face = 'OFF'
            mod.use_negative_direction = True
            mod.use_positive_direction = True
            mod.offset = 0.012

def get_pngs(images_folder):
    '''Get a list of all the PNGs in the folder'''
    pngs_folder = bpy.path.abspath(images_folder)
    real_path = os.path.normpath(pngs_folder)
    pngs = [f for f in os.listdir(real_path) if f[-3:].lower()=="png"]
    return pngs

def unwrap_obj(obj):
    '''UV Unwrap the object'''
    # This can be improved in the future by using bmesh instead
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action= 'SELECT')
    # bpy.ops.uv.unwrap(correct_aspect= True)
    bpy.ops.uv.smart_project(angle_limit= 66, island_margin= 0, use_aspect= True, stretch_to_bounds= True)
    bpy.ops.object.mode_set(mode='OBJECT')

def assign_image(image, material):
    '''Assign image to material'''
    image = bpy.data.images.get(image)
    image_node = material.node_tree.nodes['decal']

    if not image_node is None:    
        image_node.image = image
    else:
        print("The given material doesn't have a decal node!")

def create_decal(image_name, image_size, decal_mat_name):
    '''Create a new mesh plane object with the same image name and aspect ratio'''
    size_x = image_size[0] / 1000
    size_y = image_size[1] / 1000
    name = image_name[:-4]

    # # create a new mesh
    # bm = bmesh.new()
    # v1 = bm.verts.new((size_x/2, size_y/2, 0))
    # v2 = bm.verts.new((-size_x/2, size_y/2, 0))
    # v3 = bm.verts.new((-size_x/2, -size_y/2, 0))
    # v4 = bm.verts.new((size_x/2, -size_y/2, 0))
    # verts = [v1, v2, v3, v4]

    # bm.faces.new(verts)

    # mesh = bpy.data.meshes.new(name)
    # bm.to_mesh(mesh)
    # bm.free()

    # # create a new object
    # ob = bpy.data.objects.new(name, mesh)

    # # link the object to the scene collection
    # bpy.context.collection.objects.link(ob)
    # bpy.context.view_layer.objects.active = ob

    bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
    plane = bpy.context.active_object

    if plane.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    plane.dimensions = size_x, size_y, 0.0
    plane.data.name = plane.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # create a new material
    decal_template_mat = bpy.data.materials.get(decal_mat_name)
    if not decal_template_mat is None:
        mat = decal_template_mat.copy()
        mat.name = name
        assign_image(image_name, mat)

        # assign the new material to object
        plane.data.materials.append(mat)
    else:
        print("Decal template material was not imported correctly")

    # unwrap
    # unwrap_obj(ob)
    return plane





