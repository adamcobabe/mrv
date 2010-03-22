from mayarv.test.lib import *
import tempfile
import time
import os

__all__ = ('save_temp_file', 'save_for_debugging', 'get_maya_file', 'with_scene')


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


#{ TestBases 

# must not be put in __all__ !
class StandaloneTestBase( unittest.TestCase ):
	"""Provides a base implementation for all standalone tests which need to 
	initialize the maya module to operate. It will bail out if the module 
	is initialized already. Otherwise it will call the post_standalone_initialized
	method to allow additional tests to run.
	
	Before the maya standalone module is initialized, the setup_environment method
	will be called in order to adjust the configuration. Whether the post_standalone_initialized
	method runs or not, the undo_setup_environment method is called for you to undo your changes.
	
	It is advised to name your TestCase class in a descriptive way as it will show 
	up in the message printed if the test cannot run."""
	
	def setup_environment(self):
		raise NotImplementedError("To be implemented in subclass")
	
	def test_init_standalone(self):
		self.setup_environment()
		try:
			st = time.time()
			import mayarv.maya
			# too fast ? It was loaded already as we have not been run standalone
			if time.time() - st < 0.1:
				print "%s standalone test bailed out at it couldn't be the first one to initialize mayarv.maya" % type(self).__name__
				return
			# END handle non-standalone mode
			
			self.post_standalone_initialized()
		finally:
			self.undo_setup_environment()
		# END assure environment setup gets undone
			
	def undo_setup_environment(self):
		raise NotImplementedError("To be implemented in subclass")
		
	def post_standalone_initialized(self):
		raise NotImplementedError("To be implemented in subclass")
#} END testbases
