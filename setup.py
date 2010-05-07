import os
import sys
import __builtin__

from distutils.core import setup
from distutils.dist import Distribution as BaseDistribution
from distutils import log


import distutils.command.build_py

build_py = distutils.command.build_py.build_py

try:
	from setuptools import find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import find_packages
# END get find_packages


#{ Distutils Fixes 

def __init__(self, dist):
	"""Okay, its getting interesting: cmd checks for the type of dist - we 
	have derived from it and provide our own type. Distribution is an oldstyle class
	which doesn't even work with isinstance - to workaround this, we derive from object
	as well. In the moment we call __init__ on the BaseDistribution part of our instance, 
	it claims not to be an instance of type Distribution(Base) anymore. Something is 
	fishy here. As a workaround, we get rid of the typecheck in the command base."""
	self.distribution = dist
	self.initialize_options()
	self._dry_run = None
	self.verbose = dist.verbose
	self.force = None
	self.help = 0
	self.finalized = 0

distutils.cmd.Command.__init__ = __init__

#} END Distutils fixes


#{ Utilities

def get_root_package():
	"""Make sure the root package is in the python path
	:return: root package object"""
	ospd = os.path.dirname
	packageroot = ospd((os.path.realpath(os.path.abspath(__file__))))
	root_package_name = os.path.basename(packageroot)
	try:
		return __import__(root_package_name)
	except ImportError:
		sys.path.append(ospd(packageroot))
		try:
			return __import__(root_package_name)
		except ImportError:
			del(sys.path[-1])
			raise ImportError("Failed to import MRV as it could not be found in your syspath, nor could it be deduced"); 
		# END second attempt exception handling
	# END import exception handling
#} END utilities


#{ Decorators


#} END decorators 

#{ Commands 

class BuildPython(build_py):
	"""Customize the command preparing python modules in order to skip copying 
	original py files if compile is specified. Additionally we allow the python 
	interpreter to be specified as the bytecode is incompatible between the versions"""
	
	#{ Configuration
	
	description="Implements byte-compilation with different python interpreter versions"
	
	opt_maya_version = 'maya-version'
	build_py.user_options.extend((( '%s=' % opt_maya_version, 'm', 
									'maya version you would like to compile the bytecode for. \
									Determines the interpreter used. If not set, the current \
									one will be used' ), 
									))
	#} END configuration 
	
	#{ Overridden Methods 
	
	def initialize_options(self):
		build_py.initialize_options(self)
		self.py_version = None
		self.maya_version = None		# set later by distutils
		
	def finalize_options(self):
		build_py.finalize_options(self)
		
		# assign final value to our py_version
		if self.maya_version is not None:
			import mrv.cmd.base 
			try:
				self.py_version = mrv.cmd.base.python_version_of(float(self.maya_version))
			except ValueError:
				raise ValueError("Incorrect MayaVersion format: %s" % self.maya_version)
		# END handle maya version
		
	def byte_compile( self, files, **kwargs):
		"""If we are supposed to compile, remove the original file afterwards"""
		needs_compilation = self.compile or self.optimize
		if needs_compilation and self.py_version is None:
			raise ValueError("If compilation is requested, the'%s' option must be specified" % self.opt_maya_version)
		# END handle errors
		
		# assure we byte-compile in a standalone interpreter, manipulating the 
		# sys.executable as it will be used later
		prev_debug = __debug__
		prev_executable = sys.executable
		if needs_compilation:
			# this forces to use a standalone process
			__builtin__.__debug__ = False
			
			# which is hopefully in the path
			sys.executable = "python%g" % self.py_version
		# END preparation
		
		# TODO: allow choosing the python version
		# Additionally: allow to rename pyo back to pyc possibly if maya wants it 
		rval = build_py.byte_compile(self, files, **kwargs)
		
		if needs_compilation:
			# restore original values
			__builtin__.__debug__ = prev_debug
			sys.executable = prev_executable
			
			# super class implementation handles the compilation and optimization 
			# as if it was a totally separate case and duplicates code for whichever 
			# reason 
			for py_file in (f for f in files if f.endswith('.py')):
				log.info("Removing original file after byte compile: %s" % py_file)
				os.remove(py_file)
			# END for each python file to remove
		# END post processing
		
		return rval
	
	def build_packages(self):
		"""Makes sure that the external modules are found as well and handled 
		properly"""
		build_py.build_packages(self)
		
	
	#} END overridden methods 


