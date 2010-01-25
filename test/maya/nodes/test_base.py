# -*- coding: utf-8 -*-
"""Test basic node features """

import unittest
import mayarv.maya as bmaya
import mayarv.maya.nodes as nodes
import maya.OpenMaya as api
import maya.cmds as cmds

class TestTransform( unittest.TestCase ):
	
	def test_tranformation_overrides(self):
		p = nodes.Node('persp')
		getters = ('getScale', 'getShear')
		setters = ('setScale', 'setShear')
		def cmp_val(lhs, rhs, loose):
			if loose:
				assert lhs != rhs
			else:
				assert lhs == rhs
		# END util
		
		def assert_values(fgetname, fsetname, loose):
			getter = getattr(p, fgetname)
			v = getter()
			assert isinstance(v, api.MVector)
			
			nv = api.MVector(i+v.x+1.0, i+v.y+2.0, i+v.z+3.0)
			getattr(p, fsetname)(nv)
			
			cmp_val(nv, getter(), loose)
			
			cmds.undo()
			cmp_val(v, getter(), loose)
			cmds.redo()
			cmp_val(nv, getter(), loose)
		# END utility
		
		for i,(fgetname, fsetname) in enumerate(zip(getters, setters)):
			assert_values(fgetname, fsetname, loose=False)
		# END for each fname
		
		setters = ("scaleBy", "shearBy")
		for i,(fgetname, fsetname) in enumerate(zip(getters, setters)):
			assert_values(fgetname, fsetname, loose=True)
		# END for each name
