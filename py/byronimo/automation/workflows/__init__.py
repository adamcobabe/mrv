"""B{byronimo.automation.workflows}
Keeps all workflows specific to maya  

@note: L{createWorkflow} method must be supported in a module keeping workflows
@todo: it would be better to have the createWorkflow method in some sort of workflowManager, 
for now that appears like overkill though
@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


from byronimo.path import Path
_this_module = __import__( "byronimo.automation.workflows", globals(), locals(), ['workflows'] )
import pydot
import processes



#{ Interface 
def createWorkflow( workflowName ):
	"""Create the workflow matching the given name - its up to the module how it 
	achieves that. The easiest implementation is to load the workflow from a file
	@note: without an interface method to create a workflow, nested workflows could not 
	resolve their dependencies as they require the workflows they wrap to be existing. To achieve
	that, they call this function to do so on demand"""
	import byronimo.automation.base as common
	return common.loadWorkflowFromDotFile( Path( __file__ ).p_parent / workflowName + ".dot" )

#} END interface 

#{ Initialization


# assure we only do certain things once
if 'init_done' not in locals():
	init_done = False
	
# SYSTEM INITIALIZATIONs
if not init_done:
	import byronimo.automation.base as common
	
	# load all workflows at once 
	common.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dot" ) )

#} END initialization





