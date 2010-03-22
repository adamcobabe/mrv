# -*- coding: utf-8 -*-
import os
import mrv.test.maya.util as tutil

class TestPersistenceEnabled( tutil.StandaloneTestBase ):
	envvarname = 'MRV_PERSISTENCE_ENABLED'
	prev_val = None
	
	def setup_environment(self):
		self.prev_val = os.environ.get(self.envvarname, "0") 
		os.environ[self.envvarname] = "1"
		
	def undo_setup_environment(self):
		os.environ[self.envvarname] = self.prev_val
		
	def post_standalone_initialized(self):
		# plugin should have loaded automatically
		import maya.cmds as cmds
		import mrv.maya.nt
		persistence_plugin_file = os.path.splitext(mrv.maya.nt.persistence.__file__)[0] + '.py'
		assert cmds.pluginInfo( persistence_plugin_file, q=1, loaded=1 )
		
