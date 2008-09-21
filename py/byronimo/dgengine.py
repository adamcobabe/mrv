"""B{byronimo.automation.dgengine}
Contains a simple but yet powerful dependency graph engine allowing computations 
to be organized more efficiently.

@todo: not using the look-up (dict) based networkx can bring performance ( just by linking nodes directly )
@todo: optimize plug-dirtying - as the call path is mostly predetermined, one could decide much smarter whether
a cache has to be cleared or not ... possibly
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

from networkx import DiGraph, NetworkXError
from collections import deque
import inspect
import weakref
import itertools 

#####################
## EXCEPTIONS ######
###################
#{ Exceptions 

class ConnectionError( Exception ):
	"""Exception base for all plug related errors"""

class PlugIncompatible( ConnectionError, TypeError ):
	"""Thrown whenever plugs are not compatible with each other during connection"""
	
class PlugAlreadyConnected( ConnectionError ):
	"""Thrown if one tries to connect a plug to otherplug when otherplug is already connected"""	

class AccessError( Exception ):
	"""Base class for all errors indicating invalid access"""

class NotWritableError( AccessError ):
	"""Thrown if a non-writable plug is being written to"""
	
class NotReadableError( AccessError ):
	"""Thrown if a non-readable attribute is being read""" 

class MissingDefaultValueError( AccessError ):
	"""Thrown if a default value is missing for input attributes that are not connected"""

class ComputeError( Exception ):
	"""Thrown if the computation done by a plug failed by an unknown exception
	It will be passed on in the exception"""

class ComputeFailed( ComputeError ):
	"""Raised by the derived class computing a value if the computational goal 
	cannot be achieved ( anymore )"""
	
class PlugUnhandled( ComputeError ):
	"""Raised if a plug was not handled by the node's compute method"""

#} END exceptions



#####################
## Iterators  ######
###################
def iterPlugs( rootPlugShell, stopAt = lambda x: False, prune = lambda x: False, 
			   direction = "up", visit_once = False, branch_first = False ):
	"""Iterator starting at rootPlugShell going "up"stream ( input ) or "down"stream ( output )
	breadth first over plugs, applying filter functions as defined.
	@param rootPlugShell: shell at which to start the traversal. The root plug will be returned as well
	@param stopAt: if function returns true for given PlugShell, iteration will not proceed 
	at that point ( possibly continuing at other spots ). Function will always be called, even 
	if the shell would be pruned as well. The shell serving as stop marker will not be returned
	@param prune: if function returns true for given PlugShell, the shell will not be returned 
	but iteration continues.
	@direction: 
		- "up" - upstream, in direction of inputs of plugs
		- "down" - downstream, in direction of outputs of plugs 
	@param visit_once: if True, plugs will only be returned once, even though they are
	@param branch_first: if True, individual branches will be travelled first ( thuse the node 
	will be left quickly following the datastream. 
	If False, the plugs on the ndoe will be returned first before proceeding to the next node
	encountered several times as several noodes are connected to them in some way."""
	visited = set()
	stack = deque()
	stack.append( rootPlugShell )
	
	def addToStack( node, stack, lst, branch_first ):
		if branch_first:
			stack.extend( node.toShell( plug ) for plug in lst )
		else:
			reviter = ( node.toShell( lst[i] ) for i in range( len( lst )-1,-1,-1) )
			stack.extendleft( reviter )
	# END addToStack local method
	
	def addOutputToStack( stack, lst, branch_first ):
		if branch_first:
			stack.extend( lst )
		else:
			stack.extendleft( reversed( lst[:] ) )
	# END addOutputToStack local method 
	
	while stack:
		shell = stack.pop()
		if shell in visited:
			continue
		
		if visit_once:
			visited.add( shell )
		
		if stopAt( shell ):
			continue
			
		if not prune( shell ):
			yield shell
			
		if direction == 'up':
			if shell.plug.providesOutput():			# get internal affects
				addToStack( shell.node, stack, shell.plug._affectedBy, branch_first )
			# END if provides output 
			
			if shell.plug.providesInput():
				# get the inputplug 
				ishell = shell.getInput( )
				if ishell:
					if branch_first:
						stack.append( ishell )
					else:
						stack.appendleft( ishell )
			# END if provides input 
		# END upstream
		else:
			if shell.plug.providesInput():
				# could also be connected - follow them 
				if branch_first:
					# fist the outputs, then the internals ( this ends up with the same effect )
					addToStack( shell.node, stack, shell.plug._affects, branch_first )
					addOutputToStack( stack, shell.getOutputs(), branch_first )
				else:
					addOutputToStack( stack, shell.getOutputs(), branch_first )
					addToStack( shell.node, stack, shell.plug._affects, branch_first )
					
			# END if shell provides input
			
			if shell.plug.providesOutput():
				addOutputToStack( stack, shell.getOutputs(), branch_first )
			# END if shell provides output 
		# END downstream
	# END for each shell on work stack
	


