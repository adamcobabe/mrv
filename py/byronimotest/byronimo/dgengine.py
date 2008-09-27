"""B{byronimotest.byronimo.util}
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
from random import randint

A = Attribute

#{ TestNodes 
class SimpleNode( NodeBase ):
	"""Create some simple attributes"""
	#{ Plugs 
	outRand = plug( A( float, 0 ) )
	outMult = plug( A( float, A.uncached ) )
	
	inInt = plug( A( int, A.writable ) )
	inFloat = plug( A( float, 0, default = 2.5 ) )
	inFloatNoDef = plug( A( float, 0 ) )
	outFailCompute = plug( A( str, A.computable ) )
	
	inFloat.affects( outRand )
	inFloatNoDef.affects( outRand )
	
	inInt.affects( outMult )
	inFloat.affects( outMult )
	
	#} END plugs 
	
		
	#{ iDuplicatable Interface 
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it
		@note: override by subclass  - the __init__ methods shuld do the rest"""
		return self.__class__( self.name )
	#} END iDuplicatable
	
	
	def __init__( self , name ):
		super( SimpleNode, self ).__init__( )
		self.name = name
		
	def __str__( self ):
		return self.name 
		
	def compute( self, plug, mode ):
		"""Compute some values"""
		if plug == SimpleNode.outFailCompute:
			raise ComputeFailed( "Test compute failed" )
		elif plug == SimpleNode.outRand:
			return float( randint( 1, self.inFloat.get( ) * 10000 ) )
		elif plug == SimpleNode.outMult:
			return self.inInt.get( ) * self.inFloat.get( )
		raise PlugUnhandled( )


#}


