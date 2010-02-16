# -*- coding: utf-8 -*-
"""
Intialize suite checking all workflows



"""


import unittest
import sys
import mayarv.test.automation.processes as process # assure procs are initialized
import mayarv.test as common
import mayarv.automation.base as wflbase
from mayarv.path import Path
from mayarv.automation.qa import QAWorkflow

#{ Interface
def createWorkflow( workflowName ):
	"""Create the workflow matching the given name """
	return wflbase.loadWorkflowFromDotFile( Path( __file__ ).p_parent / workflowName + ".dot" )
# END interface


#{ Initialize
def init_loadWorkflows( ):
	_this_module = __import__( "mayarv.test.automation.workflows", globals(), locals(), ['workflows'] )
	wflbase.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dot" ) )
	wflbase.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dotQA" ), workflowcls = QAWorkflow )


# load all the test workflows
init_loadWorkflows( )


#} initialize


def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import mayarv.test.automation.workflows as self
	return common.get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests  """
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )

