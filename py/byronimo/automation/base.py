"""B{byronimo.automation.base}
general methods and classes   

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


#{ Edit

def _getNodeInfo( node ):
	"""@return: ( nodename, args, kwargs ) - all arguments have been parsed"""
	
	# node.toplabel, node.bottomlabel
	return ( node.label, [], {} )

def _loadWorkflowFromDotFile( dotfile ):
	"""Create a graph from the given dotfile and create a workflow from it.
	The workflow will be fully intiialized with connected process instances
	@return: initialized Workfflow class"""
	import pydot
	import processes
	from workflow import Workflow
	dotgraph = pydot.graph_from_dot_file( dotfile )
	
	if not dotgraph: 
		raise AssertionError( "Returned graph from file %r was None" % dotfile )
	
	
	# use the filename as name
	edge_lut = {}									# string -> processinst
	wfl = Workflow( name=dotfile.p_namebase )
	
	for node in dotgraph.get_node_list():
		
		# can have initializers
		nodeid = node.get_name().strip( '"' )
		processname,args,kwargs = _getNodeInfo( node ) 
		
		# skip nodes with incorrect label - the parser returns one node each time it appears 
		# in the file, although its mentioned in connections, at least if labels are used
		if not isinstance( processname, basestring ):
			continue
		
		# GET PROCESS CLASS
		try: 
			processcls = getattr( processes, processname )
		except AttributeError:
			raise TypeError( "Process '%s' not found in 'processes' module" % processname )
	
		# create instance and add to workflow
		processinst = processcls( wfl, *args, **kwargs )
		edge_lut[ nodeid ] = processinst
		wfl.add_node( processinst )
		
	# END for each node in graph
	
	# ADD EDGES 
	for edge in dotgraph.get_edge_list():
		wfl.add_edge( ( edge_lut[ edge.get_source() ], edge_lut[ edge.get_destination() ] ) )
	
	return wfl
	
	
def addWorkflowsFromDotFiles( module, dotfiles ):
	"""Create workflows from a list of dot-files and add them to the module"""
	for dotfile in dotfiles:
		wflinst = _loadWorkflowFromDotFile( dotfile )
		setattr( module, str( wflinst ) , wflinst )

	
#} END interface 

