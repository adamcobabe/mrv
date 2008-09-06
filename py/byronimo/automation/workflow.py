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
		__slots__ = ( 'target', 'starttime', 'endtime' ) 
		def __init__( self, process, target ):
			self.target = target				
			self.starttime = time.clock()
			self.endtime = self.starttime
			self.exception = None				# stores exception on error
			
		def getElapsed( ):
			"""@return: time to process the call"""
			return self.endtime - self.starttime
			
	#} END utility classes 
	
				
	#{ Overridden Methods 
	def __init__( self, **kwargs ):
		"""Initalized base class"""
		super( Workflow, self ).__init__( **kwargs )
		
		self._callgraph = None		# only populated after make target call
		self._process_stack = None
	
	def __str__( self ):
		return self.name
	#} 
	
	#{ Main Interface
	
	def makeTarget( self, target, dry_run = False, plan = None ):
		"""Make or update the target using a process in our workflow
		@param target: target to make - can be class or instance
		@param dry_run: if True, the target's creation will only be simulated
		@param plan: if Plan instance, the plan will be filled with information of 
		our callstack allowing to recreate the happened events 
		@return: result when producing the target"""
		# find suitable process 
		process = self.getTargetRating( target )[1]
		if process is None:
			raise ValueError( "Cannot handle target %r" % target )
			
		# clear previous callgraph
		self._callgraph = DiGraph( name="Callgraph" )
		self._process_stack = []			# keeps the process currently computing 
		
		# reset all process to prep for computation 
		for p in self.nodes_iter():
			p.prepareProcess( )
		
		
		
		# trigger the output
		result = process.getOutputBase( target, dry_run = dry_run  )
		return result
		
		
	def makePlan( self, target, plan ):
		"""Create a plan that describes how the target will be made
		@param target: the target whose plan you would like to have 
		@param plan: Plan to populate with information"""
		# make the target as dry run
		self.makeTarget( target , dry_run = True )
		
		# analyse the callgraph to fill the plan instance !
		raise NotImplementedError( "TODO" )
	
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
	
	def _trackOutputQueryStart( self, process, target ):
		"""Called by process base to indicate the start of a call of curProcess to targetProcess 
		This method tracks the actual call path taken through the graph ( which is dependent on the 
		dirty state of the prcoesses, allowing to walk it depth first to resolve the calls.
		This also allows to create precise plans telling how to achieve a certain goal"""
		pdata = Workflow.ProcessData( process, target )
		
		# keep the call graph
		curdata = None
		if self._process_stack:
			curdata = self._process_stack[ -1 ]
			self._callgraph.add_edge( pdata, curdata )
		else:
			# its the first call, thus we add it as node - would work on first edge add too though
			self._callgraph.add_node( pdata )	
			
		self._process_stack.append( pdata )
		return pdata			# return so that decorators can use this information 
		
	def _trackOutputQueryEnd( self ):
		"""Track that the process just finished its computation - thus the previously active process
		should be on top of the stack again"""
		# update last data and its call time 
		lastprocessdata = self._process_stack.pop( )
		lastprocessdata.endtime = time.clock( )
	#}
	
	
	def _populateFromGraph( self, graph ):
		"""Parse the networkx graph and populate ourselves with the respective process 
		instances as described by the graph
		@param graph: networkx graph whose nodes are process names to be found in the processes 
		module """
		raise NotImplementedError( "TODO" )
		
