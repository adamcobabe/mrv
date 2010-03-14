from mayarv.test.lib import *
import tempfile

def save_temp_file( filename ):
	"""save the current scene as given filename in a temp directory, print path"""
	import mayarv.maya as mrvmaya		# late import
	filepath = tempfile.gettempdir( ) + "/" + filename
	savedfile = mrvmaya.Scene.save( filepath )
	print "SAVED TMP FILE TO: %s" % savedfile
	return savedfile


def save_for_debugging(scene_name):
	"""Save the currently actve scene as MayaAscii for debugging purposes
	@return: absolute path string at which the file was saved"""
	import mayarv.maya as mrvmaya		# late import
	scene_path = os.path.join(tempfile.gettempdir(), scene_name + ".ma")
	mrvmaya.Scene.save(scene_path, force=True)
	
	print "Saved scene for debugging at: %r" % scene_path
	return scene_path

def get_maya_file( filename ):
	"""@return: path to specified maya ( test ) file """
	return fixturePath( "ma/"+filename )

#{ Decorators
def with_scene( basename ):
	"""Loads the specified scene . the basename is supposed to be in our fixtures
	directory"""
	import mayarv.maya as mrvmaya		# late import
	if not isinstance(basename, basestring):
		raise ValueError("Need basename of a scene as string, not %r" % basename)
	# END arg check
	
	def wrapper(func):
		def scene_loader(self, *args, **kwargs):
			scene_path = get_maya_file(basename)
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
