"""B{byronimo.ui.dialogs}

Contains some default dialogs as well as layouts suitable for layout dialogs 

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
import byronimo.util as util
import byronimo.maya.util as mutil

#{ Exceptions
################################################################################


#} End Exceptions


class Dialog( ui.BaseUI ):
	""" Base for all dialog classes """
	
	#{ Overridden Methods
	
	#}
	
	
class PromptDialog( Dialog ):
	""" Wrapper class for maya form layout """
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __init__( self, title, message, okText, cancelText, **kvargs ):
		""" Create a prompt dialog and allow to query the result """
		ret = cmds.promptDialog( t = title, m = message, b = [okText,cancelText], db = okText, cb = cancelText,**kvargs )
		self._text = None
		if ret == okText:
			self._text = cmds.promptDialog( q=1, text = 1 )

	def getText( self ):
		"""@return: the entered text or None if the box has been aborted"""
		return self._text
