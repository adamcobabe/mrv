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
	""" Wrapper class for maya prompt dialog"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __init__( self, title, message, okText, cancelText, **kwargs ):
		""" Create a prompt dialog and allow to query the result 
		@note: return default text in batch mode, given with 'text' key"""
		if cmds.about( batch=1 ):
			return kwargs.get( 'text', kwargs.get( 't', '' ) )
			
		ret = cmds.promptDialog( t = title, m = message, b = [okText,cancelText], 
									db = okText, cb = cancelText,**kwargs )
		self._text = None
		if ret == okText:
			self._text = cmds.promptDialog( q=1, text = 1 )

	def getText( self ):
		"""@return: the entered text or None if the box has been aborted"""
		return self._text
		
		
class ConfirmDialog( Dialog ):
	""" Wrapper class for maya confirm dialog"""
	def __init__( self, title, message, confirmButton="Confirm", middleButton=None, 
				 	cancelButton="Cancel", defaultToConfirm = True, align = "center" ):
		""" Prompt for confirmation. Call isConfirmed or isCancelled afterwards. Call getReturnValue
		to get the exact return value ( could be middleButton string )
		@note: if a button is None, it will not appear, current button maximum is 3
		@note: in batch mode, it will always confirm"""
		if cmds.about( batch=1 ):
			self._ret = confirmButton
			self._isConfirmed = True
			return
			
		buttons = [confirmButton]
		for b in middleButton, cancelButton:
			if b:
				buttons.append( b )
				
		cancelValue = cancelButton or middleButton or confirmButton
		self._ret = cmds.confirmDialog( t = title,	m = message, b = buttons, 
										db = ( defaultToConfirm and confirmButton or cancelButton or confirmButton or middleButton ), 
										ma = align, cb = cancelValue, ds = cancelValue )
		self._isConfirmed = self._ret == confirmButton
	
	def isConfirmed( self ):
		return self._isConfirmed
		
	def isCancelled( self ):
		return not self._isConfirmed
		
	def getReturnValue( self ):
		return self._ret
