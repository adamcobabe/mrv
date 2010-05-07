import os
import sys
import __builtin__

from distutils.core import setup
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


#{ Utilities

def prepare_mrv_syspath():
	"""Make sure mrv is in the python path"""
	try:
		import mrv
	except ImportError:
		ospd = os.path.dirname
		sys.path.append(ospd(ospd((os.path.realpath(os.path.abspath(__file__))))))
		try:
			import mrv
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
	
	#} END overridden methods 

#} END commands

# apply patches - this is the official way to do it actually, which surprised me
distutils.command.build_py.build_py = BuildPython


#{ Utility Classes

class Library(object):
	"""Setup library providing additional functions"""

	#{ Configuration
	rootpackage = 'mrv'
	
	#} END configuration

	#{ Path Generators
	
	def _rootpath(self):
		""":return: path to the root of the rootpackage, which includes all modules
		and subpackages directly"""
		return os.path.dirname(os.path.abspath(__file__)) 
	
	#} END path generators

	def get_packages(self):
		""":return: list of all packages in rootpackage in __import__ compatible form"""
		return [self.rootpackage] + [ self.rootpackage + '.' + pkg for pkg in find_packages(self._rootpath()) ]
		

#} END utility classes


def main(args, library_type=Library):
	lib = library_type()
	
	setup(name = "MRV",
		  version = "1.0.0-preview",
		  description = "MRV Development Framework",
		  author = "Sebastian Thiel",
		  author_email = "byronimo@gmail.com",
		  url = "http://gitorious.org/mrv",
		  packages = lib.get_packages(),
		  package_dir = {'mrv' : ''},
		  scripts=['bin/mrv', 'bin/imrv'],
		  license = "BSD License",
		  requires = ['nose', ], 
		  long_description = """"MRV is a multi-platform python development environment to ease rapid development 
	of maintainable, reliable and high-performance code to be used in and around Autodesk Maya."
	""",
		  classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: BSD License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2.5",
			"Programming Language :: Python :: 2.6",
			"Topic :: Software Development :: Libraries :: Python Modules",
			]
		  )
	

if __name__ == '__main__':
	prepare_mrv_syspath()
	main(sys.argv[1:])
