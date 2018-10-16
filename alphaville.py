# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# Copyright (C) Milovann Yanatchkov 2017 
#

import bpy
import os
import sys
import json
import bmesh
from bpy_extras import object_utils

from bpy.props import (
		BoolProperty,
		EnumProperty,
		FloatProperty,
		StringProperty,
		)

from bpy_extras.io_utils import (
		ImportHelper,
		ExportHelper,
		orientation_helper_factory,
		axis_conversion,
		)


def load_objs(operator,
		context,
		filepath="",
		constrain_size=0.0,
		use_image_search=True,
		use_apply_transform=True,
		global_matrix=None,
		):
	sub_path = bpy.context.scene.arx_alpha_collect_path 
	path = bpy.path.abspath(filepath)
	dirs = os.listdir(path)
	name="obj.obj"
	for d in dirs:
		_dir = path + d
		if os.path.isdir(_dir):
			f = path + d + sub_path
			if os.path.isfile(f):
				size = os.path.getsize(f)
				print("size",size)
				max_size = bpy.context.scene.arx_alpha_file_max_size * 1000 
				if(size>max_size):
					print("[WARNING]",f,"too large")
				else:
					bpy.ops.import_scene.obj(filepath=f)
			else:
				print("Not a file:"+f)


def add_plane(context,ox,oy,oz,w,h):

	x =0
	y = 0
	z = 0
	verts = [
			(x,y,z),
			(x+w,y,z),
			(x+w,y+h,z),
			(x,y+h,z)

			]

	faces = [(0, 1, 2, 3)]
	mesh = bpy.data.meshes.new("Plane")
	bm = bmesh.new()

	for v in verts:
		bm.verts.new(v)

	bm.verts.ensure_lookup_table()
	for f_idx in faces:
		bm.faces.new([bm.verts[i] for i in f_idx])

	bm.to_mesh(mesh)
	mesh.update()

	ob = bpy.data.objects.new("Plane",mesh)
	bpy.context.scene.objects.link(ob)
	ob.location.x = ox
	ob.location.y = oy
	ob.location.z = oz
	ob.show_wire = True

def load_blends(operator,
		context,
		filepath="",
		constrain_size=0.0,
		use_image_search=True,
		use_apply_transform=True,
		global_matrix=None,
		):
	sub_path = bpy.context.scene.arx_alpha_collect_path 
	path = bpy.path.abspath(filepath)
	dirs = os.listdir(path)
	name="obj.obj"
	current_column = 0
	current_cell = 0
	for d in sorted(dirs):
		_dir = path + d
		if os.path.isdir(_dir):
			f = path + d + sub_path
			if os.path.isfile(f):
				size = os.path.getsize(f)
				max_size = bpy.context.scene.arx_alpha_file_max_size * 1000 
				use_offset = bpy.context.scene.arx_alpha_use_offset
				if(size>max_size):
					print("[WARNING]",f,"too large:",size)
				else:
					cell_dim = bpy.context.scene.arx_alpha_cell_dim 
					grid_dim = bpy.context.scene.arx_alpha_grid_dim 
					offset_dim = bpy.context.scene.arx_alpha_offset_dim
					with bpy.data.libraries.load(f) as (src,dst):
						dst.objects = [name for name in src.objects]

					for ob in dst.objects:
						current_cell
						if ob is not None:
							x = (cell_dim + offset_dim) * current_cell
							y = (cell_dim + offset_dim) * current_column
							z = 0
							if use_offset:
								ob.location.x += x  
								ob.location.y += y  

							bpy.context.scene.objects.link(ob)
							ob.show_wire = True

							if use_offset and offset_dim > 0:
								if current_column == 0:
									if current_cell < grid_dim - 1:
										ox = x  + (cell_dim / 2)
										oy = y - (cell_dim / 2 ) 
										oz = 0
										w = offset_dim
										h = cell_dim
										add_plane(context,ox,oy,oz,w,h)
								else:
									ox = x - (cell_dim / 2)
									oy = y - ((cell_dim / 2 ) + offset_dim)
									oz = 0
									w = cell_dim
									h = offset_dim
									add_plane(context,ox,oy,oz,w,h)

									if current_cell < grid_dim - 1:
										ox = x  + (cell_dim / 2)
										oy = y - ((cell_dim / 2 ) + offset_dim)
										oz = 0
										w = offset_dim
										h = offset_dim
										add_plane(context,ox,oy,oz,w,h)

										ox = x  + (cell_dim / 2)
										oy = y - (cell_dim / 2 ) 
										oz = 0
										w = offset_dim
										h = cell_dim
										add_plane(context,ox,oy,oz,w,h)



							if current_cell >= grid_dim-1:
								current_cell = 0
								current_column = current_column + 1
							else:
								current_cell += 1

			else:
				print("Not a file:"+f)

