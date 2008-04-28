"""B{byronimo.decorators}

Contains all decorator functions 

Decorators are used to 
	- check method parameter types for compatibility
	- check parameter value prequesites
	- check return types
	- enable special checking during debugging

@warn: all methods without a leading underscore will be made available as decorators
@NOTE: All decorators will return unaltered methods if the DEBUG mode is not enabled
@see: L{byronimo.test.decorators}
@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='you@somedomain.tld'
__version__=1
__license__='GPL'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"

from byronimo.exceptions import TypecheckDecoratorError, MethodTypeError






def __checktype( arg, argpos, definetype, *exc_addargs ):
	""" check whether the type of arg is correct """
	actualtype = isinstance( definetype, type ) and definetype or type( definetype )
	if not isinstance( arg, actualtype ):
			m = "arg at pos %s defined as %s, but was %s" % ( str(argpos), str( actualtype ), str( type( arg ) ) )
			raise MethodTypeError( m, *exc_addargs )
		


def __methodtypecheck( type_signature, rval_inst, index=0 ):
	""" compare the concrete rval type with the target_type
	@param type_signature: an iterator of types or simple type
	@param rval_inst: returned value of func, usually a concrete class instance
	or iterable
	@param index: if this method gets called, you can leave information about the index
	of the type signature that is the basis for the call ( used in neseted structures )
	@note: raises if the types do not match
	"""
	# check for iterators
	try:
		# is dict ?
		if isinstance( type_signature, dict ):
			__checktype( rval_inst, index, dict )
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
			__checktype( rval_inst, index, type_signature, rval_inst )
	except LookupError,TypeError:
		raise MethodTypeError( "The signature type had an unsupported format - use ony simple types, lists and dicts" )


#{ Typecheck Helper Classes
class TypeBase( ):
	""" Class defining base interface ( command pattern ) for all types allowing
		simple type comparison
		
		Allows definition of: type should equal one of ( ... ), or one or more of ( ... )
		This equals regular expressions for types.
		
		TypeClasses can be freely combined
		@todo: implementation - this will be kind of slow - perhaps this is why it will never be done ...
	"""
	pass 


#} END GROUP
		
#{ Typecheck Decorators 		
def typecheck_param( *args, **kvargs ):
	"""Assure parameters have expected type before using them 
	
	Python does not offer compile time type checking but moves it into the runtime.
	Usually this is indicated by error like "None type does not support method ... "
	
	This decorator assures that the named or listed parameters actually support the type
	required.
	
	@param args: list of existing typenames of unnamed method parameters, like
	[ object, int, string ]
	@note: each arg, even self, requires a type class - type definitions can be deeply nested
	
	@param kvargs: dict of named parameters with their associated types, like
	{ x : int, z : myclass }
	@note: you can supply the types for the keyword args of your choice - make sure
	that the dict's key names actually match the variable names
	
	@return: A function that takes a function object and applies the typechecking
	as implied by our *args and **kvargs parameters.
	
	@raise MethodTypeError: 
	@raise TypecheckDecoratorError: inidcates incorrect decorator usage
	@note: Will only work in debug mode - otherwise the method will be returned
	unaltered
	@see: L{byronimo.test.decorators.TestTypecheckDecorators}
	"""
	def _dotypecheck( func ):
		# if not debug mode return func
		argtypelist = args
		argtypedict = kvargs
		
		# assure that the args are correct for our function !
		ndefaultargs = func.func_defaults and len( func.func_defaults ) or 0
		numargs = func.func_code.co_argcount - ndefaultargs
		if len( args ) != numargs:
			m = "%i of %i args of %s decorated with type" % ( len( args ), numargs, func.func_name )
			raise TypecheckDecoratorError( m )
		
		
		def _inner_dotypecheck( *args, **kvargs ):
			""" Does actual runtime type check """			
			
			# check args - its garantued that we have at least as many types as arglists
			for i in xrange( 0, len( argtypelist ) ):
				__methodtypecheck( argtypelist[i], args[i], index=i ) 
					
			# check kvargs
			numkeysunmatched = 0
			for k in argtypedict.iterkeys():
				if not k in kvargs:
					numkeysunmatched += 1
				else:
					__methodtypecheck( argtypedict[k], kvargs[k], index=k )
					
			# assure the dict is (still) correct
			if numkeysunmatched:
				m = "Found %i unmatched type keys in function %s" % ( numkeysunmatched, func.func_name )
				raise TypecheckDecoratorError( m )
			
			# finally call actual function
			return func( *args, **kvargs )
			
			
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
	
	B{Examples}
		1. E{@}typecheck_rval( int )
			- expects a simple integer as return value
		2. E{@}typecheck_rval( int, string )
			- expects a an int B{or} string as return value
		3. E{@}typecheck_rval( (int,string,myclass),None )
			- expects a tuple with members int,string,myclass B{or} None
		4. E{@}typecheck_rval( {a=int,b=string,c=myclass} )
			- expects a dict to be returned with keys holding classes of the given types
			
	@note: its discouraged to create methods with more than one possible return types
	as they are harder to use and more error prone.
	
	@raise MethodReturnTypeError: 
	@note: will not apply if NOT in DEBUG mode
	"""
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
		def _inner_dorvaltypecheck( *args, **kvargs ):
			""" Called instead of the actual function that it wrappes """
			rval = func( *args, **kvargs )
			
			# do the check
			__methodtypecheck( requ_type, rval )
				
			return rval
			
		# adjust name
		_inner_dorvaltypecheck.func_name = func.func_name
		return _inner_dorvaltypecheck
		
	# this returned method will be called during decorator initialization
	return _dorvaltypecheck
	
	
#} END GROUP
