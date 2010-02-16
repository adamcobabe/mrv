# -*- coding: utf-8 -*-
"""
Intialize the byronimo maya nodes testing suite



"""


import unittest
import mayarv.test as common

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
	import mayarv.test.maya.nodes as self

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

