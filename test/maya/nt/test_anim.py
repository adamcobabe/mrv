# -*- coding: utf-8 -*-
""" Test animCurves and related types """
from mrv.test.maya import *

import mrv.maya as mmaya
import mrv.maya.nt as nt

import maya.OpenMaya as api
import maya.OpenMayaAnim as apianim



class TestAnim( unittest.TestCase ):
	def test_anim_overrides(self):
		# create test anim curve
		p = nt.Node('persp')
		anim_curve = nt.anim.apianim.MFnAnimCurve().create(p.rx)
		assert isinstance(anim_curve, nt.api.MObject)		
		
		# test mfn wrapping
		anim_curve = nt.Node(anim_curve)
		assert anim_curve.numKeyframes() == 0
		
		# assure we are connected to the plug, for curiousity
		assert p.rx in anim_curve.output.moutputs()
		assert p.ry not in anim_curve.output.moutputs()
		
		# set key
		anim_curve.setIsWeighted(True)
		anim_curve.addKeyframe(nt.api.MTime(-1.0), 5.0)
		anim_curve.addKeyframe(nt.api.MTime(1.0), 10.0)
		assert anim_curve.numKeyframes() == 2
		
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
		
	def test_get_animation( self ):
		mmaya.Scene.new(force=True)
		p = nt.Node("persp")
		
		# translate is animated
		for tc in p.translate.mchildren():
			apianim.MFnAnimCurve().create(tc)	
		# END set animation
		
		# test animation iteration
		for converter in (lambda x: x, lambda x: nt.toSelectionList(x)):
			for as_node in range(2):
				nc = 0
				target_type = nt.api.MObject
				if as_node:
					target_type = nt.Node
				# END define target type
				for anode in nt.AnimCurve.findAnimation(converter([p]), as_node):
					assert isinstance(anode, target_type)
					nc += 1
				# END for each anim node
				assert nc == 3
			# END for each as_node mode
		# END for each converter
		
		
		
	
