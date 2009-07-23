# -*- coding: utf-8 -*-
"""B{mayarvtest.byronimo.automation}

Test provided base processes
@note: this file is here containing all default prcess tests one gets nasty
dependency probles with the python import system as we always need workflows for testing

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
from byronimo.automation.report import Plan
import processes


class TestProcesses( unittest.TestCase ):
	"""Test workflow class"""

	def test_workflowProcess( self ):
		"""byronimo.automation.process: check workflow nested into process"""
		wfl = workflows.workflowwrap
		workflows.multiinput.writeDot("/usr/tmp/mygraph.dot" )

		self.failUnless( len( list( wfl.iterNodes() ) ) ==  1 )
		rate, process = wfl.getTargetRating( unicode( "this" ) )
		self.failUnless( rate != 0 )

		# shuold be able to provide exactly the same output the workflow itself
		res = wfl.makeTarget( unicode( "this" ) )
		print res
		self.failUnless( res == "this10.020202020202020202020202020202020" )

		# CALLGRAPH
		################
		# nested nodes are containers that do not show as they do not do anything
		# they are just containers after all and should yield the same result if
		# compared to the unwrapped workflow
		miwfl = workflows.multiinput
		miwfl.makeTarget( unicode( "this" ) )
		self.failUnless( miwfl._callgraph.number_of_nodes() == wfl._callgraph.number_of_nodes() )

		# NESTED WFLS AND PLANS
		########################
		#print wfl._callgraph.nodes()
		plan = wfl.getReportInstance( Plan )
		lines = plan.getReport( headline = "WRAPPED WORKFLOW" )


		# MULTI-NESTED WORKFLOW
		########################
		# Two wrapped workflows combined
		mwfl = workflows.multiWorkflow

		# iterate it - nodes should be facaded and you should not get inside
		# we cannot get different nodes than workflow wrappers, even if we
		# traverse the connections
		wnode2 = mwfl.getNodes()[-1]
		lastshell = None
		for shell in wnode2.outChain.iterShells( direction = "up" ):
			self.failUnless( isinstance( shell.node, processes.WorkflowWrapTestProcess ) )
			lastshell = shell

		for shell in lastshell.iterShells( direction = "down" ):
			self.failUnless( isinstance( shell.node, processes.WorkflowWrapTestProcess ) )


		res = mwfl.makeTarget( list( (5,) ) )[0]		# target only
		self.failUnless( res == 65 )			# it went through 6 nodes

		# compute the value directly using the plug as the workflow
		# cannot determine which input is the suitable one
		#self.failUnless( miwfl.makeTarget( object )[0] < res )
		self.failUnlessRaises( AssertionError, miwfl.makeTarget, object )
		mires = miwfl.getNodes()[-1].outChain.get( )

		self.failUnless( mires[0] < res )		# must be 3 nodes only, thus its smaller at least

		# report
		plan = mwfl.getReportInstance( Plan )
		lines = plan.getReport( headline = "MULTI WRAPPED WORKFLOW" )
		self.failUnless( len( lines ) == 7 )
		for l in lines:
			print l

