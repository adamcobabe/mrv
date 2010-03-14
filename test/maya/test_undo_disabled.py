# -*- coding: utf-8 -*-
""" This module has to be started standalone as it initializes mayarv.maya with 
the undo system disabled. If that was not the case, it will bail out early."""
import unittest
import time
import os

class TestUndo( unittest.TestCase ):
	
	def test_undo_disabled(self):
		envvarname = 'MAYARV_UNDO_ENABLED'
		os.environ[envvarname] = "0"
		
		st = time.time()
		import mayarv.maya
		import maya.cmds as cmds
		
		# too fast ? It was loaded already as we have not been run standalone
		if time.time() - st < 0.1:
			os.environ[envvarname] = "1"
			print "Undo-disabled test bailed out at it couldn't be the first one to initialize mayarv.maya"
			return
		# END handle non-standalone mode
		
		# plugin shouldn't have loaded
		undo_plugin_file = os.path.splitext(mayarv.maya.undo.__file__)[0] + '.py'
		assert not cmds.pluginInfo( undo_plugin_file, q=1, loaded=1 )
