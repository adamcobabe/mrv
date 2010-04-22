# -*- coding: utf-8 -*-
"""Contains routines required to initialize mrv"""
__docformat__ = "restructuredtext"

#{ Maya-Intiialization
	
def setup_maya_environment(maya_version=8.5):
	"""Configure os.environ to allow Maya to run in standalone mode
	:param maya_version: The maya version to prepare to run, either 8.5 or 2008 to 
	20XX. This requires the respective maya version to be installed in a default location."""
	raise NotImplementedError("todo");

def arg_parser():
	""":return: Argument parser initialized with all arguments supported by mrv"""

def replace_procress(options, args):
	"""Replace this process with a python process as determined by the given options.
	This will either be the respective python interpreter, or mayapy
	
	:param options: Optparse options providing additional information
	:param args: remaining arguments which should be passed to the process
	:raise EnvironmentError: If no suitable executable could be started"""

#} END Maya initialization





