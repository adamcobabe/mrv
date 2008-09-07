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

class Workflow( DiGraph ):
	"""Implements a workflow as connected processes
	@note: if you have to access the processes directly, use the DiGraph methods"""

	#{ Utility Classes 
	class ProcessData( object ):
		"""Allows to store additional information with each process called during the workflow"""
		__slots__ = ( 'process','target', '_result', 'starttime', 'endtime','exception','index' ) 
		def __init__( self, process, target ):
			self.process = process
			self.target = target
			self._result = None				# can be weakref or actual value 
			self.starttime = time.clock()
			self.endtime = self.starttime
			self.exception = None				# stores exception on error
			self.index = 0						# index of the child - graph stores nodes unordered
			
		def __repr__( self ):
			out = "%s(%r)" % ( self.process, self.target )
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
		self._dry_run = False 
	
	def __str__( self ):
		return self.name
	#} 
	
	#{ Main Interface
	
	def makeTarget( self, target, dry_run = False, report = None ):
		"""Make or update the target using a process in our workflow
		@param target: target to make - can be class or instance
		@param dry_run: if True, the target's creation will only be simulated
		@param report: if Report instance, the report will be filled with information of 
		our callstack allowing to recreate the happened events 
		@return: result when producing the target"""
		# find suitable process 
		process = self.getTargetRating( target )[1]
		if process is None:
			raise ValueError( "Cannot handle target %r" % target )
			
		# clear previous callgraph
		self._callgraph = Workflow.CallGraph( )
		self._dry_run = dry_run
		
		# reset all process to prep for computation 
		for p in self.nodes_iter():
			p.prepareProcess( )
			
		# trigger the output
		result = process.getOutputBase( target )
		
		if report:
			report.analyseCallgraph( self._callgraph )
		
		if len( self._callgraph._call_stack ):
			raise AssertionError( "Callstack was not empty after calculations for %r where done" % target )
		
		return result
		
		
	def makeReport( self, target, report ):
		"""Create a report that describes how the target will be made - nothing is 
		actually being changed as the target is made in dry_run mode
		@param target: the target whose report you would like to have 
		@param report: Report to populate with information
		@return: report instance whose getReport method can be called to retrieve it"""
		# make the target as dry run
		self.makeTarget( target , dry_run = True, report = report )
		return report
	
	#} END main interface


	#{ Query 
		
	def getTargetSupportList( self ):
		"""@return: list of all supported target type
		@note: this method is for informational purposes only"""
		uniqueout = set()
		for p in self.nodes_iter():
			uniqueout.update( set( p.getSupportedTargetTypes() ) )
		return list( uniqueout )
			
			
	def getTargetRating( self, target ):
		"""@return: int range(0,255) indicating how well a target can be made
		0 means not at all, 255 means perfect.
		Return value is tuple ( rate, process ), containing the process with the 
		highest rating or None if rate is 0
		Walk the dependency graph such that leaf nodes have higher ratings than 
		non-leaf nodes 
		@note: you can use the L{processes.ProcessBase} enumeration for comparison"""
		rescache = list()
		best_process = None
		for p in self.nodes_iter():
			rate = p.canOutputTarget( target )
			if not self.successors( p ): 		# is leaf ?
				rate = rate * 2					# prefer leafs in the rating 
			rescache.append( ( rate, p ) )
		# END for each process 
		
		rescache.sort()
		if not rescache or rescache[-1][0] == 0:
			return ( 0, None )
			
		bestpick = rescache[-1]
		
		# check if we have several best picks - raise if so
		allbestpicks = [ pick for pick in rescache if pick[0] == bestpick[0] ]
		if len( allbestpicks ) > 1: 
			raise AssertionError( "There should only be one suitable process for %r, found %i" % ( target, len( allbestpicks ) ) )
			
		p = bestpick[1]
		return ( int( p.canOutputTarget( target ) ), p )
	
	#} END query 
	
	#{ Internal Process Interface 
	
	def _isDryRun( self ):
		"""@return: True if the current computation is a dry run"""
		return self._dry_run
	
	def _trackOutputQueryStart( self, process, target ):
		"""Called by process base to indicate the start of a call of curProcess to targetProcess 
		This method tracks the actual call path taken through the graph ( which is dependent on the 
		dirty state of the prcoesses, allowing to walk it depth first to resolve the calls.
		This also allows to create precise reports telling how to achieve a certain goal"""
		pdata = Workflow.ProcessData( process, target )
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
		
