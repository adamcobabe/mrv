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

__all__ = [ 'InputError', 'NoSuitableInput', 'AmbiguousInput', 'ComputationFailed', 'TargetUnreachable' ]


#####################
## EXCEPTIONS ######
###################
#{ Exceptions 
class InputError( ValueError ):
	"""General exception raised if something is wrong with the input"""

class NoSuitableInput( InputError ):
	"""Raised if no input matching target could be found"""
	
class AmbiguousInput( InputError ):
	"""There are two equally well suited inputs and the system cannot decide which one 
	to use. Use an input selector process to resolve that"""
	
class ComputationFailed( InputError ):
	"""An unhandled exception was thrown when the input was about to be retrieved.
	This usually indicates a bug """
	
class TargetUnreachable( InputError ):
	"""The target can not be obtained anymore as the context of the process does not 
	allow that anymore"""
	

class DirtyException( ValueError ):
	"""Exception thrown when system is in dirty query mode and the process detects
	that it is dirty.
	
	The exception can also contain a report that will be returned using the 
	getReport function.
	"""
	def __init__( self ):
		self.report = ''
		
	#{ Interface
		
	def getReport( ):
		"""@return: printable report, usually a string or some object that 
		responds to str() appropriately"""
		return self.report
	
	#} END interface
	
#} END exceptions 


#####################
## Methods    ######
###################
def track_output_call( func ):
	"""Wraps the proecss.getOutputBase function allowing to gather plenty of information 
	about the call, as well as error statistics"""
	
	def track_func( self, target, **kwargs ):
		pdata = self._wfl._trackOutputQueryStart( self, target )
		
		try:
			result = func( self, target, **kwargs )
		except Exception,e:
			pdata.exception = e
			self._wfl._trackOutputQueryEnd( None )
			raise 
			
		self._wfl._trackOutputQueryEnd( result )
		return result 
		
	# END track func 
		
	
	return track_func


#####################
## Classes    ######
###################

