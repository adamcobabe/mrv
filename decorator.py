# -*- coding: utf-8 -*-
"""
Contains all decorator functions

Decorators are used to
	- check method parameter types for compatibility
	- check parameter value prequesites
	- check return types
	- enable special checking during debugging

@warn: all methods without a leading underscore will be made available as decorators
@NOTE: All decorators will return unaltered methods if the DEBUG mode is not enabled



"""

__author__='$Author$'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'


import sys

from exc import ( 	TypecheckDecoratorError,
					MethodTypeError,
					InterfaceError,
					InterfaceSetupError,
					ProtectedMethodError)

class __classobjtype( object ):
	""" Required to find out whether something is a classobj

	Some old classes are not derived from object, and are always type 'classobj'
	if typed. This object type though is supposed to be in __builtin__ namespace, but
	it acutally isnt. Thus I create my own dummy class to be able to compare
	against and check for this type.

	One can also check for __class__ members here which appears to be one of the
	markers for new style classes """
	pass


def _getactualtype( definetype ):
	"""@param definetype: an instance of type L{interface}, a classobj or a type
	@return: a type that can be handled properly by L{_checktype} """
	# THIS APPEARS TO ONLY WORK FOR PYTHON version 2.5 or higher
	if sys.version_info[1] > 4:
		if type( __classobjtype ) != type( definetype ) and not isinstance( definetype, type ):
			return type( definetype )
	return definetype


def _checktype( arg, argpos, definetype, *exc_addargs ):
	""" check whether the type of arg is correct """
	# definetype could be an instace of list, tuple or dict - get the proper type
	# special interface ?
	if isinstance( definetype, interface ):
		definetype.compare( arg )
	else:
		definetype = _getactualtype( definetype )
		if not isinstance( arg, definetype ):
			m = "arg at pos %s defined as %s, but was %s" % ( str(argpos), str( definetype ), str( type( arg ) ) )
			raise MethodTypeError( m, *exc_addargs )


class interface( object ):
	""" Simple command class allowing to compare interface with each other """
	def __init__( self, ref_interface, ignore=[], only=[], add=[] ):
		""" Keep the reference interface for later comparison
		@param ref_interface: the reference interface the later instance has to match with
		@param ignore: functions in reference interface that do not need a match
		@param only: only check these functions of ref_interface, ignore the others
		@param add: add the given method names to the ones being required
		@raise InterfaceSetupError:  """
		if len( only ) and ( len( ignore ) or len( add ) ):
			raise InterfaceSetupError( '( ignore or add ) and only keys are mutually exclusive' )

		self.ref_interface = ref_interface
		if len( only ):
			self.match_names = only
		else:
			self.match_names = [ attr for attr in ref_interface.__dict__.iterkeys() if not attr.startswith( '_' ) ]
		self.ignore_names = ignore

	def compare( self, instance ):
		""" Compare the interface of instance with the stored reference interface

		Currently, this will try to find all functions in the reference interface in
		the instance's interface

		@raise InterfaceError: if at least one function cannot be found """
		missing = []
		instattrs = dir( instance )
		for funcname in self.match_names:
			if not funcname in instattrs and not funcname in self.ignore_names:
				missing.append( funcname )

		if len( missing ):
			m = "instance %s does not support %s interface because of missing functions" % ( str( _getactualtype( instance ) ), self.ref_interface )
			raise InterfaceError( m, missing )



def __methodtypecheck( type_signature, rval_inst, index=0 ):
	""" compare the concrete rval type with the target_type
	@param type_signature: an iterator of types or simple type
	@param rval_inst: returned value of func, usually a concrete class instance
	or iterable
	@param index: if this method gets called, you can leave information about the index
	of the type signature that is the basis for the call ( used in neseted structures )
	@note: raises if the types do not match """
	# check for iterators
	try:
		# is dict ?
		if isinstance( type_signature, dict ):
			_checktype( rval_inst, index, dict )
			try:
				for k in type_signature:
					__methodtypecheck( type_signature[k], rval_inst[k] )
			except KeyError:
				raise MethodTypeError( "Key %s not found in rval" % k, rval_inst )
		# is iterable ( but NO dict ) ?
		elif isinstance( type_signature, ( list , tuple ) ):
			# the other item must be an iterator type
			if not isinstance( rval_inst, ( list, tuple ) ):
				m = "Signature required iterator, rval instance is not iterable"
				raise MethodTypeError( m, type_signature, rval_inst )

			if len( type_signature ) != len( rval_inst ):
				m = "Lengths of signature and rval iterable did not match"
				raise MethodTypeError( m, type_signature, rval_inst )

			rval_iter = iter( rval_inst )
			for i in xrange( 0, len( type_signature ) ):
				__methodtypecheck( type_signature[i], rval_iter.next(), index=i )
		# is scalar value
		else:
			_checktype( rval_inst, index, type_signature, rval_inst )
	except LookupError,TypeError:
		raise MethodTypeError( "The signature type had an unsupported format - use ony simple types, lists and dicts" )


#{ Typecheck Helper Classes
class TypeBase( object ):
	""" Class defining base interface ( command pattern ) for all types allowing
		simple type comparison

		Allows definition of: type should equal one of ( ... ), or one or more of ( ... )
		This equals regular expressions for types.

		TypeClasses can be freely combined
		@todo: implementation - this will be kind of slow - perhaps this is why it will never be done ... """
	pass


