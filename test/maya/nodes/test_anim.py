# -*- coding: utf-8 -*-
"""
Test animCurves and related types
"""
from mayarv.test.maya import *

import maya.OpenMaya as api
import maya.OpenMayaAnim as manim

import mayarv.maya as mrvmaya
import mayarv.maya.nodes as nodes



class TestAnim( unittest.TestCase ):
	def test_anim_overrides(self):
		# create test anim curve
		p = nodes.Node('persp')
		anim_curve = nodes.anim.manim.MFnAnimCurve().create(p.rx)
		assert isinstance(anim_curve, nodes.api.MObject)		
		
		# test mfn wrapping
		anim_curve = nodes.Node(anim_curve)
		assert anim_curve.getNumKeyframes() == 0
		
		# assure we are connected to the plug, for curiousity
		assert p.rx in anim_curve.output.p_outputs
		assert p.ry not in anim_curve.output.getOutputs()
		
		# set key
		anim_curve.setIsWeighted(True)
		anim_curve.addKeyframe(nodes.api.MTime(-1.0), 5.0)
		anim_curve.addKeyframe(nodes.api.MTime(1.0), 10.0)
		assert anim_curve.getNumKeyframes() == 2
		
		# test method overrides 
		
		for index in range(anim_curve.numKeyframes()):
			for isInTangent in range(2):
				rval = anim_curve.getTangent(index, isInTangent)
				assert isinstance(rval, tuple) and len(rval) == 2
				assert rval[0] != 0.0 and rval[1] != 0.0
				
				rval = anim_curve.getTangentAsAngle(index, isInTangent)
				assert len(rval) == 2
				assert isinstance(rval[0], api.MAngle)
				assert rval[0].value() != 0.0 and rval[1] != 0.0
			# END for each isInTangent value
		# END for each keyindex
		
		
		# save_for_debugging('anim')
		
	def test_get_animation( self ):
		mrvmaya.Scene.new(force=True)
		p = nodes.Node("persp")
		
		# translate is animated
		for tc in p.translate.getChildren():
			manim.MFnAnimCurve().create(tc)	
		# END set animation
		
		# test animation iteration
		for converter in (lambda x: x, lambda x: nodes.toSelectionList(x)):
			for as_node in range(2):
				nc = 0
				target_type = nodes.api.MObject
				if as_node:
					target_type = nodes.Node
				# END define target type
				for anode in nodes.AnimCurve.getAnimation(converter([p]), as_node):
					assert isinstance(anode, target_type)
					nc += 1
				# END for each anim node
				assert nc == 3
			# END for each as_node mode
		# END for each converter
		
		
		
	
