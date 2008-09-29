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
from byronimo.automation.processes import *

class TestWorkflow( unittest.TestCase ):
	"""Test workflow class"""
	
	def test_simpleworkflowcreation( self ):
		"""byronimo.automation.workflow: create a simple workflow from a dot file"""
		scwfl = workflows.simpleconnection
		self.failUnless( isinstance( scwfl, Workflow ) )
		
		
		# contents
		self.failUnless( len( list( scwfl.iterNodes() ) ) == 2 )
		
		p1 = scwfl.nodes()[0]
		p2 = scwfl.nodes()[1]
		
		# CONNECTION
		# tested in dgengine test
		
		
		# QUERY TARGETS
		##################
		# assure list is pruned, otherwise it would be 4
		self.failUnless( len( scwfl.getTargetSupportList( ) ) == 5 )
		
		# both are the same and produce the same rating
		self.failUnless( scwfl.getTargetRating( 5 )[0] == 255 )
		self.failUnless( scwfl.getTargetRating( "this" )[0] == 255 )
		# self.failUnless( scwfl.getTargetRating( basestring )[0] == 127 ) # cannot work as we need instance
		self.failUnless( scwfl.getTargetRating( unicode("this") )[0] == 0 ) # cannot be handled, as its too high for us
		self.failUnless( scwfl.getTargetRating( {} )[0] == 0 )	 			# cannot be handled 
		
		self.failUnless( scwfl.getTargetRating( float(2.3) )[0] == 255 )
		
		
		# Target Creation 
		#################
		# generators are always dirty, everyting else depends on something
		res = scwfl.makeTarget( 5 )
		self.failUnless( res == 10 )
		
		res = scwfl.makeTarget( "someInput" )
		self.failUnless( res == "hello world" )
		
		res = scwfl.makeTarget( 4 )
		self.failUnless( res == 8 )
		
		res = scwfl.makeTarget( 2.0 )
		self.failUnless( res == 4.0 )
		
		res = scwfl.makeTarget( 2.5 )
		self.failUnless( res ==5.0 )

	
	def test_callgraph( self ):
		"""byronimo.automation.workflow: assure callgraph can be generated properly"""
		scwfl = workflows.simpleconnection
		
		# ONE NODE ONLY
		####################
		# target resolved by the actual node - no input needed 
		res = scwfl.makeTarget( 5 )		# computes in-node
		from byronimo.automation.report import Plan
		
		cg = scwfl._callgraph
		self.failUnless( len( cg.nodes() ) == 1 )
		self.failUnless( len( cg.edges() ) == 0 )
		
		
		# INPUT REQUIRED  - multiple nodes 
		###############################
		res = scwfl.makeTarget( 2.0 )
		
		cg = scwfl._callgraph
		self.failUnless( len( cg.nodes() ) == 1 )
		self.failUnless( len( cg.edges() ) == 0 )
		
		miwfl = workflows.multiinput
		res = miwfl.makeTarget( unicode( "this" ) )
		cg = miwfl._callgraph
		
		self.failUnless( len( cg.nodes() ) == 4 )
		self.failUnless( len( cg.edges() ) == 3 )
		
	def test_workflowfacades( self ):
		"""byronimo.automation.workflow:  test facades of workflows"""
		wfl = workflows.multiWorkflow
		
