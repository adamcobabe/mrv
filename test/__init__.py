# -*- coding: utf-8 -*-
"""Initialize the testing framework """
import os
import lib
import logging


#{ Initialization 
def setup_mayafilebase():
	"""Assure the environment variable to the fixtures files is set"""
	os.environ['MAYAFILEBASE'] = os.path.dirname(os.path.dirname(lib.get_maya_file('ignored.ma')))		# mrv/test/fixtures/ma/ignored.ma 

def init_logging():
	"""Assure there is a basic logging so we see all messages"""
	logging.basicConfig(level=logging.DEBUG)
	
setup_mayafilebase()
init_logging()
#} END initialization 
