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
	def __init__( self, callgraph ):
		"""intiialize the report with the given callgraph"""
		self._callgraph = callgraph
			
	#} END overridden Methods 
	
	#{ Base Methods 
	def _toCallList( self, reverse = True, pruneIfTrue = lambda x: False ):
		"""@return: flattened version of graph as list of ProcessData edges in call order , having
		the root as last element of the list
		@param pruneIfTrue: Function taking ProcessData to return true if the node
		should be pruned from the result
		@param reverse: if true, the calllist will be properly reversed ( taking childre into account """
		
		def getPredecessors( node, nextNode, reverse, pruneIfTrue ):
			out = []
			
			# invert the callorder - each predecessor list defines the getInput calls
			# a process has made - to properly reporoduce that, the call order needs to be 
			# inverted as well 
			predlist = self._callgraph.predecessors( node )
			lenpredlist = len( predlist ) - 1
			if not reverse:
				lenpredlist *= -1 	# will keep the right, non reversed order
				
			predlist = [ ( lenpredlist - p.index, p ) for p in predlist ]	 
			predlist.sort()
			
			prednextnode = node
			pruneThisNode = pruneIfTrue( node )
			if pruneThisNode:
				prednextnode = nextNode
				
			# enumerate the other way round, as the call list needs to be inverted
			for i,pred in predlist:
				out.extend( getPredecessors( pred, prednextnode, reverse, pruneIfTrue ) )
					
			if not pruneThisNode:
				out.append( ( node, nextNode ) )
			return out
		# END getPredecessors
		
		calllist = getPredecessors( self._callgraph.getCallRoot(), None, reverse, pruneIfTrue )
		if not reverse:
			calllist.reverse() 	# actually brings it in the right order, starting at root 
		return calllist
	#}
	
	#{ Report Methods
	
	def getReport( self ):
		"""@return: report as result of a prior Callgraph analysis"""
		raise NotImplementedError( "This method needs to be implemented by subclasses" )
		
	#} END report methods 
	

class Plan( ReportBase ):
	"""Create a plan-like text describing how the target is being made"""
	
	def _analyseCallgraph( self , skipUtilityProcesses ):
		"""Create a list of ProcessData instances that reflects the call order"""
		kwargs = {}
		if skipUtilityProcesses:
			def pruneFunc( pdata ):
				return isinstance( pdata.process, ( processes.PassThroughProcess ) )
			kwargs[ 'pruneIfTrue' ] = pruneFunc
		# END skipUtilityProcesses
		kwargs[ 'reverse' ] = True
		
		return self._toCallList( **kwargs )
		                                                           
		
	def getReport( self, headline=None, skipUtilityProcesses=True ):
		"""@return: list of strings ( lines ) resembling a plan-like formatting 
		of the call graph
		@param headline: line to be given as first line 
		@param skipUtilityProcesses: if True, utility process, those that do not do real work, 
		will be skipped"""
		cl = self._analyseCallgraph( skipUtilityProcesses )
		
		out = []
		if headline:
			out.append( headline )
			
		for i,pedge in enumerate( cl ):
			sp,ep = pedge
			i += 1 		# plans start at 1
			# its an edge
			if ep:
				line = "%i. %s provides %r to %s for %r" % ( i, sp.process.noun, sp.getResult(), ep.process.noun, sp.target )
			else:
				# its root 
				line = "%i. %s %s %r to produce %r" % ( i, sp.process.noun, sp.process.verb, sp.target, sp.getResult() )
			out.append( line )
		# END for each process data edge 
		return out
		