#####################
## Classes    ######
###################

		

class _PlugShell( tuple ):
	"""Handles per-node-instance plug connection setup and storage. As plugs are 
	descriptors and thus an instance of the class, per-node-instance information needs
	special treatment.
	This class is being returned whenever the descriptors get and set methods are called, 
	it contains information about the node and the plug being involved, allowing to track 
	connection info directly using the node dict
	
	This allows plugs to be connected, and information to flow through the dependency graph.
	Plugs never act alone since they always belong to a parent node that will be asked for 
	value computations if the value is not yet cached.
	@note: Do not instantiate this class youself, it must be created by the node as different 
	node types can use different versions of this shell"""
	
	#{ Object Overrides 
	
	def __new__( cls, *args ):
		return tuple.__new__( cls, args )
	
	def __init__( self, *args ):
		"""initialize the shell with a node and a plug"""
		self.node, self.plug = args
		
	def __repr__ ( self ):
		return "%s.%s" % ( self.node, self.plug )
		
	def __str__( self ):
		return repr( self )
		
	#} END object overrides 
	
	
	#{ Values  
	
	def get( self, mode = None ):
		"""@return: value of the plug
		@mode: optional arbitary value specifying the mode of the get attempt"""
		if self.hasCache( ):
			return self.getCache( )
		
		# Output plugs compute values 
		if self.plug.providesOutput( ):
			
			# otherwise compute the value
			try: 
				result = self.node.compute( self.plug, mode )
			except ComputeError,e:
				raise 			
			except Exception,e:		# except all - this is an unknown excetion
				raise ComputeError( "Computation of %r failed with an unhandled exception" % repr( self ), str( e ),e )
				
			# try to cache computed values 
			self.setCache( result )
			return result
		# END plug provides output
		elif self.plug.providesInput( ):	# has to be separately checked 
			# check for connection
			inputshell = self.getInput()
			if not inputshell:
				# check for default value
				if self.plug.attr.default is not None:
					return self.plug.attr.default
				else:
					raise MissingDefaultValueError( "Plug %r has no default value and is not connected - no value can be provided" % repr( self ) )
			# END if we have no input 
			
			# query the connected plug for the value
			return inputshell.get( mode )
		# END plug provides input 
		
		
		
	def set( self, value, ignore_connection = False ):
		"""Set the given value to be used in our plug
		@param ignore_connection: if True, the plug can be destination of a connection and 
		will still get its value set - usually it would be overwritten by the value form the 
		connection. The set value will be cleared if something upstream in it's connection chain 
		changes.
		@raise AssertionError: the respective attribute must be cached, otherwise 
		the value will be lost"""
		flags = self.plug.attr.flags
		if not flags & Attribute.writable:
			raise NotWritableError( "Plug %r is not writable" % repr(self) )
		
		if self.plug.providesOutput( ):
			raise NotWritableError( "Plug %r is not writable as it provides an output itself" % repr(self) ) 
							
		if flags & Attribute.uncached:
			raise AssertionError( "Writable attributes must be cached - otherwise the value will not be held" )
		
		# check connection 
		if not ignore_connection and self.getInput() is not None:
			raise NotWritableError( "Plug %r is connected to %r and thus not explicitly writable" % ( self, self.getInput() ) )
		
		self.setCache( value )
		
		
	def getCompatabilityRate( self, value ):
		"""@return: value between 0 and 255, 0 means no compatability, 255 a perfect match
		if larger than 0, the plug can hold the value ( assumed the flags are set correctly )"""
		return self.plug.attr.getCompatabilityRate( value )
		
		
	#} END values 
	
	#{ Connections 
	
	def connect( self, otherplug, **kwargs ):
		"""Connect this plug to otherplug such that otherplug is an input plug for our output
		@param force: if False, existing connections to otherplug will not be broken, but an exception is raised
		if True, existing connection may be broken
		@return self: on success, allows chained connections 
		@raise PlugAlreadyConnected: if otherplug is connected and force is False
		@raise PlugIncompatible: if otherplug does not appear to be compatible to this one"""
		if not isinstance( otherplug, _PlugShell ):
			raise AssertionError( "Invalid Type given to connect: %r" % repr( otherplug ) )
		
		return self.node.graph.connect( self, otherplug, **kwargs )
		
	
	def disconnect( self, otherplug ):
		"""Remove the connection to otherplug if we are connected to it.
		@note: does not raise if no connection is present"""
		if not isinstance( otherplug, _PlugShell ):
			raise AssertionError( "Invalid Type given to connect: %r" % repr( otherplug ) )
			
		return self.node.graph.disconnect( self, otherplug )
	
	def getInput( self ):
		"""@return: the connected input plug or None if there is no such connection
		@param predicate: plug will only be returned if predicate is true for it
		@note: input plugs have on plug at most, output plugs can have more than one 
		connected plug"""
		return self.node.graph.getInput( self )
		
	def getOutputs( self, **kwargs ):
		"""@return: a list of plugs being the destination of the connection
		@param predicate: plug will only be returned if predicate is true for it - shells will be passed in """
		return self.node.graph.getOutputs( self, **kwargs )
		
	#} END connections

	
	#{Caching
	def _cachename( self ):
		return self.plug._name + "_c"
		
	def hasCache( self ):
		"""@return: True if currently store a cached value"""
		return hasattr( self.node, self._cachename() )
		
	def setCache( self, value ):
		"""Set the given value to be stored in our cache
		@raise: TypeError if the value is not compatible to our defined type"""
		# attr compatability - always run this as we want to be warned if the compute 
		# method returns a value that does not match
		if self.plug.attr.getCompatabilityRate( value ) == 0:
			raise TypeError( "Plug %r cannot hold value %r as it is not compatible" % ( repr( self ), repr( value ) ) )
			
		if self.plug.attr.flags & Attribute.uncached:
			return
		
		setattr( self.node, self._cachename(), value )
		
		# our cache changed - dirty downstream plugs - thus clear the cache
		prune_me = lambda x: x == self
		for shell in iterPlugs( self, direction = "down", prune = prune_me, branch_first = True ):
			shell.clearCache()
			
		
	def getCache( self ):
		"""@return: the cached value or raise
		@raise: ValueError"""
		if self.hasCache():
			return getattr( self.node, self._cachename() )
		
		raise ValueError( "Plug %r did not have a cached value" % repr( self ) )
		
	def clearCache( self ):
		"""Empty the cache of our plug"""
		if self.hasCache():
			del( self.node.__dict__[ self._cachename() ] )
			
	#} END caching
	
	
	
