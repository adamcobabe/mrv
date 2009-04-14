# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo}
initialize the byronimo main tests

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-05 00:46:40 +0430 (Tue, 05 Aug 2008) $"
__revision__="$Revision: 40 $"
__id__="$Id: __init__.py 40 2008-08-04 20:16:40Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
import byronimotest as common

def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import byronimotest.byronimo as self
	return common.get_package_suite( self )

def run_generic( packageObj, **runner_args ):
	"""
	Run all the tests defined in this testpackage

	@param runner_args: will be passed as optinoal arguments to the L{unittest.TestRunner}
	@return: L{unittest.TestResult}
	"""
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( common.get_package_suite( packageObj ) )


def run( **runner_args ):
	"""Run all the tests defined in L{byronimo.test}
	For more information see L{run_generic}
	"""
	import byronimotest.byronimo as self
	return run_generic( self, **runner_args )


def main( *args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )


if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )

