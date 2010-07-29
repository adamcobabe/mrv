# -*- coding: utf-8 -*-
""" Intialize the mrv maya testing suite """
from mrv.test.lib import *
from util import *

import tempfile
import shutil
import os

from mrv.path import make_path

env_app_dir = "MAYA_APP_DIR"


def setup_maya_app():
	"""Prepare the maya app dir to come up with a neutral environment"""
	maya_config = fixture_path("maya_config")
	target_path = make_path(os.path.join(tempfile.gettempdir(), "test_mrv_maya_config"))
	if target_path.isdir():
		shutil.rmtree(target_path)
	shutil.copytree(maya_config, target_path)
	
	# adjust the environment to assure 
	os.putenv(env_app_dir, target_path)
	os.environ[env_app_dir] = target_path
	
setup_maya_app()
