# -*- coding: utf-8 -*-
import unittest
import time
import sys

class TestStartupPerformance( unittest.TestCase ):
	""":note: this test must run alone"""
	
	def test_startup(self):
		st = time.time()
		import mrv.maya.nt
		elapsed = time.time() - st
		
		# skip if it wasn't started standalone
		if elapsed < 0.1:
			return
		
		print >> sys.stderr, "Initialized mrv and maya-standalone (import mrv.maya.nt) in %f" % elapsed
		
