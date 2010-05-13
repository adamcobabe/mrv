# -*- coding: utf-8 -*-
"""
Initialize mrv system assisting development, debugging and maintenance

	- install general `decorator` into __builtin__ namespace
"""
import __builtin__
from inspect import isfunction
import logging
import logging.config
log = logging.getLogger("mrv")

__all__ = ("init_modules", )


import os, sys
from path import Path


#{ Configuration 

## Version Info 
# See http://docs.python.org/library/sys.html#sys.version_info for more information
#               major, minor, micro, releaselevel, serial
version_info = (1,     0,     0,     'Preview',        0)

project_name = "mrv"
author = "Sebastian Thiel"
author_email = 'byronimo@gmail.com'
url = "http://gitorious.org/mrv"
description ='Convenient Animation Export and Import'
license = "BSD License"

__scripts_bin = ['bin/mrv', 'bin/imrv']
__scripts_test_bin = ['test/bin/tmrv', 'test/bin/tmrvr']
__scripts_test_bin_s = [ p.replace('test/', '') for p in __scripts_test_bin ]
setup_kwargs = dict(scripts=__scripts_bin + __scripts_test_bin, 
                    long_description = """MRV is a multi-platform python development environment to ease rapid development 
                                    of maintainable, reliable and high-performance code to be used in and around Autodesk Maya."
                                    """,
                    package_data = {   'mrv.test' : ['fixtures/ma/*', 'fixtures/maya_user_prefs/'] + __scripts_test_bin_s, 
                    					'mrv' : __scripts_bin + ['!*.gitignore'],
                    					'mrv.maya' : ['cache'],
                    					'mrv.doc' : ['source', 'makedoc', '!*source/generated/*']
                    				},   
                    classifiers = [
                        "Development Status :: 5 - Production/Stable",
                        "Intended Audience :: Developers",
                        "License :: OSI Approved :: BSD License",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Programming Language :: Python :: 2.5",
                        "Programming Language :: Python :: 2.6",
                        "Topic :: Software Development :: Libraries :: Python Modules",
                        ], 
					options = dict(build_py={	'exclude_from_compile' : ('*/maya/undo.py', '*/maya/nt/persistence.py'), 
												'exclude_items' : ('mrv.conf', 'mrv.dg', 'mrv.batch', 'mrv.mdp', 
																	'.automation',
																	'mrv.test.test_conf', 'mrv.test.test_dg', 
																	'mrv.test.test_batch', 'mrv.test.test_mdp', 
																	'mrv.test.test_conf') }) 
                    )
#} END configuration


#{ Common
def init_modules( filepath, moduleprefix, recurse=False, self_module = None):
	""" Call '__initialize' functions in submodules of module at filepath if they exist
	These functions should setup the module to be ready for work, its a callback informing
	the submodules that the super module is being requested. They return a True value if
	the initialization was performed, or a False one if they weren't for some reason.
	Throw to indicate error.
	:param filepath: your module module.__file__ value
	:param moduleprefix: prefix like "super.yourmodule." leading to the submodules from
	an available system include path
	:param recurse: if True, method will recursively initialize submodules
	:param self_module: if not None, it must be the module that called this function.
	It will be given to the __initialize functions as first arguments allowing 
	them to operate on functions of their own module - importing their own 
	module is not yet possible as it is in the course of being intialized itself.
	The module will be given only to intermediate submodules in case recurse is True.
	:note: in this moment, all submodules will be 'pulled' in"""
	moduledir = Path( filepath  ).parent()
	moduleitems = moduledir.listdir( )
	moduleitems.sort()					# assure we have the same order on every system
	extensions = ( ".py", ".pyc", ".pyo" )
	initialized_modules = set()
	
	if not moduleprefix.endswith( "." ):
		moduleprefix += "."

	# import each module
	for path in moduleitems:

		# SUB-PACKAGE ?
		if path.isdir( ):
			if not recurse:
				continue

			packageinitfile = None
			for ext in extensions:
				testpackageinitfile = path / "__init__%s" % ext
				if testpackageinitfile.exists():
					packageinitfile = testpackageinitfile
					break
				# END if packageinit file exists
			# END for each possible extension
			
			# skip non-existing ones
			if not packageinitfile:
				continue
			
			init_modules( packageinitfile, moduleprefix + path.basename(), recurse=True )
			continue
		# END path handling

		if path.ext() not in extensions:
			continue

		modulename = path.namebase()
		if modulename.startswith( "_" ) or modulename.startswith( "." ) or modulename in ('all', 'mdb'):
			continue

		fullModuleName = moduleprefix + modulename
		if fullModuleName in initialized_modules:
			continue
		# END prevent duplicate initialization due to different endings
		initialized_modules.add(fullModuleName)
		module = __import__( fullModuleName , globals(), locals(), [ modulename ] )

		# call init
		args = ( self_module and [ self_module ] ) or tuple()
		if hasattr( module, "__initialize" ):
			res = module.__initialize( *args )
			if res:
				log.info("Initialized " + module.__name__)
			# EMD handle result
	# END for each file or dir


