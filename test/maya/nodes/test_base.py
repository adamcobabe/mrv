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
		
	def test_doc_examples(self):
		from mayarv.maya.nodes import *
		import __builtin__
		
		# NODES
		#######
		p = Node("persp")
		t = Node("time1")
		assert p == p
		assert p != t
		assert p in [p]
		
		s = __builtin__.set()
		s.add(p)
		s.add(t)
		assert p in s and t in s and len(s | s) == 2
		
		# getApiObject returns the api object which represents the underlying maya node best
		assert isinstance(p.getApiObject(), api.MDagPath)
		assert isinstance(t.getApiObject(), api.MObject)
		
		# api types
		assert isinstance(p, Transform) and p.getApiType() == api.MFn.kTransform
		assert isinstance(t, Time) and t.getApiType() == api.MFn.kTime
		assert p.hasFn(p.getApiType())
		
		# get the MObject repreentation
		assert isinstance(p.getMObject(), api.MObject) and isinstance(t.getMObject(), api.MObject)
		
		# DagNodes have a DagPath as well
		assert p.getDagPath() == p.getMDagPath()
		assert isinstance(p.getDagPath(), DagPath) and not isinstance(p.getMDagPath(), DagPath)
		
		
		# METHODS
		#########
		self.failUnlessRaises(AttributeError, getattr, p, 'doesnt_exist')
		
		assert p.getName == p.name
		
		assert isinstance(p.getMFnClasses(), list)
		
		# DAG NAVIGATION
		################
		ps = p.getChildren()[0]
		assert ps == p[0]
		assert ps[-1] == p
		
		assert ps == p.getShapes()[0]
		assert ps.getParent() == p == ps.getTransform()
		
		# filtering
		assert len(p.getChildrenByType(Transform)) == 0
		assert p.getChildrenByType(Camera) == p.getChildrenByType(Shape)
		
		# deep and iteration
		assert ps.iterParents().next() == p == ps.getRoot()
		assert ps.getParentDeep()[0] == p
		assert p.getChildrenDeep()[0] == ps
		
		
