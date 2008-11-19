"""B{byronimo.ui.util}

Utilities and classes useful for user interfaces 

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


from byronimo.util import CallbackBase, Call
import maya.cmds as cmds 
import weakref

class CallbackBaseUI( CallbackBase ):
	"""Allows registration of a typical UI callback
	It basically streamlines the registration for a callback such that any 
	number of listeners can be called when an event occours - this works by 
	keeping an own list of callbacks registered for a specific event, and calling them 
	whenever the maya ui callback has been triggered
	
	To make this work it is essential that you work with one and the same instance of your 
	class.
	
	To use this class , see the documentation of L{CallbackBase}, but use the UIEvent 
	instead.
	If you want to add your own events, use your own events, use the L{Event} class instead
	
	As the class uses weakreferences for the main callback, the main class can always 
	go out of scope without being held by maya
	
	When registered for an event, the sender will be provided to each callback as first 
	argument.
	
	@note: your functions that are being registered for a certain event should 
	reside on a class that is being held alive by more than the callback
	"""
	#( Configuration 
	# we are to be put as first arguemnt, allowing listeners to do something 
	# with the sender when handling the event
	sender_as_argument = True
	#} END configuration 
	
	class WeakFunction( object ):
		"""Keeps an instance and a class level member function. When called, 
		the weakreferenced instance pointer will be retrieved, if possible, 
		to finally make the call. If it could not be retrieved, the call 
		will do nothing"""
		__slots__ = ( "_weakinst", "_clsfunc" )
		
		def __init__( self, instance, clsfunction ):
			self._weakinst = weakref.ref( instance )
			self._clsfunc = clsfunction
			
			
		def __call__( self, *args, **kwargs ):
			inst = self._weakinst()
			if not inst:	# went out of scope
				print "Instance for call has been deleted as it is weakly bound"
				return 
			
			return self._clsfunc( inst, *args, **kwargs )
	
	class UIEvent( CallbackBase.Event ):
		"""Event suitable to deal with user interface callback"""
		#( Configuration 
		use_weakref = True
		#) END configuration
		
		def __init__( self, eventname, **kwargs ):
			"""Allows to set additional arguments to be given when a callback 
			is actually set"""
			super( CallbackBaseUI.UIEvent, self ).__init__( eventname )
			self._kwargs = kwargs
		
		def __set__(  self, inst, eventfunc ):
			"""Set the given event to be called when this event is being triggered"""
			eventset = self.__get__( inst )
			
			# REGISTER IF THIS IS THE FIRST EVENT 
			# do we have to register the callback ?
			if not eventset:
				kwargs = dict()
				# generic call that will receive maya's own arguments and pass them on
				weakSendEvent = CallbackBaseUI.WeakFunction( inst, getattr( inst.__class__, "sendEvent" ) )
				call = Call( weakSendEvent, self )
				dyncall =  lambda *args, **kwargs: call( *args, **kwargs )
				
				kwargs[ 'e' ] = 1
				kwargs[ self._name ] =dyncall
				kwargs.update( self._kwargs )		# allow user kwargs 
				inst.__melcmd__( str( inst ) , **kwargs )
			# END create event 
			
			super( CallbackBaseUI.UIEvent, self ).__set__( inst, eventfunc )
			
	# END uievent
	
	#( iDuplicatable Deactivated 
	
	def createInstance( self, *args, **kwargs ):
		"""Deactivated as we cannot copy callbacks safely if the maya ui is involved"""
		raise RuntimeError( "A CallbackBaseUI instance cannot be duplicated" )
		
	def copyFrom( self, other, *args, **kwargs ):
		raise RuntimeError( "A CallbackBaseUI instance cannot be copied" )
		
	#) end iduplicatable deactivated
	
	
class UIContainerBase( object ):
	"""A ui container is a base for all classes that can have child controls or 
	other containers. 
	This class is just supposed to keep references to it's children so that additional 
	information stored in python will not get lost
	Child-Instances are always unique, thus adding them several times will not 
	keep them several times , but just once"""
	
	
	def __init__( self, *args, **kwargs ):
		self._children = list()
		super( UIContainerBase, self ).__init__( *args, **kwargs )
	
	def add( self, child, set_self_active = False, revert_to_previous_parent = True ):
		"""Add the given child UI item to our list of children
		@param set_self_active: if True, we explicitly make ourselves the current parent 
		for newly created UI elements
		@param revert_to_previous_parent: if True, the previous parent will be restored 
		once we are done, if Fales we stay the parent - only effective if set_self_active is True
		@return: the newly added child, allowing contructs like 
		button = layout.addChild( Button( ) )"""
		if child in self._children:
			return child 
			
		prevparent = None
		if set_self_active:
			prevparent = self.getCurrentParent()
			self.setActive( )
		# END set active handling
		
		self._children.append( child )
		
		if revert_to_previous_parent and prevparent:
			cmds.setParent( prevparent )
			
		return child
		
	def remove( self, child ):
		"""Remove the given child from our list
		@return: True if the child was found and has been removed, False otherwise"""
		try:
			self._children.remove( child )
			return True
		except ValueError:
			return False
	
	def deleteChild( self, child ):
		"""Delete the given child ui physically so it will not be shown anymore
		after removing it from our list of children"""
		if self.removeChild( child ):
			child.delete()
			
	def listChildren( self ):
		"""@return: list with our child instances
		@note: it's a copy, so you can freely act on the list
		@note: children will be returned in the order in which they have been added"""
		return self._children[:]
		
	def setActive( self ):
		"""Set this container active, such that newly created items will be children 
		of this layout
		@note: always use the addChild function to add the children !"""
		cmds.setParent( self )
