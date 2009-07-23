# -*- coding: utf-8 -*-
"""B{mayarvtest.mayarv.maya.nodes}

Intialize the byronimo maya nodes testing suite

@newfield revision: Revision
@newfield id: SVN Id
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
import test as common

import mayarv.maya.nodes as nodes

test_modules = set()

#{ Interface
def mayRun( modulename ):
	"""@return: True if the given interface may run"""
	global test_modules

	if not test_modules:
		return True

	return modulename in test_modules
#} END interface


def get_suite( ):
	""" @return: testsuite with all tests of this package"""
	import test.maya.nodes as self

	# each test has to check whether he can run in batch mode or not
	return common.get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests"""
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" Run the tests if called with the start script """
	global test_modules
	test_modules = set( args )
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	import sys
	main( *sys.argv )

