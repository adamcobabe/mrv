"""B{byronimo.automation.processes.base}
Contains base class and common methods for all processes  

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

__all__ = []

class ProcessBase( object ):
	"""The base class for all processes, defining a common interface"""
	kNo, kGood, kPerfect = 0, 127, 255			# specify how good a certain target can be produced 
	__all__.append( "ProcessBase" )
	
	def __init__( self, noun, verb, workflow, allow_cache = True, pipe_through = True ):
		"""Initialize process with most common information
		@param noun: noun describing the process, ( i.e. "Process" )
		@param verb: verb describing the process, ( i.e. "processing" )
		@param allow_cache: if true, results will automatically be cached and need no recomputation
		if the result is gathered multiple times
		@param pipe_through: if True, our inputs as well as our target will be available as output 
		during our own calculation. This allows a datastream to be accessed by many processes.Processes 
		attempting to access these attributes need to be connected to the respective node. 
		Piped attributes will only be passed automatically if you do not provide an output of that type 
		yourself.
		@param workflow: workflow this instance of part of """
		self._noun = noun			# used in plans
		self._verb = verb			# used in plans 
		
		self._targetcache = None
		if allow_cache:
			self._targetcache = dict()
			
		self._wfl = workflow
		# dry run !! Attr on workflow ?
		
	def __str__( self ):
		"""@return: just the process noun"""
		return self._noun

	#{ Query
	def canOutputTarget( self, target ):
		"""@return: int between 0 and 255 - 255 means target matches perfectly, 0 
		means complete incompatability. Any inbetweens indicate the target can be 
		achieved, but maybe just in a basic way
		@param target: instance or class of target to check for compatability
		@note: use the enumeration members of this class ( i.e. kPerfect )"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
		
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
	
	#} END query 

	#{ Interface
	
	def _getClassRating( self, target, comparecls ):
		"""@return: rating based on target being a class and compare
		0 : target is no type
		255: target matches comparecls, or linearly less if is just part of the mro of target"""
		if not isinstance( target, type ):
			return 0
			
		mro = target.mro()
		mro.reverse()
		if not comparecls in mro:
			return 0
			
		if len( mro ) == 1:
			return 255
		
		return ( float( mro.index( comparecls ) ) / float( len( mro ) - 1 ) ) * 255 
	
	def getOutput( self, target, is_dry_run ):
		"""@return: an instance suitable for the given targetType
		@param target: target that should be produced by the process - this should be done 
		as efficient as possible. target can either be abstract as it specifies a target type using 
		a class instance, or it can be an instance exactly specifying the target. The caller must 
		check whether the target is actually acceptable for him, but can be sure that it matches a type 
		returned by L{getSupportedTargetTypes}
		@param is_dry_run: if True, no change may be made , and the method is strictly read-only.
		It should proceed as far as possible simulating the process that will actually be run, assuming 
		success in all mutating methods
		
		The call takes place as there is no cache for targetType. you must find out yourself
		whether your target needs to be produced or is already available and uptodate.
		@note: needs to be implemented by subclasses"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
		
	def needsUpdate( self, target ):
		"""@return: true if process is dirty for the given target and needs to recompute it.
		One must not pull any inputs from non-generators as this may trigger a computation that changes
		the state of the environment the process in running in. One must try to decide on the prequesites
		yourself
		@note: this method is only being called because the process appears to be able to 
		handle the targetType of target
		@note: should not be called directly, as it is being called by the base interface 
		@note: recomputing a target means that it's current state does not represent the form 
		it needs to have to be considered up-to-date"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
	
	# } END interface
	
	#{ Base 
	# methods that drive the actual call
	def getInput( self, target, *args ):
		"""Get an input from a connected process producing the given target 
		@param target: target you wish to receive. Can be either a target type as an abstract 
		indicator of the type you wish to have, or a concrete instance of something that 
		should be brought into an up-to-date state
		@param data: additional data that the process may understand and use. It will 
		be passed implicitly if the called process requests an input that is otherwise 
		not available.
		@raises AmbiguousInput: if several inputs exist delivering the same goal
		@raises CycleError: if the same process and goal is already being visited
		@raises ComputationFailed: computation has thrown an unknown exception
		@raises InputNotFound: there is no input having the requested type
		@raises GoalUnreachable: the goal cannot be achieved anymore 
		@return: the requested input as result of achieving the goal"""
		
		# do bookkeeping 
		
		# trigger actual computation 
		raise NotImplementedError( "TODO" ) 
	
	
	def getOutputBase( self, target, dry_run = False ):
		"""Base implementation of the output, called by L{getInput} Method. 
		Handles caching and flow tracking before the actual implementation is called
		This allows to create plans and analyse the flow of execution
		Handle dry runs
		@param *args: will be made available as cached output of this process"""
		if self.hasCache( target ):
			return self.getCache( target )
			
		# call actually implemented method
		raise NotImplementedError( "TODO" )
		
		# cache result if possible 
		
	def needsUpdateBase( self, target ):
		"""@return: True if target needs to be updated
		@note: base implementation that takes the cache into consideration"""
		# try to get it from cache
		if self.hasCache( target ):
			return False
			
		# check parent class 
		return self.needsUpdate( target )
		
		
	def setCache( self, target, data ):
		"""Set the processes cache for the given target type
		@param target: target you wish to associate the data with 
		@param data: the data you would like to be returned if the given targetType is 
		requested
		@note: this method has no effect if caching is disabled"""
		if self._targetcache is None:
			return 
			
		self._targetcache[ target ] = data
		
	def getCache( self, target ):
		"""@return: cached data associcated with the given target
		@raise ValueError: if no cache value exists for given target""" 
		try: 
			return self._targetcache[ target ]
		except KeyError:
			raise ValueError( "Target %r was not cached in %s" % ( target, self ) )
			
	def hasCache( self, target ):
		"""@return: True if the target has a cached value, False otherwise"""
		if self._targetcache is None:
			return False 
			
		try:
			self.getCache( target )
		except:
			return False
		else:
			return True
		
	def prepareProcess( self ):
		"""Will be called on all processes of the workflow once before a target is 
		actually being queried by someone
		It must be used to clear the own state and reset the instance such that 
		it can get repeatable results"""
		# clear cache 
		if self._targetcache is not None:
			self._targetcache = dict()
			
	
	#} END base 
	
	
	
class WorkflowProcessBase( ProcessBase ):
	"""A process wrapping a workflow, allowing workflows to be nested
	Derive from this class and initialize it with the workflow you would like to have wrapped"""
	__all__.append( "WorkflowProcessBase" )
	
	#{ Overridden Object Methods 
	
	def __init__( self, workflowinst, *args, **kwargs ):
		"""@param workflowinst: instance of the Workflow you would like to wrap
		@param *args, **kwargs: all arguments required to initialize the ProcessBase"""
		super( WorkflowProcessBase, ProcessBase ).__init__( self, *args, **kwargs )
		
		self._wrappedwfl = workflowinst		# wrapped workflow 
		
		
	def __getattr__( self , attr ):
		"""@return: attribute on the wrapped workflow"""
		try:
			return getattr( self._wrappedwfl, attr )
		except AttributeError:
			return super( WorkflowProcessBase, self ).__getattribute__( attr )
			
	
	#} END overridden methods 
	
	
	#{ ProcessBase Methods 
	
	
	#} END processbase methods 
		
	
