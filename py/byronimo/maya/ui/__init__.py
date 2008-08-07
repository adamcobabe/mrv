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

from byronimo.util import capitalize, uncapitalize, DAGTree
from byronimo.path import Path
from byronimo.exceptions import ByronimoError
from byronimo.maya.util import StandinClass
_thismodule = __import__( "byronimo.maya.ui", globals(), locals(), ['ui'] )

#####################
#### META 		####
##################

class MetaUIClassCreator( type ):
	""" Builds the base hierarchy for the given classname based on our
	typetree """
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		
		# recreate the hierarchy of classes leading to the current type
		global _typetree
		nameNoCap = uncapitalize( name )
		parentclsname = capitalize( _typetree.parent( nameNoCap ) )
		
		parentcls = _thismodule.__dict__[ parentclsname ]
		if isinstance( parentcls, StandinClass ):
			parentcls = parentcls.createCls( )
		
		bases += ( parentcls, )
		
		# create the class 
		# newcls = type.__new__( metacls, name, bases, clsdict )
		newcls = super( MetaUIClassCreator, metacls ).__new__( metacls, name, bases, clsdict )
		
		# replace the dummy class in the module 
		global _thismodule
		_thismodule.__dict__[ name ] = newcls
		
		return newcls


#####################
#### CLASSES	####
##################


class BaseUI(object):
	def __init__( self, *args, **kvargs ):
		return object.__init__(self, *args, **kvargs )
		

class NamedUI( BaseUI ):
    def __repr__(self):
        return u"%s('%s')" % (self.__class__.__name__, self)
		
    def getChildren(self, **kwargs):
        kwargs['long'] = True
        return filter( lambda x: x.startswith(self) and not x == self, lsUI(**kwargs))
		
    def getParent(self):
        return UI( '|'.join( self.split('|')[:-1] ) )
		
    def type(self):
        return objectTypeUI(self)
		
    def shortName(self):
        return self.split('|')[-1]
    #delete = _factories.functionFactory( 'deleteUI', _thisModule, rename='delete' )
    #rename = _factories.functionFactory( 'renameUI', _thisModule, rename='rename' )
    #type = _factories.functionFactory( 'objectTypeUI', _thisModule, rename='type' )
     




############################
#### TYPE CACHE	 	   ####
#########################
_typetree = None 



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
	init_uiclasshierarchy()
	
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

		_thismodule.__dict__[ clsname ] = StandinClass( clsname, MetaUIClassCreator )
	# END for each uitype


if 'init_done' not in locals():
	init_done = False
	

if not init_done:
	# assure we do not run several times
	# import modules 
	from dialogs import *
	from layouts import *
	
	init_uiwrappers( )
	
init_done = True