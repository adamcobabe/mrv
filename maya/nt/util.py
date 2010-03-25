# -*- coding: utf-8 -*-
"""General utility methods"""
__docformat__ = "restructuredtext"

import maya.OpenMaya as api
import mrv.maya.undo as undo

MScriptUtil = api.MScriptUtil
#{ Decorators

#} END decorators


#{ Conversion Methods
def in_double3_out_vector(function):
	"""
	:return: MVector containing result of function with signature 
		function(double [3])"""
	su = MScriptUtil()
	su.createFromDouble(0.0, 0.0, 0.0)
	ptr = su.asDoublePtr()
	function(ptr)
	
	return api.MVector(su.getDoubleArrayItem(ptr,0), su.getDoubleArrayItem(ptr,1), su.getDoubleArrayItem(ptr,2))

def in_two_floats_out_tuple(function):
	"""
	:return: tuple containing result of function with signature 
		function(float& f1, float& f2)"""
	suf1 = MScriptUtil()	# keep it, otherwise it might deinitialize its memory
	suf2 = MScriptUtil()
	pf1 = suf1.asFloatPtr()
	pf2 = suf2.asFloatPtr()
	
	function(pf1, pf2)
	
	return (MScriptUtil.getFloat(pf1), MScriptUtil.getFloat(pf2))

def in_double3_as_vector(function, vec_value):
	"""Set the value in vec_value to passed in function as double [3] and 
	return the result"""
	su = MScriptUtil()
	su.createFromList([vec_value.x, vec_value.y, vec_value.z], 3)
	ptr = su.asDoublePtr()
	return function(ptr)
	

def undoable_in_double3_as_vector(function, vec_old_value, vec_new_value):
	"""function supports the signature function(double [3] const) and will 
	change the underlying instance to the respective values as retrieved 
	from the passed in vector.
	The calling method must be enclosed in an undoable decorator.
	
	:param vec_old_value: vector with the old value of the corresponding getX method
	:param vec_new_value: vector with new value that is to be set"""
	op = undo.GenericOperation()
	op.setDoitCmd( in_double3_as_vector, function, vec_new_value)
	op.setUndoitCmd( in_double3_as_vector, function, vec_old_value )
	return op.doIt()
	

#}END conversion methods


#{ Utility Classes
class MFnEnumeration(list):
	"""Simple enumeration class which allows access to its enumeration using 
	getattr access. 
	As it is a list as well, one can access the enumeration values in the right sequencial
	order as well"""
	def __init__(self, name):
		self.name = name
		
	def __str__(self):
		return self.name
	
	def __repr__(self):
		return "MFnEnumeration(%s)" % self.name
	
	#{ Interface
	
	def nameByValue(self, value):
		""":return: name string with the given integer value
		:param value: integer value of this enumeration
		:raise ValueError: if value is not in the enumeration"""
		for n,v in self.__dict__.items():
			if n.startswith('k') or not isinstance(v, int):
				continue
				
			if v == value:
				return n
			# END if value matches
		# END for each item in our dict
		raise ValueError("Value %i not in enumeration" % value)
		
	#} END interface
#} END utility classes
