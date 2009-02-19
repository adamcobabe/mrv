# -*- coding: utf-8 -*-
"""B{byronimo.ui.base}

Contains some basic  classes that are required to run the UI system

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
import weakref
import maya.cmds as cmds
from byronimo.util import capitalize, iDagItem
from util import CallbackBaseUI
import byronimo.maya.util as mutil
import util as uiutil
from byronimo.exceptions import ByronimoError


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
			out.append( getattr( ui, clsname )( name=uiname,  wrap_only = 1 ) )
		except AttributeError:
			RuntimeError( ui.__name__ + " has no class named " + clsname )
	# END for each uiname
	
	if islisttype:
		return out
	
	return out[0]
	
	
def lsUI( **kwargs ):
	""" List UI elements as python wrapped types 
	@param **kwargs: flags from the respective maya command are valid
	If no special type keyword is specified, all item types will be returned
	@return: [] of NamedUI instances of respective UI elements """
	long = kwargs.pop( 'long', kwargs.pop( 'l', True ) )
	head = kwargs.pop( 'head', kwargs.pop( 'hd', None ) )
	tail = kwargs.pop( 'tail', kwargs.pop( 'tl', None) )
	
	if not kwargs:
		kwargs = { 
			'windows': 1, 'panels' : 1, 'editors' : 1, 'controls' : 1, 
			'controlLayouts' : 1,'collection' : 1, 'radioMenuItemCollections' : 1, 
			'menus' : 1, 'menuItems' : 1, 'contexts' : 1, 'cmdTemplates' : 1 }
	# END kwargs handling
	
	kwargs['long'] = long
	if head is not None: kwargs['head'] = head
	if tail is not None: kwargs['tail'] = tail
	
	# NOTE: controls and controlLayout will remove duplcate entries - we have to 
	# prune them ! Unfortunately, you need both flags to get all items, even layouts 
	return wrapUI( set( cmds.lsUI( **kwargs ) ) )


############################
#### Classes		  	####
##########################

class BaseUI( object ):
	
	__melcmd__	= None					# every class deriving directly from it must define this !
	
	def __init__( self, *args, **kwargs ):
		if self.__class__ == BaseUI:
			raise ByronimoError( "Cannot instantiate" + self.__class__.__name__ + " directly - it can only be a base class" )
		
		# return object.__init__( self , *args, **kwargs )
		super( BaseUI, self ).__init__( *args, **kwargs )
		

class NamedUI( unicode, BaseUI , iDagItem, CallbackBaseUI ):
	"""Implements a simple UI element having a name  and most common methods one 
	can apply to it. Derived classes should override these if they can deliver a
	faster implementation. 
	If the 'name' keyword is supplied, an existing UI element will be wrapped
	
	Events 
	-------
	As subclass of CallbackBaseUI, it can provide events that are automatically 
	added by the metaclass as described by the _events_ attribute list.
	This allows any number of clients to register for one maya event. Derived classes
	may also use their own events which is useful if you create components
	
	Register for an event like:K 
	uiinstance.e_eventlongname = yourFunction( sender, *args, **kwargs )
	*args and **kwargs are determined by maya
	
	@note: although many access methods look quite 'repeated' as they are quite
	similar except for a changing flag, they are hand-written to provide proper docs for them"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	#( Configurtation 
	_sep = "|"			# separator for ui elements in their name, same as for dag paths 
	_is_menu = False	# if True, some methods will handle special cases for menus
	#) end configuration 
	
	#{ Overridden Methods
	@classmethod
	def _exists( cls, uiname ):
		"""@return: 1 if the given UI element exists, 0 if it does not exist 
		and 2 it exists but the passed in name does not guarantee there are not more 
		objects with the same name"""
		try:
			uitype = cmds.objectTypeUI( uiname )
		except RuntimeError:
			return 0
		else:
			# short names can only be used with top level items like 
			# windows - for everything else we cannot know how many items 
			# with the same name exist and which one we should actually wrap
			# Claim it does not exist
			if "Window" not in uitype and cls._sep not in uiname:
				return 2
			return 1 
			
	def __new__( cls, *args, **kwargs ):
		"""If name is given, the newly created UI will wrap the UI with the given name.
		Otherwise the UIelement will be created
		@param name: name of the user interface to wrap or the target name of a new elf element.
		Valid names for creation are short names ( without a | in it's path ), valid names 
		for wrapping are short and preferably long names.
		@param wrap_only: if True, default False, a wrap will be done even if the passed 
		in name uses the short form ( for non-window elements ). If it exists, one cannot be sure
		whether more elements with the given name exist. If False, the system will create a new 
		element of our type.
		@note: you can use args safely for your own purposes 
		@note: if name is set but does not name a valid user interface, a new one 
		will be created, and passed to the constructor"""
		name = kwargs.pop( "name", None )
		exists = ( ( name is not None ) and NamedUI._exists( str( name ) ) ) or False
		
		# pretend named element does not exist if existance is ambigous
		if not kwargs.pop( "wrap_only", False ) and exists == 2:
			exists = 0
			
		if name is None or not exists:
			try:
				if name:	# use name to create named object
					name = cls.__melcmd__( name, **kwargs )
					
					# assure we have a long name - mel sometimes returns short ones 
					# that are ambigous ... 
					if cls._sep not in name and Window not in cls.mro():
						raise AssertionError( "%s instance named '%s' does not have a long name after creation" % ( cls, name ) )
				else:
					name = cls.__melcmd__( **kwargs )
			except (RuntimeError,TypeError), e:
				raise RuntimeError( "Creation of %s using melcmd %s failed: %s" % ( cls, cls.__melcmd__, str( e ) ) )
			# END name handling 
		# END auto-creation as required 
			
		return unicode.__new__( cls, name )
		
	def __repr__( self ):
		return u"%s('%s')" % ( self.__class__.__name__, self )
	
	def __setattr__( self, attr, value ):
		"""Prevent properties or events that do not exist to be used by anyone, 
		everything else is allowed though"""
		if ( attr.startswith( "p_" ) or attr.startswith( "e_" ) ):
			try:
				getattr( self, attr )
			except AttributeError:
				raise AttributeError( "Cannot create per-instance properties or events: %s.%s ( did you misspell an existing one ? )" % ( self, attr ) )
			except Exception:
				# if there was another exception , then the attribute is at least valid and MEL did not want to 
				# accept the querying of it 
				pass 
			# END exception handling 
		# END check attribute validity 
		return super( NamedUI, self ).__setattr__( attr, value )
		
	def __init__( self , *args, **kwargs ):
		""" Initialize instance and check arguments """
		# assure that new instances are being created initially
		forbiddenKeys = [ 'edit', 'e' , 'query', 'q' ]
		for fkey in forbiddenKeys:
			if fkey in kwargs:
				raise ui.UIError( "Edit or query flags are not permitted during initialization as interfaces must be created onclass instantiation" )
			# END if key found in kwargs
		# END for each forbidden key
		
		super( NamedUI, self ).__init__( *args, **kwargs )
		#return BaseUI.__init__( self, *args, **kwargs )
	#} END overridden methods
			
	#{ Hierachy Handling
	def getChildren( self, **kwargs ):
		"""@return: all intermediate child instances
		@note: the order of children is lexically ordered at this time 
		@note: this implementation is slow and should be overridden by more specialized subclasses"""
		return filter( lambda x: len( x.replace( self , '' ).split('|') ) - 1 ==len( self.split( '|' ) ), self.getChildrenDeep() )
		
	def getChildrenDeep( self, **kwargs ):
		"""@return: all child instances recursively
		@note: the order of children is lexically ordered at this time 
		@note: this implementation is slow and should be overridden by more specialized subclasses"""
		kwargs['long'] = True
		return filter( lambda x: x.startswith(self) and not x == self, lsUI(**kwargs))
		
	def getParent( self ):
		"""@return: parent instance of this ui element"""
		return wrapUI( '|'.join( self.split('|')[:-1] ) )
		
	@classmethod
	def getCurrentParent( cls ):
		"""@return: NameUI of the currently set parent"""
		# MENU 
		if cls._is_menu:
			curparentmenu = cmds.setParent( q=1, m=1 )
			if not curparentmenu:
				raise AssertionError( "No current menu parent set" )
				
			return wrapUI( name=curparentmenu )
		else:
			# NON-MENU 
			return wrapUI( cmds.setParent( q=1 ) ) 
		
	#}	END hierarchy handling
	
	
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
		
	def exists( self ):
		"""@return: True if this instance still exists in maya"""
		try:
			return self.__melcmd__( self, e=1 )
		except RuntimeError:
			# although it should just return False if it does NOT exist, it raises
			return False
		
	#{ Properties 
	p_parent = property( getParent )
	p_children = property( getChildren )
	#} END properties 
		
