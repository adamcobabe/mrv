# -*- coding: utf-8 -*-
"""
Contains different multi-purpose iterators allowing to conveniently walk the dg and
dag.
@todo: more documentation



"""



import maya.OpenMaya as api
import maya.cmds as cmds

import base

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


def getDgIterator( *args, **kwargs ):
	"""@return: MItDependencyNodes configured according to args - see docs at
	L{iterDgNodes}.
	@note: use this method if you want to use more advanced features of the iterator"""
	typeFilter = _argsToFilter( args )
	iterObj = api.MItDependencyNodes( typeFilter )
	return iterObj


def iterDgNodes( *args, **kwargs ):
	""" Iterator on MObjects of nodes of the specified types in the Maya scene,
		if a list of tyes is passed as args, then all nodes of a type included in the list will be iterated on,
		if no types are specified, all nodes of the scene will be iterated on
		the types are specified as Maya API types
		@param asNode: if True, the returned value will be wrapped as nod
		default True
		@param predicate: returns True for every object that can be returned by the iteration,
		default : lambda x: True
		@note: adjusted pymel implementation"""

	iterObj = getDgIterator( *args, **kwargs )
	predicate = kwargs.get( "predicate", lambda x: True )
	asNode = kwargs.get( "asNode", True )
	while not iterObj.isDone() :
		obj = iterObj.thisNode()
		if asNode:
			node = base.Node( obj, 1 )
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

	# set start object
	if root is not None :
		startObj = startPath = None
		if isinstance( root, api.MDagPath ):
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
						default True
		@param depth: 	if True Nodes will be returned as a depth first traversal of the hierarchy tree ( ~6k path/s )
				 		if False as a post-order (breadth first) ( ~3.5k paths/s, or slower, depending on the scene )
						default True
		@param underworld: if True traversal will include a shape's underworld (dag object parented to the shape),
			  				if False underworld will not be traversed,
							default is False (do not traverse underworld )
		@param asNode: 	if True, default True, the returned item will be wrapped into a Node ( 2k Nodes/s )
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
	asNode = kwargs.get('asNode', True )
	predicate = kwargs.get('predicate', lambda x: True )
	if dagpath:
		while not iterObj.isDone( ) :
			dPath = api.MDagPath( )
			iterObj.getPath( dPath )
			if asNode:
				node = base.Node( dPath, 1 )
				if predicate( node ):
					yield node
			else:
				if predicate( dPath ):
					yield dPath
			iterObj.next()
		# END while not is done
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
		# END while not is done
	# END if using mobjects


