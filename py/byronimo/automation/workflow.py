"""B{byronimo.automation.workflow}
Contains workflow classes that conenct processes in a di - graph  

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

from networkx.digraph import DiGraph
from byronimo.dgengine import Graph
import time 
import weakref

#####################
## EXCEPTIONS ######
###################
class TargetError( ValueError ):
	"""Thrown if target is now supported by the workflow ( and thus cannot be made )"""
	


#####################
## CLASSES    ######
###################	

class Workflow( Graph ):
	"""Implements a workflow as connected processes
	@note: if you have to access the processes directly, use the DiGraph methods"""

	#{ Utility Classes 
	class ProcessData( object ):
		"""Allows to store additional information with each process called during the workflow"""
		__slots__ = ( 'process','plug','mode', '_result', 'starttime', 'endtime','exception','index' ) 
		def __init__( self, process, plug, mode ):
			self.process = process
			self.plug = plug
			self.mode = mode
			self._result = None					# can be weakref or actual value 
			self.starttime = time.clock()
			self.endtime = self.starttime
			self.exception = None				# stores exception on error
			self.index = 0						# index of the child - graph stores nodes unordered
			
		def __repr__( self ):
			out = "%s.%s" % ( self.process, self.plug )
			if self.exception:
				out += "&ERROR"
			return out
			
		def getElapsed( ):
			"""@return: time to process the call"""
			return self.endtime - self.starttime
			
		def setResult( self, result ):
			"""Set the given result
			@note: uses weak references as the tracking structure should not cause a possible
			mutation of the program flow ( as instances stay alive although code expects it to be 
			deleted"""
			if result is not None:
				try:
					self._result = weakref.ref( result )
				except TypeError:
					self._result = result
			# END if result not None
			
		def getResult( self ):
			"""@return: result stored in this instance, or None if it is not present or not alive"""
			if self._result:
				if isinstance( self._result, weakref.ref ):
					return self._result()
				return self._result
				
			return None
	
	
	class CallGraph( DiGraph ):
		"""Simple wrapper storing a call graph, keeping the root at which the call started
		@note: this class is specialized to be used by workflows, its not general for that 
		purpose"""
		def __init__( self ):
			super( Workflow.CallGraph, self ).__init__( name="Callgraph" )
			self._call_stack = []
			self._root = None
			
		def startCall( self, pdata ):
			"""Add a call of a process"""
			# keep the call graph
			if self._call_stack:
				curdata = self._call_stack[ -1 ]
				pdata.index = self.in_degree( curdata )
				self.add_edge( pdata, curdata )
			else:
				# its the first call, thus we add it as node - would work on first edge add too though
				self.add_node( pdata )
				self._root = pdata
				
			self._call_stack.append( pdata )
			
		def endCall( self, result ):
			"""End the call start started previously
			@param result: the result of the call"""
			lastprocessdata = self._call_stack.pop( )
			lastprocessdata.endtime = time.clock( )
			lastprocessdata.setResult( result )
			
		def getCallRoot( self ):
			"""@return: root at which the call started"""
			return self._root
			
	#} END utility classes
	
	
				
	#{ Overridden Methods 
	def __init__( self, **kwargs ):
		"""Initalized base class"""
		super( Workflow, self ).__init__( **kwargs )
		
		self._callgraph = None
		self._mode = False
		
	
	def __str__( self ):
		return self.name
		
	#} # END overridden methods
	
	#{ iDuplicatable Interface
	
	def copyFrom( self, other ):
		"""Only mode is required """
		self._mode = other._mode
		# shallow copy callgraph
		self._callgraph = other._callgraph
		
	#} END iDuplicatable	
	

	
	#{ Main Interface
	
	def makeTarget( self, target ):
		"""@param target: target to make - can be class or instance
		@param reportType: Report to populate with information - it must be a Plan based 
		class that can be instantiated and populated with call information.
		A report analyses the call dependency graph generated during dg evaluation
		and presents it.
		@return: result when producing the target"""
		# generate mode 
		from byronimo.automation.processes import ProcessBase as pb
		processmode = globalmode = pb.is_state | pb.target_state
		
		shell, result = self._evaluate( target, processmode, globalmode )
		return result
	
	
	def _evaluateDirtyState( self, outputplug, processmode ):
		"""Evaluate the given plug in process mode and return a dirty report tuple 
		as used by L{getDirtyReport}"""
		report = list( outputplug, None )
		try:
			outputplug.get( processmode )	# trigger computation, might raise 
		except DirtyException, e:
			report[ 1 ] = e					# remember report as well
		
		return tuple( report )
		
	
	def getDirtyReport( self, target, mode = "single" ):
		"""@return: list of tuple( shell, DirtyReport|None ) 
		If a process ( shell.node ) is dirty, a dirty report will be given explaining 
		why the process is dirty and needs an update
		@param target: target you which to check for it's dirty state
		@param mode: 
		 	single - only the process assigned to evaluate target will be checked
			graph - as single, but the whole callgraph will be checked, starting 
					at the node finally evaluating target
			deep - try to evaluate target, but fail if one process in the target's 
			call history is dirty
		"""
		from byronimo.automation.processes import ProcessBase as pb, DirtyException
		processmode = pb.is_state | pb.dirty_check
		globalmode = None
		
		# lets make the mode clear 
		if mode == "deep" :
			globalmode = processmode		# input processes may apply dirty check ( and fail )
		elif mode in ( "single", "multi" ):
			globalmode = pb.is_state		# input process should just return the current state, no checking
		else:
			raise AssertionError( "invalid mode: %s" % mode )
		
		outreports = []
		
		# GET INITIAL REPORT 
		######################
		outputplug = self._setupProcess( target, globalmode, reset_dg = True )
		outreports.append( self._evaluateDirtyState( outputplug, processmode ) )
							
							
		# STEP THE CALLGRAPH ?
		if mode == "multi":
			# walk the callgraph and get dirty reports from each node 
			self._callgraph = Workflow.CallGraph()		# reset graph for next step
			
			# keep caches
			raise NotImplementedError()
		# END if multi handling 
		
		return outreports
		
		
	
	def _setupProcess( self, target, globalmode, reset_dg = True ):
		"""Setup the workflow's dg such that the returned output shell can be queried 
		to evaluate target
		@param reset_dg: if True, the dependency graph will be reset and cached values 
		are being deleted. If not, several process calls with cached values are possible
		@param globalmode: mode with which all other processes will be handling 
		their input calls
		"""
		# find suitable process 
		inputshell = self.getTargetRating( target )[1]
		if inputshell is None:
			raise TargetError( "Cannot handle target %r" % target )
			
		# clear previous callgraph
		self._callgraph = Workflow.CallGraph( )
		self._mode = globalmode
		
		# reset all process to prep for computation
		if reset_dg:
			for node in self.iterNodes():
				node.prepareProcess( )
		# END reset dg handling
			
		# get output plug that can be queried to get the target
		outputplugs = inputshell.plug.getAffected( )
		if not outputplugs:
			raise TargetError( "Plug %r takes target %r as input, but does not affect an output plug" % ( inputshell, target ) )
		
		# we do not care about ambiguity, simply pull one
		# QUESTION: should we warn about multiple affected plugs ?
		inputshell.set( target, ignore_connection = True )
		
		return inputshell.node.toShell( outputplugs[0] )
		
	
	def _evaluate( self, target, processmode, globalmode, reset_dg = True ):
		"""Make or update the target using a process in our workflow
		@param processmode: the mode with which to call the initial process 
		@return: tuple( shell, result ) - plugshell queried to get the result 
		"""
		outputshell = self._setupProcess( target, globalmode, reset_dg = reset_dg )
		######################################################
		result = outputshell.get( processmode )
		######################################################
		
		if len( self._callgraph._call_stack ):
			raise AssertionError( "Callstack was not empty after calculations for %r where done" % target )
		
		return ( outputshell, result )
		
		
	def getReportInstance( self, reportType ):
		"""Create a report instance that describes how the previous target was made 
		@param reportType: Report to populate with information - it must be a Plan based 
		class that can be instantiated and populated with call information.
		A report analyses the call dependency graph generated during dg evaluation
		and presents it.
		@return: report instance whose getReport method can be called to retrieve it"""
		# make the target as dry run
		return reportType( self._callgraph )
	
	#} END main interface
	
	
	#{ Query 
		
	def getTargetSupportList( self ):
		"""@return: list of all supported target type
		@note: this method is for informational purposes only"""
		uniqueout = set()
		for node in self.iterNodes():
			try:
				uniqueout.update( set( node.getSupportedTargetTypes() ) )
			except Exception, e:
				raise AssertionError( "Process %r failed when calling getSupportedTargetTypes" % p, e )
		# END for each p in nodes iter
		return list( uniqueout )
			
			
	def getTargetRating( self, target ):
		"""@return: int range(0,255) indicating how well a target can be made
		0 means not at all, 255 means perfect.
		Return value is tuple ( rate, PlugShell ), containing the process and plug with the 
		highest rating or None if rate is 0
		Walk the dependency graph such that leaf nodes have higher ratings than 
		non-leaf nodes 
		@note: you can use the L{processes.ProcessBase} enumeration for comparison"""
		rescache = list()
		best_process = None
		
		for node in self.iterNodes( ):
			rate, shell = node.getTargetRating( target )
			if not rate:
				continue 
				
			# is leaf node ? ( no output connections )		
			if not node.getConnections( 0, 1 ):
				rate = rate * 2									# prefer leafs in the rating
				
			rescache.append( ( rate, shell ) )
		# END for each process 
		
		rescache.sort()							# last is most suitable 
		if not rescache or rescache[-1][0] == 0:
			return ( 0, None )
			
		bestpick = rescache[-1]
		
		# check if we have several best picks - raise if so
		allbestpicks = [ pick for pick in rescache if pick[0] == bestpick[0] ]
		if len( allbestpicks ) > 1: 
			raise AssertionError( "There should only be one suitable process for %r, found %i" % ( target, len( allbestpicks ) ) )
			
		
		shell = bestpick[1]
		# recompute rate as we might have changed it 
		return shell.node.getTargetRating( target )
	
	#} END query 
	
	#{ Internal Process Interface 
	
	def _isDryRun( self ):
		"""@return: True if the current computation is a dry run"""
		return self._mode
	
	def _trackOutputQueryStart( self, process, plug, mode ):
		"""Called by process base to indicate the start of a call of curProcess to targetProcess 
		This method tracks the actual call path taken through the graph ( which is dependent on the 
		dirty state of the prcoesses, allowing to walk it depth first to resolve the calls.
		This also allows to create precise reports telling how to achieve a certain goal"""
		pdata = Workflow.ProcessData( process, plug, mode )
		
		# keep the call graph
		self._callgraph.startCall( pdata )
		return pdata			# return so that decorators can use this information
		
	def _trackOutputQueryEnd( self, result = None ):
		"""Track that the process just finished its computation - thus the previously active process
		should be on top of the stack again"""
		# update last data and its call time 
		self._callgraph.endCall( result )
	#}
	
	
	def _populateFromGraph( self, graph ):
		"""Parse the networkx graph and populate ourselves with the respective process 
		instances as described by the graph
		@param graph: networkx graph whose nodes are process names to be found in the processes 
		module """
		raise NotImplementedError( "TODO" )
		
