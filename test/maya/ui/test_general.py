# -*- coding: utf-8 -*-
"""
Test some default ui capababilities



"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import mayarv.maya.ui as ui
import mayarv.maya.ui.qa as qaui
from mayarv.util import capitalize
import maya.cmds as cmds
import sys

class TestGeneralUI( unittest.TestCase ):
	""" Test general user interace functionality """

	def setUp( self ):
		""" """
		pass

	def disabled_test_createClasses( self ):
		"""mayarv.maya.ui: Instantiate our pseudoclasses
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
		"""mayarv.maya.ui: create some windows"""
		if cmds.about( batch=1 ):
			return

		win = ui.Window( title="Test Window" )
		win.p_title = "Another Title"
		self.failUnless( win.p_title == "Another Title" )

		col = ui.ColumnLayout( adj=1 )
		self.failUnless( col.exists() )
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

		win.p_iconName = "testicon"
		self.failUnless( win.p_iconName == "testicon" )

		win.p_minimizeButton = False
		win.p_minimizeButton = True
		self.failUnless( win.p_minimizeButton == True )

		win.p_maximizeButton = False
		win.p_maximizeButton = True
		self.failUnless( win.p_maximizeButton == True )

		win.p_toolbox = False
		win.p_toolbox = True
		self.failUnless( win.p_toolbox == True )

		win.p_titleBarMenu = True
		win.p_titleBarMenu = False
		if not cmds.about( linux = 1 ):
			self.failUnless( win.p_titleBarMenu == False )

		win.p_menuBarVisible = True
		win.p_menuBarVisible = False
		self.failUnless( win.p_menuBarVisible == False )

		tlc = win.p_topLeftCorner
		win.p_topLeftCorner = ( tlc[1], tlc[0] )

		win.getMenuArray()
		self.failUnless( win.exists() )
		# win.delete()


	def test_layouts( self ):
		"""mayarv.maya.ui: test basic layout functions"""
		if cmds.about( batch=1 ):
			return
		win = ui.Window( title="Test Window" )
		sys.___layoutwin = win
		col = win.add( ui.ColumnLayout( adj=1 ) )

		if col:
			bname = "mybutton"
			b1 = col.add( ui.Button( l="one" ) )
			b2 = col.add( ui.Button( name=bname, l="two" ) )

			self.failUnless( "mybutton" in b2 )
			self.failUnless( b1.exists() )

			self.failUnless( col[ str( b1 ) ] == b1 )

			def func( b ):
				b.p_label = "pressed"
				b2.p_label = "affected"

			sys.___layoutfunc = func
			b1.e_released = func

			grid = col.add( ui.GridLayout( ) )
			if grid:
				bduplname = ui.Button( l="gone", name=bname )

				assert bduplname.getBasename() == b2.getBasename()
				grid.add( bduplname )	 # different parents may have a child with same name
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
		"""mayarv.maya.ui: test callbacks and handling - needs user interaction"""
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
			b.e_released = func
		col.setParentActive()

		win.show()

	def test_menus( self ):
		"""mayarv.maya.ui: use menu bars and menuItems"""
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
		"""mayarv.maya.ui: test progress window functionality"""
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
			time.sleep( 0.01 )
		progress.end()


		# RANGE CHECK
		progress.set( -10 )
		self.failUnless( progress.get() == 0 )

		progress.set( maxrange * 2 )
		self.failUnless( progress.get() == maxrange )

	def test_qa( self ):
		"""mayarv.maya.ui.qa: test qa interface by setting some checks"""
		if cmds.about( batch=1 ):
			return

		import mayarv.test.automation.workflows as workflows

		qawfl = workflows.qualitychecking
		checks = qawfl.listChecks( )

		win = ui.Window( title="QA Window" )
		incol = ui.ColumnLayout( adj = 1 )
		if incol:
			qa = qaui.QALayout( )
			qa.setChecks( checks )

			assert len( qa.getChecks() ) == len( checks )

			# another layout without runall button
			incol.setActive()
			qaui.QALayout.run_all_button = False
			qa = qaui.QALayout( )
			qa.setChecks( checks )
		# END incol
		incol.setParentActive()

		win.show()

	def test_prompt( self ):
		"""mayarv.maya.ui.dialog: Test prompt window"""
		ui.Prompt( title="test title", m="enter test string", d="this", cd="cthis", t="confirm", ct="cancel" ).prompt()