class Distribution(object, BaseDistribution):
	"""Customize available options and behaviour to work with mrv and derived projects"""
	
	#{ Configuration
	# root package module, will be set by the main routine, must be set 
	# for this class to work
	root = None 
	
	#} END configuration
	
	#{ Internals
	@classmethod 
	def modifiy_sys_args(cls):
		"""Parse our own arguments off the args list and modify the argument 
		stream accordingly.
		
		:note: needs to be called before setup of the distutils is called"""
		rargs = [sys.argv[0]]
		args = sys.argv[1:]
		while args:
			arg = args.pop(0)
			rargs.append(arg)
		# END while there are args
		
		del(sys.argv[:])
		sys.argv.extend(rargs)
	
	@classmethod
	def version_string(cls, version_info):
		""":return: version string from the given version info which is assumed to 
		be in the default python version_info format ( sys.version_info )"""
		base = "%i.%i.%i" % version_info[:3]
		if version_info[3]:
			base += "-%s" % version_info[3]
		return base
	
	#} END Internals 
	
	
	#{ Path Generators
	
	def _rootpath(self):                   
		""":return: path to the root of the rootpackage, which includes all modules
		and subpackages directly"""
		return os.path.dirname(os.path.abspath(self.root.__file__)) 
	
	#} END path generators

	
	#{ Interface
	
	def get_packages(self):
		""":return: list of all packages in rootpackage in __import__ compatible form"""
		base_packages = [self.root.__name__] + [ self.root.__name__ + '.' + pkg for pkg in find_packages(self._rootpath()) ]
		
		# add external packages - just pretent its a package even though it it just 
		# a path in external
		ext_path = os.path.join(os.path.dirname(__file__), 'ext')
		if os.path.isdir(ext_path):
			for root, dirs, files in os.walk(ext_path):
				# remove hidden paths
				for dir in dirs[:]:
					if not dir.startswith('.'):
						continue
					try:
						dirs.remove(dir)
					except ValueError:
						pass
					# END exception handling
				# END for each path to check
				
				# process paths
				for dir in dirs:
					base_packages.append(self.root.__name__+"."+os.path.join(root, dir).replace(os.sep, '.'))
				# END for each remaining valid directory
			# END walking external dir
		# END if external directory exists
		
		return base_packages
		
	#} END interface 
	
	#{ Overridden Methods
	def __new__(cls, *args, **kwargs):
		"""Fix the objet.__new__ call with arguments that would occur. This
		is a serious issue, not only here but also for mixin classes that need 
		initialization - types don't know who derives from them, and which hierarchy
		they are in, and they have to call super to pass on the __init__ call to 
		possible mixins in the derived hierarchy"""
		return object.__new__(cls)
		
	def __init__(self, *args, **kwargs):
		"""Initialize base and set some useful defaults"""
		BaseDistribution.__init__(self, *args, **kwargs)
		
		if self.root is None:
			raise ValueError("Root package is not set - it should be set in setup.main()")
		
		# assure we get all packages we need, including external if desired
		self.packages = self.get_packages()
		
		
	def get_command_class(self, command):
		"""Return a command class, but prefer ours. We make it explicit here instead
		of monkey-patching the existing module"""
		if command == build_py.__name__:
			return BuildPython
		return BaseDistribution.get_command_class(self, command)
	
	#} END overridden methods


#} END commands



def main(root, args, distclass=Distribution):
	distclass.root = root
	distclass.modifiy_sys_args()
	
	setup(
	      distclass=distclass,
	      name = root.project_name,
		  version = distclass.version_string(root.version_info),
		  description = root.description,
		  author = root.author,
		  author_email = root.author_email,
		  url = root.url,
		  license = root.license,
		  package_dir = {root.__name__ : ''},
		  
		  **root.setup_kwargs
		  )
	

if __name__ == '__main__':
	root = get_root_package()
	main(root, sys.argv[1:])
