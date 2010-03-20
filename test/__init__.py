# -*- coding: utf-8 -*-
"""Initialize the testing framework """
import os
import lib


#{ Initialization 
def setup_mayafilebase():
	"""Assure the environment variable to the fixtures files is set"""
	os.environ['MAYAFILEBASE'] = os.path.dirname(lib.get_maya_file('ignored.ma')) 
	
setup_mayafilebase()
#} END initialization 
