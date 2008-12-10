# -*- coding: utf-8 -*-
"""B{byronimo.uibase.dialogs}

Contains some default dialogs as well as layouts suitable for layout dialogs 

@todo: more documentation

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import base as uibase
import maya.cmds as cmds
import maya.utils as mutils
import byronimo.util as util
import byronimo.maya.util as mutil

#{ Exceptions
################################################################################


#} End Exceptions


class Dialog( uibase.BaseUI ):
	""" Base for all dialog classes """
	
	#{ Overridden Methods
	
	#}
	
	
class PromptDialog( Dialog ):
	""" Wrapper class for maya prompt dialog"""
	
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
		
		
class ChoiceDialog( util.iChoiceDialog ):
	"""Maya implementation of the generic choice dialog interface"""
	
	def choice( self ):
		"""Return the choice made by the user"""
		# don't do anything inbatch mode 
		if cmds.about( b=1 ):
			return self.default_choice
			
		return cmds.confirmDialog( 	t = self.title, 
								  	m = self.message,
									b = [ str( c ) for c in self.choices ],
									db = self.default_choice,
									ds = self.cancel_choice )
			   
		
class ProgressWindow( util.iProgressIndicator ):
	"""Simple progress window wrpping the default maya progress window"""
	def __init__( self, **kwargs ):
		"""Everything that iProgress indicator and Maya Progress Window support"""
		min = kwargs.pop( "min", kwargs.pop( "minValue" , 0 ) )
		max = kwargs.pop( "max", kwargs.pop( "maxValue", 100 ) )
		
		relative = kwargs.pop( "is_relative", 1 )
		super( ProgressWindow, self ).__init__( min = min, max = max, is_relative = relative )
		
		# remove invalid args 
		kwargs.pop( "s", kwargs.pop( "step", 0 ) )
		kwargs.pop( "pr", kwargs.pop( "progress", 0 ) )
		kwargs.pop( "ep", kwargs.pop( "endProgress", 0 ) )
		kwargs.pop( "ic", kwargs.pop( "isCancelled", 0 ) )
		kwargs.pop( "e", kwargs.pop( "edit", 0 ) )
		
		self.kwargs = kwargs  			# store for begin
		
		
	#{ iProgress Overrides
	
	def refresh( self, message = None ):
		"""Finally show the progress window"""
		mn,mx = ( self.isRelative() and ( 0,100) ) or self.getRange()
		p = self.get()
		
		myargs = dict()
		myargs[ "e" ] = 1
		myargs[ "min" ] = mn
		myargs[ "max" ] = mx
		myargs[ "pr" ] = p
		myargs[ "status" ] = message or ( "Progress %s" % ( "." * ( int(p) % 4 ) ) )
		
		try:
			cmds.progressWindow( **myargs )
		except RuntimeError,e:
			print str( e )
			pass 		# don't know yet why that happens
		
	def begin( self ):
		"""Show our window"""
		super( ProgressWindow, self ).begin( )
		cmds.progressWindow( **self.kwargs )
	
	def end( self ):
		"""Close the progress window"""
		# damn, has to be deferred to actually work
		super( ProgressWindow, self ).end( )
		mutils.executeDeferred( cmds.progressWindow, ep=1 )
		
	def isCancelRequested( self ):
		"""@return: True if the action should be cancelled, False otherwise"""
		return cmds.progressWindow( q=1, ic=1 )
		
	def isAbortable( self ):
		"""@return : true if the process can be aborted"""
		return cmds.progressWindow( q=1, ii=1 )
		
	def setAbortable( self, state ):
		cmds.progressWindow( e=1, ii=state )
		return super( ProgressWindow, self ).setAbortable( state ) 
	#} END iProgressOverrides 
