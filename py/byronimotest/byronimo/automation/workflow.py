"""B{byronimotest.byronimo.automation.workflow}

Test the workflow class 

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
import workflows
from byronimo.automation.workflow import Workflow

class TestWorkflow( unittest.TestCase ):
	"""Test workflow class"""
	
	def test_simpleworkflowcreation( self ):
		"""byronimo.automation.workflow: create a simple workflow from a dot file"""
		scwfl = workflows.simpleconnection
		self.failUnless( isinstance( scwfl, Workflow ) )
		
		# contents
		self.failUnless( len( scwfl.nodes() ) == 2 )
		self.failUnless( len( scwfl.edges() ) == 1 )
		
		p1 = scwfl.nodes()[0]
		p2 = scwfl.nodes()[1]
		
		# CONNECTION 
		self.failUnless( len( scwfl.out_edges( p1 ) ) == 1 )
		self.failUnless( scwfl.out_edges( p1 )[0][1]  == p2 )
		self.failUnless( len( scwfl.in_edges( p2 ) ) == 1 )
		self.failUnless( scwfl.in_edges( p2 )[0][0] == p1 )
		
		self.failUnless( scwfl.successors( p1 )[0] == p2 )
		self.failUnless( scwfl.predecessors( p2 )[0] == p1 )
		
		
		# QUERY TARGETS
		##################
		# assure list is pruned, otherwise it would be 4 
		self.failUnless( len( scwfl.getTargetSupportList( ) ) == 2 )
		
		# both are the same and produce the same rating
		self.failUnless( scwfl.getTargetRating( 5 )[0] == 255 )
		self.failUnless( scwfl.getTargetRating( str )[0] == 127 )
		self.failUnless( scwfl.getTargetRating( basestring )[0] == 255 )	 
		
		self.failUnless( scwfl.getTargetRating( unicode )[0] == 127 )
		self.failUnless( scwfl.getTargetRating( bool )[1] == None )
		
		
		
		# Target Creation  
		#################
		# generators are always dirty, everyting else depends on something
		
		
		
		
		
		