#} END common

#{ Initialization
def _init_syspath( ):
	""" Initialize the path such that additional modules can be found"""
	import site
	mrvroot = os.path.dirname( __file__ )
	
	# fix sys.path: if there are empty entries and our cwd is the mrvroot
	# we will be in trouble as we try to import our own 'maya' module which 
	# will not provide the original maya packages of course.
	# realpath to handle links correctly
	if os.path.realpath(mrvroot) == os.path.realpath(os.getcwd()):
		while '' in sys.path:
			sys.path.remove('')
		# END while we have whitespace
	# END find and remove empty paths
	
	# process additional site-packackes
	# The startup script may add additional site-package paths, but if these
	# are non-default, they will not be handled which leads to an incomplete 
	# environment. Hence we process them.
	# Fortunately, the function handles multiple initializations gracefully
	for syspath in sys.path[:]:
		if syspath.endswith('site-packages'):
			site.addsitedir(syspath, set(sys.path))
		# END found site-packages path
	# END for each path to possibly initialize
	
	# get external base
	extbase = os.path.join( mrvroot, "ext" )

	# pyparsing
	pyparsing = os.path.join( extbase, "pyparsing", "src" )

	# pydot
	pydot = os.path.join( extbase, "pydot" )

	# networkx
	networkxpath = os.path.join( extbase, "networkx" )

	# add all to the path
	sys.path.append( pyparsing )
	sys.path.append( pydot )
	sys.path.append( networkxpath )


# end __init_syspath


def _init_configProvider( ):
	""" Install the configuration provider system

	This allows values and settings to be stored in a convenient way. """
	pass

def _init_internationalization( ):
	"""Install internationalization module

	Using the default python gettext module, internationalization compatibility
	can be garantueed.

	Will map the '_' function to translate enclosed strings """
	import gettext
	gettext.install( "mrv" )


def _init_logging( ):
	""" Initialize the default mrv logging interface

	The logging interface unifies the way messages for the end user are handled
	and assure a flexible message handling.
	
	:note: will not raise even if the logging module could not be setup
	
	:note: in the current implementation, it is based on the default python logging
		package"""
	logcfgfile = os.environ.get('MRV_LOGGING_INI', None)
	if logcfgfile is None:
		return
		
	try:
		logcfgfile = Path(logcfgfile).expand_or_raise()
		logging.config.fileConfig(logcfgfile)
	except Exception, e:
		print "Failed to apply logging configuration at %s with error: %s" % (logcfgfile, str(e))
	else:
		log.debug("Initialized logging configuration from file at %s" % logcfgfile)
	# END exception handling
	


def _init_python( ):
	"""
	Assure that certain python classes have the least possible amount of compatablity
	so that we can work with them
	"""
	

#} END initialization

# INITIALIZE
#############
_init_syspath( )
_init_configProvider( )
_init_internationalization( )
_init_logging( )
_init_python( )