# -*- coding: utf-8 -*-
"""Performance Testing"""
from mrv.test.maya import *

import mrv.maya.nt as nt
import time
import sys

class TestSetsPerformance( unittest.TestCase ):
	
	@with_scene('mesh40k.mb')
	def test_set_assignments(self):
		m = nt.Node('mesh40k')
		isb = nt.ShadingEngine()
		
		for ignore_failure in range(2):
			if ignore_failure > 0:
				isb.removeMember(m, m.cf[:])
			# END initial assignment clearing
			
			# IntArray
			np = m.numPolygons()
			st = time.time()
			isb.addMember(m, m.cf[:np], ignore_failure=ignore_failure)
			elapsed = time.time() - st
			
			print >>sys.stderr, "Assigned %i polygons (IntArray, ignore_failure=%i) in %f s ( %f polys/s )" % (np, ignore_failure, elapsed, np/elapsed)
			
			# remove with complete data
			st = time.time()
			isb.removeMember(m, m.cf[:])
			elapsed = time.time() - st
			
			print >>sys.stderr, "Unassigned %i polygons (setComplete) in %f s ( %f polys/s )" % (np, elapsed, np/elapsed)
			
			
			# with complete data
			st = time.time()
			c = m.cf.empty()
			c.setCompleteData(np)
			isb.addMember(m, c, ignore_failure=ignore_failure)
			elapsed = time.time() - st
			
			print >>sys.stderr, "Assigned %i polygons (setCompleteData, ignore_failure=%i) in %f s ( %f polys/s )" % (np, ignore_failure, elapsed, np/elapsed)
		# END for each ignore_failure value
		
		
