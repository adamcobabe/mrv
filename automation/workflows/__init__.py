# -*- coding: utf-8 -*-
"""Keeps all workflows specific to maya

@note: L{createWorkflow} method must be supported in a module keeping workflows
@todo: it would be better to have the createWorkflow method in some sort of workflowManager,
for now that appears like overkill though
@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


from mayarv.path import Path
_this_module = __import__( "mayarv.automation.workflows", globals(), locals(), ['workflows'] )
import pydot
import mayarv.automation.processes


#{ Initialization


# assure we only do certain things once
if 'init_done' not in locals():
	init_done = False

# SYSTEM INITIALIZATIONs
if not init_done:
	import mayarv.automation.base as common

	# load all workflows at once
	common.addWorkflowsFromDotFiles( _this_module, Path( __file__ ).p_parent.glob( "*.dot" ) )

#} END initialization





