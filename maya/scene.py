# -*- coding: utf-8 -*-
"""
Provides methodes to query and alter the currently loaded scene. It covers
most of the functionality of the 'file' command, but has been renamed to scene
as disambiguation to a filesystem file.

@todo: more documentation
"""
# export filter
__all__ = [ 'Scene' ]


#import mayarv.maya.util as util
import mayarv.util as util
import ref as refmod

import maya.OpenMaya as om
import maya.cmds as cmds
from mayarv.path import Path



class _SceneCallbacks( util.EventSender ):
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



class Scene( util.Singleton ):
	"""Singleton Class allowing access to the maya scene"""


	kFileTypeMap = { 	""	  : "mayaAscii",		# treat untitled scenes as ma
						".ma" : "mayaAscii",
						".mb" : "mayaBinary" }

	#{ Public Members
	events = _SceneCallbacks()
	#}


	#{ Edit Methods
	@classmethod
	def open( cls, filePath, force=False, **kwargs ):
		""" Open a scene
		@param filePath: The path to the file to be opened
		If None or "", the currently loaded file will reopened
		@param force - if True, the new scene will be loaded although currently
		loaded contains unsaved changes
		@return: a path object to the loaded scene"""
		if filePath is None or filePath == "":
			filePath = cls.getName()

		# NOTE: it will return the last loaded reference instead of the loaded file - lets fix this !
		sourcePath = Path( filePath )
		lastReference = cmds.file( sourcePath.abspath(), open=1, force=force, **kwargs )
		return Path( sourcePath )

	@classmethod
	def new( cls, force = False, **kwargs ):
		""" Create a new scene
		@param force: if True, the new scene will be created even though there
		are unsaved modifications
		@return: Path object with name of current file"""
		return Path( cmds.file( new = True, force = force, **kwargs ) )

	@classmethod
	def rename( cls, new_scenepath ):
		"""Rename the currently loaded file to be the file at new_scenepath
		@note: as opposed to the normal file -rename it will also adjust the
		extension which for some annoying reason is not easily done with the default command"""
		cmds.file( rename = new_scenepath )
		cmds.file( type = cls.kFileTypeMap[ Path( new_scenepath ).p_ext ] )

	@classmethod
	def save( cls, scenepath=None, autodelete_unknown = False, **kwargs ):
		"""The save the currently opened scene under scenepath in the respective format
		@param scenepath: if None or "", the currently opened scene will be used
		@param autodelete_unknown: if true, unknown nodes will automatically be deleted
		before an attempt is made to change the maya file's type
		@param **kwargs: passed to cmds.file """
		if scenepath is None or scenepath == "":
			scenepath = cls.getName( )

		scenepath = Path( scenepath )
		curscene = cls.getName()
		try :
			filetype = cls.kFileTypeMap[ scenepath.p_ext ]
			curscenetype = cls.kFileTypeMap[ curscene.p_ext ]
		except KeyError:
			raise RuntimeError( "Unsupported filetype of: " + scenepath  )

		# is it a safe as ?
		if cls.getName() != scenepath:
			cmds.file( rename=scenepath.expandvars() )

		# assure path exists
		parentdir = scenepath.dirname( )
		if not parentdir.exists( ):
			parentdir.makedirs( )

		# delete unknown before changing types ( would result in an error otherwise )
		if autodelete_unknown and curscenetype != filetype:
			cls.deleteUnknownNodes()

		# safe the file
		return Path( cmds.file( save=True, type=filetype, **kwargs ) )

	#} END edit methods

	#{ Utilities
	@classmethod
	def deleteUnknownNodes( cls ):
		"""Deletes all unknown nodes in the scene
		@note: only do this if you are about to change the type of the scene during
		save or export - otherwise the operation would fail if there are still unknown nodes
		in the scene"""
		unknownNodes = cmds.ls( type="unknown" )		# using mel is the faatest here
		if unknownNodes:
			cmds.delete( unknownNodes )

	#} END utilities

	#{ Query Methods
	@classmethod
	def getName( cls ):
		return Path( cmds.file( q=1, exn=1 ) )

	@classmethod
	def isModified( cls ):
		return cmds.file( q=1, amf=True )
	#} END query methods


	#{ Properties
	p_name = property( lambda self: self.getName() )
	p_anyModified = property( lambda self: self.isModified() )
	#} END Properties

# END SCENE

