"""B{byronimo.maya.scene}

Provides methodes to query and alter the currently loaded scene. It covers 
most of the functionality of the 'file' command, but has been renamed to scene
as disambiguation to a filesystem file.

@todo: more documentation
@todo: create real class properties - currently its only working with instances. 

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
mayautil = __import__( "byronimo.maya.util", globals(), locals(), [ "util" ] )
util = __import__( "byronimo.util", globals(), locals(), [ "util" ] )
import maya.OpenMaya as om
import maya.cmds as cmds
refmod = __import__( "byronimo.maya.reference", globals(), locals(), ['reference'] )
from byronimo.util import iDagItem


	
class _SceneCallback( mayautil.CallbackBase ):
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
		mayautil.CallbackBase.addListener( self, listenerID, callback, callbackID = sceneMessageId )

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
	def open( filePath, loadReferenceDepth="all", force=False, **kwargs ):
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
			
		# NOTE: it will return the last loaded reference instead of the loaded file - lets fix this !
		sourcePath = Path( filePath )
		lastReference = cmds.file( sourcePath.abspath(), open=1, loadReferenceDepth=loadReferenceDepth, force=force, **kwargs )
		return Path( sourcePath )
		
	@staticmethod
	def new( force = False, **kwargs ):
		""" Create a new scene 
		@param force: if True, the new scene will be created even though there 
		are unsaved modifications
		@return: Path object with name of current file"""
		return Path( cmds.file( new = True, force = force, **kwargs ) )
		
	@staticmethod
	def save( scenepath, **kwargs ):
		"""The save the currently opened scene under scenepath in the respective format
		@param scenepath: if None or "", the currently opened scene will be used
		@param **kwargs: passed to cmds.file """
		if scenepath is None or scenepath == "":
			scenepath = Scene.getName( )
			
		scenepath = Path( scenepath )
		try :
			filetype = Scene._fileTypeMap[ scenepath.p_ext ]
		except KeyError:
			raise RuntimeError( "Unsupported filetype of: " + scenepath  )
			
		# is it a safe as ?
		if Scene.getName() != scenepath:
			cmds.file( rename=scenepath.expandvars() )
			
		# assure path exists
		parentdir = scenepath.dirname( )
		if not parentdir.exists( ):
			parentdir.makedirs( )
			
		# safe the file	
		return Path( cmds.file( save=True, type=filetype, **kwargs ) )
		
	@staticmethod
	def createReference( filepath, **kwargs ):
		"""Create a reference
		@param filepath: filepath of the reference you wish to create
		@param **kwargs: all arguments supported by L{FileReference.create} 
		@return: newly created FileReference"""
		return refmod.FileReference.create( filepath, **kwargs )
	
	@staticmethod
	def importReference( filepath, **kwargs ):
		"""Import a reference ( straight away )
		@note: this method will only work with files that can also be referenced - use the default
		file -import command for other file types 
		@param filepath: path to file to import 
		@param **kwargs: arguments supported by L{FileReference.create}
		@raise RuntimeError: On failure"""
		reference = Scene.createReference( filepath, **kwargs )
		reference.importRef( depth = 0 )
		
		
	#} END edit methods
	
	
	#{ Query Methods
	@staticmethod
	def getName(  ):
		return Path( cmds.file( q=1, exn=1 ) )
		
	@staticmethod
	def isModified(  ):
		return cmds.file( q=1, amf=True )
		
	@staticmethod
	def lsReferences( referenceFile = "", predicate = lambda x: True ):
		""" list all references in the scene or in referenceFile
		@param referenceFile: if not empty, the references below the given reference file will be returned
		@param predicate: method returning true for each valid file reference object
		@return: list of L{FileReference}s objects"""
		out = []
		for reffile in cmds.file( str( referenceFile ), q=1, r=1, un=1 ):
			refobj = refmod.FileReference( filepath = reffile )
			if predicate( refobj ):
				out.append( refobj )
		# END for each reference file
		return out
	
	@staticmethod
	def lsReferencesDeep( predicate = lambda x: True, **kwargs ):
		""" Return all references recursively 
		@param **kwargs: support for arguments as in lsReferences"""
		refs = Scene.lsReferences( **kwargs )
		out = refs
		for ref in refs:
			out.extend( ref.getChildrenDeep( order = iDagItem.kOrder_BreadthFirst, predicate=predicate ) )
		return out
		
	#} END query methods
	
	
	#{ Properties 
	p_name = property( lambda self: self.__class__.getName( ) )
	p_anyModified = property( lambda self: self.__class__.isModified( ) )
	#} END Properties 

 
	

# END SCENE

