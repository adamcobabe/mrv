# -*- coding: utf-8 -*-
import os
import mrv.test.maya.util as tutil

class TestStartup( tutil.StandaloneTestBase ):
	"""For the sake of brevity, we turn all options on and test for all of them, 
	although in fact each of these are independent. The test will not be able to 
	detect if the configuration we test for always applies. Here we rely on the
	implementors capabilities"""
	
	
	def setup_environment(self):
		os.environ['MRV_STANDALONE_INIT_MEL'] = "1"
		os.environ['MRV_STANDALONE_RUN_USER_SETUP'] = "1"
		os.environ['MRV_STANDALONE_AUTOLOAD_PLUGINS'] = "1"
		
	def undo_setup_environment(self):
		os.environ['MRV_STANDALONE_INIT_MEL'] = "0"
		os.environ['MRV_STANDALONE_RUN_USER_SETUP'] = "0"
		os.environ['MRV_STANDALONE_AUTOLOAD_PLUGINS'] = "0"
		
	def post_standalone_initialized(self):
		# plugs raise if set is used
		self.fail("todo")
