# -*- coding: utf-8 -*-
""" Intialize the maya UI testing suite - this code is required to be able to 
start the tests easily from within MEL !"""
import unittest
import mayarv.maya.ui as ui

#{ Initialization

def get_package_suite( moduleObject ):
	"""
	@param moduleObject: the module object pointing to the package ( or module within a package )
	@return: testsuite containing all testSuites of all package submodules
	@todo: make this work recursively with sub-packages
	"""
	from glob import glob
	import os

	# assure we have a directory
	packageDir = os.path.dirname( moduleObject.__file__ )

	# get all submodules
	basenameNoExt = lambda n: os.path.splitext( os.path.split( n )[1] )[0]
	
	# testing is only for developers, hence we assume we have the code ( *.py )
	pymodules = glob( os.path.join( packageDir, "*.py" ) )
	pymodules.sort()
	pymodules = [ moduleObject.__name__+"."+basenameNoExt( m ) for m in pymodules
							if not os.path.basename( m ).startswith( '_' ) ]

	# now we have a dotted package notation
	packagesuite = unittest.TestSuite()
	subsuites = unittest.defaultTestLoader.loadTestsFromNames( pymodules )
	packagesuite.addTests( subsuites )

	return packagesuite


def get_suite( ):
	""" @return: testsuite with all tests of this package"""
	import mayarv.test.maya.ui as self
	import maya.cmds as cmds

	# each test has to check whether he can run in batch mode or not
	return get_package_suite( self )

def run( **runner_args ):
	"""Run all the tests"""
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )


def main( *args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )

