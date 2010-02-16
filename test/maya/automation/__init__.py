# -*- coding: utf-8 -*-
"""
Intialize the maya automation test suite



"""


import unittest
import mayarv.test as common

def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import mayarv.test.maya.automation as self
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

