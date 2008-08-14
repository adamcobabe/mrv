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
import re 

class TestDAGTree( unittest.TestCase ):
	
	def test_dagMethods( self ):
		"""byronimo.util.DAGTree: Test general methods"""
		self.tree = DAGTree( )
		self.tree.add_edge( (0,1) )
		self.tree.add_edge( (0,2) )
		self.tree.add_edge( (0,3) )
		self.tree.add_edge( (1,4) )
		self.tree.add_edge( (4,5) )
	
		self.failUnless( self.tree.parent( 1 ) == 0 )
		self.failUnless( self.tree.parent( 5 ) == 4 )
		self.failUnless( len( list( self.tree.parent_iter( 5 ) ) ) == 3 )
		
	def test_filters( self ):
		"""byronimo.util: test generalized filters"""
		# AND 
		sequence = [ 1,1,1,1,0,1,1 ]
		self.failUnless( len( filter( And( bool, bool, bool ), sequence ) ) == len( sequence ) - 1 ) 
	
		sequence = [ 0, 0, 0, 0, 0, 0 ]
		self.failUnless( len( filter( And( bool ), sequence ) ) == 0 )
		self.failUnless( len( filter( And( lambda x: not bool(x) ), sequence ) ) == len( sequence ) )
		
		# OR
		sequence = [ 0, 0, 1 ]
		self.failUnless( len( filter( Or( bool, lambda x: not bool(x) ), sequence ) ) == 3 )
		
		# regex
		regex = re.compile( "\w" )
		seq = [ "%", "s" ]
		self.failUnless( len( filter( RegexHasMatch( regex ), seq ) ) == 1 )
		
		
	def test_intGenerator( self ):
		"""byronimo.util: test IntKeygenerator"""
		for i in IntKeyGenerator( [ 1,2,3 ] ):
			self.failUnless( isinstance( i, int ) )