class Graph( DiGraph ):
	"""Holds the nodes and their connections
	
	Nodes are kept in a separate list whereas the plug connections are kept 
	in the underlying DiGraph"""
	
	#{ Overridden Object Methods
	def __init__( self, **kwargs ):
		"""initialize the DiGraph and add some additional attributes"""
		super( Graph, self ).__init__( **kwargs )
		self._nodes = set()			# our processes from which we can make connections
		
	#} END object methods 
	
	
	def copy( self ):
		"""Copy this instance and return it
		@note: its only a shallow copy, all nodes will remain the same, but can 
		have different connections in the copied graph"""
		cpy = super( Graph, self ).copy( )
		cpy._nodes = self._nodes.copy()
		
		return cpy
		
	
	#{ Node Handling 
	def addNode( self, node ):
		"""Add a new node instance to the graph"""
		if not isinstance( node, NodeBase ):
			raise TypeError( "Node %r must be of type NodeBase" % node )
			
		self._nodes.add( node )
		
	def removeNode( self, node ):
		"""Remove the given node from the graph ( if it exists in it )"""
		try:
			self._nodes.remove( node )
		except KeyError:
			pass 
			
	#} END node handling
	
	#{ Query 
	
	def hasNode( self , node ):
		"""@return: True if the node is in this graph, false otherwise"""
		return node in self._nodes
	
	def iterNodes( self, predicate = lambda node: True ):
		"""@return: generator returning all nodes in this graph
		@param predicate: if True for node, it will be returned
		@note: there is no particular order"""
		for node in self._nodes:
			if predicate( node ):
				yield node
		# END for each node 
		
	def iterConnectedNodes( self, predicate = lambda node: True ):
		"""@return: generator returning all nodes that are connected in this graph
		@param predicate: if True for node, it will be returned"""
		# iterate digraph keeping the plugs only ( and thus connected nodes )
		nodes_seen = set()
		for node,plug in self.nodes_iter():
			if node in nodes_seen:
				continue
			nodes_seen.add( node )
			if predicate( node ):
				yield node
		# END for each node 
	#} END query
	
	#{ Connecitons 
	def connect( self, sourceplug, destinationplug, force = False ):
		"""Connect this plug to destinationplug such that destinationplug is an input plug for our output
		@param sourceplug: PlugShell being source of the connection 
		@param destinationplug: PlugShell being destination of the connection 
		@param force: if False, existing connections to destinationplug will not be broken, but an exception is raised
		if True, existing connection may be broken
		@return self: on success, allows chained connections 
		@raise PlugAlreadyConnected: if destinationplug is connected and force is False
		@raise PlugIncompatible: if destinationplug does not appear to be compatible to this one"""
		# assure both nodes are known to the graph
		self._nodes.add( sourceplug.node )
		self._nodes.add( destinationplug.node )
		
		# check compatability 
		if sourceplug.plug.attr.getConnectionAffinity( destinationplug.plug.attr ) == 0:
			raise PlugIncompatible( "Cannot connect %r to %r as they are incompatible" % ( repr( sourceplug ), repr( destinationplug ) ) )
		
		
		oinput = destinationplug.getInput( )
		if oinput is not None:
			if oinput == sourceplug:
				return sourceplug 
				
			if not force:
				raise PlugAlreadyConnected( "Cannot connect %r to %r as it is already connected" % ( repr( sourceplug ), repr( destinationplug ) ) )
				
			# break existing one
			oinput.disconnect( destinationplug )
		# END destinationplug already connected
		
		# connect us
		print "Connected %r -> %r" % ( repr(sourceplug), repr(destinationplug) )
		self.add_edge( sourceplug, v = destinationplug )
		return sourceplug
		
	
	def disconnect( self, sourceplug, destinationplug ):
		"""Remove the connection between sourceplug to destinationplug if they are connected
		@note: does not raise if no connection is present"""
		self.delete_edge( sourceplug, v = destinationplug )
	
	def getInput( self, plugshell ):
		"""@return: the connected input plug of plugshell or None if there is no such connection
		@param predicate: plug will only be returned if predicate is true for it
		@note: input plugs have on plug at most, output plugs can have more than one 
		connected plug"""
		try:
			pred = self.predecessors( plugshell )
			if pred:
				return pred[0]
		except NetworkXError:
			pass		
		
		return None
		
	def getOutputs( self, plugshell, predicate = lambda x : True ):
		"""@return: a list of plugs being the destination of the connection to plugshell 
		@param predicate: plug will only be returned if predicate is true for it - shells will be passed in """
		try:
			return [ s for s in self.successors( plugshell ) if predicate( s ) ]
		except NetworkXError:
			return list()
		
	#} END connections
	
	

