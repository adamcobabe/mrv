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
	
class TestGeneralUI( unittest.TestCase ):
	""" Test general user interace functionality """
	
	def setUp( self ):
		""" """
		pass
	
	def test_dummyTest( self ):
		"""byronimo.maya.ui: Instantiate our pseudoclasses """
		# for uitype in ui._typetree.nodes_iter():
		print type( ui.Button )
		print type( ui.MenuItem )
		
		inst = ui.Button( "othertype", myrarg="type" )
		ui.MenuItem(  )
		
		print type( ui.Button )
		print type( ui.MenuItem )
		print type( ui.BaseUI )
	
	
	def tearDown( self ):
		""" Cleanup """
		pass 
	
