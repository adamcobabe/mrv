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


class Scene( object ):
	"""Singleton Class allowing access to the maya scene"""
	
	@staticmethod
	def open( filePath, loadReferenceDepth="all", force=False ):
		""" Open a scene 
		@param filePath: The path to the file to be opened
		@param loadReferenceDepth: 'all' - load all references
		'topOnly' - only top level references, no subreferences
		'none' - load no references
		@param force - if True, the new scene will be loaded although currently 
		loaded contains unsaved changes """
		
		
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
