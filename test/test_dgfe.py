# -*- coding: utf-8 -*-
"""Test dependency graph engine """
import unittest
from mayarv.dge import *
from mayarv.dgfe import *

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
		return self.__class__( self.getID() )
	#} END iDuplicatable


	def __init__( self , name ):
		super( SimpleIONode, self ).__init__( id = name )

	def compute( self, plug, mode ):
		"""Compute some values"""
		if plug == SimpleIONode.outAdd:
			return self.inFloat.get() + 1
		raise PlugUnhandled( )

class LessSimpleIONode( SimpleIONode ):
	"""more attributes added"""
	#{ Plugs
	outBool = plug( A( bool, A.uncached ) )

	inBool = plug( A( bool, 0, default = False ) )

	#} END plugs
	inBool.affects( outBool )


class TestDGFacadeEngine( unittest.TestCase ):

	def test_graphFacadeNode( self ):
		"""dgengine: graphFacadeNodes: full facade test """

		# create simple graph facade
		g = Graph( )
		s1 = SimpleIONode( "s1" )
		s2 = SimpleIONode( "s2" )

		g.addNode( s1 )
		g.addNode( s2 )

		s1.outAdd >> s2.inFloat

		# EVALUATION CHECK
		# run through two evals
		self.failUnless( s2.outAdd.get( ) == 2)


		# wrap it
		og = Graph( )				# other graph
		gn1 = GraphNodeBase( g, id="GN_1" )		# node wrapping the graph
		og.addNode( gn1 )

		self.failUnless( len( gn1.inputPlugs() ) == 2 )		# does not consider connections
		self.failUnless( len( gn1.outputPlugs() ) == 2 )		# does not consider connections


		# GET ATTR
		###########
		self.failUnlessRaises( AttributeError, getattr, gn1, "inFloat" )

		# ATTR AFFECTS
		###############
		affected = gn1._FP_s1_inFloat.plug.affected()
		self.failUnless( len( affected ) == 2 )

		affectedby = affected[-1].affectedBy()
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
		self.failUnless( s1ifloat.hasCache() and s1ifloat.cache() == 10.0 )

		# as its a copy, we have to set the value there as well
		# fail due to connection
		self.failUnlessRaises( NotWritableError, gn1._FP_s2_inFloat.set, 10.0 )
		gn1s1ifloat = gn1._FP_s1_inFloat
		gn1s2outAdd = gn1._FP_s2_outAdd

		gn1s1ifloat.set( 10.0 )
		self.failUnless( gn1s1ifloat.hasCache() and gn1s1ifloat.cache() == 10.0 )
		self.failUnless( s2.outAdd.get() == gn1s2outAdd.get() )


		# SET VALUE AND CACHE DIRTYING
		################################
		SimpleIONode.outAdd.attr.flags = 0  	 # enable caching now for all SimpleNodes
		# assure its working - pull to have a cache
		self.failUnless( s2.outAdd.get() == gn1._FP_s2_outAdd.get() )
		self.failUnless( s2.outAdd.hasCache() and gn1s2outAdd.hasCache() )

		# adjust input to clear the caches
		s1.inFloat.set( 20.0 )
		self.failUnless( not s2.outAdd.hasCache() )

		gn1s1ifloat.set( 20.0 )
		self.failUnless( not gn1s2outAdd.hasCache() )

		# ITERATION
		###############
		# One should never get inside
		for shell in gn1s1ifloat.iterShells( direction = "down" ):
			self.failUnless( isinstance( shell.node, GraphNodeBase ) )

		# MULTI-GRAPHNODE CONNECTIONS
		#############################
		# AND ALL THE ADDITIONAL TESTS

		gn2 = GraphNodeBase( g, id="GN_2" )
		og.addNode( gn2 )
		gn1s1ifloat.set( 0.0 )				# no offset
		gn1s2oadd = gn1._FP_s2_outAdd
		gn2s2oadd = gn2._FP_s2_outAdd

		gn1s2oadd.connect( gn2._FP_s1_inFloat )

		# ITERATION
		###############
		# One should never get inside
		for shell in gn1._FP_s1_inFloat.iterShells( direction = "down", visit_once=True ):
			self.failUnless( isinstance( shell.node, GraphNodeBase ) )

		# simple comutation - expect 4 computations !
		self.failUnless( gn2s2oadd.get() == 4 )

		# change offset - it must propagate so g2s2 reevalutates
		gn1s1ifloat.set( 10.0 )
		self.failUnless( gn1s1ifloat.cache() == 10.0 )
		self.failUnless( gn2s2oadd.get() == 14 )

		# SUPER GRAPHNODE CONTAINING OTHER GRAPH NODES !!!
		###################################################
		sog = Graph()
		sgn1 = GraphNodeBase( og, id="SGN_1" )
		sgn2 = GraphNodeBase( og, id="SGN_2" )

		sog.addNode( sgn1 )
		sog.addNode( sgn2 )

		# SIMPLE CONNECTION
		####################
		sgn1._FP_GN_2__FP_s2_outAdd >> sgn2._FP_GN_1__FP_s1_inFloat

		sg1inFloat = sgn1._FP_GN_1__FP_s1_inFloat
		sg2inFloat = sgn2._FP_GN_1__FP_s1_inFloat
		sg2outAdd = sgn2._FP_GN_2__FP_s2_outAdd


		# ITERATION
		###############
		# One should never get inside
		for shell in sg1inFloat.iterShells( direction = "down", visit_once=True ):
			self.failUnless( isinstance( shell.node, GraphNodeBase ) )


		# AFFECTS
		################
		self.failUnless( len( sg1inFloat.plug.affected( ) ) == 7 )
		self.failUnless( len( sg2outAdd.plug.affectedBy( ) ) == 4 )

		# SIMPLE COMPUTATION
		######################
		self.failUnless( sg2outAdd.get( ) == 8 )		# 2 * 2 * 2 = 2simpleNodes * 2graphnodes * 2sgn
		self.failUnless( sg2outAdd.get( ) == 8 )		# its cached now
		# DIRTYING - set the input cache
		sg1inFloat.set( 10.0 )
		self.failUnless( sg2outAdd.get( ) == 18 )
		self.failUnless( sg2outAdd.get( ) == 18 )		# its cached now


		# PLUG OVERRIDES
		##################
		# internal plugs can be explicitly set, the cache will be used on evaluation
		# even if a connection is coming in from the ( outside ) facade node
		sg2outAdd >> sg1inFloat
		sg1inFloat.set( 20.0 )
		self.failUnless( sg2outAdd.get( ) == 28 )	# if it didnt work, we would go into recursion

		sg2inFloat.clearCache( clear_affected = True )		# make it sg1 dirty - now its connected with sg2
		self.failUnless( sg1inFloat.get() == 0.0 )


	def test_graphNodeIncludeExclude( self ):
		"""dgending: graphnode configuration"""

		# INCLUDE / EXCLUDE PARAMETERS
		class Gnode( GraphNodeBase ):
			caching_enabled = False
			include = [ "node.doesnotexist" ]


		g = Graph( )
		s1 = LessSimpleIONode( "s1" )
		s2 = LessSimpleIONode( "s2" )

		g.addNode( s1 )
		g.addNode( s2 )

		s1.outBool >> s2.inBool

		# wrap it
		og = Graph( )				# other graph
		gn = Gnode( g, id="GNode" )		# node wrapping the graph
		og.addNode( gn )


		# TEST INCLUDE
		###################
		# should not find include plug
		self.failUnlessRaises( AssertionError, gn.plugs )

		gn.ignore_failed_includes = True

		# now it should work
		gn.plugs()

		# explicit include, no auto includes
		gn.include = [ "s1.outAdd" ]
		gn.allow_auto_plugs = False

		# just include should be left
		self.failUnless( len( gn.plugs() ) == 1 )

		# TEST PLUG EXCLUDE
		####################
		gn.exclude = gn.include
		self.failUnless( len( gn.plugs( ) ) == 0 )
		gn.exclude = tuple()

		# test whole node include
		gn.include = [ "s1" ]
		self.failUnless( len( gn.plugs() ) == 4 )


		# TEST NODE EXCLUDE
		###############
		gn.exclude = gn.include
		self.failUnless( len( gn.plugs( ) ) == 0 )


