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


class ProcessBase( object ):
	"""The base class for all processes, defining a common interface"""
	kNo, kGood, kPerfect = 0, 127, 255			# specify how good a certain target can be produced 
	
	def __init__( self, noun, verb, workflow, allow_cache = True ):
		"""Initialize process with most common information
		@param noun: noun describing the process, ( i.e. "Process" )
		@param verb: verb describing the process, ( i.e. "processing" )
		@param allow_cache: if true, results will automatically be cached and need no recomputation
		if the result is gathered multiple times
		@param workflow: workflow this instance of part of """
		self._noun = noun
		self._verb = verb
		self._allow_cache = allow_cache
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
		@param target: instance or class of target to check for compatability"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
		
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
	
	#} END query 

	#{ Interface 		
	def getOutput( self, targetType, is_dry_run ):
		"""@return: an instance suitable for the given targetType
		@param targetType: type that should be produced by the process - this should be done 
		as efficient as possible
		@param is_dry_run: if True, no change may be made , and the method is strictly read-only.
		It should proceed as far as possible simulating the process that will actually be run, assuming 
		success in all mutating methods
		
		The call takes place as there is no cache for targetType. you must find out yourself
		whether your target needs to be produced or is already available and uptodate.
		@note: needs to be implemented by subclasses"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
		
	def isDirty( self, target ):
		"""@return: true if process is dirty for the given target
		@note: this method is only being called because the process appears to be able to 
		handle the targetType of target"""
		raise NotImplementedError( "This method needs to be implemented by the subclass" )
	
	# } END interface
	
	#{ Base 
	# methods that drive the actual call
	def getInput( self, targetType, data = None ):
		"""Get an input from a connected process producing the given targetType 
		@param targetType: target type you wish to receive
		@param data: additional data that the process may understand and use. It will 
		be passed implicitly if the called process requests an input that is otherwise 
		not available.
		@raises AmbiguousInput: if several inputs exist delivering the same goal
		@raises CycleError: if the same process and goal is already being visited
		@raises ComputationFailed: computation has thrown an unknown exception
		@raises InputNotFound: there is no input having the requested type
		@raises GoalUnreachable: the goal cannot be achieved anymore 
		@return: the requested input as result of achieving the goal"""
		raise NotImplementedError( "TODO" )
	
	
	def getOutputBase( self, targetType, data ):
		"""Base implementation of the output, called by L{getInputMethod}.
		Handles caching and flow tracking before the actual implementation is called
		This allows to create plans and analyse the flow of execution
		Handle dry runs"""
		raise NotImplementedError( "TODO" )
	
	#} END base 