class ProcessBase( object ):
	"""The base class for all processes, defining a common interface
	
	Inputs and Outputs of this node are statically described using plugs
	"""
	kNo, kGood, kPerfect = 0, 127, 255				# specify how good a certain target can be produced
	is_state, target_state, dirty_check = ( 1,2,4 )
	output_mask = is_state & target_state & dirty_check		# mask applied before calling inputs  
	
	__all__.append( "ProcessBase" )
	
	#{ Plug Lists
	__input_plugs__ = []			# list of plugs defining which inputs this node supports
	__output_plugs__ = []			# list of plugs defining which outputs this node supports
	#}
	
	def __init__( self, noun, verb, workflow, allow_cache = True, provide_own_target = True ):
		"""Initialize process with most common information
		@param noun: noun describing the process, ( i.e. "Process" )
		@param verb: verb describing the process, ( i.e. "processing" )
		@param allow_cache: if true, results will automatically be cached and need no recomputation
		if the result is gathered multiple times
		@param pipe_through: if True, our target instance will be handed out if the target instance's 
		tyoe is requested, allowing more versatile Processes as the originally supplied target can be 
		piped to many different processes at once and automatically ( as long as they are connected )
		@param workflow: workflow this instance of part of """
		self.noun = noun			# used in plans
		self.verb = verb			# used in plans 
		
		self._targetcache = None
		if allow_cache:
			self._targetcache = dict()
			
		self._wfl = workflow
		self._provide_own_target = provide_own_target
		
	def __str__( self ):
		"""@return: just the process noun"""
		return self.noun

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
	@staticmethod
	def _isCompatibleWith( target, thisclass ):
		"""@return: True if target is a class and thisclass is in it's mro"""
		if not isinstance( target, type ) or thisclass not in target.mro():
			return False
		return True
	
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
	
	def getOutput( self, target, mode ):
		"""@return: an instance suitable for the given targetType or the handed in instance itself
		@param target: target that should be produced by the process - this should be done 
		as efficient as possible. target can either be abstract as it specifies a target type using 
		a class instance, or it can be an instance exactly specifying the target. The caller must 
		check whether the target is actually acceptable for him, but can be sure that it matches a type 
		returned by L{getSupportedTargetTypes}
		@param mode: bit flags as follows:
		is_state: your return value represents the current state of the process - your output will 
				represent what actually is present. You may not alter the state of your environment, 
				thus this operation is strictly read-only.
				According to your output, when called you need to setup a certain state 
				and return the results according to that state. This flag means you are requrested
				to return everything that is right according to the state you shall create.
				If this state is disabled, you should not return the current state, but behave 
				according to the other ones.
		target_state: your return value must represent the 'should' state - thus you must assure 
				that the environment is left in a state that matches your target state - the result 
				of that operation will be returned.
				Usually, but not necessarily, the is_state is also requested so that the output
				represents the complete new is_state ( the new state after you changed the environment
				to match the target_state )
		dirty_check: Always comes in conjunction with is_state. You are required to return the is_state
				but raise a DirtyException if your inputs would require you to adjust the environment 
				to deliver the target state. If the is_state if the environment is the target_state
				as there is nothing to do for you, do not raise and simply return your output.
		The call takes place as there is no cache for targetType.
		@note: needs to be implemented by subclasses"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
		
	def needsUpdate( self, target ):
		"""@return: true if process is dirty for the given target and needs to recompute it.
		One must not pull any inputs from non-generators as this may trigger a computation that changes
		the state of the environment the process in running in. One must try to decide on the prequesites
		yourself, thus everything you do here is something you check as process alone without any help 
		of other processes
		@note: You can also return a UpdateReport that will always be True when compared with
		and carry additional information about the reason why it needs an update
		@note: this method is only being called because the process appears to be able to 
		handle the targetType of target
		@note: should not be called directly, as it is being called by the base interface 
		@note: recomputing a target means that it's current state does not represent the form 
		it needs to have to be considered up-to-date"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
	
	# } END interface
	
	#{ Base 
	# methods that drive the actual call
	def _getSuitableProcess( self , target ):
		"""@return: process suitable to make target"""
		candidateList = []		# list of ( rate, input_process ) tuples 
		for inputprocess in self._wfl.predecessors_iter( self ):
			rate = inputprocess.canOutputTarget( target )
			if not rate:
				continue
			candidateList.append( ( rate, inputprocess ) )
		# END for each input process
		if not candidateList:
			raise NoSuitableInput( "Cannot find input of %s suitable to make target %r" % ( self, target ) )
			
		candidateList.sort()			# sort by rate - last one is best 
		rate, inputprocess = candidateList[-1]
		
		# search for ambituous inputs
		valid_candidates = []
		for r, p in candidateList:
			if r == rate:
				valid_candidates.append( p )
		
		if len( valid_candidates ) > 1:
			cstrings = [ str( p ) for p in valid_candidates ]
			raise AmbiguousInput( "Found %i input processes ( %s ) able to deliver target %r for process %s" % (len(valid_candidates), ", ".join( cstrings ), target, self ) )
			
		return inputprocess
		
		
	def getInput( self, target ):
		"""Get an input from a connected process producing the given target 
		@param target: target you wish to receive. Can be either a target type as an abstract 
		indicator of the type you wish to have, or a concrete instance of something that 
		should be brought into an up-to-date state
		@raises AmbiguousInput: if several inputs exist delivering the same target
		@raises ComputationFailed: computation has thrown an unknown exception
		@raises NoSuitableInput: there is no input having the requested type
		@raises TargetUnreachable: the target cannot be achieved anymore 
		@return: the requested input as result of achieving the target"""
		# find compatible process 
		targetProcess = self._getSuitableProcess( target )
		
		# trigger actual computation 
		result = targetProcess.getOutputBase( target )
		
		return result
		
	
	@track_output_call
	def getOutputBase( self, target ):
		"""Base implementation of the output, called by L{getInput} Method. 
		Handles caching and flow tracking before the actual implementation is called
		This allows to create plans and analyse the flow of execution
		Handle dry runs
		@param target: target to make"""
		if self.hasCache( target ):
			return self.getCache( target )
		
		# Store the target as we can hand it out to other nodes if requested
		# this allows easy data sharing of targets known at a certain processing 
		# step - will only work for instances
		if self._provide_own_target:
			if not isinstance( target, type ):
				self.setCache( type( target ), target )
		
		try: 
			# call actually implemented method
			result = self.getOutput( target, self._wfl._isDryRun() )
		except InputError:
			raise 			
		except Exception,e:		# except all - this is an unknown excetion
			raise ComputationFailed( "Computation of %s for target %r failed" % ( self, target ), str(e),e )
		
		
		# cache result 
		self.setCache( target, result )
		return result 
		
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
			# try check compatability by taking class inheritance into account
			if isinstance( target, type ):
				cachelist = []
				for key in self._targetcache.iterkeys():
					cachelist.append( ( self._getClassRating( key, target ), key ) )
					                                        
				if cachelist:
					cachelist.sort()
					# TODO: check for ambiguous cache entries - thus two cached 
					# items having the same values
					rate,key = cachelist[-1]
					if rate:
						return self._targetcache[ key ]
				# END compatible cached item found 
			# END is class
			
			# no other way but throw 
			raise ValueError( "Target %r was not cached in %s" % ( target, self ) )
		# END no direct key match
			
	def hasCache( self, target ):
		"""@return: True if the target has a cached value, False otherwise"""
		if self._targetcache is None:
			return False 
			
		try:
			self.getCache( target )
		except ValueError:
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
	
	
class PassThroughProcess( ProcessBase ):
	"""Simple process passing through calls to the most appropriate input
	It should be used as mostly neutral baseclass for process that alter inputs or generate them"""
	__all__.append( "PassThroughProcess" )
	
	def getOutput( self, target, is_dry_run ):
		"""Pass-through of all targets - we cannot do any work"""
		return self.getInput( target )
		
	def canOutputTarget( self, target ):
		"""Pass-thourgh all calls by default"""
		try:
			inputprocess = self._getSuitableProcess( target )
		except InputError:
			return 0
		return inputprocess.canOutputTarget( target )
	
	def needsUpdate( self, target ):
		"""Pass-thourgh all calls by default"""
		inputprocess = self._getSuitableProcess( target )
		return inputprocess.needsUpdate( target )
		
	
