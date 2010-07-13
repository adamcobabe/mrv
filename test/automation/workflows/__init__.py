# -*- coding: utf-8 -*-
""" Intialize suite checking all workflows """
import mrv.test.automation.processes as process # assure procs are initialized
import mrv.automation.base as wflbase
from mrv.path import make_path
from mrv.automation.qa import QAWorkflow

#{ Interface
def createWorkflow( workflowName ):
	"""Create the workflow matching the given name """
	return wflbase.loadWorkflowFromDotFile( make_path( __file__ ).parent() / workflowName + ".dot" )
# END interface


#{ Initialize
def init_loadWorkflows( ):
	_this_module = __import__( "mrv.test.automation.workflows", globals(), locals(), ['workflows'] )
	wflbase.addWorkflowsFromDotFiles( _this_module, make_path( __file__ ).parent().glob( "*.dot" ) )
	wflbase.addWorkflowsFromDotFiles( _this_module, make_path( __file__ ).parent().glob( "*.dotQA" ), workflowcls = QAWorkflow )


# load all the test workflows
init_loadWorkflows( )


#} initialize
