# -*- coding: utf-8 -*-
import os
import mrv.test.maya.util as tutil

class TestUndoDisabled( tutil.StandaloneTestBase ):
	envvarname = 'MRV_DEBUG_MPLUG_SETX'
	prev_val = None
	
	def setup_environment(self):
		self.prev_val = os.environ.get(self.envvarname, "0") 
		os.environ[self.envvarname] = "1"
		
	def undo_setup_environment(self):
		os.environ[self.envvarname] = self.prev_val
		
	def post_standalone_initialized(self):
		# plugs raise if set is used
		from mrv.maya.nt import Node
		p = Node("persp")
		val = 30.0
		assert p.tx.asDouble() != val
		p.tx.msetDouble(val)		# fine
		assert p.tx.asDouble() == val
		self.failUnlessRaises(AssertionError, getattr, p.tx, 'setDouble')