#} END GROUP

#{ Typecheck Decorators
def typecheck_param( *args, **kwargs ):
	"""Assure parameters have expected type before using them

	Python does not offer compile time type checking but moves it into the runtime.
	Usually this is indicated by error like "None type does not support method ... "

	This decorator assures that the named or listed parameters actually support the type
	required.

	@param args: list of existing typenames of unnamed method parameters, like
	[ object, int, string ]
	@note: each arg, even self, requires a type class - type definitions can be deeply nested

	@param kwargs: dict of named parameters with their associated types, like
	{ x : int, z : myclass }
	@note: you can supply the types for the keyword args of your choice - make sure
	that the dict's key names actually match the variable names

	@return: A function that takes a function object and applies the typechecking
	as implied by our *args and **kwargs parameters.

	@raise MethodTypeError:
	@raise TypecheckDecoratorError: inidcates incorrect decorator usage
	@note: Will only work in debug mode - otherwise the method will be returned
	unaltered"""
	def _dotypecheck( func ):
		# if not debug mode return func
		argtypelist = args
		argtypedict = kwargs

		# assure that the args are correct for our function !
		ndefaultargs = func.func_defaults and len( func.func_defaults ) or 0
		numargs = func.func_code.co_argcount - ndefaultargs
		if len( args ) != numargs:
			m = "%i of %i args of method '%s' decorated with type" % ( len( args ), numargs, func.func_name )
			raise TypecheckDecoratorError( m )


		def _inner_dotypecheck( *args, **kwargs ):
			""" Does actual runtime type check """

			if len( args ) != len( argtypelist ):
				raise TypecheckDecoratorError( "Mismatching argument count( %i of %i )" % ( len(args), len( argtypelist ) ) )

			# check args - its garantued that we have at least as many types as arglists
			for i in xrange( 0, len( argtypelist ) ):
				__methodtypecheck( argtypelist[i], args[i], index=i )

			# check kwargs
			numkeysunmatched = 0
			for k in argtypedict.iterkeys():
				if not k in kwargs:
					numkeysunmatched += 1
				else:
					__methodtypecheck( argtypedict[k], kwargs[k], index=k )

			# assure the dict is (still) correct
			if numkeysunmatched:
				m = "Found %i unmatched type keys in function %s" % ( numkeysunmatched, func.func_name )
				raise TypecheckDecoratorError( m )

			# finally call actual function
			return func( *args, **kwargs )


		# make sure names match
		_inner_dotypecheck.func_name = func.func_name
		return _inner_dotypecheck


	return _dotypecheck




def typecheck_rval( rval_type ):
	"""compare the actual methods return value with the given return value signature

	This check is supposed to assure that the return value conforms to one of the
	given return value types. Thus one of the given rval types must match for the
	method to succeed.

	@param rval_type: A list of any combination of iterables or dicts and 'type' references,
	each of them indicating one of the return types that can be expected by the method.

			1. E{@}typecheck_rval( int )
			- expects a simple integer as return value
		2. E{@}typecheck_rval( int, string )
			- expects a an int or string as return value
		3. E{@}typecheck_rval( (int,string,myclass),None )
			- expects a tuple with members int,string,myclass or None
		4. E{@}typecheck_rval( {a=int,b=string,c=myclass} )
			- expects a dict to be returned with keys holding classes of the given types

	@note: its discouraged to create methods with more than one possible return types
	as they are harder to use and more error prone.

	@raise MethodReturnTypeError:
	@note: will not apply if NOT in DEBUG mode """
	# decorator check: assure that all rvals are actually types, and not values
	def __deco_typecheck( type_signature ):
		""" @note: could possible get into loop if there are cyclic references """
		if isinstance( type_signature, dict ):
			for k in type_signature:
				__deco_typecheck( type_signature[k] )
		elif isinstance( type_signature, ( list , tuple ) ):
			for item in type_signature:
				__deco_typecheck( item ) # its a nested iterable - check its members
		else:
			if type( type_signature ) is not type:
				m = "%s is an instance, but needs to be a type" % str( type_signature )
				raise TypecheckDecoratorError( m )


	__deco_typecheck( rval_type )

	# create a wrapper method that actually does the job
	def _dorvaltypecheck( func ):

		# make the requested rval types available to the worker function
		requ_type = rval_type

		# does the actual work
		def _inner_dorvaltypecheck( *args, **kwargs ):
			""" Called instead of the actual function that it wrappes """
			rval = func( *args, **kwargs )

			# do the check
			__methodtypecheck( requ_type, rval )

			return rval

		# adjust name
		_inner_dorvaltypecheck.func_name = func.func_name
		return _inner_dorvaltypecheck

	# this returned method will be called during decorator initialization
	return _dorvaltypecheck


#} END GROUP


def protected( exactClass ):
	"""Raise an exception if self is an instance of exacATtClass, and not a subclass of it
	@raise ProectedMethodError:
	@note: method must take self as first argument, thus must be a class method """
	def _protectedCheck( func ):

		def _inner_protectedCheck( self, *args, **kwargs ):
			if self.__class__ == exactClass:
				raise ProtectedMethodError( "Cannot instantiate" + self.__class__.__name__ + " directly - it can only be a base class" )

			return func( self, *args, **kwargs )

		# return method actually doing the work
		return _inner_protectedCheck

	return _protectedCheck
