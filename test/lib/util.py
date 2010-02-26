# -*- coding: utf-8 -*-
import os
import tempfile
import mayarv.maya as mrvmaya

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
	

#{ Decorators
def with_scene( basename ):
	"""Loads the specified scene . the basename is supposed to be in our fixtures
	directory"""
	if not isinstance(basename, basestring):
		raise ValueError("Need basename of a scene as string, not %r" % basename)
	# END arg check
	
	def wrapper(func):
		def scene_loader(self, *args, **kwargs):
			scene_path = fixturePath(basename)
			mrvmaya.Scene.open(scene_path, force=True)
			print "Opened Scene: '%s'" % basename
			
			try:
				return func(self, *args, **kwargs)
			finally:
				mrvmaya.Scene.new(force=1)
			# END assure new scene is loaded after test
		# END internal wrapper

		scene_loader.__name__ = func.__name__
		return scene_loader
	# END wrapper	
	return wrapper

#} END decorator
