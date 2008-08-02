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
from byronimo.path import Path
#import byronimo.maya.util as util
util = __import__( "byronimo.maya.util", globals(), locals(), [ "util" ] )
import maya.OpenMaya as om
import maya.cmds as cmds



	
class _SceneCallback( util.CallbackBase ):
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
		util.CallbackBase.addListener( self, listenerID, callback, callbackID = sceneMessageId )

	def _getCallbackGroupID( self, sceneMessageId ):
		if sceneMessageId in self._checkCBSet:
			return 0
		elif sceneMessageId in self._checkFileCBSet:
			return 1
		else:
			return 2

	def _addMasterCallback( self, callbackGroup, sceneMessageId ):
		""" Setup or delete a scene callback 
		@return : the possibly created callback id """
		groupId = self._getCallbackGroupID( sceneMessageId )
		messageCreator = self._cbgroupToMethod[ groupId ]
		return messageCreator( sceneMessageId, self._call, callbackGroup )
		
		

class Scene( util.Singleton ):
	"""Singleton Class allowing access to the maya scene"""
	
	
	_fileTypeMap = { 	".ma" : "mayaAscii",
						".mb" : "mayaBinary" }
	
	#{ Public Members
	Callbacks = _SceneCallback()
	#}
	
	
	#{ Edit Methods 
	@staticmethod
	def open( filePath, loadReferenceDepth="all", force=False, **kvargs ):
		""" Open a scene 
		@param filePath: The path to the file to be opened
		If None or "", the currently loaded file will reopened
		@param loadReferenceDepth: 'all' - load all references
		'topOnly' - only top level references, no subreferences
		'none' - load no references
		@param force - if True, the new scene will be loaded although currently 
		loaded contains unsaved changes 
		@return: a path object to the loaded scene"""
		if filePath is None or filePath == "":
			filePath = Scene.getName()
			
		sourcePath = Path( filePath )
		loadedFile = cmds.file( sourcePath.abspath(), open=1, loadReferenceDepth=loadReferenceDepth, force=force, **kvargs )
		return Path( loadedFile )
		
	@staticmethod
	def new( force = False, **kvargs ):
		""" Create a new scene 
		@param force: if True, the new scene will be created even though there 
		are unsaved modifications
		@return: Path object with name of current file"""
		return Path( cmds.file( new = True, force = force, **kvargs ) )
		
	@staticmethod
	def save( scenepath, **kvargs ):
		"""The save the currently opened scene under scenepath in the respective format
		@param scenepath: if None or "", the currently opened scene will be used
		@param **kvargs: passed to cmds.file """
		if scenepath is None or scenepath == "":
			scenepath = Scene.getName( )
			
		scenepath = Path( scenepath )
		try :
			filetype = Scene._fileTypeMap[ scenepath.p_ext ]
		except KeyError:
			raise RuntimeError( "Unsupported filetype of: " + scenepath  )
			
		# is it a safe as ?
		if Scene.getName() != scenepath:
			cmds.file( rename=scenepath )
			
		# assure path exists
		parentdir = scenepath.dirname()
		if not parentdir.exists( ):
			parentdir.makedirs( )
			
		# safe the file
		return Path( cmds.file( save=True, type=filetype, **kvargs ) ) 
		
	#} END edit methods
	
	
	#{ Query Methods
	@staticmethod
	def getName(  ):
		return Path( cmds.file( q=1, exn=1 ) )
		
	@staticmethod
	def isModified(  ):
		return cmds.file( q=1, amf=True )
	#} END query methods
	
	
	#{ Properties 
	p_name = property( lambda self: self.__class__.getName( ) )
	p_anyModified = property( lambda self: self.__class__.isModified( ) )
	#} END Properties 

 
	

# END SCENE

