# -*- coding: utf-8 -*-
"""
Intialize and run all benchmark - the system is currently unittest based and
proper benchmarks should be implemented on per test basis.

It is possible though to supply command line arguments, see L{main}



"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: __init__.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
import mayarv.maya as bmaya
import mayarv.test as common
import os


test_cases = set()

#{ Interface
def mayRun( testcase ):
	"""@return: True if the given testcase may run - this helps
	to focuse on individual tests"""
	global test_cases

	if not test_cases:
		return True

	return testcase in test_cases
#} END interface



def get_maya_file( filename ):
	"""@return: path to specified maya ( test ) file """
	return os.path.join( os.path.dirname( __file__ ), "ma/"+filename )


def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	bmaya.Mel.putenv( "MAYAFILEBASE", os.path.dirname( __file__ ) )

	import mayarv.test.maya.benchmark as self
	return common.get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests  """
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" required for standalone start up
	@param *args: if given, they identify the tests to run. If none
	is given, all will run"""
	global test_cases
	test_cases = set( args )
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( )

