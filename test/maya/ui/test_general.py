# -*- coding: utf-8 -*-
""" Test some default ui capababilities """
from mrv.test.maya import *
import mrv.maya.ui as ui
from mrv.util import capitalize
import maya.cmds as cmds
import sys

if not cmds.about(batch=1):
	class TestGeneralUI( unittest.TestCase ):
		""" Test general user interace functionality """
	
		def setUp( self ):
			""" """
			pass
	
		def _disabled_test_createClasses( self ):
			win = ui.Window( title="Collector" )
			col = ui.ColumnLayout( adj=1 )
	
			for uitype in ui.typ._typetree.nodes_iter():
				capuitype = capitalize( uitype )
				if capuitype in [ "BaseUI", "NamedUI" ]:
					continue
				
				try:
					inst = ui.__dict__[ capuitype ](  )
				except (RuntimeError, TypeError):
					# TypeError in case of overridden special elements
					# RuntimeError in case the UI element just can't be created
					# standalone
					continue
				# END exception handing
	
				assert isinstance( inst, ui.BaseUI ) 
				if not isinstance( inst, ui.BaseUI ):
					assert isinstance( inst, ui.NamedUI ) 
	
				assert hasattr( inst, '__melcmd__' ) 
	
				# layouts should not stay open
				if isinstance( inst, ui.Layout ):
					inst.setParentActive()
	
			# END for each uitype
	
			col.setParentActive()
			assert len( win.children() ) 
			win.delete()
	
	
		def test_createWindows( self ):
			win = ui.Window( title="Test Window" )
			win.p_title = "Another Title"
			assert win.p_title == "Another Title" 
	
			col = ui.ColumnLayout( adj=1 )
			assert col.exists() 
			assert isinstance( col, ui.Layout ) 
			if col:
				ui.Button( l="first" )
				ui.Button( l="second" )
				ui.Button( l="third" )
				
				# worked last time it was tested, its a simple implementation as well
				# Causes error in python 2.4 though, hence its disabled
				#with ui.ColumnLayout( w=20 ):
				#	ui.Button( l="sub" )
				# END with test
				#b = ui.Button( l="previous column" )
				#assert b.parent() == col 
				# END python 2.6 or higher required
			# END column layout
			win.show()
			
			win.p_iconify = True
			win.p_iconify = False
			assert win.p_iconify == False 
	
			win.p_sizeable = False
			win.p_sizeable = True
	
			# on linux ( gnome at least ), they are always sizeable
			if not cmds.about( linux = 1 ):
				assert win.p_sizeable == True 
	
			win.p_iconName = "testicon"
			assert win.p_iconName == "testicon" 
	
			win.p_minimizeButton = False
			win.p_minimizeButton = True
			assert win.p_minimizeButton == True 
	
			win.p_maximizeButton = False
			win.p_maximizeButton = True
			assert win.p_maximizeButton == True 
	
			win.p_toolbox = False
			win.p_toolbox = True
			assert win.p_toolbox == True 
	
			win.p_titleBarMenu = True
			win.p_titleBarMenu = False
			if cmds.about( nt = 1 ):
				assert win.p_titleBarMenu == False 
	
			win.p_menuBarVisible = True
			win.p_menuBarVisible = False
			assert win.p_menuBarVisible == False 
	
			tlc = win.p_topLeftCorner
			win.p_topLeftCorner = ( tlc[1], tlc[0] )
	
			win.menuArray()
			assert win.exists() 
			# win.delete()
	
	
		def test_layouts( self ):
			win = ui.Window( title="Test Layout Window" )
			col = win.add( ui.ColumnLayout( adj=1 ) )
	
			if col:
				bname = "mybutton"
				b1 = col.add( ui.Button( l="one" ) )
				b2 = col.add( ui.Button( name=bname, l="two" ) )
	
				assert "mybutton" in b2 
				assert b1.exists() 
	
				assert col[ str( b1 ) ] == b1 
	
				def func( b, *args ):
					b.p_label = "pressed"
					b2.p_label = "affected"
	
				b1.e_released = func
	
				grid = col.add( ui.GridLayout( ) )
				if grid:
					bduplname = ui.Button( l="gone", name=bname )
	
					assert bduplname.basename() == b2.basename()
					grid.add( bduplname )	 # different parents may have a child with same name
					grid.add( ui.Button( l="gtwo" ) )
				grid.setParentActive( )
	
	
				btwo = col.add( ui.Button( l="two" ) )
				def func2( b, *args ):
					btwo.p_label = "2nd receiver"
					
				b1.e_released = func2
	
				assert len( col.children( ) ) == 4 
				assert len( col.childrenDeep( ) ) == 6 
				assert grid.parent( ) == col 
				assert grid.parent() is not col 
			col.setParentActive()
	
			win.show()
			# win.delete()	# does not really work as windows stays as zombie
	
		def test_callbacks( self ):
			win = ui.Window( title="Test Callback Window" )
	
			col = win.add( ui.ColumnLayout( adj=1 ) )
			assert win.childByName( str( col ) ) == col 
			def func( b, *args ):
				b.p_label = "pressed"
				sys.stdout.write( str( args ) )
	
			if col:
				b = col.add( ui.Button( l="b with cb" ), set_self_active=1 )
				b.e_released = func
			col.setParentActive()
	
			win.show()
	
		def test_menus( self ):
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
				def cb( self, *args ):
					self.p_label = "pressed"
				mi.e_command = cb
			# END main menu
			menu.setParentActive( )
	
			ui.Menu( l = "second" )
			win.show()
	
		def test_progressWindow( self ):
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
			assert progress.get() == 0 
	
			progress.set( maxrange * 2 )
			print progress.get()
			assert progress.get() == 100.0 
	
	
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
			assert progress.get() == 0 
	
			progress.set( maxrange * 2 )
			assert progress.get() == maxrange 
	
		def test_qa( self ):
			try:
				import mrv.maya.ui.qa as qaui
			except ImportError:
				return
			# END handle existence of QA - maybe this should go into a separate module to exclude, soon
			import mrv.test.automation.workflows as workflows
	
			qawfl = workflows.qualitychecking
			checks = qawfl.listChecks( )
	
			win = ui.Window( title="QA Window" )
			incol = ui.ColumnLayout( adj = 1 )
			if incol:
				qa = qaui.QALayout( )
				# the first one gets strongly bound to the event as this is the default
				# for UI events
				qa.setChecks( checks )
	
				assert len( qa.checks() ) == len( checks )
	
				# another layout without runall button
				incol.setActive()
				qaui.QALayout.run_all_button = False
				qa = qaui.QALayout( )
				# the second one gets only weakly bound as this is the default 
				# for the library events it connects to. Hence we must keep the 
				# instance around
				qa.setChecks( checks )
				sys._qatmp = qa
			# END incol
			incol.setParentActive()
	
			win.show()
	
		def test_uideleted_event(self):
			class Window(ui.Window):
				def uiDeleted(self):
					print "WINDOW DELETION CALLED", self
					super(Window, self).uiDeleted()
					
				def __del__(self):
					print "DESTRUCTOR CALLED ... never happens", self
			# END window class
			
			w = Window(t="uiDelete Callback Checker")
			w.show()
			
		def test_prompt( self ):
			ui.Prompt( title="test title", m="enter test string", d="this", cd="cthis", t="confirm", ct="cancel" ).prompt()
# END if not batch mode
