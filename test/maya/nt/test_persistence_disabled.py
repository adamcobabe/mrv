# -*- coding: utf-8 -*-
import os
import mayarv.test.maya.util as tutil

class TestUndoDisabled( tutil.StandaloneTestBase ):
	envvarname = 'MAYARV_PERSISTENCE_ENABLED'
	prev_val = None
	
	def setup_environment(self):
		self.prev_val = os.environ.get(self.envvarname, "1") 
		os.environ[self.envvarname] = "0"
		
	def undo_setup_environment(self):
		os.environ[self.envvarname] = self.prev_val
		
	def post_standalone_initialized(self):
		# plugin shouldn't have loaded
		import maya.cmds as cmds
		import mayarv.maya.nt
		persistence_plugin_file = os.path.splitext(mayarv.maya.nt.persistence.__file__)[0] + '.py'
		assert not cmds.pluginInfo( persistence_plugin_file, q=1, loaded=1 )
		
		# if we enforce persitence, it should be loaded and available !
		mayarv.maya.nt.enforcePersistance()
		assert cmds.pluginInfo( persistence_plugin_file, q=1, loaded=1 )
