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

from byronimo.exceptions import ByronimoError
from byronimo.util import capitalize, uncapitalize, DAGTree
from byronimo.maya.util import MetaClassCreator
from byronimo.path import Path
from byronimo.maya.util import StandinClass
_thismodule = __import__( "byronimo.maya.ui", globals(), locals(), ['ui'] )
import maya.cmds as mcmds


############################
#### Exceptions		 	####
#########################
class  UIError( ByronimoError ):
	""" Base Class for all User Interface errors"""
	pass 



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
			clsdict['__melcmd__'] = getattr( mcmds, cmdname ) 
		else:
			pass # don't bother, can be one of our own classes that will 
			#raise UIError( "Did not find command for " + cmdname ) 	
				
		newcls = super( MetaClassCreatorUI, metacls ).__new__( _typetree, _thismodule, 
																metacls, name, bases, clsdict, 
																nameToTreeFunc=uncapitalize,
																treeToNameFunc=capitalize )
				
		# print newcls.mro()
		return newcls



############################
#### CACHES		 	   ####
#########################
_typetree = None
_uiinstances = {}			# keeps all instances we created so far 




############################
#### INITIALIZATION   ####
#########################


def init_uiclasshierarchy( ):
	""" Read a simple hiearchy file and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent / "cache/UICommandsHierachy"
	lines = mfile.lines( retain=False )
	
	tree = None
	lastparent = None
	lastchild = None
	lastlevel = 0
	
	# PARSE THE FILE INTO A TREE 
	# currently we expect all the nodes to have one root class 
	for no,line in enumerate( mfile.lines( retain=False ) ):
		level = line.count( '\t' )
		name = line.lstrip( '\t' )
		
		if level == 0:
			if tree != None:
				raise ByronimoError( "Ui tree must currently be rooted - thus there must only be one root node, found another: " + name )
			else:
				tree = DAGTree(  )		# create root
				tree.add_node( name )
				lastparent = name
				lastchild = name
				continue
		
		direction = level - lastlevel 
		if abs( direction ) > 1:
			raise ByronimoError( "Can only change by one level, changed by %i" % direction )
			
		lastlevel = level
		if direction == 0:
			pass 
		elif direction == 1 :
			lastparent = lastchild
		elif direction == -1:
			lastparent = tree.parent( lastparent )
			
		tree.add_edge( ( lastparent, name ) )
		lastchild = name
	# END for each line in hiearchy map
	
	# STORE THE TYPE TREE
	global _typetree
	_typetree = tree
	

def init_uiwrappers( ):
	""" Create dummy classes that will create the actual class once creation is
	requested.
	NOTE: must be called once all custom written UI classes are available in this module """	 
	
	# create dummy class that will generate the class once it is first being instatiated
	global _typetree
	global _thismodule
	
	class Holder:
		def __init__( self, name ):
			self.name = name
	
	for uitype in _typetree.nodes_iter( ):
		clsname = capitalize( uitype )
		
		# do not overwrite hand-made classes
		if clsname in _thismodule.__dict__:
			continue

		_thismodule.__dict__[ clsname ] = StandinClass( clsname, MetaClassCreatorUI )
	# END for each uitype


if 'init_done' not in locals():
	init_done = False
	

if not init_done:
	init_uiclasshierarchy()				# populate hierarchy DAG from cache
	init_uiwrappers( )					# create wrappers for all classes
	
	# assure we do not run several times
	# import modules - this way we overwrite actual wrappers lateron
	from base import *
	from dialogs import *
	from layouts import *
	
	
init_done = True