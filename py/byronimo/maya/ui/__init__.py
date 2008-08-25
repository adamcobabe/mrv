"""B{byronimo.maya.ui}
Initialize the UI framework allowing convenient access to most common user interfaces

All classes of the ui submodules can be accessed by importing this package. 

@newfield revision: Revision
@newfield id: SVN Id
"""
__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-30 16:59:35 +0200 (Wed, 30 Jul 2008) $"
__revision__="$Revision: 29 $"
__id__="$Id: configuration.py 29 2008-07-30 14:59:35Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import byronimo.maya as bmaya
from byronimo.util import capitalize, uncapitalize
from byronimo.maya.util import MetaClassCreator
from byronimo.path import Path
_thismodule = __import__( "byronimo.maya.ui", globals(), locals(), ['ui'] )
import maya.cmds as mcmds



############################
#### Exceptions		 	####
#########################



#####################
#### META 		####
##################

class MetaClassCreatorUI( MetaClassCreator ):
	""" Builds the base hierarchy for the given classname based on our
	typetree """
	
	melcmd_attrname = '__melcmd__'
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global _typetree
		global _thismodule

		cmdname = uncapitalize( name )
		if hasattr( mcmds, cmdname ):
			clsdict['__melcmd__'] = staticmethod( getattr( mcmds, cmdname ) ) 
		else:
			pass # don't bother, can be one of our own classes that will 
			#raise UIError( "Did not find command for " + cmdname ) 	
				
		newcls = super( MetaClassCreatorUI, metacls ).__new__( _typetree, _thismodule, 
																metacls, name, bases, clsdict )
				
		# print newcls.mro()
		return newcls



############################
#### CACHES		 	   ####
#########################
_typetree = None
_typemap = { "floatingWindow" : "window" } 




############################
#### INITIALIZATION   ####
#########################


def init_classhierarchy( ):
	""" Read a simple hiearchy file and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent / "cache/UICommandsHierachy"

	# STORE THE TYPE TREE
	global _typetree
	_typetree = bmaya._dagTreeFromTupleList( bmaya._tupleListFromFile( mfile ) )
	

def init_wrappers( ):
	""" Create Standin Classes that will delay the creation of the actual class till 
	the first instance is requested"""	 
	global _typetree
	global _thismodule
	bmaya._initWrappers( _thismodule, _typetree.nodes_iter(), MetaClassCreatorUI )


if 'init_done' not in locals():
	init_done = False
	

if not init_done:
	init_classhierarchy()				# populate hierarchy DAG from cache
	init_wrappers( )					# create wrappers for all classes
	
	# assure we do not run several times
	# import modules - this way we overwrite actual wrappers lateron
	from base import *
	from controls import *
	from dialogs import *
	from layouts import *
	
	
init_done = True