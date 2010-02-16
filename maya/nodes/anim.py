# -*- coding: utf-8 -*-
"""
Contains implementations of animation specific types and utilities
"""


import base
import maya.OpenMaya as api
import maya.OpenMayaAnim as manim
import util

class AnimCurve( base.DependNode ):
	"""Type representing a maya animation cuvrve, fixes existing MFnAnimCurve
	methods and provides new convenience methods as well"""
	
	def getTangent( self, index, isInTangent ):
		"""@return: tuple(x,y) tuple containing the x and y positions of the 
		tangent at index.
		x is the x value of the slope of the tangent in seconds
		y is the absolute y value of the slope of the tangent
		@param index: Index of the key for which the tangent x,y value is required
		@param isInTangent: If true, the in-tangent is returned, else, the out-tangent is returned"""
		return util.in_two_floats_out_tuple(lambda x, y: self._api_getTangent(index, x, y, isInTangent))
		
	def getTangentAsAngle(self, index, isInTangent):
		"""@return: tuple(MAngle, weight) tuple containing the angle and weight of
		the tangent. 
		@param *args, **kwargs: See L{getTangent}"""
		sud = api.MScriptUtil()
		pd = sud.asDoublePtr()
		a = api.MAngle()
		
		self._api_getTangent(index, a, pd, isInTangent)
		return (a, sud.getDouble(pd))
	
