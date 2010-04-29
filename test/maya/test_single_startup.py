# -*- coding: utf-8 -*-
import os
import sys
import mrv.test.maya.util as tutil
from mrv.test.lib import *
from mrv.path import Path
import tempfile

class TestStartup( tutil.StandaloneTestBase ):
	"""For the sake of brevity, we turn all options on and test for all of them, 
	although in fact each of these are independent. The test will not be able to 
	detect if the configuration we test for always applies. Here we rely on the
	implementors capabilities"""
	temp_app_dir = Path(tempfile.gettempdir()) / "testmaya" 
	
	def _rm_test_dir(self):
		if self.temp_app_dir.isdir():
			try:
				self.temp_app_dir.rmtree()
			except OSError:
				# on windows, maya usually keps the maya.log open, so the 
				# full removal fails. Ignore that ... .
				pass 
		# END delete test dir
	
	def setup_environment(self):
		os.environ['MRV_STANDALONE_INIT_OPTIONVARS'] = "1"
		os.environ['MRV_STANDALONE_RUN_USER_SETUP'] = "1"
		os.environ['MRV_STANDALONE_AUTOLOAD_PLUGINS'] = "1"
		
		self._rm_test_dir()
		if not self.temp_app_dir.isdir():
			self.temp_app_dir.mkdir()
		# END assure we have a target directory
		
		# copy default user preferences for 32 and 64 bit versions - on darwin
		# they is no difference, as they only support one version on it
		prefs_base = tutil.fixture_path('maya_user_prefs')
		mayaversion = os.environ['MRV_MAYA_VERSION']
		
		# setup maya app dir to be in a temporary directory
		suffixes = ['']
		if sys.platform != 'darwin':
			suffixes.append('-x64')
			
		for suffix in suffixes:
			prefs_base.copytree(self.temp_app_dir / (mayaversion + suffix))
		# copy prefs data
		
		# setup maya to use our prefs directory 
		os.environ['MAYA_APP_DIR'] = str(self.temp_app_dir)
		
		
	def undo_setup_environment(self):
		os.environ['MRV_STANDALONE_INIT_OPTIONVARS'] = "0"
		os.environ['MRV_STANDALONE_RUN_USER_SETUP'] = "0"
		os.environ['MRV_STANDALONE_AUTOLOAD_PLUGINS'] = "0"
		
		# remove our temporary data
		self._rm_test_dir()
		
		
	def post_standalone_initialized(self):
		from mrv.maya.util import OptionVarDict
		import maya.cmds as cmds
		import maya.mel
		
		ovars = OptionVarDict()
		ovar = "TEST_OVAR"
		
		# check runtime comamnds
		assert 'MyTestRuntimeCommand' in (cmds.runTimeCommand(q=1, uca=1) or list())
		
		plugins = ("ge2Export", "decomposeMatrix")
		for plugname in plugins:
			assert cmds.pluginInfo(plugname, q=1, loaded=1)
		# check auto load plugins
		
		
		# check option vars
		assert ovar in ovars
		assert ovars[ovar] == 3 
		
		# check user setup
		tscript = """global int $gTestVar;
		if( $gTestVar != 5 ){
			error("AssertionError, global variable was not set");
		}"""
		maya.mel.eval(tscript)		# shouldn't raise
		assert hasattr(sys, 'userSetup') and sys.userSetup == True
		
