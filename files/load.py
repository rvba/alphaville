import bpy
import os
import sys

pref = bpy.context.user_preferences
pref.inputs.select_mouse = 'LEFT'
pref.view.use_auto_perspective = True

f = os.getcwd() + os.path.sep + "01.blend"
print(f)

with bpy.data.libraries.load(f) as (src,dst):
	dst.objects = [name for name in src.objects]

bpy.context.scene.objects.active = None
for ob in dst.objects:
	if ob is not None:
		print("loading:",ob)
		bpy.context.scene.objects.link(ob)
		ob.show_wire = True
		#bpy.context.scene.objects.active = ob
		#bpy.ops.object.mode_set(mode='EDIT')

bpy.data.objects['Elevation'].select = True
bpy.context.scene.objects.active = bpy.data.objects['Elevation']
bpy.ops.object.mode_set(mode='EDIT')


# vim: set noet sts=8 sw=8 :
