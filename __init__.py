# -*- coding: utf-8 -*-
"""B{mayarv.init}

Initialize mayarv system assisting development, debugging and maintenance

	- install general L{decorators} into __builtin__ namespace

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'

import __builtin__
from inspect import isfunction

# EXPORTsd
__all__ = []


import os, sys
from path import Path


#{ Common
def init_modules( filepath, moduleprefix, recurse=False ):
	""" Call '__initialize' functions in submodules of module at filepath if they exist
	These functions should setup the module to be ready for work, its a callback informing
	the submodules that the super module is being requested
	@param filepath: your module module.__file__ value
	@param moduleprefix: prefix like "super.yourmodule." leading to the submodules from
	an available system include path
	@param recurse: if True, method will recursively initialize submodules
	@note: in this moment, all submodules will be 'pulled' in"""
	moduledir = Path( filepath  ).p_parent
	moduleitems = moduledir.listdir( )
	moduleitems.sort()					# assure we have the same order on every system

	if not moduleprefix.endswith( "." ):
		moduleprefix += "."

	# import each module
	for path in moduleitems:

		# SUB-PACKAGE ?
		if path.isdir( ):
			if not recurse:
				continue

			packageinitfile = path / "__init__.py"
			if not packageinitfile.exists():
				continue

			init_modules( packageinitfile, moduleprefix + path.basename(), recurse=True )
			continue
		# END path handling

		if path.p_ext != ".py":
			continue

		modulename = path.p_namebase
		if modulename.startswith( "_" ) or modulename.startswith( "." ):
			continue

		fullModuleName = moduleprefix + modulename
		module = __import__( fullModuleName , globals(), locals(), [ modulename ] )

		# call init
		if hasattr( module, "__initialize" ):
			print "Initializing " + module.__name__
			module.__initialize( )
	# END for each file or dir

#} END common

#{ Initialization
def _init_syspath( ):
	""" Initialize the path such that additional modules can be found"""
	# get external base
	extbase = os.path.join( os.path.split( __file__ )[0], "ext" )

	# pyparsing
	pyparsing = os.path.join( extbase, "pyparsing" )

	# pydot
	pydot = os.path.join( extbase, "pydot" )

	# networkx
	networkxpath = os.path.join( extbase, "networkx" )

	# add all to the path
	sys.path.append( pyparsing )
	sys.path.append( pydot )
	sys.path.append( networkxpath )


# end __init_syspath


def _init_decorators( ):
	"""Installs general decorators

	Decorators will help maintaining the system - this method installs
	them in the __builtin__ namespace to make them available to all L{mayarv}
	classes """
	import decorators

	pred = lambda x: isfunction( x ) and not x.func_name.startswith( "_" )
	decorator_functions = [ func for func in decorators.__dict__.itervalues() if pred( func ) ]

	# put decoratrors into __builtin__ namespace
	for func in decorator_functions:
		__builtin__.__dict__[ func.func_name ] = func

	# add the interface class to the builtin namespace also
	__builtin__.__dict__[ 'interface' ] = decorators.interface


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
	gettext.install( "mayarv" )


def _init_logging( ):
	""" Initialize the default mayarv logging interface

	The logging interface unifies the way messages for the end user are handled
	and assure a flexible message handling.

	@note: in the current implementation, it is based on the default python logging
	package """
	pass


def _init_python( ):
	"""
	Assure that certain python classes have the least possible amount of compatablity
	so that we can work with them
	"""
	# must have proper exceptions
	e = Exception()
	if not hasattr( e, 'message' ):
		# put in a special __init__ function
		Exception.__init__old = Exception.__init__
		def myinit( self, *args, **kwargs ):
			self.message = ''
			Exception.__init__old( self, *args, **kwargs )

		Exception.__init__ = myinit

#} END initialization

# INITIALIZE
#############
_init_syspath( )
_init_decorators( )
_init_configProvider( )
_init_internationalization( )
_init_logging( )
_init_python( )