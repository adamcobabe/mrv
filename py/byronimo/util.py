"""B{byronimo.util}
All kinds of utility methods and classes that are used in more than one modules

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: configuration.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import networkx.tree as nxtree
from collections import deque as Deque

class Singleton(object) :
	""" Singleton classes can be derived from this class,
		you can derive from other classes as long as Singleton comes first (and class doesn't override __new__ ) """
	def __new__(cls, *p, **k):
		if not '_the_instance' in cls.__dict__:
			cls._the_instance = super(Singleton, cls).__new__(cls)
		return cls._the_instance


def capitalize(s):
	"""@return: s with first letter capitalized"""
	return s[0].upper() + s[1:]

def uncapitalize(s, preserveAcronymns=False):
	"""@return: s with first letter lower case
	@param preserveAcronymns: enabled ensures that 'NTSC' does not become 'nTSC'
	@note: from pymel
	"""
	try:
		if preserveAcronymns and s[0:2].isupper():
			return s
	except IndexError: pass
	
	return s[0].lower() + s[1:]
	

class CallOnDeletion( object ):
	"""Call the given callable object once this object is being deleted
	Its usefull if you want to assure certain code to run once the parent scope 
	of this object looses focus"""
	def __init__( self, callableobj ):
		self.callableobj = callableobj
		
	def __del__( self ):
		self.callableobj( )
		

class iDagItem( object ):
	""" Describes interface for a DAG item.
	Its used to unify interfaces allowing to access objects in a dag like graph
	@note: all methods of this class are abstract and need to be overwritten """
	
	kOrder_DepthFirst, kOrder_BreadthFirst = range(2)
	
	#{ Overridden Methods
	def __init__( self, separator = None ):
		"""Intiialize the instance with the path separator - this helps
		the default implementation to natively work with most path types.
		If this is not the case, you have to override the methods using it 
		with your specialized version"""
		self._sep = separator
	#} 
	
	#{ Query Methods 
	
	def isRoot( self ):
		"""@return: True if this path is the root of the DAG """
		return self ==  self.getRoot()
		
	def getRoot( self ):
		"""@return: the root of the DAG - it has no further parents"""
		parents = self.getParentDeep( )
		if not parents:
			return self
		return parents[-1]
	
	def getBasename( self ):
		"""@return: basename of this path, '/hello/world' -> 'world'"""
		return self.split( self._sep )[-1]
		
	def getParent( self ):
		"""@return: parent of this path, '/hello/world' -> '/hello' or None if this path 
		is the dag's root"""
		tokens =  self.split( self._sep )
		if len( tokens ) <= 2:		# its already root 
			return None
			
		return self.__class__( self._sep.join( tokens[0:-1] ) )
		
	def getParentDeep( self ):
		"""@return: all parents of this path, '/hello/my/world' -> [ '/hello/my','/hello' ]"""
		out = []
		curpath = self
		while True:
			parent = curpath.getParent( )
			if not parent:
				break
			
			out.append( parent )
			curpath = parent
		# END while true
		
		return out 
		
	def getChildren( self , predicate = lambda x: True):
		"""@return: list of intermediate children of path, [ child1 , child2 ]
		@param predicate: return True to include x in result
		@note: the child objects returned are supposed to be valid paths, not just relative paths"""
		raise NotImplementedError( )
		
	def getChildrenDeep( self , order = kOrder_BreadthFirst, predicate=lambda x: True ):
		"""@return: list of all children of path, [ child1 , child2 ]
		@param order: order enumeration 
		@param predicate: returns true if x may be returned
		@note: the child objects returned are supposed to be valid paths, not just relative paths"""
		out = []
		
		if order == self.kOrder_DepthFirst:
			def depthSearch( child ):
				if not predicate( c ):
					return 
				children = child.getChildren( predicate = predicate )
				for c in children:
					depthSearch( c )
				out.append( child )
			# END recursive search method
			
			depthSearch( self )
		# END if depth first 
		elif order == self.kOrder_BreadthFirst:
			childstack = Deque( [ self ] )		
			while childstack:
				item = childstack.pop( )
				if not predicate( item ):
					continue 
				children = item.getChildren( predicate = predicate )
				
				childstack.extendleft( children )
				out.extend( children )
			# END while childstack
		# END if breadth first 
		return out
		
	#} END Query Methods


class DAGTree( nxtree.DirectedTree ):
	"""Adds utility functions to DirectedTree allowing to handle a directed tree like a dag
	@note: currently this tree does not support instancing
	@todo: add instancing support"""
	
	def children( self, n ):
		""" @return: list of children of given node n """
		return list( self.children_iter( n ) ) 
	
	def children_iter( self, n ):
		""" @return: iterator with children of given node n"""
		return ( e[1] for e in self.out_edges_iter( n ) )
		
	def parent( self, n ):
		"""@return: parent of node n
		@note: currently there is only one parent, as instancing is not supported yet"""
		for parent in  self.predecessors_iter( n ):
			return parent
		return None
		
	def parent_iter( self, n ):
		"""@return: iterator returning all parents of node n"""
		while True:
			p = self.parent( n )
			if p is None:
				raise StopIteration( )
			yield p
			n = p
		
