"""B{byronimo.automation.report}
contains report implementations allowing to analyse the callgraph of   

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
## CLASSES    ######
###################	

import networkx.search as search
import processes

class ReportBase( object ):
	"""Provides main interface for all reports as well as the basic implementation"""
	
	#{ Overridden Methods 
	def __init__( self, callgraph = None ):
		"""intiialize the report with the given callgraph or None"""
		if callgraph:
			self.analyseCallgraph( callgraph )
			
	#} END overridden Methods 
	
	#{ Base Methods 
	def _toCallList( self, callgraph ):
		"""@return: flattened version of graph as list of ProcessData nodes , having
		the root as last element of the list"""
		# return search.dfs_postorder( callgraph )
		def getPredecessors( node ):
			out = []
			predlist = [ (p.index,p) for p in callgraph.predecessors( node ) ]
			predlist.sort()
			for i,pred in predlist:
				out.extend( getPredecessors( pred ) )
			out.append( node )
			return out
		
		calllist = getPredecessors( callgraph.getCallRoot() )
		calllist.reverse()
		return calllist
		# return search.dfs_postorder( callgraph )
	#}
	
	#{ Report Methods
	
	def analyseCallgraph( self, callgraph ):
		"""Analyse the given callgraph as produced by a workflow instance to create
		a report
		@param callgraph: Workflow.Callgraph instance
		@note: parse the callgraph and keep enough information to generate a report
		This allows to provide getReport methods haveing different signatures, and 
		returning different reports everytime you call them, the initial analysis will 
		then only be done once"""
		raise NotImplementedError( "This method needs to be implemented by subclasses" )
		
	def getReport( self ):
		"""@return: report as result of a prior Callgraph analysis"""
		raise NotImplementedError( "This method needs to be implemented by subclasses" )
		
	#} END report methods 
	

class Plan( ReportBase ):
	"""Create a plan-like text describing how the target is being made"""
	
	def __init__( self, headline, **kwargs ):
		"""intialize the Plan with the headling for the plan"""
		super( Plan, self ).__init__( **kwargs )
		self._headline = headline
		
	def analyseCallgraph( self , callgraph ):
		"""Create a list of ProcessData instances that reflects the call order"""
		self._calllist = self._toCallList( callgraph )
		self._calllist.reverse( )
		                                                           
		
	def getReport( self ):
		"""@return: list of strings ( lines ) resembling a plan-like formatting 
		of the call graph"""
		out = []
		out.append( self._headline )
		skipcount = 0
		for i,p in enumerate( self._calllist ):
			if isinstance( p.process, processes.SelectorBase ):
				skipcount += 1 
				continue 
				
			line = "%i. %s %s %r" % ( i-skipcount+1, p.process.noun, p.process.verb, p.target )
			out.append( line )
		return out
		