class SizedControl( NamedUI ):
	"""Base Class for all controls having a dimension""" 
	__metaclass__ = ui.MetaClassCreatorUI
	_properties_ = ( 	"dt", "defineTemplate", 
					  	"ut", "useTemplate", 
						"w","width", 
						"h", "height", 
						"v", "visible", 
						"m", "manage", 
						"en", "enable", 
						"io", "isObscured", 
						"npm", "numberOfPopupMenus", 
						"po", "preventOverride", 
						"bgc", "backgroundColor", 
						"dt", "doctTag" )

	_events_ = ( 	"dgc", "dragCallback" ,
					"dpc", "dropCallback" )
	
	#{ Query Methods 
	
	def getAnnotation( self ):
		"""@return : the annotation string """
		try:
			return self.__melcmd__( self, q=1, ann=1 )
		except TypeError:
			return ""
			
	def getDimension( self ):
		"""@return: (x,y) tuple of x and y dimensions of the UI element""" 
		return ( self.__melcmd__( self, q=1, w=1 ), self.__melcmd__( self, q=1, h=1 ) )
		
	def getPopupMenuArray( self ):
		"""@return: popup menus attached to this control"""
		return wrapUI( self.__melcmd__( self, q=1, pma=1 ) )
		
	#}END query methods
	
	#{ Edit Methods 
	
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
	
	p_annotation = property( getAnnotation, setAnnotation )
	p_ann = p_annotation
	p_dimension = property( getDimension, setDimension )
	p_pma = property( getPopupMenuArray )
	p_popupMenuArray = property( getPopupMenuArray )
		
	

