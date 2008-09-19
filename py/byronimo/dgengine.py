"""B{byronimo.automation.dgengine}
Contains a simple but yet powerful dependency graph engine allowing computations 
to be organized more efficiently.

@todo: plug-internal dirty tracking 
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

from networkx import DiGraph 

#####################
## EXCEPTIONS ######
###################
#{ Plug Exceptions 

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
## Classes    ######
###################


class NodeBase( object ):
	"""Base class that provides support for plugs to the superclass.
	It will create some simple tracking attriubtes required for the plug system 
	to work"""
	__slots__ = 'graph'
	
	def __init__( self, digraph, *args, **kwargs ):
		"""We require a directed graph to track the connectivity between the plugs.
		It must be supplied by the super class and should be as global as required to 
		connecte the NodeBases together properly.
		@note: we are super() compatible, and assure our base is initialized correctly"""
		if not isinstance( digraph, DiGraph ):
			raise TypeError( "A DiGrpah instance is required as input, got %r" % digraph )
			
		self.graph = digraph

	
	#{ Interface
	def compute( self, plug, mode ):
		"""Called whenever a plug needs computation as the value its value is not 
		cached or marked dirty ( as one of the inputs changed )
		@param plug: the static plug instance that requested which requested the computation
		@param mode: the mode of operation. Its completely up to the superclasses how that 
		attribute is going to be used
		@note: to be implemented by superclass """
		raise NotImplementedError( "To be implemented by subclass" )
		
	#} END interface 
		

class PlugShell( tuple ):
	"""Handles per-node-instance plug connection setup and storage. As plugs are 
	descriptors and thus an instance of the class, per-node-instance information needs
	special treatment.
	This class is being returned whenever the descriptors get and set methods are called, 
	it contains information about the node and the plug being involved, allowing to track 
	connection info directly using the node dict
	
	This allows plugs to be connected, and information to flow through the dependency graph.
	Plugs never act alone since they always belong to a parent node that will be asked for 
	value computations if the value is not yet cached.."""
	
	#{ Object Overrides 
	
	def __new__( cls, *args ):
		return tuple.__new__( cls, *args )
	
	def __init__( self, *args ):
		"""initialize the shell with a node and a plug"""
		self.node, self.plug = args
		self._cache = None
		
	def __repr__ ( self ):
		return "%s.%s" % ( self.node, self, plug )
		
	def __str__( self ):
		return str( self.plug )
		
	#} END object overrides 
	
	
	#{ Values  
	
	def getValue( self, mode ):
		"""@return: value of the plug"""
		if self.hasCache( ):
			return self.getCache( )
			
		
		# Output plugs compute values 
		if self.plug.providesOutput( ):
			
			# readable check 
			if not self.plug.attr.flags & Attribute.readable:
				raise NotReadableError(  "Plug %r is not readable and has no cache" )
			
			# otherwise compute the value
			try: 
				result = self.node.compute( self.plug, mode )
			except ComputeError,e:
				raise 			
			except Exception,e:		# except all - this is an unknown excetion
				raise ComputeError( "Computation of %r" % self, str( e ),e )
				
			# try to cache computed values 
			self.setCache( result )
			return result
		# END plug provides output
		else:
			# check for connection
			inputshell = self.getInput()
			if not inputshell:
				# check for default value
				if self.plug.attr.default is not None:
					return self.plug.attr.default
				else:
					raise MissingDefaultValueError( "Plug %r has no default value and is not connected - no value can be provided" % self )
			# END if we have no input 
			
			# query the connected plug for the value
			return inputshell.getValue( mode )
		# END plug provides input 
		
		
		
	def setValue( self, value ):
		"""Set the given value to be used in our plug
		@raise AssertionError: the respective attribute must be cached, otherwise 
		the value will be lost"""
		flags = self.plug.attr.flags
		if not flags & Attribute.writable:
			raise NotWritableError( "Plug %r is not writable" % self )
		
		if not self.plug.providesOutput( ):
			raise NotWritableError( "Plug %r is not writable as it provides an output itself" % self ) 
							
		if not flags & Attribute.cached:
			raise AssertionError( "Writable attributes must be cached - otherwise the value will not be held" )
		
		
		# QUESTION: should the value be set on connected  plugs or ours ? I think not 
		# as plugs will get values recursively anyway
		self.setCache( value )
		
		
	def getCompatabilityRate( self, value ):
		"""@return: value between 0 and 255, 0 means no compatability, 255 a perfect match
		if larger than 0, the plug can hold the value ( assumed the flags are set correctly )"""
		return self.plug.attr.getCompatabilityRate( value )
		
		
	#} END values 
	
	#{ Connections 
	
	def connect( self, otherplug, force = False ):
		"""Connect this plug to otherplug such that otherplug is an input plug for our output
		@param force: if False, existing connections to otherplug will not be broken, but an exception is raised
		if True, existing connection may be broken
		@return otherplug: on success, allows chained connections 
		@raise PlugAlreadyConnected: if otherplug is connected and force is False
		@raise PlugIncompatible: if otherplug does not appear to be compatible to this one"""
		if not isinstance( otherplug, PlugShell ):
			raise AssertionError( "Invalid Type given to connect: %r" % otherplug )
		
		# check compatability 
		if self.plug.attr.getConnectionAffinity( otherplug.plug.attr ) == 0:
			return PlugIncompatible( "Cannot connect %r to %r as they are incompatible" % ( self, otherplug ) )
		
		
		oinput = otherplug.getInput( )
		if oinput is not None:
			if oinput == self:
				return 
				
			if not force:
				raise PlugAlreadyConnected( "Cannot connect %r to %r as it is already connected" % ( self, otherplug ) )
				
			# break existing one
			oinput.disconnect( otherplug )
		# END otherplug already connected
		
		# connect us 
		self.node.graph.add_edge( self, v = otherplug )
		
	
	def disconnect( self, otherplug ):
		"""Remove the connection to otherplug if we are connected to it.
		@note: does not raise if no connection is present"""
		if not isinstance( otherplug, PlugShell ):
			raise AssertionError( "Invalid Type given to connect: %r" % otherplug )
			
		self.node.graph.delete_edge( self, v = otherplug )
	
	def getInput( self ):
		"""@return: a list of connected plugs
		@param predicate: plug will only be returned if predicate is true for it
		@note: input plugs have on plug at most, output plugs can have more than one 
		connected plug"""
		self.node.graph.predecessors( self ) 
		
	def getOutputs( self, predicate = lambda x : True ):
		"""@return: a list of plugs being the destination of the connection
		@param predicate: plug will only be returned if predicate is true for it - shells will be passed in """
		outlist = []
		for shell in self.node.graph.successors( self ):
			if predicate( shell ):
				outlist.append( shell )
		return outlist
		
	#} END connections

	
	#{Caching 
	def hasCache( self ):
		"""@return: True if currently store a cached value"""
		return self._cache != None
		
	def setCache( self, value ):
		"""Set the given value to be stored in our cache
		@raise: TypeError if the value is not compatible to our defined type"""
		# attr compatability 
		if self.plug.attr.getCompatabilityRate( value ):
			raise TypeError( "Plug %r cannot hold value %r as it is not compatible" % ( self, value ) )
			
		self._cache = value
		
	def getCache( self ):
		"""@return: the cached value or raise
		@raise: ValueError"""
		if self._cache:
			return self._cache
		
		raise ValueError( "Plug %r did not have a cached value" % self )
		
	def clearCache( self ):
		"""Empty the cache of our plug"""
		self._cache = None
	#} 
	
	

class Attribute( object ):
	"""Simple class defining the type of a plug and several flags that 
	affect it
	Additionally it can determine how well suited another attribute is"""
	kNo, kGood, kPerfect = 0, 127, 255				# specify how good attributes fit together
	exact_type, writable, readable, instance, cached, connectable = ( 1, 2, 4, 8, 16, 32 )
	__slots__ = ( 'typecls', 'flags', 'default' )
	
	def __init__( self, typeClass, flags, default = None ):
		self.typecls = None
		self.flags = 0				# used for bitflags describing mode
		self.default = default		# the default value to be returned for input attributes 


	def _getClassRating( self, value, exact_type ):
		"""@return: rating based on value being a class and compare
		0 : value is no type
		255: value matches comparecls, or linearly less if is just part of the mro of value"""
		if not isinstance( value, type ):
			return 0
			
		mro = value.mro()
		mro.reverse()
		if not self.typecls in mro:
			return 0
			
		if len( mro ) == 1:
			return self.kPerfect
		
		rate = ( float( mro.index( self.typecls ) ) / float( len( mro ) - 1 ) ) * self.kPerfect
		
		if exact_type and rate != self.kPerfect:		# exact type check
			return 0
			
		return rate 

	#{ Interface 
	
	def getConnectionAffinity( self, otherattr ):
		"""@return: rating from 0 to 255 defining the quality of the connection to 
		otherplug. an affinity of 0 mean connection is not possible, 255 mean the connection 
		is perfectly suited.
		The connection is a directed one from self -> otherplug"""
		if not otherattr.flags & self.connectable:		# destination must be connectable
			return 0
			
		if not self.flags & self.readable:				# we need to be readable 
			return 0
			
		# see whether our instance flags match
		if self.flags & self.instance != otherattr.flags & self.instance:
			return 0
			
		# finally check how good our types match 
		return self._getClassRating( otherattr.typecls, otherattr.flags & self.exact_type )
		
		
		
	def getCompatabilityRate( self, value ):
		"""@return: value between 0 and 255, 0 means no compatability, 255 a perfect match
		if larger than 0, the plug can hold the value ( assumed the flags are set correctly )"""
		if isinstance( value, type ):
			# do we need an instance ?
			if self.flags & self.instance:
				return 0		# its a class 
			
			# check compatability
			return self._getClassRating( value, self.flags & self.exact_type )
		# END is class type
		else:
			if self.flags & self.instance:
				return self._getClassRating( value.__class__ )
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
	__slots__ = ( '__name', 'attr', 'affected' )
	
	#{ Overridden object methods 
	def __init__( self, name, attribute ):
		"""Intialize the plug with a distinctive name"""
		self.__name = name
		self.attr = attribute
		self.affected = list()			# list of plugs that are affected by us
		
	def __str__( self ):
		return self.__name
		
	#}
	
	#{ Value access 
	def __get__( self, obj, cls=None ):
		"""A value has been requested - return our plugshell that brings together
		both, the object and the static plug"""
		if cls != None:
			raise AssertionError( "Class-plugs cannot be handled - get needs to be called through instance" )
			
		return PlugShell( obj, self )
		
	
	def __set__( self, obj, value ):
		"""Just call the setValue method directly"""
		PlugShell( obj, self ).setValue( value )
		
	#}
	
	#{ Interface 
	
	def affects( self, otherplug ):
		"""Set an affects relation ship between this plug and otherplug, saying 
		that this plug affects otherplug."""
		if otherplug not in self.affected:
			self.affected.append( otherplug )
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations"""
		return len( self.affected ) == 0
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		return not self.providesOutput( )
	#}
	
	
	#{ Types 
	
	
	
	#} END types 
