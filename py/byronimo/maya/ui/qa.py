# -*- coding: utf-8 -*-
"""B{byronimo.ui.qa}

Contains a modular UI able to display quality assurance checks, run them and 
present their results. It should be easy to override and adjust it to suit additional needs
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


import base as uibase
import controls
import maya.cmds as cmds
import byronimo.util as util
import byronimo.maya.util as mutil
import util as uiutil
import layouts
from byronimo.automation.qa import QAWorkflow
import maya.OpenMaya as api
from itertools import chain 


class QACheckLayout( layouts.RowLayout ):
	"""Row Layout able to display a qa check and related information
	@note: currently we make assumptions about the positions of the children in the 
	RowLayout, thus you may only append new ones"""
	isNodeTypeTreeMember = False
	
	#{ Configuration
	# paths to icons to display
	# [0] = check not run
	# [1] = check success
	# [2] = check failed
	# [3] = check threw exception
	icons = [ "offRadioBtnIcon.xpm", "onRadioBtnIcon.xpm", "fstop.xpm", "fstop.xpm" ]	# explicitly a list
	height = 25
	#} END configuration 
	
	def __new__( cls, *args, **kwargs ):
		"""Initialize this RowColumnLayout instance with a check instance
		@param check: the check this instance should attach itself to - it needs to be set"""
		check = kwargs.pop( "check" )
		
		numcols = 3 # without fix
		if check.plug.implements_fix:
			numcols = 4
		
		kwargs[ 'numberOfColumns' ] = numcols
		kwargs[ 'adj' ] = 1
		kwargs[ 'h' ] = cls.height
		kwargs[ 'cw%i' % numcols ] = ( cls.height, ) * numcols
		self = super( QACheckLayout, cls ).__new__( cls, *args, **kwargs )
		
		# create instance variables 
		self._check = check
		return self
		
	def __init__( self, *args, **kwargs ):
		"""Initialize our instance with members"""
		super( QACheckLayout, self ).__init__( *args, **kwargs )
		
		# populate 
		self._create( )
	
	def _create( self ):
		"""Create our layout elements according to the details given in check"""
		# assume we are active
		self.add( controls.Text( label = self.getCheck().plug.getName() ) )
		ibutton = self.add( controls.IconTextButton( 	style="iconOnly", 
														h = self.height, w = self.height ) )
		sbutton = self.add( controls.Button( label = "S", w = self.height, 
												ann = "Select faild or fixed items" ) )
		
		# if we can actually fix the item, we add an additional button
		if self.getCheck().plug.implements_fix:
			fbutton = self.add( controls.Button( label = "Fix", ann = "Attempt to fix failed items" ) )
			fbutton.e_pressed = self._runCheck 
		# END fix button setup
			
		# attach callbacks 
		ibutton.e_command = self._runCheck
		sbutton.e_pressed = self.selectPressed
	
	def update( self ):
		"""Update ourselves to match information in our stored check"""
		# check the cache for a result - if so, ask it for its state
		# otherwise we are not run and indicate that 
		bicon = self.listChildren()[1]
		bicon.p_image = self.icons[0]
		
		check = self.getCheck()
		if check.hasCache():
			result = check.getCache()
		# END if previous result exists
			
		
	def getCheck( self ):
		"""@return: check we are operating upon"""
		return self._check
	
	#{ Check Callbacks
	
	def _runCheck( self, *args, **kwargs ):
		"""Run our check
		@note: we may also be used as a ui callback and figure out ourselves
		whether we have been pressed by the fix button or by the run button
		@param force_check: if True, default True, a computation will be forced, 
		otherwise a cached result may be used
		@return: result of our check"""
		check = self.getCheck()
		wfl = check.node.getWorkflow()
		force_check = kwargs.get( "force_check", True )
		
		mode = check.node.eMode.query
		if args and isinstance( args[0], controls.Button ):
			mode = check.node.eMode.fix
		# END fix button handling 
		
		return wfl.runChecks( [ check ], mode = mode, clear_result = force_check )[0][1]
	
	def selectPressed( self, *args ):
		"""Called if the selected button has been pressed
		Triggers a workflow run if not yet done"""
		result = self._runCheck( force_check = False )
		
		# select items , ignore erorrs if it is not selectable 
		sellist = api.MSelectionList()
		for item in chain( result.getFixedItems(), result.getFailedItems() ):
			try:
				sellist.add( str( item ) )
			except RuntimeError:
				pass
		# END for each item to select
		
		api.MGlobal.setActiveSelectionList( sellist )
			
	
	def preCheck( self ):
		"""Runs before the check starts"""
		text = self.listChildren()[0]
		text.p_label = "Running ..."
		
	def postCheck( self, result ):
		"""Runs after the check has finished including the given result"""
		text = self.listChildren()[0]
		text.p_label = str( self.getCheck().plug.getName() )
		
		self.setResult( result )
		
	def checkError( self ):
		"""Called if the checks fails with an error"""
		text = self.listChildren()[0]
		text.p_label = str( self.getCheck().plug.getName() ) + " ( ERROR )"
	
	def setResult( self, result ):
		"""Setup ourselves to indicate the given check result
		@return: our adjusted iconTextButton Member"""
		target_icon = self.icons[2]		# failed by default
		
		if result.isSuccessful():
			target_icon = self.icons[1]
		elif result.isNull():		# indicates failure, something bad happened
			target_icon = self.icons[3]
		
		# annotate the text with the result
		children = self.listChildren()
		text = children[0]
		text.p_annotation = str( result )
		
		bicon = children[1]
		bicon.p_image = target_icon
		
		return bicon
	#} END interface

class QALayout( layouts.ColumnLayout, uiutil.iItemSet ):
	"""Layout able to dynamically display QAChecks, run them and display their result"""
	isNodeTypeTreeMember = False 
	
	#{ Configuration
	# class used to create a layout displaying details about the check
	# it must be compatible to QACheckLayout as a certain API is expected
	checkuicls = QACheckLayout	
	qaworkflowcls = QAWorkflow
	#} END configuration 
	
	def __new__( cls, *args, **kwargs ):
		"""Set some default arguments"""
		kwargs[ 'adj' ] = 1
		return super( QALayout, cls ).__new__( cls, *args, **kwargs )
	
	#{ Interface
	
	def setChecks( self, checks ):
		"""Set the checks this layout should display
		@param checks: iterable of qa checks as retrieved by L{listChecks}"""
		
		# map check names to actual checks
		name_to_check_map = dict( ( ( str( c ), c ) for c in checks ) )
		name_to_child_map = dict()
		
		self.setItems( name_to_check_map.keys(), 	name_to_check_map = name_to_check_map, 
					  								name_to_child_map = name_to_child_map )
		
		# SET EVENTS 
		#############
		# NOTE: currently we only register ourselves for callbacks, and deregeister 
		# automatically through the weak reference system
		wfls_done = list()
		for check in checks:
			cwfl = check.node.getWorkflow()
			if cwfl in wfls_done:
				continue 
			wfls_done.append( cwfl )
			
			cwfl.e_preCheck = self.checkHandler
			cwfl.e_postCheck = self.checkHandler
			cwfl.e_checkError = self.checkHandler
		# END for each check
	
	#} END interface
	
	#{ iItemSet Implementation 
	
	def getCurrentItemIds( self, name_to_child_map = None, **kwargs ):
		"""@return: current check ids as defined by exsiting children. 
		@note: additionally fills in the name_to_child_map"""
		outids = list()
		for child in self.listChildren():
			check = child.getCheck()
			cid = str( check )
			outids.append( cid )
			
			name_to_child_map[ cid ] = child
		# END for each of our children
		return outids
		
	def handleEvent( self, eventid, **kwargs ):
		"""Assure we are active before we start creating items"""
		if eventid == self.eSetItemCBID.preCreate:
			self.setActive()
	
	def createItem( self, checkid, name_to_child_map = None, name_to_check_map = None ):
		"""Create and return a layout displaying the given check instance
		@note: its using self.checkuicls to create the instance"""
		check_child = self.checkuicls( check = name_to_check_map[ checkid ] )
		name_to_child_map[ checkid ] = check_child
		newItem = self.add( check_child )
		
		self.setActive()		# assure we are active, as we are called in a loop
		return newItem
		
	def updateItem( self, checkid, name_to_child_map = None, **kwargs ):
		"""Update the item identified by the given checkid so that it represents the 
		current state of the application"""
		name_to_child_map[ checkid ].update( )
	
	def removeItem( self, checkid, name_to_child_map = None, **kwargs ):
		"""Delete the user interface portion representing the checkid"""
		self.deleteChild( name_to_child_map[ checkid ] )
		
	#} END iitemset implementation
	
	def checkHandler( self, event, check, *args ):
		"""Called for the given event - it will find the UI element handling the 
		call respective function on the UI instance
		@note: find the check using predefined names as they server as unique-enough keys.
		This would possibly be faster, but might not make a difference after all"""
		# find a child handling the given check
		# skip ones we do not find 
		checkchild = None
		for child in self.listChildren():
			if child.getCheck() == check:
				checkchild = child
				break
			# END if check matches
		# END for each child in children
		
		# this could actually happen as we get calls for all checks, not only 
		# for the ones we actually have 
		if checkchild is None:
			return
			
		if event == self.qaworkflowcls.e_preCheck:
			checkchild.preCheck( )
		elif event == self.qaworkflowcls.e_postCheck:
			checkchild.postCheck( args[0] )			# the result
		elif event == self.qaworkflowcls.e_checkError:
			checkchild.checkError( )
			
		
	 
	