class NodeBase( object ):
	"""Base class that provides support for plugs to the superclass.
	It will create some simple tracking attriubtes required for the plug system 
	to work"""
	__slots__ = 'graph'
	shellcls = _PlugShell					# class used to instantiate new shells 
	
	def __init__( self, graph, *args, **kwargs ):
		"""We require a directed graph to track the connectivity between the plugs.
		It must be supplied by the super class and should be as global as required to 
		connecte the NodeBases together properly.
		@note: we are super() compatible, and assure our base is initialized correctly"""
		if not isinstance( graph, Graph ):
			raise TypeError( "A Graph instance is required as input, got %r" % graph )
			
		self.graph = weakref.proxy( graph )		# assure that we do not prevent the workflow from being deleted

	
	#{ Interface
	def compute( self, plug, mode ):
		"""Called whenever a plug needs computation as the value its value is not 
		cached or marked dirty ( as one of the inputs changed )
		@param plug: the static plug instance that requested which requested the computation.
		It is the instance you defined on the class
		@param mode: the mode of operation. Its completely up to the superclasses how that 
		attribute is going to be used
		@note: to be implemented by superclass """
		raise NotImplementedError( "To be implemented by subclass" )
		
	#} END interface
	
	#{ Base
	def toShells( self, plugs ):
		"""@return: list of shells made from plugs and our node"""
		return [ self.shellcls( self, plug ) for plug in plugs ]
		
	def toShell( self, plug ):
		"""@return: a plugshell as suitable to for this class"""
		return self.shellcls( self, plug )
		
	@classmethod
	def getPlugs( cls, predicate = lambda x: True, nodeInstance = None ):
		"""@return: list of static plugs as defined on this node, or PlugShells of nodeInstance
		if it is given 
		@param predicate: return static plug only if predicate is true
		@param nodeInstance: if not None but instance of NodeBase, the returned list 
		will contain plugshells for nodeInstance instead of static plugs"""
		pred = lambda m: isinstance( m, plug )
		
		# BUG: it appears python can also pass in other derived classes instead 
		# of our own one if called through self - it appears python still has some value
		# of a previous call stored
		# thus we only test for base class 
		# if nodeInstance and not isinstance( nodeInstance, cls ):
		if nodeInstance and not isinstance( nodeInstance, NodeBase ):
			msg = "getPlugs: Passed in nodeInstance had invalid type: was %r, should be %r" % ( type( nodeInstance ), cls )
			raise AssertionError( msg )
		# END sanity check
		
		pluggen = ( m[1] for m in inspect.getmembers( cls, predicate = pred ) if predicate( m[1] ) )
		if not nodeInstance:
			return list( pluggen )
		
		# otherwise return the shells right away 
		return [ nodeInstance.toShell( p ) for p in pluggen ]
		
		
	@classmethod
	def getInputPlugs( cls, **kwargs ):
		"""@return: list of plugs suitable as input
		@note: convenience method"""
		return cls.getPlugs( predicate = lambda p: p.providesInput(), **kwargs )
	
	@classmethod
	def getOutputPlugs( cls, **kwargs ):
		"""@return: list of plugs suitable to deliver output
		@note: convenience method"""
		return cls.getPlugs( predicate = lambda p: p.providesOutput(), **kwargs )

	def getConnections( self, inpt, output ):
		"""@return: Tuples of input shells defining a connection of the given type from 
		tuple( InputNodeOuptutShell, OurNodeInputShell ) for input connections and 
		tuple( OurNodeOuptutShell, OutputNodeInputShell )
		@param inpt: include input connections to this node
		@param output: include output connections ( from this node to others )"""
		outConnections = list()
		plugs = self.getPlugs()
		
		# HANDLE INPUT 
		if inpt:
			shells = self.toShells( ( p for p in plugs if p.providesInput() ) )
			for shell in shells:
				ishell = shell.getInput( )
				if ishell:
					outConnections.append( ( ishell, shell ) )
			# END for each shell in this node's shells
		# END input handling 
			
		# HANDLE OUTPUT 
		if output:
			shells = self.toShells( ( p for p in plugs if p.providesOutput() ) )
			for shell in shells:
				outConnections.extend( ( ( shell, oshell ) for oshell in shell.getOutputs() ) )
		# END output handling 
		
		return outConnections
		
	@staticmethod
	def filterCompatiblePlugs( plugs, attribute, raise_on_ambiguity = False ):
		"""@return: sorted list of plugs suitable to deal with the given attribute.
		Thus they could connect to it as well as get their value set.
		List contains tuples of (rate,plug) pairs, the most suitable plug comes first.
		Incompatible plugs will be pruned.
		@param raise_on_ambiguity: if True, the method raises if a plug has the same
		rating as another plug already on the output list, thus it's not clear anymore 
		which plug should handle a request
		@raise TypeError: if ambiguous input was found"""
		
		outSorted = list()
		for plug in plugs:
			rate = plug.attr.getConnectionAffinity( attribute )
			if not rate: 
				continue
			
			outSorted.append( ( rate, plug ) )
		# END for each plug 
		
		outSorted.sort()
		outSorted.reverse()		# high rates first 
		 
		if raise_on_ambiguity:
			prev_rate = -1
			for rate,plug in outSorted:
				if rate == prev_rate:
					raise TypeError( "At least two plugs delivered the same compatabliity rate" )
				prev_rate = rate
			# END for each compatible plug
		# END ambiguous check
		
		return outSorted
	#} END base
	
	
	
