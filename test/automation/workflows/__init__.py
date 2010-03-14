# -*- coding: utf-8 -*-
""" Intialize suite checking all workflows """
import mayarv.test.automation.processes as process # assure procs are initialized
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
