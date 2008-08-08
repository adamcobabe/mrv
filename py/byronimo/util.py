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
		