class _FacadeShellMeta( type ):
	"""Metaclass building the method wrappers for the _FacadeShell class - not 
	all methods should be overridden, just the ones important to use"""
	
	@staticmethod
	def getUnfacadeMethod( funcname ):
		def unfacadeMethod( self, *args, **kwargs ):
			return getattr( self._toShell(), funcname )( *args, **kwargs )
			
		unfacadeMethod.__name__ = funcname
		return unfacadeMethod
		
	def __new__( metacls, name, bases, clsdict ):
		unfacadelist = clsdict.pop( '__unfacade__' )
		newcls = type.__new__( metacls, name, bases, clsdict )
		
		# create the wrapper functions for the methods that should wire to the 
		# original shell, thus we unfacade them
		for funcname in unfacadelist:
			setattr( newcls, funcname, metacls.getUnfacadeMethod( funcname ) )
		# END for each unfacade method name 
		return newcls
		

class _FacadePlugShell( _PlugShell ):
	"""All connections from and to the FacadeNode must actually start and end there.
	Iteration over internal plugShells is not allowed.
	Thus we override only the methods that matter and assure that the call is handed 
	to the acutal plugShell
	"""
	# list all methods that should not be a facade to our facade node 
	__unfacade__ = [ 'get', 'set', 'hasCache', 'setCache', 'getCache', 'clearCache' ]
	__metaclass__ = _FacadeShellMeta
	
	def _toShell( self ):
		"""@return: convert ourselves to the real shell actually behind this facade plug"""
		return self.node._realShell( self.plug )
		
	
	
	
