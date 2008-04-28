"""B{byronimo.exceptions}

Contains all exceptions used by the byronimo package in general 

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


class ByronimoError( Exception ):
	""" Base Class for all exceptions that the byronimo framework throws"""
	pass

	

#{Decorator Exceptions
class MethodTypeError( TypeError, ByronimoError ):
	""" Indicates that a method either produced or returned a type that was not anticipated """
	pass

#}

#{ Decorator Internal Exceptions 
class DecoratorError( ByronimoError ):
	""" Thrown if decorators are used in an incorrect way
	@note: this can only happen if decorators take arguments that do not resolve as 
	requested
	@todo: store actual function that caused the error
	"""
	pass

class TypecheckDecoratorError( DecoratorError ):
	""" Thrown if a typecheck_param decorator encounters an incorrect argument 
	specification for the given method
	"""
	pass
	
	
#}