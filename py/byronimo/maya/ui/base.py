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


############################
#### Classes		  	####
##########################

class BaseUI( object ):
	
	__melcmd__	= None					# every class deriving directly from it must define this !
	
	def __init__( self, *args, **kvargs ):
		if self.__class__ == BaseUI:
			raise ui.UIError( "Cannot instantiate" + self.__class__.__name__ + " directly - it can only be a base class" )
		
		# Call the mel command attached to this base UI 
		self._callMelCmd( *args, **kvargs )
		return object.__init__(self, *args, **kvargs )
		
	def _callMelCmd( self, *args, **kvargs ):
		"""Call the command associated with this UI instance to create it  
		@note: should be overridden by subclasses that need more specialized handling"""
		raise NotImplementedError()
		

class NamedUI( BaseUI ):
	""" Implements a simple UI element having a name  and most common methods one 
	can apply to it. Derived classes should override these if they can deliver a
	faster implementation """
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __repr__( self ):
		return u"%s('%s')" % ( self.__class__.__name__, self )
	
	def __str__( self ):
		return self.name
		
	def __init__( self , *args, **kvargs ):
		self.name = None
		
		# assure that new instances are being created initially
		forbiddenKeys = [ 'edit', 'e' , 'query', 'q' ]
		for fkey in forbiddenKeys:
			if fkey in kvargs:
				raise ui.UIError( "Edit or query flags are not permitted during initialization as interfaces must be created onclass instantiation" )
			# END if key found in kvargs
		# END for each forbidden key
		return BaseUI.__init__( self, *args, **kvargs )
		
	def _callMelCmd( self, *args, **kvargs ):
		""" Create the user interface using our specific mel command """
		if self.name != None:
			raise ui.UIError( "UI elements can only be created once" )
		
		self.name = self.__melcmd__( *args, **kvargs )
		
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
		cmds.showWindow( self.name )
		
	def delete(self):
		cmds.deleteUI( self.name , window=True)