class FacadeNodeBase( NodeBase ):
	"""Node having no own plugs, but retrieves them by querying other other nodes
	and claiming its his own ones.
	
	Using a non-default shell it is possibly to guide all calls through to the 
	virtual PlugShell.
	
	Derived classes must override _getPlugShells which will be queried when 
	plugs or plugshells are requested. This node will cache the result and do 
	everything required to integrate itself. 
	
	It lies in the nature of this class that the plugs are dependent on a specific instance 
	of this node, thus classmethods of NodeBase have been overridden with instance versions 
	of it.	
	
	@note: this class could also be used for facades Container nodes that provide 
	an interface to their internal nodes"""
	shellcls = _FacadePlugShell		# overriden from NodeBase
	
	
	#{ Overridden Object Methods
	
	def __init__( self, graph, *args, **kwargs ):
		""" Initialize the instance
		@param graph: graph this node is part of"""
		NodeBase.__init__( self, graph, *args, **kwargs )
	
	#} END overridden methods 
	
	#{ Internal Methods 
	def _realShell( self, virtualplug ):
		"""Calls _toRealShell with virtualplug and then all plugs we find in the direcft
		affects relationships. Afterall, all we need is a node owning one of the affected plugs, 
		then we know the node of the original plug"""
		node = None
		try:
			node = self._getNodeByPlug( virtualplug )
		except ValueError:
			# try all that are internally connected
			allaffected = itertools.chain( iter( virtualplug._affectedBy ), iter( virtualplug._affects ) )
			for plug in allaffected:
				try:
					node = self._getNodeByPlug( plug )
				except ValueError:
					pass
			# END for each affected plug 
		# END get real node for virtual plug 
		
		# get the actual shell
		if node:
			return node.toShell( virtualplug )
			
		# no node ?
		raise AssertionError( "%r did not find matching node for plug %r" % ( self, virtualplug ) )
			
	#} END internal methods 
	
	
	#{ NodeBase Methods
	def _getNodeByPlug( self, virtualplug ):
		"""Called when the facade class encounters a virtual plug that needs to be 
		converted to its real shell, thus the (node,plug) pair that originally owns the plug.
		Thus the method shall return a node owning the virtualplug. 
		It will only be called once a facade shell is supposed to be altered, see 
		L{_FacadePlugShell}
		@raise ValueError: if the virtualplug is unknown.
		@note: iterPlugs may actually traverse the plug-internal affects relations and 
		possibly return a shell to a client that your derived class has never seen before.
		You should take that into consideration and raise L{ValueError} if you do not know 
		the plug"""
		raise NotImplementedError( "_toRealShell needs to be implemented by the subclass" )
	                                  
	#} end nodebase methods

