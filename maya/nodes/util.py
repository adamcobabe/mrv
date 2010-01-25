# -*- coding: utf-8 -*-
"""General utility methods"""
import maya.OpenMaya as api
import mayarv.maya.undo as undo
#{ Decorators

#} END decorators


#{ Conversion Methods
def in_double3_out_vector(function):
	"""@return: MVector containing result of function with signature 
	function(double [3])"""
	su = api.MScriptUtil()
	su.createFromDouble(0.0, 0.0, 0.0)
	ptr = su.asDoublePtr()
	function(ptr)
	
	return api.MVector(su.getDoubleArrayItem(ptr,0), su.getDoubleArrayItem(ptr,1), su.getDoubleArrayItem(ptr,2))

def in_double3_as_vector(function, vec_value):
	"""Set the value in vec_value to passed in function as double [3] and 
	return the result"""
	su = api.MScriptUtil()
	su.createFromList([vec_value.x, vec_value.y, vec_value.z], 3)
	ptr = su.asDoublePtr()
	return function(ptr)
	

def undoable_in_double3_as_vector(function, vec_old_value, vec_new_value):
	"""function supports the signature function(double [3] const) and will 
	change the underlying instance to the respective values as retrieved 
	from the passed in vector.
	The calling method must be enclosed in an undoable decorator.
	@param vec_old_value: vector with the old value of the corresponding 
	getX method
	@param vec_new_value: vector with new value that is to be set"""
	op = undo.GenericOperation()
	op.addDoit( in_double3_as_vector, function, vec_new_value)
	op.addUndoit( in_double3_as_vector, function, vec_old_value )
	return op.doIt()
	

#}END conversion methods