class Window( SizedControl, uiutil.UIContainerBase ):
	"""Simple Window Wrapper
	@note: Window does not support some of the properties provided by sizedControl"""
	__metaclass__ = ui.MetaClassCreatorUI
	_properties_ = (	"t", "title", 
					   	"i", "iconify", 
						"s", "sizeable", 
						"iconName", 
						"tb","titleBar",
					   	"mnb", "minimizeButton",
						"mxb", "maximizeButton", 
						"tlb", "toolbox", 
						"tbm", "titleBarMenu", 
						"mbv", "menuBarVisible",
						"tlc", "topLeftCorner", 
						"te", "topEdge",
						"tl", "leftEdge",
						"mw", "mainWindow", 
						"rt", "resizeToFitChildren", 
						"dt", "docTag" )
	
	_events_ = ( "rc", "restoreCommand", "mnc", "minimizeCommand" )
	
	
	#{ Window Specific Methods
	
	def show( self ):
		""" Show Window"""
		cmds.showWindow( self )
		
	def delete( self ):
		""" Delete window """
		cmds.deleteUI( self )
	
	def getNumberOfMenus( self ):
		"""@return: number of menus in the menu array"""
		return int( self.__melcmd__( self, q=1, numberOfMenus=1 ) )
	
	def getMenuArray( self ):
		"""@return: Menu instances attached to this window"""
		return wrapUI( self.__melcmd__( self, q=1, menuArray=1 ) )
		
	def isFrontWindow( self ):
		"""@return: True if we are the front window """
		return bool( self.__melcmd__( self, q=1, frontWindow=1 ) )
		
	def setMenuIndex( self, menu, index ):
		"""Set the menu index of the specified menu
		@param menu: name of child menu to set 
		@param index: new index at which the menu should appear"""
		return self.__melcmd__( self, e=1, menuIndex=( menu, index ) )
		
	#} END window speciic
	
	p_numberOfMenus = property( getNumberOfMenus )
	p_nm = p_numberOfMenus
	
	
class MenuBase( NamedUI ):
	"""Common base for all menus"""
	
	#( Configuration
	_is_menu = True
	#) END configuration
	
	_properties_ = (	
					   "en", "enable", 
					   	"l", "label", 
						"mn", "mnemonic", 
						"aob", "allowOptionBoxes", 
						"dt", "docTag"
					 )
	
	_events_ = ( 		
					 	"pmc", "postMenuCommand", 
						"pmo", "postMenuCommandOnce"	
				)
	
	
class ContainerMenuBase( uiutil.UIContainerBase ):
	"""Implements the container abilities of all menu types"""
	
	def setActive( self ):
		"""Make ourselves the active menu"""
		cmds.setParent( self, m=1 )
		
	def setParentActive( self ):
		"""Make our parent the active menu layout
		@note: only useful self is a submenu"""
		cmds.setParent( ".." , m=1 )
	

class Menu( MenuBase, ContainerMenuBase ):
	_properties_ = ( 	
					  	"hm", "helpMenu", 
						"ia", "itemArray",
						"ni", "numberOfItems",
						"dai", "deleteAllItems",
						"fi", "familyImage" 
					)

	
class MenuItem( MenuBase ):
	
	_properties_ = (
						"d", "divider", 
						"cb", "checkBox", 
						"icb", "isCheckBox", 
						"rb", "radioButton", 
						"irb", "isRadioButton", 
						"iob", "isOptionBox", 
						"cl", "collection", 
						"i", "image", 
						"iol", "imageOverlayLabel", 
						"sm", "subMenu", 
						"ann", "annotation", 
						"da", "data", 
						"rp", "radialPosition", 
						"ke", "keyEquivalent", 
						"opt", "optionModifier", 
						"ctl", "controlModifier", 
						"sh", "shiftModifier", 
						"ecr", "enableCommandRepeat", 
						"ec", "echoCommand", 
						"it", "italicized", 
						"bld", "boldFont" 
					)
	
	_events_ = ( 
						"dmc", "dragMenuCommand", 
						"ddc", "dragDoubleClickCommand",
						"c", "command"
				)
	
	def toMenu( self ):
		"""@return: Menu representing self if it is a submenu
		@raise TypeError: if self i no submenu"""
		if not self.p_sm:
			raise TypeError( "%s is not a submenu and cannot be used as menu" )
			
		return Menu( name = self ) 
