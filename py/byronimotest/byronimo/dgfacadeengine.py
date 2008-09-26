"""B{byronimotest.byronimo.dgfacadeengine}
Test dependency graph engine


@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-06 12:45:38 +0200 (Tue, 06 May 2008) $"
__revision__="$Revision: 8 $"
__id__="$Id: decorators.py 8 2008-05-06 10:45:38Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
from networkx import DiGraph
from byronimo.dgengine import *
from byronimo.dgfacadeengine import *
from random import randint

A = Attribute

class SimpleIONode( NodeBase ):
	"""Create some simple attributes"""
	#{ Plugs 
	outAdd = plug( A( float, A.uncached ) )
	
	inFloat = plug( A( float, 0, default = 0.0 ) )
	
	#} END plugs 
	inFloat.affects( outAdd )
	
		
	#{ iDuplicatable Interface 
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it
		@note: override by subclass  - the __init__ methods shuld do the rest"""
		return self.__class__( self.name )
	#} END iDuplicatable
	
	
	def __init__( self , name ):
		super( SimpleIONode, self ).__init__( )
		self.name = name
		
	def __str__( self ):
		return self.name 
		
	def compute( self, plug, mode ):
		"""Compute some values"""
		if plug == SimpleIONode.outAdd:
			return self.inFloat.get() + 10
		raise PlugUnhandled( )


class TestDGFacadeEngine( unittest.TestCase ):
	
	def test_graphFacadeNode( self ):
		"""dgengine: Simple Facade test"""
		
		# create simple graph facade
		g = Graph( )
		s1 = SimpleIONode( "s1" )
		s2 = SimpleIONode( "s2" )
		
		g.addNode( s1 )
		g.addNode( s2 )
		
		s1.outAdd > s2.inFloat
		
		# wrap it
		og = Graph( )				# other graph
		gn = GraphNodeBase( g )		# node wrapping the graph
		
		for p in gn.getPlugs(): print "%s: Provides Input: %i, output: %i" % ( p , p.providesInput(), p.providesOutput() )
		# for p in gn.getInputPlugs(): print p
		
	
