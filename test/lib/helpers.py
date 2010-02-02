# -*- coding: utf-8 -*-
import os
import tempfile

def fixturePath( name ):
	"""@return:
		path to fixture file with ``name``, you can use a relative path as well, like
		subfolder/file.ext"""
	return os.path.abspath( os.path.join( os.path.dirname( __file__ ), "../fixtures/%s" % name ) )
	
def save_for_debugging(scene_name):
	"""Save the currently actve scene as MayaAscii for debugging purposes"""
	from mayarv.maya.scene import Scene
	scene_path = os.path.join(tempfile.gettempdir(), scene_name + ".ma")
	Scene.save(scene_path, force=True)
	
	print "Saved scene for debugging at: %r" % scene_path