class WorkflowProcessBase( ProcessBase ):
	"""A process wrapping a workflow, allowing workflows to be nested
	Derive from this class and initialize it with the workflow you would like to have wrapped
	@note: to prevent dependency issues, the workflow instance will be bound on first use"""
	__all__.append( "WorkflowProcessBase" )
	
	#{ Overridden Object Methods 
	
	def __init__( self, workflow, workflowModulePath, workflowName, **kwargs ):
		"""@param workflowinst: instance of the Workflow you would like to wrap
		@param workflow: the workflow we are in ( the parent workflow )
		@param workflowModulePath: module import path which will contain the workflow
		@param workflowName: name of the workflow as it will exist in workflowModule 
		@param **kwargs: all arguments required to initialize the ProcessBase"""
		self.__wrappedwfl = None
		workflowModule = __import__( workflowModulePath, globals(), locals(), [''] )
		self._wflmod = workflowModule
		self._wflname = workflowName
		super( WorkflowProcessBase, self ).__init__( "TO BE SET", "passing on", workflow, **kwargs )
		
	def __getattr__( self , attr ):
		"""@return: attribute on the wrapped workflow"""
		try:
			return getattr( self.getWorkflow(), attr )
		except AttributeError:
			return super( WorkflowProcessBase, self ).__getattribute__( attr )
			
	
	#} END overridden methods 
	
	
	#{ ProcessBase Methods
	def getWorkflow( self ):
		"""@return: our wrapped workflow instance
		@note: Assures that the workflow instance is bound, it will be bound 
		as required """
		if not self.__wrappedwfl:
			self.__wrappedwfl = getattr( self._wflmod, self._wflname )
			self.noun = self.__wrappedwfl.name
			
		return self.__wrappedwfl
		
	def getOutput( self, target, is_dry_run ):
		"""Ask our workflow instead """
		result = self.getWorkflow().makeTarget( target, dry_run = is_dry_run )
		
		# UPDATE CALLGRAPH
		wgraph = self.__wrappedwfl._callgraph
		owngraph = self._wfl._callgraph 
		
		# add all edges and connect our graph by simulating an input call
		owngraph.add_edges_from( wgraph.edges_iter() )
		owngraph.startCall( wgraph.getCallRoot() )
		owngraph.endCall( result )
		
		return result
		
		
	def canOutputTarget( self, target ):
		"""Ask our workflow"""
		return self.getWorkflow().getTargetRating( target )[0]
	
	def needsUpdate( self, target ):
		"""Pass-thourgh all calls by default"""
		rating,process = self.getWorkflow().getTargetRating( target )
		if not rating:	
			raise AssertionError( "needsUpdate called to %r for unsupported target %r" % ( self, target ) ) 
		return process.needsUpdate( target )
	
	
	#} END processbase methods 
		
	
