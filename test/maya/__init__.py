# -*- coding: utf-8 -*-
"""
Intialize the byronimo maya testing suite



"""


from mayarv.test.lib import *
import mayarv.maya as bmaya
import mayarv.test as common
import maya.cmds as cmds
import os
import tempfile

#{ Interface
def get_maya_file( filename ):
	"""@return: path to specified maya ( test ) file """
	return fixturePath( "ma/"+filename )


def _saveTempFile( filename ):
	"""save the current scene as given filename in a temp directory, print path"""
	filepath = tempfile.gettempdir( ) + "/" + filename
	savedfile = bmaya.Scene.save( filepath )
	print "SAVED TMP FILE TO: %s" % savedfile
	return savedfile

#} Interface


def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	bmaya.Mel.putenv( "MAYAFILEBASE", os.path.dirname( __file__ ) )
	import mayarv.test.maya as self
	return common.get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests  """
	testrunner = TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )

