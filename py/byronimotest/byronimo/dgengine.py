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

nodegraph = DiGraph()
A = Attribute

#{ TestNodes 
class SimpleAttrs( NodeBase ):
	"""Create some simple attributes"""
	#{ Plugs 
	outRand = plug( "outRand", A( float, 0 ) )
	outMult = plug( "outMult", A( float, A.uncached ) )
	
	inInt = plug( "inInt", A( int, A.writable ) )
	inFloat = plug( "inFloat", A( float, 0, default = 2.5 ) )
	inFloatNoDef = plug( "inFloatNoDef", A( float, 0 ) )
	outFailCompute = plug( "outFail", A( str, A.computable ) )
	
	inFloat.affects( outRand )
	inFloatNoDef.affects( outRand )
	
	inInt.affects( outMult )
	inFloat.affects( outMult )
	
	#inFloat.affects( 
	#}
	
	
	def __init__( self ):
		super( SimpleAttrs, self ).__init__( nodegraph )
		
		
	def compute( self, plug, mode ):
		"""Compute some values"""
		if plug == SimpleAttrs.outFailCompute:
			raise ComputeFailed( "Test compute failed" )
		elif plug == SimpleAttrs.outRand:
			return float( randint( 1, self.inFloat.get( 0 ) * 10000 ) )
		elif plug == SimpleAttrs.outMult:
			return self.inInt.get(0) * self.inFloat.get( 0 )
		raise PlugUnhandled( )


#}


class TestDAGTree( unittest.TestCase ):
	
	def test_simpleConnection( self ):
		"""dgengine: create some simple connections"""
		s1 = SimpleAttrs( )
		
		self.failUnless( SimpleAttrs.outRand.providesOutput() )
		self.failUnless( SimpleAttrs.inFloat.providesInput() )
		
		# SET VALUES
		#############
		self.failUnlessRaises( NotWritableError, s1.inFloat.set, "this" )
		self.failUnlessRaises( NotWritableError, s1.outRand.set, "that" )
		
		# computation failed check
		self.failUnlessRaises( ComputeFailed, s1.outFailCompute.get, 0  )
		
		# missing default value
		self.failUnlessRaises( MissingDefaultValueError, s1.inInt.get, 0 )
		
		# now we set a value 
		self.failUnlessRaises( TypeError, s1.inInt.set, "this" )	# incompatible type
		s1.inInt.set( 5 )											# this should work though
		self.failUnless( s1.inInt.get( 0 ) == 5 )					# should be cached 
		s1.inInt.clearCache()
		
		self.failUnlessRaises( MissingDefaultValueError, s1.inInt.get, 0 )	# cache is gone
		self.failUnless( s1.inFloat.get( 0 ) == 2.5 )
		self.failUnlessRaises( NotWritableError, s1.inFloat.set, "this" )
		
		myint = s1.outRand.get( 0 )		# as it is cached, the value should repeat
		self.failUnless( s1.outRand.hasCache() )
		self.failUnless( s1.outRand.get( 0 ) == myint )
		s1.outRand.plug.attr.flags &= Attribute.uncached
		
		
		# CONNECTIONS
		##############
		s2 = SimpleAttrs()
		s3 = SimpleAttrs()
		s1.outRand.connect( s2.inFloat )
		s1.outRand.connect( s2.inFloat )		# works as it is already connected to what we want
		
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
		self.failUnlessRaises( ComputeError, s3.outMult.get, 0 )	
		
		# set in int and it should work
		s2.inInt.set( 4 )
		self.failUnless( s3.outMult.get( 0 ) == 10 )	# 2.5 * 4
		
		# make the float writable 
		s1.inFloat.plug.attr.flags |= A.writable
		s1.inFloat.set( 2.0 )
		self.failUnless( s3.outMult.get( 0 ) == 8 )	# 2.0 * 4
		
		
