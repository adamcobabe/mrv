"""B{byronimo.init}

Initialize Byronimo system assisting development, debugging and maintenance 

	- install general L{decorators} into __builtin__ namespace
	
@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'

import __builtin__
from inspect import isfunction

def init_decorators( ):
	"""Installs general decorators
	
	Decorators will help maintaining the system - this method installs 
	them in the __builtin__ namespace to make them available to all L{byronimo}
	classes """
	import byronimo.decorators
	
	pred = lambda x: isfunction( x ) and not x.func_name.startswith( "_" )
	decorator_functions = [ func for func in byronimo.decorators.__dict__.itervalues() if pred( func ) ]
	
	# put decoratrors into __builtin__ namespace
	for func in decorator_functions:
		__builtin__.__dict__[ func.func_name ] = func
		
	# add the interface class to the builtin namespace also 
	__builtin__.__dict__[ 'interface' ] = byronimo.decorators.interface
	
	
def init_configProvider( ):
	""" Install the configuration provider system 
	
	This allows values and settings to be stored in a convenient way. """
	pass
	
def init_internationalization( ):
	"""Install internationalization module
	
	Using the default python gettext module, internationalization compatibility
	can be garantueed.
	
	Will map the '_' function to translate enclosed strings """
	import gettext
	gettext.install( "byronimo" )
	

def init_logging( ):
	""" Initialize the default byronimo logging interface
	
	The logging interface unifies the way messages for the end user are handled
	and assure a flexible message handling.
	
	@note: in the current implementation, it is based on the default python logging 
	package """
	pass 
	
	
# INITIALIZE
#############
init_decorators( )
init_configProvider( )
init_internationalization( )
init_logging( )