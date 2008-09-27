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
	
	inFloat = plug( A( float, A.writable, default = 0.0 ) )
	
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
			return self.inFloat.get() + 1
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
		
		# EVALUATION CHECK
		# run through two evals
		self.failUnless( s2.outAdd.get( ) == 2 )
		
		
		# wrap it
		og = Graph( )				# other graph
		gn1 = GraphNodeBase( g )		# node wrapping the graph
		og.addNode( gn1 )
		
		self.failUnless( len( gn1.getInputPlugs() ) == 2 )		# does not consider connections  
		self.failUnless( len( gn1.getOutputPlugs() ) == 2 )		# does not consider connections 
		
		
		# GET ATTR 
		###########
		self.failUnlessRaises( AttributeError, getattr, gn1, "inFloat" )
		
		# ATTR AFFECTS
		###############
		affected = gn1._FP_s1_inFloat.plug.getAffected()
		self.failUnless( len( affected ) == 2 )
		
		affectedby = affected[-1].getAffectedBy()
		self.failUnless( len( affectedby ) == 2 )
		
		
		# GET VALUE
		##############
		# same result as in std mode !
		origres = s2.outAdd.get()
		fres = gn1._FP_s2_outAdd.get()
		self.failUnless( fres == origres )
		
		# CLEAR CACHE
		# adjust input value inside - it should affect outside world as well
		s1ifloat = s1.inFloat
		s1ifloat.set( 10.0 )
		self.failUnless( s1ifloat.hasCache() and s1ifloat.getCache() == 10.0 )
		
		# as its a copy, we have to set the value there as well
		# fail due to connection
		self.failUnlessRaises( NotWritableError, gn1._FP_s2_inFloat.set, 10.0 )
		gn1s1ifloat = gn1._FP_s1_inFloat
		gn1s2outAdd = gn1._FP_s2_outAdd
		
		gn1s1ifloat.set( 10.0 )
		self.failUnless( gn1s1ifloat.hasCache() and gn1s1ifloat.getCache() == 10.0 )
		self.failUnless( s2.outAdd.get() == gn1s2outAdd.get() )
		
		
		# SET VALUE AND CACHE DIRTYING
		################################
		SimpleIONode.outAdd.attr.flags = 0  	 # default is cached now for all 
		# assure its working - pull to have a cache  
		self.failUnless( s2.outAdd.get() == gn1._FP_s2_outAdd.get() )
		self.failUnless( s2.outAdd.hasCache() and gn1s2outAdd.hasCache() )
		
		# adjust input to clear the caches
		s1.inFloat.set( 20.0 )
		self.failUnless( not s2.outAdd.hasCache() )
		
		gn1s1ifloat.set( 20.0 )
		self.failUnless( not gn1s2outAdd.hasCache() )
		
		
		# MULTI-GRAPHNODE CONNECTIONS
		#############################
		# AND ALL THE ADDITIONAL TESTS
		
		#gn2 = GraphNodeBase( g )
		
		
		
		# SUPER GRAPHNODE CONTAINING OTHER GRAPH NODES !!!
		###################################################
		
