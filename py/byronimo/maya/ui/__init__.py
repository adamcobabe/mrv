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

from byronimo.util import capitalize, uncapitalize
from byronimo.path import Path
from networkx.trees import DirectedTree

class NamedUI(unicode):
    def __new__( cls, name=None, create=False, *args, **kwargs ):
        """ Provides the ability to create the UI Element when creating a class
		@note: based on pymel """
		
		# if a parent is requested, the element needs to be created !
        parent = kwargs.get( 'parent', kwargs.get('p', None))
        if name is None or create or parent:
            name = cls.__melcmd__()(name, *args, **kwargs)
			
        return unicode.__new__(cls,name)
    
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
#### INITIALIZATION   ####
#########################


def init_uiclasshierarchy( ):
	""" Read a simple hiearchy file and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent / "cache/UICommandsHierachy"
	lines = mfile.lines( retain=False )
	
	#lastParent = None
	#lastLevel = 0
	#tree = DirectedTree( )
	#for no,line in enumerate( mfile.lines( retain=False ) ):
	#	level = line.count( '\t' )
	#	name = line.lstrip( '\t' )
	#	tree.add( name, parent=lastParent )
	
	


def init_uiwrappers( ):
	""" Create dummy classes that will create the actual class once creation is
	requested. 
	"""
	
	init_uiclasshierarchy()
	
	pass 

if 'init_done' not in locals():
	init_done = False
	

if not init_done:
	# assure we do not run several times
	# import modules 
	from dialogs import *
	from layouts import *
	
	init_uiwrappers( )
	
init_done = True