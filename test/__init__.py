# -*- coding: utf-8 -*-
"""Initialize the test framework

@newfield revision: Revision
@newfield id: SVN Id
"""


__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-16 16:08:43 +0200 (Sat, 16 Aug 2008) $"
__revision__="$Revision: 67 $"
__id__="$Id: configuration.py 67 2008-08-16 14:08:43Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
from cStringIO import StringIO

#{ Utilities

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

#}


def get_suite( ):
	"""@return: all tests in this package"""
	import inspect

	import test
	import mayarv.test.automation as automation
	import mayarv.test.automation.processes as automationproceses
	import mayarv.test.automation.workflows as automationworkflows
	import mayarv.test.maya as maya
	import mayarv.test.maya.ui as mayaui
	import mayarv.test.maya.nodes as Nodes
	import mayarv.test.maya.benchmark as benchmark

	testmodules = [ t[1] for t in locals().iteritems() if t[0] != 'inspect' and inspect.ismodule( t[1] ) ]

	# gather suites
	alltests = unittest.TestSuite()
	for module in testmodules:
		try:
			alltests.addTests( module.get_suite( ) )
		except AttributeError:
			print "%s did not define test" % module.__name__
			raise

	return alltests

def run_all( ):
	"""Run all tests modules we know. Currently its a manual process adding the compatible modules
	@todo: Make it find all modules automatically, or implement a recursive approch"""
	# imports
	output = StringIO()
	testrunner = unittest.TextTestRunner( stream = output, verbosity = 2 )
	testrunner.run( get_suite( ) )

	# print the output ( for now this should be enough )
	print output.getvalue()


def main( *args ):
	"""Run all tests by default if started from commandline """
	run_all()
