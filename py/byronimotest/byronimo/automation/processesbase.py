"""B{byronimotest.byronimo.automation}

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

class TestProcesses( unittest.TestCase ):
	"""Test workflow class"""
	
	def test_workflowProcess( self ):
		"""byronimo.automation.processes: check workflow nested into process"""
		wfl = workflows.workflowwrap
		rate, process = wfl.getTargetRating( unicode( "this" ) )
		self.failUnless( rate != 0 )
		
		# shuold be able to provide exactly the same output the workflow itself
		res = wfl.makeTarget( unicode( "this" ) )
		self.failUnless( res == "this3.020202020" )
		
		# CALLGRAPH 
		################
		# should have just one more node 
		miwfl = workflows.multiinput
		miwfl.makeTarget( unicode( "this" ) )
		self.failUnless( miwfl._callgraph.number_of_nodes() == wfl._callgraph.number_of_nodes() - 1 )
		
		# NESTED WFLS AND PLANS 
		########################
		plan = wfl.getReportInstance( Plan )
		lines = plan.getReport( )
		for l in lines:
			print l
		
