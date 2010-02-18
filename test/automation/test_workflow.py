# -*- coding: utf-8 -*-
"""
Test the workflow class



"""
import unittest
import workflows
import mayarv.automation.workflow as workflow
from mayarv.automation.workflow import Workflow
from mayarv.automation.process import *
from cStringIO import StringIO

class TestWorkflow( unittest.TestCase ):
	"""Test workflow class"""

	def test_simpleworkflowcreation( self ):
		"""mayarv.automation.workflow: create a simple workflow from a dot file"""
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
		self.failUnless( res == 20 )

		res = scwfl.makeTarget( "someInput" )
		self.failUnless( res == "hello world" )

		res = scwfl.makeTarget( 4 )
		self.failUnless( res == 16 )

		res = scwfl.makeTarget( 2.0 )
		self.failUnless( res == 8.0 )

		res = scwfl.makeTarget( 2.5 )
		self.failUnless( res == 10.0 )


	def test_simpleDirtyCheck( self ):
		"""mayarv.automation.workflow: test a simple dirtycheck"""
		scwfl = workflows.simpleconnection
		scwfl.getDirtyReport( 5, mode="deep" )
		d = workflow.DirtyException()


	def test_callgraph( self ):
		"""mayarv.automation.workflow: assure callgraph can be generated properly"""
		scwfl = workflows.simpleconnection

		# ONE NODE ONLY
		####################
		# target resolved by the actual node - no input needed
		res = scwfl.makeTarget( 5 )		# computes in-node
		from mayarv.automation.report import Plan

		cg = scwfl._callgraph
		self.failUnless( len( cg.nodes() ) == 2 )
		self.failUnless( len( cg.edges() ) == 1 )


		# INPUT REQUIRED  - multiple nodes
		###############################
		res = scwfl.makeTarget( 2.0 )

		cg = scwfl._callgraph
		self.failUnless( len( cg.nodes() ) == 2 )
		self.failUnless( len( cg.edges() ) == 1 )

		miwfl = workflows.multiinput
		res = miwfl.makeTarget( unicode( "this" ) )
		cg = miwfl._callgraph

		self.failUnless( len( cg.nodes() ) == 5 )
		self.failUnless( len( cg.edges() ) == 4 )

	def test_multiTarget( self ):
		"""mayarv.automation.workflow: test multiple targets at once"""
		scwfl = workflows.simpleconnection
		listtypes = ( None, list, StringIO )

		# test it with all possible value types
		for errtype in listtypes:
			errtypeinst = errtype
			if errtype is not None:
				errtypeinst = errtype()
			for outtype in listtypes:
				outtypeinst = outtype
				if outtype is not None:
					outtypeinst = outtype()

				scwfl.makeTargets( (1.0,2.0,3.0), errtypeinst, outtypeinst )
			# END for each done type
		# END for each outtype



	def test_workflowfacades( self ):
		"""mayarv.automation.workflow:  test facades of workflows"""
		wfl = workflows.multiWorkflow