class Load_obj(bpy.types.Operator,ImportHelper):
	"""Load obj"""
	bl_idname = "import_scene.load_objs"
	bl_label = 'Load Objs'
	bl_options = {'UNDO'}

	def execute(self, context):
		keywords = self.as_keywords(ignore=("axis_forward",
			"axis_up",
			"filter_glob",
			))

		path = context.scene.arx_alpha_collect_path
		parts = path.split("/")
		filename = parts[-1]
		exts = filename.split(".")
		ext = exts[-1]

		if ext == "blend":
			load_blends(self, context, **keywords)
		elif ext == "obj":
			load_objs(self, context, **keywords)
		else:
			print("[alphaville] not a supported extension:",ext)

		return {'FINISHED'}

class Alphaville(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="scene"
	bl_label="Alphaville"

	@classmethod
	def poll(cls,context):
		return context.scene

	def load_pref(item):
		path = bpy.utils.resource_path('LOCAL') + "alphaville.txt"
		if os.path.isfile(path):
			with open(path) as data_file:
				data = json.load(data_file)
				if item in data.keys():
					return data[item]

		if item == "path": return ""
		elif item == "max_size": return 100
		elif item == "use_offset": return 0
		elif item == "cell_dim": return 20
		elif item == "grid_dim": return 2
		elif item == "offset_dim": return 0
		else:
			return 0


	bpy.types.Scene.arx_alpha_collect_path = bpy.props.StringProperty("arx_alpha_collect_path", default = load_pref("path"))
	bpy.types.Scene.arx_alpha_frame_use_border = bpy.props.BoolProperty("arx_alpha_frame_use_border", default=False)
	bpy.types.Scene.arx_alpha_file_max_size = bpy.props.IntProperty("arx_alpha_file_max_size", default=load_pref("max_size"))
	bpy.types.Scene.arx_alpha_use_offset = bpy.props.BoolProperty("arx_alpha_use_offset", default=load_pref("use_offset"))
	bpy.types.Scene.arx_alpha_cell_dim = bpy.props.IntProperty("arx_alpha_cell_dim", default=load_pref("cell_dim"))
	bpy.types.Scene.arx_alpha_grid_dim = bpy.props.IntProperty("arx_alpha_grid_dim", default=load_pref("grid_dim"))
	bpy.types.Scene.arx_alpha_offset_dim = bpy.props.IntProperty("arx_alpha_offset_dim", default=load_pref("offset_dim"))

	def draw(self,context):

		scene = bpy.context.scene
		layout=self.layout
		col=layout.column(align=True)
		col.prop(context.scene,"arx_alpha_collect_path",text="")
		col.operator(Load_obj.bl_idname,text="Import")
		col.prop(scene,"arx_alpha_file_max_size",text="max size (ko)")


		col=layout.column(align=True)
		col.prop(scene,"arx_alpha_use_offset",text="use offset", toggle=True)
		if scene.arx_alpha_use_offset:
			col.prop(scene,"arx_alpha_cell_dim",text="cell")
			col.prop(scene,"arx_alpha_grid_dim",text="grid")
			col.prop(scene,"arx_alpha_offset_dim",text="offset")


def import_alphaville(self, context):
	self.layout.operator(_IMPORT_Alphaville.bl_idname, text="Alphaville" , icon='FILE_IMAGE')
	return {'FINISHED'}

# vim: set noet sts=8 sw=8 :
