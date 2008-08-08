"""B{byronimo.ui.base}

Contains some basic  classes that are required to run the UI system
@note: user defined classes must not name the default base classes explicitly as 
they will receive the bases as defined in the UICache Tree. If there is some additional 
base though, it should be given as super class of course.
@todo: more documentation

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


ui = __import__( "byronimo.maya.ui",globals(), locals(), ['ui'] )
import maya.cmds as cmds
from byronimo.util import capitalize


############################
#### Methods		  	####
##########################
def wrapUI( uinameOrList ):
	""" @return: a new instance ( or list of instances ) of a suitable python UI wrapper class for the 
	UI with the given uiname(s)
	@param uinameOrList: if single name, a single instance will be returned, if a list of names is given, 
	a list of respective instances
	@raise RuntimeError: if uiname does not exist or is not wrapped in python """
	uinames = uinameOrList
	islisttype = isinstance( uinameOrList, ( tuple, list ) ) 
	if not islisttype:
		uinames = [ uinameOrList ]
		
	out = []
	for uiname in uinames:
		uitype = cmds.objectTypeUI( uiname )
		clsname = capitalize( uitype )
		
		try:
			out.append( getattr( ui, clsname )( name=uiname ) )
		except:
			RuntimeError( ui.__name__ + " has no class named " + clsname )
	# END for each uiname
	
	if islisttype:
		return out
	
	return out[0]
	
	
def lsUI( **kvargs ):
	""" List UI elements as python wrapped types 
	@param **kvargs: flags from the respective maya command are valid
	If no special type keyword is specified, all item types will be returned
	@return: [] of NamedUI instances of respective UI elements
	"""
	long = kwargs.pop( 'long', kwargs.pop( 'l', False ) )
    head = kwargs.pop( 'head', kwargs.pop( 'hd', None ) )
    tail = kwargs.pop( 'tail', kwargs.pop( 'tl', None) )
    
    if not kwargs:
        kwargs = { 
            'windows': 1, 'panels' : 1, 'editors' : 1, 'controls' : 1, 'controlLayouts' : 1,
            'collection' : 1, 'radioMenuItemCollections' : 1, 'menus' : 1, 'menuItems' : 1, 'contexts' : 1, 'cmdTemplates' : 1 }
    kwargs['long'] = long
    if head is not None: kwargs['head'] = head
    if tail is not None: kwargs['tail'] = tail


############################
#### Classes		  	####
##########################

class BaseUI( object ):
	
	__melcmd__	= None					# every class deriving directly from it must define this !
	
	def __init__( self, *args, **kvargs ):
		if self.__class__ == BaseUI:
			raise ui.UIError( "Cannot instantiate" + self.__class__.__name__ + " directly - it can only be a base class" )
		
		return object.__init__(self, *args, **kvargs )
		

class NamedUI( unicode, BaseUI ):
	""" Implements a simple UI element having a name  and most common methods one 
	can apply to it. Derived classes should override these if they can deliver a
	faster implementation 
	If the 'name' keyword is supplied, an existing UI element will be wrapped"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __new__( cls, name=None, *args, **kvargs ):
		"""If name is given, the newly created UI will wrap the UI with the given name.
		Otherwise the UIelement will be created"""
		if name is None:
			name = cls.__melcmd__( *args, **kvargs )
	
		return unicode.__new__( cls, name )
		
	def __repr__( self ):
		return u"%s('%s')" % ( self.__class__.__name__, self )
	
		
	def __init__( self , *args, **kvargs ):
		
		# assure that new instances are being created initially
		forbiddenKeys = [ 'edit', 'e' , 'query', 'q' ]
		for fkey in forbiddenKeys:
			if fkey in kvargs:
				raise ui.UIError( "Edit or query flags are not permitted during initialization as interfaces must be created onclass instantiation" )
			# END if key found in kvargs
		# END for each forbidden key
		
		return BaseUI.__init__( self, *args, **kvargs )
			
	def getChildren( self, **kwargs ):
		kwargs['long'] = True
		return filter( lambda x: x.startswith(self) and not x == self, lsUI(**kwargs))
		
	def getParent( self ):
		return UI( '|'.join( self.split('|')[:-1] ) )
		
	def type( self ):
		return objectTypeUI(self)
		
	def shortName( self ):
		return self.split('|')[-1]
		
	#delete = _factories.functionFactory( 'deleteUI', _thisModule, rename='delete' )
	#rename = _factories.functionFactory( 'renameUI', _thisModule, rename='rename' )
	#type = _factories.functionFactory( 'objectTypeUI', _thisModule, rename='type' )
     

class Window( NamedUI ):
	"""Simple Window Wrapper"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	def show( self ):
		cmds.showWindow( self )
		
	def delete(self):
		cmds.deleteUI( self , window=True )
