# -*- coding: utf-8 -*-
import os
import mrv.test.maya.util as tutil

class TestUndoDisabled( tutil.StandaloneTestBase ):
	envvarname = 'MRV_UNDO_ENABLED'
	prev_val = None
	
	def setup_environment(self):
		self.prev_val = os.environ.get(self.envvarname, "1") 
		os.environ[self.envvarname] = "0"
		
	def undo_setup_environment(self):
		os.environ[self.envvarname] = self.prev_val
		
	def post_standalone_initialized(self):
		# plugin shouldn't have loaded
		import maya.cmds as cmds
		import mrv.maya
		undo_plugin_file = os.path.splitext(mrv.maya.undo.__file__)[0] + '.py'
		assert not cmds.pluginInfo( undo_plugin_file, q=1, loaded=1 )
		
		# should still be able to use MPlug.msetX
		import mrv.maya.nt as nt
		p = nt.Node("persp")
		p.tx.msetDouble(10.0)
		assert p.tx.asDouble() == 10.0
