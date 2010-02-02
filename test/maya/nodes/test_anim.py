# -*- coding: utf-8 -*-
"""
Test animCurves and related types
"""
__license__='MIT License'
__copyright__='(c) 2010 Sebastian Thiel'

import unittest
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
		
		anim_curve.setOutTangentType(0, 4)
		anim_curve.setTangent(0, 3.0, 4.0, False)
		
		# test method overrides 
		for isInTangent in range(2):
			for index in range(anim_curve.numKeyframes()):
				rval = anim_curve.getTangent(index, isInTangent)
				assert isinstance(rval, tuple) and len(rval) == 2
				print rval
			# END for each keyindex
		# END for each isInTangent value
		
