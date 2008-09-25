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
import processes 


class TestProcesses( unittest.TestCase ):
	"""Test workflow class"""
	
	def test_workflowProcess( self ):
		"""byronimo.automation.processes: check workflow nested into process"""
		wfl = workflows.workflowwrap
		
		workflows.multiinput.writeDot("/usr/tmp/mygraph.dot" )
		
		self.failUnless( len( list( wfl.iterNodes() ) ) ==  1 )
		rate, process = wfl.getTargetRating( unicode( "this" ) )
		self.failUnless( rate != 0 )
		
		# shuold be able to provide exactly the same output the workflow itself
		res = wfl.makeTarget( unicode( "this" ) )
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
		wnode2 = mwfl.getNodes()[-1]
		print "ITERATIING FROM %s upstream" % repr( wnode2.outChain )
		lastshell = None
		for shell in wnode2.outChain.iterShells( direction = "up" ):
			print shell
			lastshell = shell
		print "\n"
		
		# travel downstream again
		for shell in lastshell.iterShells( direction = "down" ):
			print shell 
		print "\n"
		
		# we cannot get different nodes than workflow wrappers, even if we 
		# traverse the connections 
		lastnode = list( mwfl.iterNodes() )[1]
		for shell in lastnode.outChain.iterShells( direction="up" ):
			self.failUnless( isinstance( shell.node, processes.WorkflowWrapTestProcess ) )
		
		res = mwfl.makeTarget( object )[0]		# target only
		print "MultiWorkflow Result = %i" % res
		self.failUnless( res == 45 )			# it went through many nodes
		
		# must be less nodes  - its just one workflow
		self.failUnless( miwfl.makeTarget( object )[0] < res )		
		
		# report 
		plan = mwfl.getReportInstance( Plan )
		lines = plan.getReport( headline = "MULTI WRAPPED WORKFLOW" )
		for l in lines:
			print l
		
