# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo.automation.workflows}

Intialize suite checking all workflows

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: __init__.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
import byronimotest.byronimo.automation.processes as process # assure procs are initialized
import byronimotest as common
import byronimo.automation.base as wflbase
from byronimo.path import Path
from byronimo.automation.qa import QAWorkflow

#{ Interface
def createWorkflow( workflowName ):
	"""Create the workflow matching the given name """
	return wflbase.loadWorkflowFromDotFile( Path( __file__ ).p_parent / workflowName + ".dot" )
# END interface


#{ Initialize
def init_loadWorkflows( ):
	_this_module = __import__( "byronimotest.byronimo.automation.workflows", globals(), locals(), ['workflows'] )
	wflbase.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dot" ) )
	wflbase.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dotQA" ), workflowcls = QAWorkflow )


# load all the test workflows
init_loadWorkflows( )


#} initialize


def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import byronimotest.byronimo.automation.workflows as self
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