class TestDGEngine( unittest.TestCase ):
	
	def test_fullFeatureTest( self ):
		"""dgengine: Test full feature set"""
		graph = Graph()
		s1 = SimpleNode( "s1" )
		graph.addNode( s1 )
		
		self.failUnless( SimpleNode.outRand.providesOutput() )
		self.failUnless( SimpleNode.inFloat.providesInput() )
		
		# ADD / REMOVE 
		#################
		addrem = SimpleNode( "addrem" )
		graph.addNode( addrem )
		self.failUnless( graph.hasNode( addrem ) )
		graph.removeNode( addrem )
		self.failUnless( not graph.hasNode( addrem ) )
		graph.addNode( addrem )
		self.failUnless( graph.hasNode( addrem ) )
		
		# del node - it will stay in the graph thoguh 
		del( addrem )
		self.failUnless( len( list( graph.iterNodes() ) ) == 2 )
		# get the node back and remove it properly 
		addrem = list( graph.iterNodes() )[1]
		graph.removeNode( addrem )
		del( addrem )
		self.failUnless( len( list( graph.iterNodes() ) ) == 1 )
		self.failUnless( len( list( graph.iterConnectedNodes() ) ) == 0 )
		
		# SET VALUES
		#############
		self.failUnlessRaises( NotWritableError, s1.inFloat.set, "this" )
		self.failUnlessRaises( NotWritableError, s1.outRand.set, "that" )
		
		# computation failed check
		self.failUnlessRaises( ComputeFailed, s1.outFailCompute.get  )
		
		# missing default value
		self.failUnlessRaises( MissingDefaultValueError, s1.inInt.get )
		
		# now we set a value 
		self.failUnlessRaises( TypeError, s1.inInt.set, "this" )	# incompatible type
		s1.inInt.set( 5 )											# this should work though
		self.failUnless( s1.inInt.get( ) == 5 )					# should be cached 
		s1.inInt.clearCache()
		
		self.failUnlessRaises( MissingDefaultValueError, s1.inInt.get )	# cache is gone
		self.failUnless( s1.inFloat.get( ) == 2.5 )
		self.failUnlessRaises( NotWritableError, s1.inFloat.set, "this" )
		
		myint = s1.outRand.get( )		# as it is cached, the value should repeat
		self.failUnless( s1.outRand.hasCache() )
		self.failUnless( s1.outRand.get( ) == myint )
		s1.outRand.plug.attr.flags &= Attribute.uncached
		
		
		# CONNECTIONS
		##############
		s2 = SimpleNode( "s2" )
		s3 = SimpleNode( "s3" )
		graph.addNode( s2 )
		graph.addNode( s3 )
		s1.outRand.connect( s2.inFloat )
		s1.outRand.connect( s2.inFloat )		# works as it is already connected to what we want
		
		# fail set due to connection 
		self.failUnlessRaises( NotWritableError, s2.inFloat.set, 2.0 ) 
		
		# disconnect 
		s1.outRand.disconnect( s2.inFloat )
		self.failUnless( len( s1.outRand.getOutputs() ) == 0 and not s2.inFloat.getInput() )
		
		s1.outRand.connect( s2.inFloat )
		
		# check its really connected
		self.failUnless( s2.inFloat.getInput( ) == s1.outRand )
		self.failUnless( s1.outRand.getOutputs()[0] == s2.inFloat )
		
		
		# connecting again should throw without force
		self.failUnlessRaises( PlugAlreadyConnected, s3.outRand.connect, s2.inFloat )
		# force works though, disconnects otheone
		s3.outRand.connect( s2.inFloat, force = 1 )
		self.failUnless( s2.inFloat.getInput( ) == s3.outRand )
		self.failUnless( len( s1.outRand.getOutputs() ) == 0 )
		
		
		
		# MULTI CONNECT 
		##################
		s1.inFloat.connect( s3.inFloat )
		s2.inInt.connect( s3.inInt )
		
		# inInt does not have a default value, so computation fails unhandled 
		self.failUnlessRaises( ComputeError, s3.outMult.get )	
		
		# set in int and it should work
		s2.inInt.set( 4 )
		self.failUnless( s3.outMult.get( ) == 10 )	# 2.5 * 4
		
		# make the float writable 
		s1.inFloat.plug.attr.flags |= A.writable
		s1.inFloat.set( 2.0 )
		self.failUnless( s3.outMult.get( ) == 8 )	# 2.0 * 4
		
		
		# DIRTY CHECKING
		###################
		s3.outMult.plug.attr.flags ^= A.uncached
		self.failUnless( s3.outMult.get( ) == 8 )		# now its cached 
		s1.inFloat.set( 3.0 )								# plug is being dirtied and cache is deleted 
		self.failUnless( s3.outMult.get( ) == 12 )
		
		
		
		
		# ITERATION
		############
		# breadth first by default, no pruning, UP
		piter = iterShells( s3.outMult )
		
		self.failUnless( piter.next() == s3.outMult )
		self.failUnless( piter.next() == s3.inFloat )
		self.failUnless( piter.next() == s3.inInt )
		self.failUnless( piter.next() == s1.inFloat )
		self.failUnless( piter.next() == s2.inInt )
		self.failUnlessRaises( StopIteration, piter.next )
		
		# branch_first 
		piter = iterShells( s3.outMult, branch_first = True )
		self.failUnless( piter.next() == s3.outMult )
		self.failUnless( piter.next() == s3.inFloat )
		self.failUnless( piter.next() == s1.inFloat )
		self.failUnless( piter.next() == s3.inInt )
		self.failUnless( piter.next() == s2.inInt )
		self.failUnlessRaises( StopIteration, piter.next )
		
		# DOWN ITERATION
		##################
		piter = iterShells( s2.inInt, direction="down", branch_first = True )
		
		self.failUnless( piter.next() == s2.inInt )
		self.failUnless( piter.next() == s3.inInt )
		self.failUnless( piter.next() == s3.outMult )
		self.failUnless( piter.next() == s2.outMult )
		self.failUnlessRaises( StopIteration, piter.next )
		
		piter = s2.inInt.iterShells( direction="down", branch_first = False )
		
		self.failUnless( piter.next() == s2.inInt )
		self.failUnless( piter.next() == s3.inInt )
		self.failUnless( piter.next() == s2.outMult )
		self.failUnless( piter.next() == s3.outMult )
		self.failUnlessRaises( StopIteration, piter.next )
		
		# NODE BASED CONNECTION QUERY 
		##############################
		self.failUnless( len( s3.getConnections( 1, 0 ) ) == 2 )
		self.failUnless( len( s3.getConnections( 0, 1 ) ) == 1 )
		self.failUnless( len( s3.getConnections( 1, 1 ) ) == 3 )
		
		# SHELL BASED CONNECTION QUERY 
		###################################
		iedges = s3.inInt.getConnections( 1, 0 )
		self.failUnless( len( iedges ) == 1 )
		self.failUnless( iedges[0][0] == s2.inInt and iedges[0][1] == s3.inInt )
		
		oedges = s2.inInt.getConnections( 0, 1 )
		self.failUnless( len( oedges ) == 1 )
		self.failUnless( oedges[0][0] == s2.inInt and oedges[0][1] == s3.inInt )
		
		
		# iterconnectednodes 
		self.failUnless( len( list( graph.iterConnectedNodes() ) ) == 3 )
		
		graph.writeDot( "/usr/tmp/PreRemove.dot" )
		# remove nodes and check connections 
		graph.removeNode( s3 )
		graph.removeNode( s2 )
		graph.removeNode( s1 )
		
		self.failUnless( len( graph._nodes ) == 0 )
		self.failUnless( len( list( graph.iterNodes() ) ) == 0 )
		self.failUnless( len( list( graph.iterConnectedNodes() ) ) == 0 )
		
		# PLUG FILTERING 
		#################
		intattr = A( int, 0 )
		floatattr = A( float, 0 )
		inplugs = SimpleNode.getInputPlugsStatic()
		
		self.failUnless( len( SimpleNode.filterCompatiblePlugs( inplugs, intattr ) ) == 1 )
		self.failUnless( len( SimpleNode.filterCompatiblePlugs( inplugs, intattr, raise_on_ambiguity=1 ) ) == 1 )
		
		self.failUnless( len( SimpleNode.filterCompatiblePlugs( inplugs, floatattr ) ) == 2 )
		self.failUnlessRaises( TypeError, SimpleNode.filterCompatiblePlugs, inplugs, floatattr, raise_on_ambiguity = 1 )
		
	def test_duplication( self ):
		"""dgengine: duplicate a graph"""
		# test shallow copy 
		graph = Graph()
		s1 = SimpleNode( "s1" )
		s2 = SimpleNode( "s2" )
		s3 = SimpleNode( "s3" )
		
		graph.addNode( s1 )
		graph.addNode( s2 )
		graph.addNode( s3 )
		
		s1.outRand > s2.inFloat
		s2.outMult > s3.inFloat
		
		g2 = graph.duplicate( )
		
		self.failUnless( len( list( graph.iterNodes() ) ) == len( list( g2.iterNodes() ) ) )
		self.failUnless( len( list( graph.iterConnectedNodes() ) ) == len( list( g2.iterConnectedNodes() ) ) )
		
		
