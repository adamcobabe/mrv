"""B{byronimo.automation.processes}
Contains all processes 

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

_this_module = __import__( "byronimo.automation.processes", globals(), locals(), ['processes'] )
from base import ProcessBase

#} Interface
def addProcesses( *args ):
	"""Add the given process classes to the list of known process types. They will be regeistered
	with their name obtained by str( processCls ). 
	Workflows loaded from files will have access to the processes in this package
	@param *args: process classes to be registered to this module."""
	global _this_module
	for pcls in args:
		if ProcessBase not in pcls.mro():
			raise TypeError( "%r does not support the process interface" % pcls )
	
	setattr( _this_module, pcls.__name__, pcls )
	# END for each arg 

#} END interface

# assure we only do certain things once
if 'init_done' not in locals():
	init_done = False
	
# SYSTEM INITIALIZATION
if not init_done:
	# import everything into the processes module 
	from base import *

#} END initialization