class GraphNodeBase( FacadeNodeBase ):
	"""A node wrapping a graph, allowing it to be nested within the node 
	All inputs and outputs on this node are purely virtual, thus they internally connect
	to the wrapped graph.
	
	Internally it keeps a plug -> node association based on what it returns  
	in getPlugs - currently it never delete them.
	"""
	#{ Overridden Object Methods
	
	def __init__( self, graph, wrappedGraph, *args, **kwargs ):
		""" Initialize the instance
		@param graph: graph this node is part of 
		@param wrappedGraph: graph we are wrapping"""
		self.wgraph = wrappedGraph
		self._plugmap = dict()		# plug -> node 
		
		FacadeNodeBase.__init__( self, graph, *args, **kwargs )
	
	#} END overridden methods               
	
	#{ Base Methods
	
	def _iterNodes( self ):
		"""@return: generator for nodes in our graph
		@note: derived classes could override this to just return a filtered view on 
		their nodes"""
		return self.wgraph.iterNodes( )
		
	#} END base
	
	#{ NodeBase Methods 
	
	def _getNodeByPlug( self, virtualplug ):
		"""@return: node matching virtual plug according to our cache"""
		try:
			return self._plugmap[ virtualplug ]
		except KeyError:
			raise ValueError
	
	def getPlugs( self, **kwargs ):
		"""@return: all plugs on leaf node basees
		@note: must be called through an instance, the baseclass version is a class method !"""
		outlist = list()
		hasInstance = kwargs.get( 'nodeInstance', None ) is not None

		for node in self._iterNodes():
			plugresult = node.getPlugs( **kwargs )
			outlist.extend( plugresult )
			
			# update our lookup map
			if hasInstance:
				for shell in plugresult:
					self._plugmap[ shell.plug ] = node
			else:
				for plug in plugresult:
					self._plugmap[ plug ] = node 
			# END update lut map
		# END for node in nodes 
			
		return outlist

	def getInputPlugs( self ):
		"""@return: list of plugs suitable as input
		@note: convenience method
		@note: must be called through an instance, the baseclass version is a class method !"""
		return self.getPlugs( predicate = lambda p: p.providesInput() )

	def getOutputPlugs( self ):
		"""@return: list of plugs suitable to deliver output
		@note: convenience method
		@note: must be called through an instance, the baseclass version is a class method !"""
		return self.getPlugs( predicate = lambda p: p.providesOutput() )
		
	
	#} end NodeBase methods
		
	

class Attribute( object ):
	"""Simple class defining the type of a plug and several flags that 
	affect it
	Additionally it can determine how well suited another attribute is
	
	Flags
	-----
	exact_type: if True, derived classes of our typecls are not considered to be a valid type
	writable: if True, the attribute's plug can be written to
	computable: Nodes are automatically computable if they are affected by another plug.
				If this is not the case, they are marked input only and are not computed.
				If this flag is true, even unaffeted plugs are computable.
				Plugs that affect something are automatically input plugs and will not be computed.
				If the plug does not affect anything and this flag is False, they are seen as input plugs 
				anyway. 
				The system does not allow plugs to be input and output plugs at the same time, thus your compute
				cannot be triggered by your own compute
	cls: if True, the plug requires classes to be set ( instances of 'type' ) , but no instances of these classes
	uncached: if False, computed values may be cached, otherwise they will always be recomputed.
	unconnectable: if True, the node cannot be the destination of a connection
	"""
	kNo, kGood, kPerfect = 0, 127, 255				# specify how good attributes fit together
	exact_type, writable, computable, cls, uncached, unconnectable = ( 1, 2, 4, 8, 16, 32 )
	__slots__ = ( 'typecls', 'flags', 'default' )
	
	def __init__( self, typeClass, flags, default = None ):
		self.typecls = typeClass
		self.flags = flags			# used for bitflags describing mode
		self.default = default
		
		# check default value for compatability !
		if default is not None:
			if self.getCompatabilityRate( default ) == 0:
				raise TypeError( "Default value %r is not compatible with this attribute" % default )
		# END default type check 
		
	def _getClassRating( self, cls, exact_type ):
		"""@return: rating based on value being a class and compare
		0 : value is no type
		255: value matches comparecls, or linearly less if is just part of the mro of value"""
		if not isinstance( cls, type ):
			return 0
			
		mro = self.typecls.mro()
		mro.reverse()
		
		if not cls in mro:
			return 0
			
		if len( mro ) == 1:
			return self.kPerfect
		
		rate = ( float( mro.index( cls ) ) / float( len( mro ) - 1 ) ) * self.kPerfect
		
		if exact_type and rate != self.kPerfect:		# exact type check
			return 0
			
		return rate 

	#{ Interface 
	
	def getConnectionAffinity( self, otherattr ):
		"""@return: rating from 0 to 255 defining the quality of the connection to 
		otherplug. an affinity of 0 mean connection is not possible, 255 mean the connection 
		is perfectly suited.
		The connection is a directed one from self -> otherplug"""
		if otherattr.flags & self.unconnectable:		# destination must be connectable
			return 0
			
		# see whether our class flags match
		if self.flags & self.cls != otherattr.flags & self.cls:
			return 0
			
		# finally check how good our types match 
		return self._getClassRating( otherattr.typecls, otherattr.flags & self.exact_type )
		
		
		
	def getCompatabilityRate( self, value ):
		"""@return: value between 0 and 255, 0 means no compatability, 255 a perfect match
		if larger than 0, the plug can hold the value ( assumed the flags are set correctly )"""
		if isinstance( value, type ):
			# do we need a class ?
			if not self.flags & self.cls:
				return 0		# its a class 
			
			# check compatability
			return self._getClassRating( value, self.flags & self.exact_type )
		# END is class type
		else:
			if not self.flags & self.cls:
				return self._getClassRating( value.__class__, self.flags & self.exact_type )
		# END is instance type 
		
		return 0

	#}


