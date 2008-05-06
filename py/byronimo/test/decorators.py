"""B{byronimo.test.decorators}
Test all aspects of decorators

	- use test classes and run test on their possibly decorated functions

@note: decorator tests will always succeed if NOT in debug mode ( as custom decorators are
deactivated in that case

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import sys
from byronimo.exceptions import *


class TestTypecheckDecorators( unittest.TestCase ):
	
	def _check_decorator_exceptions( self, c, iskv=False ):
		# each of these should fail with a type error
		args = [ ( "wantsDummyDerived", Dummy() ), ( "wantsDummy", "string" ) ]
		for method, arg in args:
			args = [ arg ]
			kvargs = {}
			callmethod = method
			
			if iskv:
				callmethod = method+'kv'
				kvargs['dum'] = arg
				args = []
				
			# finally make call
			self.failUnlessRaises( MethodTypeError, getattr( c, callmethod ), *args, **kvargs )

	
	def test_typecheck_param_args( self ):
		"""Decorators: Assure that the typecheck param is able to send type error exceptions """
		# these should work
		c = _TypecheckClass()
		c.wantsDummyDerived( DummyDerived() )
		c.wantsDummy( Dummy() )
		c.wantsDummykv( dum=Dummy() )
		c.wantsDummyDerivedkv( dum=DummyDerived() )
		
		
		# each of these should fail with a type error
		self._check_decorator_exceptions( c, iskv=False )
		self._check_decorator_exceptions( c, iskv=True )

	def test_typecheck_param_misspelledkvarg( self ):
		"""Decorators: Assure that people do not set kv type checks that do not match any actual method variable """
		try:
			_TypecheckClass().wantsDummyDerivedMisspelledkv( dum=DummyDerived() )
		except TypecheckDecoratorError:
			#print( "Success: Cought: " + str( sys.exc_value) )
			pass
		except:
			raise
		else:
			self.fail()
		
			
	def test_typecheck_rval( self ):
		"""Decorators: Assure that the rval test decorator is able to catch these kinds of  type errors  """
		method_names = [ 'return_int', 'return_complex' ]
		
		# these should work 
		c = _TypecheckClass()
		for method in method_names:
			try:
				getattr( c, method )( )
			except:
				raise
		
		# these should fail with appropriate exception 
		for method in method_names:
			try:
				getattr( c, method+'_bad' )( )
			except MethodTypeError:
				# print( "Success: Cought: " + str( sys.exc_value) )
				pass
			except: 
				raise # something else went wrong
			else:
				self.fail()	# we need an exception here !
				
	
		
	def test_typecheck_combined( self ):
		"""Decorators: Tests whether methods using both, rval and parameter type checking works as expected """
		c = _TypecheckClass() 
		# this one should work
		c.return_and_param( 2 )
		
		# incorrect rval
		self.failUnlessRaises( MethodTypeError, getattr( c, 'return_and_param_badrval' ), 2 )
		
		# incorrect parameter type
		self.failUnlessRaises( MethodTypeError, getattr( c, 'return_and_param_badrval' ), "wrongtype" )
		
######################		
# HELPER CLASSES ###
##################
			
class Dummy( object ):
	""" A new type for type checking """
	
	def sayHello( self ):
		# print "hello"
		pass 
	
		
class DummyDerived( Dummy ):
	""" A new type for type checking """
	
	def sayHello( self ):
		# print "helloDerived"
		pass
		
		
class _TypecheckClass( object ):
	""" Class using the typecheck_param decorator """
	

#{Parameter Type Check Support 
	@typecheck_param( object, DummyDerived )
	def wantsDummyDerived( self, dum ):
		return dum.sayHello()

	@typecheck_param( object, Dummy )
	def wantsDummy( self, dum ):
		dum.sayHello()
	

	@typecheck_param( object, dum=Dummy )
	def wantsDummykv( self, dum=None ):
		dum.sayHello()
	
	
	@typecheck_param( object, dum=DummyDerived )
	def wantsDummyDerivedkv( self, dum=None ):
		dum.sayHello()
		
	
	@typecheck_param( object, dumMisspelled=DummyDerived )
	def wantsDummyDerivedMisspelledkv( self, dum=None ):
		dum.sayHello()
		
		
#{Return Value Type Check Support 
	@typecheck_rval( int )
	def return_int( self ):
		return 2		
		
	@typecheck_rval( int )
	def return_int_bad( self ):
		return None
		
	@typecheck_rval( ( int, Dummy, [ str ], { 'a' : dict } ) )
	def return_complex( self ):
		return ( 2, DummyDerived(), [ "abc" ], { 'a' : { 'b' : 2 } } )
		
	@typecheck_rval( ( int, Dummy, [ str ], { 'a' : dict } ) )
	def return_complex_bad( self ):
		return ( 2, Dummy(), [ "abc" ], { 'a' : [1,2] } )

#{Return Value and Parameter Type Check Support		
	@typecheck_rval( str ) 
	@typecheck_param( object, int )
	def return_and_param( self, integer ):
		return "string" * integer
		
	@typecheck_rval( str ) 
	@typecheck_param( object, int )
	def return_and_param_badrval( self, integer ):
		return integer
		
