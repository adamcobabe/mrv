# -*- coding: utf-8 -*-
""" Contains all exceptions used by the mrv package in general """

class MrvError( Exception ):
	""" Base Class for all exceptions that the mrv framework throws"""
	def __init__(self, *args, **kwargs):
		self._message = ""
		if args and isinstance(args[0], basestring):
			self._message = args[0]
			args = args[1:]
		# END args and message handling
		Exception.__init__(self,*args, **kwargs)
	
	def _get_message(self): 
		return self._message
	def _set_message(self, message): 
		self._message = message
	message = property(_get_message, _set_message)


#{Decorator Exceptions
class MethodTypeError( TypeError, MrvError ):
	""" Indicates that a method either produced or returned a type that was not anticipated """
	pass

class InterfaceError( TypeError, MrvError ):
	""" Indicates that an instances interface does not fully match the requrested interface """
	pass
#}

#{ Decorator Internal Exceptions
class DecoratorError( MrvError ):
	""" Thrown if decorators are used in an incorrect way
	@note: this can only happen if decorators take arguments that do not resolve as
	requested
	@todo: store actual function that caused the error """
	pass

class InterfaceSetupError( MrvError ):
	""" Thrown if L{interface} attributes are used incorrectly
		- only and ignore are both given, although they are mutually exclusive """
	pass

class TypecheckDecoratorError( DecoratorError ):
	""" Thrown if a typecheck_param decorator encounters an incorrect argument
	specification for the given method """
	pass

class ProtectedMethodError( DecoratorError ):
	""" Thrown if a 'protected' decorator detects a non-subclass calling a protected method"""
	pass

#}
