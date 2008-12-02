# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo.maya.ui.general}

Test some default ui capababilities 

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


import unittest
import byronimo.maya.ui as ui
from byronimo.util import capitalize
import maya.cmds as cmds
import sys
	
class TestGeneralUI( unittest.TestCase ):
	""" Test general user interace functionality """
	
	def setUp( self ):
		""" """
		pass
	
	def disabled_test_createClasses( self ):
		"""byronimo.maya.ui: Instantiate our pseudoclasses 
		@note: this test is not required anymore"""
		if cmds.about( batch=1 ):
			return
			
		win = ui.Window( title="Collector" )
		col = ui.ColumnLayout( adj=1 )
		
		for uitype in ui._typetree.nodes_iter():
			capuitype = capitalize( uitype )
			if capuitype in [ "BaseUI", "NamedUI" ]:
				continue
				
			try: 
				inst = ui.__dict__[ capuitype ](  )
			except RuntimeError:
				continue
			
			self.failUnless( isinstance( inst, ui.BaseUI ) )
			if not isinstance( inst, ui.BaseUI ):
				self.failUnless( isinstance( inst, ui.NamedUI ) )
				
			self.failUnless( hasattr( inst, '__melcmd__' ) )
			
			# layouts should not stay open
			if isinstance( inst, ui.Layout ):
				inst.setParentActive()
				
		# END for each uitype
		
		col.setParentActive()
		self.failUnless( len( win.getChildren() ) )
		win.delete()
		
		
	def test_createWindows( self ):
		"""byronimo.maya.ui: create some windows"""
		if cmds.about( batch=1 ):
			return
			
		win = ui.Window( title="Test Window" )
		win.p_title = "Another Title"
		self.failUnless( win.p_title == "Another Title" )
		
		col = ui.ColumnLayout( adj=1 )
		ui.Button( l="first" )
		ui.Button( l="second" )
		ui.Button( l="third" )
		self.failUnless( isinstance( col, ui.Layout ) )
		
		win.show()
		win.p_iconify = True
		win.p_iconify = False
		self.failUnless( win.p_iconify == False )
		
		win.p_sizeable = True
		win.p_sizeable = False
		
		# on linux ( gnome at least ), they are always sizeable
		if not cmds.about( linux = 1 ): 
			self.failUnless( win.p_sizeable == False )
		
		win.p_iconname = "testicon"
		self.failUnless( win.p_iconname == "testicon" )
		
		win.p_minimizebutton = False
		win.p_minimizebutton = True
		self.failUnless( win.p_minimizebutton == True )
		
		win.p_maximizebutton = False
		win.p_maximizebutton = True
		self.failUnless( win.p_maximizebutton == True )
		
		win.p_toolbox = False
		win.p_toolbox = True
		self.failUnless( win.p_toolbox == True )
		
		win.p_titlebarmenu = True
		win.p_titlebarmenu = False
		if not cmds.about( linux = 1 ):
			self.failUnless( win.p_titlebarmenu == False )
		
		win.p_menubarvisible = True
		win.p_menubarvisible = False
		self.failUnless( win.p_menubarvisible == False )

		tlc = win.p_topleftcorner
		win.p_topleftcorner = ( tlc[1], tlc[0] )
		
		win.getMenuArray()
		# win.delete()

	
	def test_layouts( self ):
		"""byronimo.maya.ui: test basic layout functions"""
		if cmds.about( batch=1 ):
			return
		win = ui.Window( title="Test Window" )
		sys.___layoutwin = win
		col = win.add( ui.ColumnLayout( adj=1 ) )
		
		if col:
			b1 = col.add( ui.Button( l="one" ) )
			b2 = col.add( ui.Button( name="mybutton", l="two" ) )
			self.failUnless( "mybutton" in b2 )
			
			self.failUnless( col[ str( b1 ) ] == b1 )
			
			def func( b ):
				b.p_label = "pressed"
				b2.p_label = "affected"
				
			sys.___layoutfunc = func
			b1.e_released = func
			
			grid = col.add( ui.GridLayout( ) )
			if grid:
				grid.add( ui.Button( l="gone" ) )
				grid.add( ui.Button( l="gtwo" ) )
			grid.setParentActive( )
			
			col.add( ui.Button( l="two" ) )
			
			self.failUnless( len( col.getChildren( ) ) == 4 )
			self.failUnless( len( col.getChildrenDeep( ) ) == 6 )
			self.failUnless( grid.getParent( ) == col )
		col.setParentActive()
		
		win.show()
		# win.delete()	# does not really work as windows stays as zombie
		
	def test_callbacks( self ):
		"""byronimo.maya.ui: test callbacks and handling - needs user interaction"""
		if cmds.about( batch=1 ):
			return
			
		win = ui.Window( title="Test Window" )
		sys.___callbackwin = win				# keep it
		
		col = win.add( ui.ColumnLayout( adj=1 ) )
		self.failUnless( win.getChildByName( str( col ) ) == col )
		def func( *args ):
			b = args[0]
			b.p_label = "pressed"
			b.p_actionissubstitute = 1
			sys.stdout.write( str( args ) )
			
		sys.__mytestfunc = func		# to keep it alive, it will be weakly bound
		
		if col:
			b = col.add( ui.Button( l="b with cb" ), set_self_active=1 )
			b.e_pressed = func
		col.setParentActive()
		
		win.show()

	def test_menus( self ):
		"""byronimo.maya.ui: use menu bars and menuItems"""
		if cmds.about( batch=1 ):
			return
			
		win = ui.Window( title="Menu Window", menuBar=1 )
		menu = ui.Menu( l = "first" )
		if menu:
			ui.MenuItem( l = "item" )
			sm = ui.MenuItem( l = "submenu", sm=1, aob=1 )
			if sm:
				smmenu = sm.toMenu()
				ui.MenuItem( l = "smmenu" )
			# END submenu
			smmenu.setParentActive()
			
			mi = ui.MenuItem( l = "otherMenuItem" )
			def cb( self ):
				self.p_label = "pressed"
			mi.e_command = cb
		# END main menu
		menu.setParentActive( )
		
		
		ui.Menu( l = "second" )
		
		
		
		win.show()

	def test_progressWindow( self ):
		"""byronimo.maya.ui: test progress window functionality"""
		if cmds.about( batch=1 ):
			return
			
		maxrange = 10
		import time
		progress = ui.ProgressWindow( min = 0, max = maxrange, is_relative = 1 )
		
		# RELATIVE ITERATION 
		progress.begin()
		for i in range( maxrange ):
			progress.set( i, "my message" )
			time.sleep( 0.025 )
		progress.end()
		
		
		# RANGE CHECK 
		progress.set( -10 )
		self.failUnless( progress.get() == 0 ) 
		
		progress.set( maxrange * 2 )
		print progress.get()
		self.failUnless( progress.get() == 100.0 )
		
		
		# ABSOLUTE ITERATION
		#######################
		progress.setRelative( False )
		progress.setAbortable( True )
		progress.begin()
		for i in range( maxrange ):
			progress.set( i )
			time.sleep( 0.025 )
		progress.end()
		
		
		# RANGE CHECK  
		progress.set( -10 )
		self.failUnless( progress.get() == 0 ) 
		
		progress.set( maxrange * 2 )
		self.failUnless( progress.get() == maxrange )
