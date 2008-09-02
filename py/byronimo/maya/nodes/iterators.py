"""B{byronimo.maya.nodes.iterators}

Contains different multi-purpose iterators allowing to conveniently walk the dg and 
dag.
@todo: more documentation 

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


import maya.OpenMaya as api
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), [ 'nodes' ] )


def _argsToFilter( args ):
	"""convert the MFnTypes in args list to the respective typeFilter"""
	typeFilter = api.MIteratorType( )
	if args:
		if len(args) == 1 :
			typeFilter.setFilterType ( args[0] ) 
		else :
			# annoying argument conversion for Maya API non standard C types
			scriptUtil = api.MScriptUtil()
			typeIntM = api.MIntArray()
			scriptUtil.createIntArrayFromList( args,  typeIntM )
			typeFilter.setFilterList( typeIntM )
		# we will iterate on dependancy nodes, not dagPaths or plugs
		typeFilter.setObjectType( api.MIteratorType.kMObject )
	# create iterator with (possibly empty) typeFilter
	return typeFilter


def getDgIteartor( *args, **kwargs ):
	"""@return: MItDependencyNodes configured according to args - see docs at 
	L{iterDgNodes}.
	@note: use this method if you want to use more advanced features of the iterator"""
	typeFilter = _argsToFilter( args )
	iterObj = api.MItDependencyNodes( typeFilter )


def iterDgNodes( *args, **kwargs ):
	""" Iterator on MObjects of nodes of the specified types in the Maya scene,
		if a list of tyes is passed as args, then all nodes of a type included in the list will be iterated on,
		if no types are specified, all nodes of the scene will be iterated on
		the types are specified as Maya API types
		@param asNode: if True, the returned value will be wrapped as nod
		default False
		@param predicate: returns True for every object that can be returned by the iteration, 
		default : lambda x: True
		@note: adjusted pymel implementation"""
	
	iterObj = getDgIteartor( *args, **kwargs )
	predicate = kwargs.get( "predicate", lambda x: True )
	asNode = kwargs.get( "asNode", False )
	while not iterObj.isDone() :
		obj = iterObj.thisNode()
		if asNode:
			node = nodes.Node( obj )
			if predicate( node ):
				yield node
		else:
			if predicate( obj ):
				yield obj
		iterObj.next()	
	# END for each obj in iteration 




def getDagIterator( *args, **kwargs ):
	"""@return: MItDagIterator configured according to args - see docs at 
	L{iterDagNodes}.
	@note: use this method if you want to use more advanced features of the iterator"""
	depth = kwargs.get('depth', True)
	underworld = kwargs.get('underworld', False)
	root = kwargs.get('root', None )
	typeFilter = _argsToFilter( args )
	
	# SETUP TYPE FILTER - reset needs to work with root 
	if root is not None:
		if isinstance( root, api.MDagPath ):
			typeFilter.setObjectType( api.MIteratorType.kMDagPathObject )
		else :
			typeFilter.setObjectType( api.MIteratorType.kMObject )
	
	# create iterator with (possibly empty) filter list and flags
	if depth :
		traversal = api.MItDag.kDepthFirst 
	else :
		traversal =	 api.MItDag.kBreadthFirst
		
	iterObj = api.MItDag( typeFilter, traversal )
	
	asNode = kwargs.get('asNode', False )
	predicate = kwargs.get('predicate', lambda x: True )
	if root is not None :
		startObj = startPath = None
		if isinstance( root, api.MDagPath ):
			print "WAS DAG PATH"
			startPath = root
		else:
			startObj = root
			
		iterObj.reset( typeFilter, startObj, startPath, traversal )
	# END if root is set
 
	if underworld :
		iterObj.traverseUnderWorld( True )
	else :
		iterObj.traverseUnderWorld( False )
		
	
	return iterObj

# Iterators on dag nodes hierarchies using MItDag (ie listRelatives)
def iterDagNodes( *args, **kwargs ):
	""" Iterate over the hierarchy under a root dag node, if root is None, will iterate on whole Maya scene
		If a list of types is provided, then only nodes of these types will be returned,
		if no type is provided all dag nodes under the root will be iterated on.
		Types are specified as Maya API types.
		The following keywords will affect order and behavior of traversal:
		@param dagpath:	if True, MDagPaths will be returned ( ~6k paths/s )
						If False, MObjects will be returned - it will return each object only once ( ~10k objs/s ) 
		@param depth: 	if True nodes Mobjects will be returned as a depth first traversal of the hierarchy tree ( ~6k path/s )
				 		if False as a post-order (breadth first) ( ¬3.5k paths/s, or slower, depending on the scene )
						default is True (depth first)
		@param underworld: if True traversal will include a shape's underworld (dag object parented to the shape),
			  				if False underworld will not be traversed,
							default is False (do not traverse underworld )
		@param asNode: 	if True, default false, the returned item will be wrapped into a Node ( 2k Nodes/s )
						default False
		@param root: 	MObject or MDagPath of the object you would like to start iteration on, or None to 
		start on the scene root. The root node will also be returned by the iteration !
		@param predicate: method returninng True if passed in iteration element can be yielded
		default: lambda x: True
		@note: adjusted pymel implementation"""

	# Must define dPath in loop or the iterator will yield
	# them as several references to the same object (thus with the same value each time)
	# instances must not be returned multiple times
	# could use a dict but it requires "obj1 is obj2" and not only "obj1 == obj2" to return true to
	iterObj = getDagIterator( *args, **kwargs )
	
	dagpath = kwargs.get('dagpath', True)
	asNode = kwargs.get('asNode', False )
	predicate = kwargs.get('predicate', lambda x: True )
	if dagpath:
		while not iterObj.isDone( ) :
			dPath = api.MDagPath( )
			iterObj.getPath( dPath )
			if asNode:
				node = nodes.Node( dPath )
				if predicate( node ):
					yield node
			else:
				if predicate( dPath ):
					yield dPath
			iterObj.next()
	# END if using dag paths 
	else:
		# NOTE: sets don't work here, as more than == comparison is required
		instanceset = []	
		
		while not iterObj.isDone() :
			obj = iterObj.currentItem()
			if iterObj.isInstanced( True ) :
				if obj not in instanceset:
					if predicate( obj ):
						yield obj
						instanceset.append( obj )
			else :
				if predicate( obj ):
					yield obj
			iterObj.next()
	# END if using mobjects 
	

def getGraphIterator( nodeOrPlug, *args, **kwargs ):
	"""@return: MItDependencyGraph configured according to args - see docs at 
	L{iterGraph}.
	@note: use this method if you want to use more advanced features of the iterator"""
	startObj = startPlug = None
	if isinstance( nodeOrPlug, api.MPlug ):
		startPlug = nodeOrPlug
	else:
		startObj = nodeOrPlug
		
	upstream = kwargs.get('upstream', False)
	breadth = kwargs.get('breadth', False)
	plug = kwargs.get('plug', False)
	prune = kwargs.get('prune', False)
	typeFilter = _argsToFilter( args )

	if startPlug is not None :
		typeFilter.setObjectType ( MIteratorType.kMPlugObject )
	else :
		typeFilter.setObjectType ( MIteratorType.kMObject )
	
	direction = MItDependencyGraph.kDownstream
	if upstream :
		direction = MItDependencyGraph.kUpstream
		
	traversal =	 MItDependencyGraph.kDepthFirst
	if breadth :
		traversal = MItDependencyGraph.kBreadthFirst 
		
	level = MItDependencyGraph.kNodeLevel
	if plug :
		level = MItDependencyGraph.kPlugLevel
	
	iterObj = MItDependencyGraph( startObj, startPlug, typeFilter, direction, traversal, level )
	
	iterObj.disablePruningOnFilter()
	if prune :
		iterObj.enablePruningOnFilter()
	
	return iterObj	  

def iterGraph( nodeOrPlug, *args, **kwargs ):
	""" Iterate over MObjects of Dependency Graph (DG) Nodes or Plugs starting at a specified root Node or Plug,
		If a list of types is provided, then only nodes of these types will be returned,
		if no type is provided all connected nodes will be iterated on.
		Types are specified as Maya API types.
		The following keywords will affect order and behavior of traversal:
		@param upstream: if True connections will be followed from destination to source,
				  if False from source to destination
				  default is False (downstream)
		@param breadth: if True nodes will be returned as a breadth first traversal of the connection graph,
				 if False as a preorder (depth first)
				 default is False (depth first)
		@param plug: if True traversal will be at plug level (no plug will be traversed more than once),
			  if False at node level (no node will be traversed more than once),
			  default is False (node level)
		@param prune : if True will stop the iteration on nodes than do not fit the types list,
				if False these nodes will be traversed but not returned
				default is False (do not prune) """
	iterObj = getGraphIterator( nodeOrPlug, *args, **kwargs )
	 
	# iterates and yields MObjects
	while not iterObj.isDone() :
		yield (iterObj.thisNode())
		iterObj.next()
	

