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
import byronimo.maya.util as mutil


############################
#### Methods		  	####
##########################

def getUIType( uiname ):
	"""@return: uitype string having a corresponding mel command - some types returned do not correspond
	to the actual name of the command used to manipulate the type """
	uitype = cmds.objectTypeUI( uiname )
	return ui._typemap.get( uitype, uitype )
	

def wrapUI( uinameOrList ):
	""" @return: a new instance ( or list of instances ) of a suitable python UI wrapper class for the 
	UI with the given uiname(s)
	@param uinameOrList: if single name, a single instance will be returned, if a list of names is given, 
	a list of respective instances. None will be interpreted as empty list
	@raise RuntimeError: if uiname does not exist or is not wrapped in python """
	uinames = uinameOrList
	islisttype = isinstance( uinameOrList, ( tuple, list, set ) ) 
	if not islisttype:
		if uinameOrList is None:
			islisttype = True
			uinames = []
		else:
			uinames = [ uinameOrList ]
	# END input list handling 
	
	out = []
	for uiname in uinames:
		uitype = getUIType( uiname )
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
	@return: [] of NamedUI instances of respective UI elements """
	long = kvargs.pop( 'long', kvargs.pop( 'l', True ) )
	head = kvargs.pop( 'head', kvargs.pop( 'hd', None ) )
	tail = kvargs.pop( 'tail', kvargs.pop( 'tl', None) )
	
	if not kvargs:
		kvargs = { 
			'windows': 1, 'panels' : 1, 'editors' : 1, 'controls' : 1, 
			'controlLayouts' : 1,'collection' : 1, 'radioMenuItemCollections' : 1, 
			'menus' : 1, 'menuItems' : 1, 'contexts' : 1, 'cmdTemplates' : 1 }
	# END kvargs handling
	
	kvargs['long'] = long
	if head is not None: kvargs['head'] = head
	if tail is not None: kvargs['tail'] = tail
	
	# NOTE: controls and controlLayout will remove duplcate entries - we have to 
	# prune them ! Unfortunately, you need both flags to get all items, even layouts 
	return wrapUI( set( cmds.lsUI( **kvargs ) ) )


############################
#### Classes		  	####
##########################

class Callback(object):
    """ Enables deferred function evaulation with 'baked' arguments.
    Useful where lambdas won't work as they bind to the free variables instead of 
	to their values.
    Example: 
        def addRigger(rigger):
            ...
            
        for rigger in riggers:
            pm.menuItem(
                label = "Add " + str(rigger),
                c = Callback(addRigger,rigger,p=1))   # will run: addRigger(rigger,p=1)
	@note: from pymel """
    def __init__(self,func,*args,**kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def __call__(self,*args):
        return self.func(*self.args,**self.kwargs)
		

class BaseUI( object ):
	
	__melcmd__	= None					# every class deriving directly from it must define this !
	
	def __init__( self, *args, **kvargs ):
		if self.__class__ == BaseUI:
			raise ui.UIError( "Cannot instantiate" + self.__class__.__name__ + " directly - it can only be a base class" )
		
		return object.__init__(self, *args, **kvargs )
		

class NamedUI( unicode, BaseUI ):
	"""Implements a simple UI element having a name  and most common methods one 
	can apply to it. Derived classes should override these if they can deliver a
	faster implementation. 
	If the 'name' keyword is supplied, an existing UI element will be wrapped
	@note: although many access methods look quite 'repeated' as they are quite
	similar except for a changing flag, they are hand-written to provide proper docs for them"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	
	#{ Overridden Methods 
	def __new__( cls, name=None, *args, **kvargs ):
		"""If name is given, the newly created UI will wrap the UI with the given name.
		Otherwise the UIelement will be created"""
		if name is None:
			name = cls.__melcmd__( *args, **kvargs )
	
		return unicode.__new__( cls, name )
		
	def __repr__( self ):
		return u"%s('%s')" % ( self.__class__.__name__, self )
	
		
	def __init__( self , *args, **kvargs ):
		""" Initialize instance and check arguments """
		# assure that new instances are being created initially
		forbiddenKeys = [ 'edit', 'e' , 'query', 'q' ]
		for fkey in forbiddenKeys:
			if fkey in kvargs:
				raise ui.UIError( "Edit or query flags are not permitted during initialization as interfaces must be created onclass instantiation" )
			# END if key found in kvargs
		# END for each forbidden key
		
		return BaseUI.__init__( self, *args, **kvargs )
	#} END overridden methods
			
	#{ Hierachy Handling
	def getChildren( self, **kvargs ):
		"""@return: all intermediate child instances
		@note: the order of children is lexically ordered at this time 
		@note: this implementation is slow and should be overridden by more specialized subclasses"""
		return filter( lambda x: len( x.replace( self , '' ).split('|') ) - 1 ==len( self.split( '|' ) ), self.getChildrenDeep() )
		
	def getChildrenDeep( self, **kvargs ):
		"""@return: all child instances recursively
		@note: the order of children is lexically ordered at this time 
		@note: this implementation is slow and should be overridden by more specialized subclasses"""
		kvargs['long'] = True
		return filter( lambda x: x.startswith(self) and not x == self, lsUI(**kvargs))
		
	def getParent( self ):
		"""@return: parent instance of this ui element"""
		return wrapUI( '|'.join( self.split('|')[:-1] ) )
	#}	END hierarchy handling
	
	#{ Query Methods 
	def isVisible( self ):
		"""@return : True if the UI element is visible """
		return self.__melcmd__( self, q=1, v=1 )
	
	def isManaged( self ):
		"""@return : True if the UI element is managed """
		return self.__melcmd__( self, q=1, m=1 )
	
	def isEnabled( self ):
		"""@return : True if the UI element is enabled """
		return self.__melcmd__( self, q=1, en=1 )

	def getAnnotation( self ):
		"""@return : the annotation string """
		try:
			return self.__melcmd__( self, q=1, ann=1 )
		except TypeError:
			return ""
			
	def getDimension( self ):
		"""@return: (x,y) tuple of x and y dimensions of the UI element""" 
		return ( self.__melcmd__( self, q=1, w=1 ), self.__melcmd__( self, q=1, h=1 ) )
		
	#}END query methods
	
	#{ Edit Methods 
	def setVisible( self, state ):
		"""Set the UI element (in)visible"""
		self.__melcmd__( self, e=1, v=state )
	
	def setManaged( self, state ):
		"""Set the UI element (un)managed"""
		self.__melcmd__( self, e=1, m=state )
		
	def setEnabled( self, state ):
		"""Set the UI element enabled"""
		self.__melcmd__( self, e=1, en=state )
	
	def setAnnotation( self, ann ):
		"""Set the UI element's annotation
		@note: not all named UI elements can have their annotation set"""
		self.__melcmd__( self, e=1, ann=ann )
	
	def setDimension( self, dimension ):
		"""Set the UI elements dimension
		@param dimension: (x,y) : tuple holding desired x and y dimension""" 
		self.__melcmd__( self, e=1, w=dimension[0] ) 
		self.__melcmd__( self, e=1, h=dimension[1] )
		
	#}END edit methods 
	
	
	def type( self ):
		"""@return: the python class able to create this class 
		@note: The return value is NOT the type string, but a class """
		uitype = getUIType( self )
		return getattr( ui, capitalize( uitype ) )
	
	def shortName( self ):
		"""@return: shortname of the ui ( name without pipes )"""
		return self.split('|')[-1]
	
	def delete( self ):
		"""Delete this UI - the wrapper instance must not be used after this call"""
		cmds.deleteUI( self )
		
	#{ Properties
	p_visible = property( isVisible, setVisible )
	p_managed = property( isManaged, setManaged )
	p_enabled = property( isEnabled, setEnabled )
	p_annotation = property( getAnnotation, setAnnotation )
	p_dimension = property( getDimension, setDimension )
	p_parent = property( getParent )
	p_children = property( getChildren )
	#} END properties
		
		

