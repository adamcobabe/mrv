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
	
	#{ Overridden Methods 
	def __init__( self, **kwargs ):
		"""Initalized base class"""
		super( Workflow, self ).__init__( **kwargs )
	
	def __str__( self ):
		return self.name
	#} 
	
	#{ Main Interface
	
	def makeTarget( self, target, dry_run = False ):
		"""Make or update the target using a process in our workflow
		@param dry_run: if True, the target's creation will only be simulated
		@return: result when producing the target"""
		# find suitable process 
		process = self.getTargetRating( target )
		if process is None:
			raise ValueError( "Cannot handle target %r" % target )
			
		# trigger the output
		result = process.getOutputBase( target, dry_run = dry_run  )
		return result
		
		
	def makePlan( self, target, plan ):
		"""Create a plan that describes how the target will be made
		@param target: the target whose plan you would like to have 
		@param plan: Plan to populate with information"""
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
	
	
	def _populateFromGraph( self, graph ):
		"""Parse the networkx graph and populate ourselves with the respective process 
		instances as described by the graph
		@param graph: networkx graph whose nodes are process names to be found in the processes 
		module """
		raise NotImplementedError( "TODO" )
		
