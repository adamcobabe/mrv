# -*- coding: utf-8 -*-
import os
import mrv.test.maya.util as tutil

class TestPersistenceEnabled( tutil.StandaloneTestBase ):
	envvarname = 'MRV_APIPATCH_APPLY_GLOBALLY'
	prev_val = None
	
	def setup_environment(self):
		self.prev_val = os.environ.get(self.envvarname, "0") 
		os.environ[self.envvarname] = "1"
		
	def undo_setup_environment(self):
		os.environ[self.envvarname] = self.prev_val
		
	def post_standalone_initialized(self):
		import mrv.maya.nt as nt
		
		# expecting overridden methods both locally and globally
		p = nt.Node("persp")
		assert hasattr(p.t, 'mconnectTo')
		assert hasattr(p.t, 'connectTo')
		
		# and it can be called
		p.tx.setDouble(10.0)
		assert p.tx.asDouble() == 10.0
		
		# original exists as well
		assert hasattr(p.tx, '_api_setDouble')
		
