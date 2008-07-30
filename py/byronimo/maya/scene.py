"""B{byronimo.maya.scene}

Provides methodes to query and alter the currently loaded scene. It covers 
most of the functionality of the 'file' command, but has been renamed to scene
as disambiguation to a filesystem file.

@todo: more documentation
@todo: create real class properties - currently its only working with instances

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


# export filter 
__all__ = [ 'currentScene', 'Scene' ]

import maya.cmds as cmds
from byronimo.path import path
import maya.OpenMaya as om
import maya.cmds as cmds


class CallbackBase( object ):
	""" Base type taking over the management part when wrapping maya messages into an 
	appropriate python class. 
	
	It has the advantage of easier usage as you can pass in any function with the 
	appropriate signature"""
	
	def __init__( self ):
		"""initialize our base variables"""
		self._middict = {}						# callbackGroup -> maya callback id
		self._callbacks = {}				# callbackGroup -> ( callbackStringID -> Callacble )
	
	def _addMasterCallback( self, callbackID, *args, **kvargs ):
		"""Called once the base has to add actual maya callback.
		It will be added once the first client adds himself, or removed otherwise once the last
		client removed himself.
		Make sure your method registers this _call method with *args and **kvargs to allow
		it to acftually deliver the call to all registered clients
		@param existingID: if -1, the callback is to be added - in that case you have to 
		return the created unique message id
		@param callbackID: if not None, specifies the callback type that was requested"""
		raise NotImplementedError()
		
	def _getCallbackGroup( self, callbackID ):
		""" Returns a group where this callbackID passed to the addListener method belongs to.
		If all callbackIDs are the same, this default implementation will take care of it
		@note: override if you have different callback groups, thus different kinds of callbacks
		that you have to register with different methods"""
		return 0
		
	def _call( self, *args, **kvargs ):
		""" Iterate over listeners and call them. The method expects the last 
		argument to be the callback group that _addMasterCallback method supplied to the 
		callback creation method
		@note: will throw only in debug mode 
		@todo: implement debug mode !"""
		cbgroup = args[-1]
		if cbgroup not in self._callbacks:
			raise KeyError( "Callback group: " + cbgroup + " did not exist" )
		
		cbdict = self._callbacks[ cbgroup ]
		for callback in cbdict.itervalues():
			callback( *args, **kvargs )
		# END callback loop
		
	def addListener( self, listenerID, callback, callbackID = None, *args, **kvargs ):
		""" Call to register to receive events triggered by this class
		@param listenerID: hashable item identifying you 
		@param callback: callable method, being called with the arguments of the respective
		callback - read the derived classes documentation about the signature
		@param callbackID: will be passed to the callback creator allowing it to create the desired callback
		@raise ValueError: if the callback could not be registered 
		@note: Override this method if you need to add specific signature arguments, and call 
		base method afterwardss"""
		
		cbgroup = self._getCallbackGroup( callbackID )
		cbdict = self._callbacks.get( cbgroup, dict() )
		if len( cbdict ) == 0: self._callbacks[ cbgroup ] = cbdict		# assure the dict is actually in there !
		
		# are we there already ?
		if listenerID in cbdict: 
			return
		
		# assure we get a callback
		if len( cbdict ) == 0:
			self._middict[ cbgroup ] = self._addMasterCallback( cbgroup, callbackID, *args, **kvargs )
			mid = self._middict[ cbgroup ]
			if mid is None or mid < 1:
				raise ValueError( "Message ID is supposed to be set to an approproriate value" )
				
		# store the callable for later use
		cbdict[ listenerID ] = callback
		
	
	def removeListener( self, listenerID, callbackID = None ):
		"""Remove the listener with the given listenerID so it will not be notified anymore if 
		events occour. Never raises
		@param callbackID: must be the callbackID you added the listener with"""
		cbgroup = self._getCallbackGroup( callbackID )
		if cbgroup not in self._callbacks:
			return 
		
		cbdict = self._callbacks[ cbgroup ]
		try: 
			del( cbdict[ listenerID ] )
		except KeyError:
			pass
		
		# if there are no listeners, remove the callback 
		if len( cbdict ) == 0:
			mid = self._middict[ cbgroup ]
			om.MSceneMessage.removeCallback( mid )
			
	
class SceneCallback( CallbackBase ):
	""" Implements Scene Callbacks """
	
	_checkCBSet = set( ( 	om.MSceneMessage.kBeforeNewCheck,
							om.MSceneMessage.kBeforeSaveCheck ) )

	_checkFileCBSet = set( ( 	om.MSceneMessage.kBeforeImportCheck,
							  	om.MSceneMessage.kBeforeOpenCheck,
								om.MSceneMessage.kBeforeExportCheck,
								om.MSceneMessage.kBeforeReferenceCheck,
								om.MSceneMessage.kBeforeLoadReferenceCheck  ) )
	
	_cbgroupToMethod = { 	0 : om.MSceneMessage.addCheckCallback, 
							1 : om.MSceneMessage.addCheckFileCallback, 
							2 : om.MSceneMessage.addCallback }
	
	def addListener( self, listenerID, callback, sceneMessageId ):
		"""Add a listener for the given sceneMessageId - all other parameters 
		correspond to the baseclass method: L{CallbackBase.addListener}
		@param sceneMessageId: MSceneMessage message id enumeration member 
		@note: this message enforces the required signature"""
		CallbackBase.addListener( self, listenerID, callback, callbackID = sceneMessageId )

	def _getCallbackGroup( self, sceneMessageId ):
		if sceneMessageId in self._checkCBSet:
			return 0
		elif sceneMessageId in self._checkFileCBSet:
			return 1
		else:
			return 2

	def _addMasterCallback( self, callbackGroup, sceneMessageId ):
		""" Setup or delete a scene callback 
		@return : the possibly created callback id """
		messageCreator = self._cbgroupToMethod[ callbackGroup ]
		return messageCreator( sceneMessageId, self._call, callbackGroup )
		
		

class Scene( object ):
	"""Singleton Class allowing access to the maya scene"""
	
	
	Callbacks = SceneCallback()
	
	@staticmethod
	def open( filePath, loadReferenceDepth="all", force=False, **kvargs ):
		""" Open a scene 
		@param filePath: The path to the file to be opened
		@param loadReferenceDepth: 'all' - load all references
		'topOnly' - only top level references, no subreferences
		'none' - load no references
		@param force - if True, the new scene will be loaded although currently 
		loaded contains unsaved changes 
		@return: a path object to the loaded scene"""
		filepath = cmds.file( filePath, loadReferenceDepth=loadReferenceDepth, force=force, **kvargs )
		return path( filepath )
		
	@staticmethod
	def new( force = False, **kvargs ):
		""" Create a new scene 
		@param force: if True, the new scene will be created even though there 
		are unsaved modifications"""
		cmds.file( new = True, force = force, **kvargs )
		
	#{ Query Methods
	def getName( self ):
		return path( cmds.file( q=1, exn=1 ) ) 
		
	
	def isModified( self ):
		return cmds.file( q=1, amf=True )
	#} END query methods
	
	
	#{ Properties 
	name = property( getName )
	anyModified = property( isModified )
	#} END Properties 

 
	

# END SCENE




## SINGLETON SCENE
####################
# store the current scene as instance, allowing to use properties
_scene = Scene( )
def currentScene( ):
	"""@return: the currrent scene class - its a singleton"""
	return _scene
