"""B{byronimo.automation.plug}
Contains plug class and related exceptions. 

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


#####################
## EXCEPTIONS ######
###################
#{ Exceptions 

class PlugError( Exception ):
	"""Exception base for all plug related errors"""

class PlugIncompatible( PlugError, TypeError ):
	"""Thrown whenever plugs are not compatible with each other during connection"""
	
class PlugAlreadyConnected( PlugError ):
	"""Thrown if one tries to connect a plug to otherplug when otherplug is already connected"""	

#} END exceptions



#####################
## Classes    ######
###################

class Type( object ):
	"""Simple class defining the type of a plug and several flags that 
	affect it"""
	exact_bit, instance_bit,  
	def __init__( self ):
		self.typecls = None
		self.mode = 0				# used for bitflags describing mode 


class Plug( object ):
	"""Defines an interface allowing to compare compatabilies according to types.
	
	This allows plugs to be connected, and information to flow through the dependency graph.
	Plugs never act alone since they always belong to a parent node that will be asked for 
	value computations if the value is not yet cached.
	
	Plugs are implemented as descriptors, thus they will be defined on process class 
	level, but currently only act if called on instance level.
	"""
	kNo,kGood,kPerfect = ( 0, 127, 255 )
	
	
	#{ Overridden object methods 
	def __init__( self, name ):
		"""Intialize the plug with a distinctive name"""
		self.__name = name
		
	def __str__( self ):
		return self.__name
		
	#}
	
	#{ Value access 
	def __get__( self, obj, cls ):
		"""A value has been requested - query our input plug"""
	
	
	def __set__( self, obj, value ):
		"""Setting of values is not allowed - values are set as return value 
		of the compute method"""
		
	#}
	
	#{Caching 
	def hasCache( self ):
		"""@return: True if currently store a cached value"""
		raise NotImplementedError()
		
	def setCache( self, value ):
		"""Set the given value to be stored in our cache
		@raise: TypeError if the value is not compatible to our defined type"""
		raise NotImplementedError()
		
	def getCache( self ):
		"""@return: the cached value or raise
		@raise: NoCacheException"""
	#} 
	
	#{ Connections 
	
	def getAffinity( self, otherplug ):
		"""@return: rating from 0 to 255 defining the quality of the connection to 
		otherplug. an affinity of 0 mean connection is not possible, 255 mean the connection 
		is perfectly suited"""
		raise NotImplementedError()
	
	def connect( self, otherplug, force = False ):
		"""Connect this plug to otherplug such that otherplug is an input plug for our output
		@param force: if False, existing connections to otherplug will not be broken, but an exception is raised
		if True, existing connection may be broken
		@return otherplug: on success, allows chained connections 
		@raise PlugAlreadyConnected: if otherplug is connected and force is False
		@raise PlugIncompatible: if otherplug does not appear to be compatible to this one"""
		raise NotImplementedError()
	
	def disconnect( self, otherplug ):
		"""Remove the connection to otherplug if we are connected to it.
		@note: does not raise if no connection is present"""
		raise NotImplementedError()
	
	def lsConnected( self, predicate = lambda x : True ):
		"""@return: a list of connected plugs
		@param predicate: plug will only be returned if predicate is true for it
		@note: input plugs have on plug at most, output plugs can have more than one 
		connected plug"""
		raise NotImplementedError()
		
		
	#} END connections 
	
	#{ Types 
	
	
	
	#} END types 
