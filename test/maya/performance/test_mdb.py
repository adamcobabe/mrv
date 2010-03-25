# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
# test import all
from mrv.maya.mdb import *
import mrv.maya.nt.typ as typ

import time
import sys

class TestMDB( unittest.TestCase ):
	def test_prefetch(self):
		st = time.time()
		nm = typ.prefetchMFnMethods()
		elapsed = time.time() - st
		print >>sys.stderr, "Pre-fetched %i methods in %f s ( %f methods / s)" % ( nm, elapsed, nm / elapsed )
		
	def test_compilation(self):
		pass
		
