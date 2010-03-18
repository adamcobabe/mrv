# -*- coding: utf-8 -*-
""" This module has to be started standalone as it initializes mayarv.maya with 
Plug debugging enabled. If that was not the case, it will bail out early.
@note: This module duplicates a lot of code from test/maya/test_undo_disabled.
It might be better to have a common base"""
import unittest
import time
import os

class TestPlug( unittest.TestCase ):
	
	def test_mplug_setx_raises(self):
		envvarname = 'MAYARV_DEBUG_MPLUG_SETX'
		os.environ[envvarname] = "1"
		
		st = time.time()
		import mayarv.maya.nt as nt
		
		# too fast ? It was loaded already as we have not been run standalone
		if time.time() - st < 0.1:
			os.environ[envvarname] = "1"
			print "MPlug.setX test bailed out at it couldn't be the first one to initialize mayarv.maya.nt"
			return
		# END handle non-standalone mode
		
		# plugs raise if set is used
		p = nt.Node("persp")
		val = 30.0
		assert p.tx.asDouble() != val
		p.tx.msetDouble(val)		# fine
		assert p.tx.asDouble() == val
		self.failUnlessRaises(AssertionError, getattr, p.tx, 'setDouble')
