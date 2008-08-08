"""B{byronimo.ui.controls}

Contains the most controls like buttons and sliders for more convenient use 

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
uibase = __import__( "byronimo.maya.ui.base",globals(), locals(), ['base'] )
import maya.cmds as cmds
import byronimo.util as util
import byronimo.maya.util as mutil


class Button( ui.NamedUI ):
	""" Simple button interface """
	def setCommand( self, func,  actOnPress=False ):
		"""Set the given func as callback once the button is pressed
		@param func: callable object
		@param actOnPress: if False, func will be called on release, otherwise on press
		@note: the command cannot be queried - never worked, not even in MEL"""
		self.__melcmd__( self, e=1, command = func, actOnPress=actOnPress )
	
