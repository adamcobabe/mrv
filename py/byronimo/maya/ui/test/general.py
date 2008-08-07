"""B{byronimo.ui.general}

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
	
class TestGeneralUI( unittest.TestCase ):
	""" Test general user interace functionality """
	
	def setUp( self ):
		""" """
		pass
	
	def test_createClasses( self ):
		"""byronimo.maya.ui: Instantiate our pseudoclasses """
		#if cmds.about( batch=1 ):
		#	return 
			
		for uitype in ui._typetree.nodes_iter():
			capuitype = capitalize( uitype )
			if capuitype in [ "BaseUI", "NamedUI" ]:
				continue
				
			print capuitype + ": Type before: " + str( ui.__dict__[ capuitype ] )
			
			inst = ui.__dict__[ capuitype ](  )
			
			self.failUnless( isinstance( inst, ui.BaseUI ) )
			if not isinstance( inst, ui.BaseUI ):
				self.failUnless( isinstance( inst, ui.NamedUI ) )
			
			self.failUnless( hasattr( inst, '__melcmd__' ) )
			#print "Type Inst: " + str( type( inst ) )
			#print "Type AnotherInst: " + str( type( anotherinst ) )
			#print "Type Class: " + str( type( ui.__dict__[ capuitype ] ) )
		
	def test_createWindows( self ):
		"""byronimo.maya.ui: create some windows"""
		if cmds.about( batch=1 ):
			return
			
		win = ui.Window( title="Test Window" )
		
		col = ui.ColumnLayout( adj=1 )
		ui.Button( l="first" )
		ui.Button( l="second" )
		ui.Button( l="third" )
		self.failUnless( isinstance( col, ui.Layout ) )
	
	def tearDown( self ):
		""" Cleanup """
		pass 
	
