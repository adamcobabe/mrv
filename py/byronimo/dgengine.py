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

from networkx import DiGraph, NetworkXError, XDiGraph
from collections import deque
import inspect
import weakref
import itertools
import copy
from byronimo.util import iDuplicatable

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
#{ Iterators 
def iterShells( rootPlugShell, stopAt = lambda x: False, prune = lambda x: False, 
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
		if len( lst ):
			print "1__adding to stack %s(%s)" % (lst[0],type(node.shellcls))
		if branch_first:
			stack.extend( node.toShell( plug ) for plug in lst )
		else:
			reviter = ( node.toShell( lst[i] ) for i in range( len( lst )-1,-1,-1) )
			stack.extendleft( reviter )
	# END addToStack local method
	
	def addOutputToStack( stack, lst, branch_first ):
		if len( lst ):
			print "2__adding OUTPUT to stack %s(%s)" % (str(lst),type(lst))
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
			print "--> YIELD %s" % repr( shell )
			yield shell
		
		print "ITERATE %s: %r" % ( direction, repr( shell ) )
		if direction == 'up':
			# I-N-O 
			addToStack( shell.node, stack, shell.plug.getAffectedBy(), branch_first )
			# END if provides output 
			
			# O<-I
			ishell = shell.getInput( )
			print "ISHELL: %r" % repr(ishell)
			if ishell:
				if branch_first:
					stack.append( ishell )
				else:
					stack.appendleft( ishell )
			# END has input connection 
		# END upstream
		else:
			# I-N-O and I->O
			# could also be connected - follow them 
			if branch_first:
				# fist the outputs, then the internals ( this ends up with the same effect )
				addToStack( shell.node, stack, shell.plug.getAffected(), branch_first )
				addOutputToStack( stack, shell.getOutputs(), branch_first )
			else:
				addOutputToStack( stack, shell.getOutputs(), branch_first )
				addToStack( shell.node, stack, shell.plug.getAffected(), branch_first )
		# END downstream
	# END for each shell on work stack

#} END iterators 


#####################
## Classes    ######
###################


#{ END Plugs and Attributes

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
	def getAffinity( self, otherattr ):
		"""@return: rating from 0 to 255 defining how good the attribtues match 
		each other in general.
		@note: for checking connections, use L{getConnectionAffinity}"""
		# see whether our class flags match
		if self.flags & self.cls != otherattr.flags & self.cls:
			return 0
			
		# finally check how good our types match 
		return self._getClassRating( otherattr.typecls, otherattr.flags & self.exact_type )
	
	def getConnectionAffinity( self, otherattr ):
		"""@return: rating from 0 to 255 defining the quality of the connection to 
		otherplug. an affinity of 0 mean connection is not possible, 255 mean the connection 
		is perfectly suited.
		The connection is a directed one from self -> otherplug"""
		if otherattr.flags & self.unconnectable:		# destination must be connectable
			return 0
			
		return self.getAffinity( otherattr )
		
		
		
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

	#} END interface 



class iPlug( object ):
	"""Defines an interface allowing to compare compatabilies according to types.
	
	Plugs can either be input plugs or output plugs - output plugs affect no other 
	plug on a node, but are affected by 0 or more plugs .
	
	By convention, a plug has a name - that name must also be the name of the 
	member attribute that stores the plag. Plugs, possibly different instances of it, 
	need to be re-retrieved on freshly duplicated nodes to allow graph duplication to 
	be done properly
	
	@note: if your plug class supports the L{setName} method, a metaclass will 
	adjust the name of your plug to match the name it has in the parent class 
	"""
	kNo,kGood,kPerfect = ( 0, 127, 255 )
	
	#{ Base Implementation 
	def __str__( self ):
		return self.getName()
	
	#} END base implementation  
	
		
	#{ Interface 
	def getName( self ):
		"""@return: name of the plug ( the name that identifies it on the node"""
		raise NotImplementedError( "Implement this in subclass" )
		
	def affects( self, otherplug ):
		"""Set an affects relation ship between this plug and otherplug, saying 
		that this plug affects otherplug."""
		raise NotImplementedError( "Implement this in subclass" )
		
	def getAffected( self ):
		"""@return: tuple containing affected plugs ( plugs that are affected by our value )"""
		raise NotImplementedError( "Implement this in subclass" )
		
	def getAffectedBy( self ):
		"""@return: tuple containing plugs that affect us ( plugs affecting our value )"""
		raise NotImplementedError( "Implement this in subclass" )
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations"""
		raise NotImplementedError( "Implement this in subclass" )
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		raise NotImplementedError( "Implement this in subclass" )
		
	#}
	

class plug( iPlug ):
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
	def __init__( self, attribute ):
		"""Intialize the plug with a distinctive name"""
		self._name = None
		self.attr = attribute
		self._affects = list()			# list of plugs that are affected by us
		self._affectedBy = list()		# keeps record of all plugs that affect us
	
	#} END object overridden methods 

	#{ Value access 
	
	def __get__( self, obj, cls=None ):
		"""A value has been requested - return our plugshell that brings together
		both, the object and the static plug"""
		# in class mode we return ourselves for access
		if obj is not None:
			return obj.toShell( self )
			
		# class attributes just return the descriptor itself for direct access
		return self
		
	
	#def __set__( self, obj, value ):
		"""We do not use a set method, allowing to override our descriptor through 
		actual plug instances in the instance dict. Once deleted, we shine through again"""
		# raise AssertionError( "To set this value, use the node.plug.set( value ) syntax" )
		# obj.toShell( self ).set( value )
		
	#} value access

	#{ Interface
	
	def getName( self ):
		"""@return: name of plug"""
		return self._name
		
	def setName( self, name ):
		"""Set the name of this plug - can be set only once"""
		if not self._name:
			self._name = name
		else:
			raise ValueError( "The name of the plug can only be set once" )
	
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
		return bool( len( self.getAffectedBy() ) != 0 or self.attr.flags & Attribute.computable )
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		#return len( self._affects ) != 0 and not self.providesOutput( )
		return not self.providesOutput() # previous version did not recognize storage plugs as input
		
	#} END interface 
	
#} END plugs and attributes


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
		
	def __getattr__( self, attr ):
		"""Allow easy attribute access while staying memory efficient"""
		if attr == 'node':
			return self[0]
		if attr == 'plug':
			return self[1]
			
		# let it raise the typical error
		return super( _PlugShell, self ).__getattribute__( attr )
		
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
	
	def getInput( self, predicate = lambda shell: True ):
		"""@return: the connected input plug or None if there is no such connection
		@param predicate: plug will only be returned if predicate is true for it
		@note: input plugs have on plug at most, output plugs can have more than one 
		connected plug"""
		sourceshell = self.node.graph.getInput( self )
		if sourceshell and predicate( sourceshell ):
			return sourceshell
		return None
		
	def getOutputs( self, predicate = lambda shell: True ):
		"""@return: a list of plugs being the destination of the connection
		@param predicate: plug will only be returned if predicate is true for it - shells will be passed in """
		return self.node.graph.getOutputs( self, predicate = predicate )
		
	def getConnections( self, inpt, output, predicate = lambda shell: True ):
		"""@return: get all input and or output connections from this shell 
		or to this shell as edges ( sourceshell, destinationshell )
		@param predicate: return true for each destination shell that you can except in the 
		returned edge or the sourceshell where your shell is the destination.
		@note: Use this method to get edges read for connection/disconnection"""
		outcons = list()
		if inpt:
			sourceshell = self.getInput( predicate = predicate )
			if sourceshell: 
				outcons.append( ( sourceshell, self ) )
		# END input connection handling 
			
		if output:
			outcons.extend( ( self, oshell ) for oshell in self.getOutputs( predicate = predicate ) )
			
		return outcons
		
	def iterShells( self, **kwargs ):
		"""Iterate plugs and their connections starting at this plug
		@return: generator for plug shells
		@note: supports all options of L{iterShells}, this method allows syntax like:
		node.outAttribute.iterShells( )"""
		return iterShells( self, **kwargs )
		
	#} END connections

	
	#{Caching
	def _cachename( self ):
		return self.plug.getName() + "_c"
		
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
		for shell in iterShells( self, direction = "down", prune = prune_me, branch_first = True ):
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
	
	
	#{ Name Overrides
	__rshift__ = lambda self,other: self.connect( other, force=True )
	__gt__ = lambda self,other: self.connect( other, force=False )
	
	#} END name overrides 
	
	
	
class Graph( DiGraph, iDuplicatable ):
	"""Holds the nodes and their connections
	
	Nodes are kept in a separate list whereas the plug connections are kept 
	in the underlying DiGraph"""
	
	#{ Overridden Object Methods
	def __init__( self, **kwargs ):
		"""initialize the DiGraph and add some additional attributes"""
		super( Graph, self ).__init__( **kwargs )
		self._nodes = set()			# our processes from which we can make connections
		
	def __del__( self ):
		"""Clear our graph"""
		self.clear()				# clear connections
		
		# NOTE : nodes will remove themselves once they are not referenced anymore
		self._nodes.clear()
		
	#} END object methods 
	
	#{ Debugging
	def writeDot( self , fileOrPath  ):
		"""Write the connections in self to the given file object or path
		@todo: remove if no longer needed"""
		import networkx.drawing.nx_pydot as dotio
		
		# associate every plugshell with its node create a more native look
		writegraph = XDiGraph()
		# but we do not use it as the edge attrs cannot be assigned anymore - dict has no unique keys
		# writegraph.allow_multiedges()	 
		
		graphattrs = { "style" : "filled" }
		nodeattrs = dict()
		edgeattrs = dict()
		
		# EXTRACT DATA 
		for node in self.iterNodes():
			nodeattrs[ node ] = { "color" : "#ebba66", "width" : "4", "height" : "2", "fontsize" : "22" }
			writegraph.add_node( node )
		# END for each node in graph 
		
		# now all the connections - just transfer them 
		for sshell,eshell in self.edges_iter():
			edge = (sshell,eshell)
			writegraph.add_edge( edge )
			
			node_to_shell = (sshell.node,sshell)
			writegraph.add_edge( node_to_shell )
			edgeattrs[ node_to_shell ] = { "color" : "#000000" }	# change color
			
			nodeattrs[ sshell ] = { "color" : "#000000", "label" : sshell.plug }	# change color
			nodeattrs[ eshell ] = { "color" : "#000000", "label" : eshell.plug }	# change color
			
			shell_to_node = (eshell,eshell.node)
			writegraph.add_edge( shell_to_node )
			edgeattrs[ shell_to_node ] = { "color" : "#000000" }	# change color
		# END for each edge in graph
		
		# WRITE DOT FILE 
		fh = dotio._get_fh( fileOrPath ,'w' ) 
		P = dotio.to_pydot( writegraph, graph_attr=graphattrs, node_attr=nodeattrs, edge_attr=edgeattrs )
		P.set( "ratio", "1" )
 		fh.write( P.to_string( ) ) 
 		fh.flush( ) # might be a user filehandle so leave open (but flush) 
		
	#} END debugging 
		
	#{ iDuplicatable Interface 
	def createInstance( self ):
		"""Create a copy of self and return it"""
		return self.__class__( )
		
	def copyFrom( self, other ):
		"""Duplicate all data from other graph into this one, create a duplicate 
		of the nodes as well"""
		print "COPY %r" % self 
		def copyshell( shell, nodemap ):
			nodecpy = nodemap[ shell.node ]
			
			# nodecpy - just get the shell of the given name directly - getattr always creates
			# shells as it is equal to node.plugname
			return getattr( nodecpy, shell.plug.getName() )
		
		# copy name ( networkx )
		self.name = other.name
		
		# copy nodes first
		nodemap = dict()
		for node in other.iterNodes():
			nodecpy = node.duplicate( add_to_graph = False )		# copy node
			nodemap[ node ] = nodecpy
		# END for each node
		
		# add all nodemap values as nodes ( now that iteration is done
		for duplnode in nodemap.itervalues():
			self.addNode( duplnode )
		
		# COPY CONNECTIONS 
		for sshell,eshell in other.edges_iter():
			# make fresh connections through shells - we do not know what kind of 
			# plugs they use, so they could be special and thus need special 
			# copy procedures
			cstart = copyshell( sshell, nodemap )
			cend = copyshell( eshell, nodemap )
			
			cstart.connect( cend )
		# END for each edge( startshell, endshell )
			
		
	# END iDuplicatable
	
		
	#{ Node Handling 
	def addNode( self, node ):
		"""Add a new node instance to the graph
		@note: node membership is exclusive, thus node instances 
		can only be in one graph at a time
		@return: self, for chained calls"""
		if not isinstance( node, NodeBase ):
			raise TypeError( "Node %r must be of type NodeBase" % node )
			
		# assure we do not remove ( and kill connections ) and re-add to ourselves 
		if node in self._nodes:
			return self
			
		# remove node from existing graph
		if node.graph is not None:
			node.graph.removeNode( node )
			
			
		self._nodes.add( node )		# assure the node knows us
		node.graph = weakref.proxy( self )
		
		return self		# assure we have the graph set 
		
	def removeNode( self, node ):
		"""Remove the given node from the graph ( if it exists in it )"""
		try:
			# remove connections 
			for sshell, eshell in node.getConnections( 1, 1 ):
				self.disconnect( sshell, eshell )
				
			# assure the node does not call us anymore 
			node.graph = None
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
		"""@return: generator returning all nodes that are connected in this graph, 
		in no particular order.
		For an ordered itereration, use L{iterShells}
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
		
	def getNodes( self ):
		"""@return: immutable copy of the nodes used in the graph"""
		return tuple( self._nodes )
		
	#} END query
	
	#{ Connecitons 
	def connect( self, sourceshell, destinationshell, force = False ):
		"""Connect this plug to destinationshell such that destinationshell is an input plug for our output
		@param sourceshell: PlugShell being source of the connection 
		@param destinationshell: PlugShell being destination of the connection 
		@param force: if False, existing connections to destinationshell will not be broken, but an exception is raised
		if True, existing connection may be broken
		@return self: on success, allows chained connections 
		@raise PlugAlreadyConnected: if destinationshell is connected and force is False
		@raise PlugIncompatible: if destinationshell does not appear to be compatible to this one"""
		# assure both nodes are known to the graph
		self._nodes.add( sourceshell.node )
		self._nodes.add( destinationshell.node )
		
		# check compatability 
		if sourceshell.plug.attr.getConnectionAffinity( destinationshell.plug.attr ) == 0:
			raise PlugIncompatible( "Cannot connect %r to %r as they are incompatible" % ( repr( sourceshell ), repr( destinationshell ) ) )
		
		
		oinput = destinationshell.getInput( )
		if oinput is not None:
			if oinput == sourceshell:
				return sourceshell 
				
			if not force:
				raise PlugAlreadyConnected( "Cannot connect %r to %r as it is already connected" % ( repr( sourceshell ), repr( destinationshell ) ) )
				
			# break existing one
			oinput.disconnect( destinationshell )
		# END destinationshell already connected
		
		# connect us
		print "CON: %r -> %r" % ( repr(sourceshell), repr(destinationshell) )
		self.add_edge( sourceshell, v = destinationshell )
		return sourceshell
		
	def disconnect( self, sourceshell, destinationshell ):
		"""Remove the connection between sourceshell to destinationshell if they are connected
		@note: does not raise if no connection is present"""
		self.delete_edge( sourceshell, v = destinationshell )
		
		# also, delete the plugshells if they are not connnected elsewhere 
		for shell in sourceshell,destinationshell:
			if len( self.neighbors( shell ) ) == 0:
				self.delete_node( shell )
	
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
	
	
class _NodeBaseCheckMeta( type ):
	"""Class checking the consistency of the nodebase class before it is being created"""
	def __new__( metacls, name, bases, clsdict ):
		"""Check:
			- every plugname must correspond to a node member name
		"""
		newcls = type.__new__( metacls, name, bases, clsdict )
		
		# EVERY PLUG NAME MUST MATCH WITH THE ACTUAL NAME IN THE CLASS
		# set the name according to its slot name in the parent class
		membersdict = inspect.getmembers( newcls )		# do not filter, as getPlugs could be overridden
		try:
			for plug in newcls.getPlugsStatic( ):
				for name,member in membersdict:
					if member == plug and plug.getName() != name:	
						# try to set it
						if hasattr( plug, 'setName' ):
							plug.setName( name )
						else:
							raise AssertionError( "Plug %r is named %s, but must be named %s as in its class %s" % ( plug, plug.getName(), name, newcls ) )
						# END setName special handling 
					# END if member nanme is wrong 
				# END for each class member
				
				# ignore plugs we possibly did not find in the physical class 
			# END for each plug in class
		except TypeError:
			# it can be that a subclass overrides this method and makes it an instance method
			# this is valid - the rest of the dgengine always accesses this method 
			# through instance - so we have to handle it
			pass 
			
		return newcls
			
		
		

class NodeBase( iDuplicatable ):
	"""Base class that provides support for plugs to the superclass.
	It will create some simple tracking attriubtes required for the plug system 
	to work"""
	__slots__ = ('graph','shellcls')		# may have a per instance shell class if required 
	shellcls = _PlugShell					# class used to instantiate new shells 
	__metaclass__ = _NodeBaseCheckMeta		# check the class before its being created 
	
	#{ Overridden from Object
	def __init__( self, *args, **kwargs ):
		"""We require a directed graph to track the connectivity between the plugs.
		It must be supplied by the super class and should be as global as required to 
		connecte the NodeBases together properly.
		@note: we are super() compatible, and assure our base is initialized correctly"""
		self.graph = None

	def __del__( self ):
		"""Remove ourselves from the graph and delete our connections"""
		# check if item does still exist - this is not the case if the graph 
		# is currently being deleted
		try:
			#self.graph.removeNode( self )		# TODO: take back in and make it work ! Problems with facade nodes
			pass 
		except (AttributeError,ReferenceError):		# .graph could be None
			pass 
		
	#} Overridden from Object
	
	#{ iDuplicatable Interface 
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it
		@note: override by subclass  - the __init__ methods shuld do the rest"""
		return self.__class__( )
		
	def copyFrom( self, other, add_to_graph = True ):
		"""Just take the graph from other, but do not ( never ) duplicate it
		@param: add to graph: if true, the new node instance will be added to the 
		graph of """
		if add_to_graph and other.graph:		# add ourselves to the graph of the other node 
			other.graph.addNode( self )
		
	#} END iDuplicatable
	
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
		# may not use it as generator as it binds variables ( of course ! )
		outlist = list()
		for plug in plugs:
			outlist.append( self.toShell( plug ) )
		return outlist
		
	def toShell( self, plug ):
		"""@return: a plugshell as suitable to for this class"""
		return getattr( self, 'shellcls' )( self, plug )		# prevent cls variable to be bound !

	@classmethod
	def getPlugsStatic( cls, predicate = lambda x: True ):
		"""@return: list of static plugs as defined on this node - they are class members
		@param predicate: return static plug only if predicate is true
		@note: Use this method only if you do not have an instance - there are nodes 
		that actually have no static plug information, but will dynamically generate them.
		For this to work, they need an instance - thus the getPlugs method is an instance 
		method and is meant to be the most commonly used one."""
		pred = lambda m: isinstance( m, plug )
		
		# END sanity check
		pluggen = ( m[1] for m in inspect.getmembers( cls, predicate = pred ) if predicate( m[1] ) )
		return list( pluggen )
	
	def getPlugs( self, predicate = lambda x: True ):
		"""@return: list of dynamic plugs as defined on this node - they are usually retrieved 
		on class level, but may be overridden on instance level
		@param predicate: return static plug only if predicate is true"""
		# the getmembers function appears to be ... buggy with my classes
		# use special handling to assure he gets all the instance members AND the class members
		# In ipython tests this worked as expected - get the dicts individually
		all_dict_holders = itertools.chain( ( self, ), self.__class__.mro() )
		all_dicts = ( instance.__dict__ for instance in all_dict_holders )
		pluggen = ( v for d in all_dicts for v in d.itervalues() if isinstance( v, plug ) and predicate( v ) )
		
		return list( pluggen )
	
	@classmethod
	def getInputPlugsStatic( cls, **kwargs ):
		"""@return: list of static plugs suitable as input
		@note: convenience method"""
		return cls.getPlugsStatic( predicate = lambda p: p.providesInput(), **kwargs )
	
	def getInputPlugs( self, **kwargs ):
		"""@return: list of plugs suitable as input
		@note: convenience method"""
		return self.getPlugs( predicate = lambda p: p.providesInput(), **kwargs )
	
	@classmethod
	def getOutputPlugsStatic( cls, **kwargs ):
		"""@return: list of static plugs suitable to deliver output
		@note: convenience method"""
		return cls.getPlugsStatic( predicate = lambda p: p.providesOutput(), **kwargs )

	def getOutputPlugs( self, **kwargs ):
		"""@return: list of plugs suitable to deliver output
		@note: convenience method"""
		return self.getPlugs( predicate = lambda p: p.providesOutput(), **kwargs )

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
	def filterCompatiblePlugs( plugs, attribute, raise_on_ambiguity = False, attr_affinity = False ):
		"""@return: sorted list of (rate,plug) tuples suitable to deal with the given attribute.
		Thus they could connect to it as well as get their value set.
		Most suitable plug comes first.
		Incompatible plugs will be pruned.
		@param raise_on_ambiguity: if True, the method raises if a plug has the same
		rating as another plug already on the output list, thus it's not clear anymore 
		which plug should handle a request
		@param attr_affinity: if True, it will not check connection affinity, but attribute 
		affinity only. It checks how compatible the attributes of the plugs are, disregarding 
		whether they can be connected or not
		@raise TypeError: if ambiguous input was found"""
		                                                      
		outSorted = list()
		for plug in plugs:
			if attr_affinity:
				rate = plug.attr.getAffinity( attribute )
			else:
				rate = plug.attr.getConnectionAffinity( attribute )
			# END which affinity type 
			
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
					raise TypeError( "At least two plugs delivered the same compatabliity rate ( plug involved is %s )" % str(plug) )
				prev_rate = rate
			# END for each compatible plug
		# END ambiguous check
		
		return outSorted
		
	#} END base
	

	

