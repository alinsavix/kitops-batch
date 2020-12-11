# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import importlib
if "bpy" in locals():
    importlib.reload(utils)
    importlib.reload(props)
    importlib.reload(ops)
    importlib.reload(ui)
else:
    import bpy
    from . import props
    from . import ops
    from . import ui


bl_info = {
    "name" : "KIT OPS BATCH",
    "author" : "Chipp Walters, Ahmed Ali",
    "description" : "",
    "blender" : (2, 83, 0),
    "version" : (1, 0, 2),
    "location" : "View 3D > KIT OPS BATCH",
    "warning" : "",
    "category" : "3D View",
    "wiki_url": "https://docs.google.com/document/d/1J0gDERPU3SZCRsqoASGu4qlgz9lJMDto64ChnmwQJcE/edit"
}

def register():
    props.register()
    ops.register()
    ui.register()

def unregister():
    props.unregister()
    ops.unregister()
    ui.unregister()