class Window( NamedUI ):
	"""Simple Window Wrapper"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	#{ Window Specific Methods
	
	def show( self ):
		""" Show Window"""
		cmds.showWindow( self )
		
	def delete( self ):
		""" Delete window """
		cmds.deleteUI( self )
	
	def getMenuArray( self ):
		"""@return: Menu instances attached to this window"""
		return wrapUI( self.__melcmd__( self, q=1, menuArray=1 ) )
		
	#} END window speciic
	
	#{ Properties
	p_title = mutil.propertyQE( cmds.window, 'title' )
	p_iconify = mutil.propertyQE( cmds.window, 'iconify' )
	p_sizeable = mutil.propertyQE( cmds.window, 'sizeable' )
	p_iconname = mutil.propertyQE( cmds.window, 'iconName' )
	p_titlebar = mutil.propertyQE( cmds.window, 'titleBar' )
	p_minimizebutton = mutil.propertyQE( cmds.window, 'mnb' )
	p_maximizebutton = mutil.propertyQE( cmds.window, 'mxb' )
	p_toolbox = mutil.propertyQE( cmds.window, 'toolbox' )
	p_titlebarmenu = mutil.propertyQE( cmds.window, 'tbm' )
	p_menubarvisible = mutil.propertyQE( cmds.window, 'mbv' )
	p_topleftcorner = mutil.propertyQE( cmds.window, 'tlc' )
	#}