class plug( object ):
	"""Defines an interface allowing to compare compatabilies according to types.
	
	Plugs are implemented as descriptors, thus they will be defined on node class 
	level, and all static information will remain static
	
	As descriptors, they are defined statically on the class, and some additional information 
	such as connectivity, is stored on the respective class instance. These special methods 
	are handled using L{NodeBase} class
	
	Plugs are implemented as descriptors as all type information can be kept per class, 
	whereas only connection information changes per node instance.
	
	Plugs can either be input plugs or output plugs - output plugs affect no other 
	plug on a node, but are affected by 0 or more plugs 
	
	@note: class is lowercase as it is used as descriptor ( acting more like a function )
	"""
	kNo,kGood,kPerfect = ( 0, 127, 255 )
	__slots__ = ( '_name', 'attr', '_affects', '_affectedBy' )
	
	#{ Overridden object methods 
	def __init__( self, name, attribute ):
		"""Intialize the plug with a distinctive name"""
		self._name = name
		self.attr = attribute
		self._affects = list()			# list of plugs that are affected by us
		self._affectedBy = list()		# keeps record of all plugs that affect us
		
	def __str__( self ):
		return self._name
		
	#}
	
	#{ Value access 
	def __get__( self, obj, cls=None ):
		"""A value has been requested - return our plugshell that brings together
		both, the object and the static plug"""
		# in class mode we return ourselves for access
		if obj is not None:	
			return obj.toShell( self )
			
		# class attributes just return the descriptor itself for direct access
		return self
		
	
	def __set__( self, obj, value ):
		"""Just call the set method directly"""
		obj.toShell( self ).set( value )
		
	#}
	
	#{ Interface 
	
	def affects( self, otherplug ):
		"""Set an affects relation ship between this plug and otherplug, saying 
		that this plug affects otherplug."""
		if otherplug not in self._affects:
			self._affects.append( otherplug )
			
		if self not in otherplug._affectedBy:
			otherplug._affectedBy.append( self )
		
	def getAffected( self ):
		"""@return: tuple containing affected plugs ( plugs that are affected by our value )"""
		return tuple( self._affects )
		
	def getAffectedBy( self ):
		"""@return: tuple containing plugs that affect us ( plugs affecting our value )"""
		return tuple( self._affectedBy )
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations"""
		return len( self._affectedBy ) != 0 or self.attr.flags & Attribute.computable
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		#return len( self._affects ) != 0 and not self.providesOutput( )
		return not self.providesOutput() # previous version did not recognize storage plugs as input
		
	#}
	
	
	#{ Types 
	
	
	
	#} END types 
