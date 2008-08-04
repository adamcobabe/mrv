"""B{byronimo.test.util}
Test misc utility classes


@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-06 12:45:38 +0200 (Tue, 06 May 2008) $"
__revision__="$Revision: 8 $"
__id__="$Id: decorators.py 8 2008-05-06 10:45:38Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
from byronimo.util import *

class TestDAGTree( unittest.TestCase ):
	
	def setUp( self ):
		""" """
		self.tree = DAGTree( )
		self.tree.add_edge( (0,1) )
		self.tree.add_edge( (0,2) )
		self.tree.add_edge( (0,3) )
		self.tree.add_edge( (1,4) )
		self.tree.add_edge( (4,5) )
	
	def test_dagMethods( self ):
		"""byronimo.util.DAGTree: Test general methods"""
		self.failUnless( self.tree.parent( 1 ) == 0 )
		self.failUnless( self.tree.parent( 5 ) == 4 )
		self.failUnless( len( list( self.tree.parent_iter( 5 ) ) ) == 3 )
	
	def tearDown( self ):
		"""  """
		pass 
	