def getGraphIterator( nodeOrPlug, *args, **kwargs ):
	"""@return: MItDependencyGraph configured according to args - see docs at
	L{iterGraph}.
	@note: use this method if you want to use more advanced features of the iterator
	@raise RuntimeError: if the filter types does not allow any nodes to be returned.
	This is a bug in that sense as it should just return nothing. It also shows that
	maya pre-parses the result and then just iterates over a list with the iterator in
	question"""
	startObj = startPlug = None

	pa = api.MPlugArray( )			# have to pass a proper empty plug pointer
	pa.setLength( 1 )				# this is an ugly way to get it - needs just to be valid
									# during mit object initialization
	if isinstance( nodeOrPlug, api.MPlug ):
		startPlug = nodeOrPlug
		startObj = api.MObject()
	elif isinstance( nodeOrPlug, base.Node ):
		startObj = nodeOrPlug._apiobj
		startPlug = pa[0]

	inputPlugs = kwargs.get('input', False)
	breadth = kwargs.get('breadth', False)
	plug = kwargs.get('plug', False)
	prune = kwargs.get('prune', False)
	typeFilter = _argsToFilter( args )

	if startPlug is not None :
		typeFilter.setObjectType( api.MIteratorType.kMPlugObject )
	else :
		typeFilter.setObjectType( api.MIteratorType.kMObject )

	direction = api.MItDependencyGraph.kDownstream
	if inputPlugs :
		direction = api.MItDependencyGraph.kUpstream

	traversal =	 api.MItDependencyGraph.kDepthFirst
	if breadth :
		traversal = api.MItDependencyGraph.kBreadthFirst

	level = api.MItDependencyGraph.kNodeLevel
	if plug :
		level = api.MItDependencyGraph.kPlugLevel

	iterObj = api.MItDependencyGraph( startObj, startPlug, typeFilter, direction, traversal, level )

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
		@param nodeOrPlug: node or plug to start the iteration at
		@param *args: list of MFn node types
		@param input: if True connections will be followed from destination to source,
				  if False from source to destination
				  default is False (downstream)
		@param breadth: if True nodes will be returned as a breadth first traversal of the connection graph,
				 if False as a preorder (depth first)
				 default is False (depth first)
		@param plug: if True traversal will be at plug level (no plug will be traversed more than once),
			  if False at node level (no node will be traversed more than once),
			  default is False (node level)
		@param prune : if True will stop the iteration on nodes that do not fit the types list,
				if False these nodes will be traversed but not returned
				default is False (do not prune)
		@param asNode: if the iteration is on node level, Nodes ( wrapped MObjects ) will be returned
						If False, MObjects will be returned
						default True
		@param predicate: method returning True if passed in iteration element can be yielded
			default: lambda x: True
		@yield: MObject, Node or Plug depending on the configuration flags
		@node: based on pymel"""
	try:
		iterObj = getGraphIterator( nodeOrPlug, *args, **kwargs )
	except RuntimeError:
		# may raise if iteration would yield no results
		raise StopIteration()

	retrievePlugs = not iterObj.atNodeLevel( )
	asNode = kwargs.get( "asNode", True )
	predicate = kwargs.get( 'predicate', lambda x: True )

	# iterates and yields MObjects
	while not iterObj.isDone():
		if retrievePlugs:
			plug = iterObj.thisPlug()
			if predicate( plug ):
				yield plug
		else:
			obj = iterObj.currentItem()
			if asNode:
				node = base.Node( obj, 1 )
				if predicate( node ):
					yield node
			else:
				if predicate( obj ):
					yield obj
		# END if return on node level

		# if node filters are used, it easily throws NULL Object returned errors
		# just because the iteration is depleted - catching this now
		try:
			iterObj.next()
		except RuntimeError:
			raise StopIteration()
	# END of iteration

def getSelectionListIterator( sellist, **kwargs ):
	"""@return: iterator suitable to iterate given selection list - for more info see
	L{iterSelectionList}"""
	filtertype = kwargs.get( "filterType", api.MFn.kInvalid )
	iterator = api.MItSelectionList( sellist, filtertype )
	return iterator

nullplugarray = api.MPlugArray()
nullplugarray.setLength( 1 )
def iterSelectionList( sellist, filterType = api.MFn.kInvalid, predicate = lambda x: True,
					  	asNode = True, handlePlugs = True, handleComponents = False ):
	"""Iterate the given selection list with a filter from *args
	@param sellist: MSelectionList to iterate
	@param filterType: MFnType id acting as simple type filter
	@param asNode: if True, returned MObjects or DagPaths will be wrapped as node, compoents will be
	wrapped as Component objects
	@param handlePlugs: if True, plugs can be part of the selection list and will be returned. This
	implicitly means that the selection list will be iterated without an iterator, and MFnType filters
	will be slower as it is implemented in python. If components are enabled, the tuple returned will be
	( Node, Plug ), asNode will be respected as well
	@param predicate: method returninng True if passed in iteration element can be yielded
	default: lambda x: True
	@param handleComponents: if True, possibly selected components of dagNodes will be returned
	as well - see docs for return value, see handlePlugs
	The predicate will receive the node as well as the component in a tuple ( same as return value )
	@return: Node or Plug on each iteration step ( assuming filter does not prevent that )
	If handleComponents is True, for each Object, a tuple will be returned as tuple( node, component ) where
	component is NullObject ( MObject ) if the whole object is on the list
	@todo: get rid of the nullplug array as it will not handle recursion properly or multithreading """
	if handlePlugs:
		# version compatibility - maya 8.5 still defines a plug ptr class that maya 2005 lacks
		plugcheckfunc = lambda obj: isinstance( obj, api.MPlug )
		if cmds.about( v=1 ).startswith( "8.5" ):
			plugcheckfunc = lambda obj: isinstance( obj, ( api.MPlug, api.MPlugPtr ) )

		# SELECTION LIST MODE
		for i in xrange( sellist.length() ):
			# DAG PATH
			iterobj = None
			component = None
			try:
				iterobj = api.MDagPath( )
				if handleComponents:
					component = api.MObject()
					sellist.getDagPath( i, iterobj, component )
				else:
					sellist.getDagPath( i, iterobj )

			except RuntimeError:
				# TRY PLUG - first as the object could be returned as well if called
				# for DependNode
				try:
					global nullplugarray
					iterobj = nullplugarray[0]
					sellist.getPlug( i, iterobj )
					# try to access the attribute - if it is not really a plug, it will
					# fail and throw - for some reason python can put just the depend node into
					# a plug
					iterobj.attribute()
				except RuntimeError:
				# TRY DG NODE
					iterobj = api.MObject( )
					sellist.getDependNode( i, iterobj )
				# END its not an MObject
			# END its not a dag node

			# should have iterobj now
			if plugcheckfunc( iterobj ):
				# apply filter
				if filterType != api.MFn.kInvalid and iterobj.node().apiType() != filterType:
					continue
					# END apply filter type

				rval = iterobj
				if handleComponents:
					if asNode:
						rval = ( iterobj.getNode(), iterobj )
					else:
						rval = ( iterobj.getNodeApiObj(), iterobj )
				# END handle components

				if predicate( rval ):
					yield rval
			# END YIELD PLUG HANDLING
			else:
				# must be dag or dg node
				filterobj = iterobj
				if isinstance( iterobj, api.MDagPath ):
					filterobj = iterobj.node()

				if filterType != api.MFn.kInvalid and filterobj.apiType() != filterType:
					continue
				# END filter handling

				if asNode:
					node = base.Node( iterobj, 1 )
					if handleComponents:
						if not component.isNull():
							component = base.Component( component )
						rval = ( node, component )
						if predicate( rval ):
							yield rval
					# END as node with components
					else:
						if predicate( node ):
							yield node
					# END asnode without components
				else:
					if predicate( iterobj ):
						yield iterobj
				# END asNode handling
			# END yield iter object  handling

		# END for each element
	else:
		# ITERATOR MODE
		iterator = getSelectionListIterator( sellist, filterType = filterType )

		while not iterator.isDone():
			# try dag object
			itemtype = iterator.itemType( )
			if itemtype == api.MItSelectionList.kDagSelectionItem:
				path = api.MDagPath( )
				if handleComponents:
					component = api.MObject( )
					sellist.getDagPath( i, iterobj, component )
				else:
					iterator.getDagPath( path )

				if asNode:
					node = base.Node( path, 1 )
					if handleComponents:
						if not component.isNull():
							component = base.Component( component )
						rval = ( node, component )
						if predicate( rval ):
							yield rval
					else:

						if predicate( node ):
							yield node
				else:
					if predicate( path ):
						yield path
			elif itemtype == api.MItSelectionList.kDNselectionItem:
				obj = api.MObject()
				iterator.getDependNode( obj )
				if asNode:
					node = base.Node( obj, 1 )
					if predicate( node ):
						yield node
				else:
					if predicate( obj ):
						yield obj
			else:
				# cannot handle the item, its animSelection item  - skip for now
				pass

			iterator.next()
		# END while not done

