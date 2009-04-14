# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo.maya}

Intialize the byronimo maya testing suite

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: __init__.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
import byronimo.maya as bmaya
import byronimotest as common
import maya.cmds as cmds
import os
import tempfile

#{ Interface
def get_maya_file( filename ):
	"""@return: path to specified maya ( test ) file """
	return os.path.join( os.path.dirname( __file__ ), "ma/"+filename )


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
	cmds.undoInfo( infinity=1 )
	import byronimotest.byronimo.maya as self
	return common.get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests  """
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )

