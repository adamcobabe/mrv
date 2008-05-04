"""B{byronimo.test.init}
initialize the byronimo main tests 

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest

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
	pymodules = glob( os.path.join( packageDir, "*.py" ) )
	pymodules = [ moduleObject.__name__+"."+basenameNoExt( m ) for m in pymodules 
							if not os.path.basename( m ).startswith( '_' ) ]
	
	# now we have a dotted package notation
	packagesuite = unittest.TestSuite()
	subsuites = unittest.defaultTestLoader.loadTestsFromNames( pymodules ) 												
	packagesuite.addTests( subsuites )
	
	return packagesuite
	
	
def run_generic( packageObj, **runner_args ):
	"""
	Run all the tests defined in this testpackage
		
	@param runner_args: will be passed as optinoal arguments to the L{unittest.TestRunner}
	@return: L{unittest.TestResult}
	"""
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_package_suite( packageObj ) )
	
	
def run( **runner_args ):
	"""Run all the tests defined in L{byronimo.test} 
	For more information see L{run_generic}
	"""
	import byronimo.test as self
	return run_generic( self, **runner_args )
	
	
if __name__ == '__main__':
	""" run all tests if run directly """
	run( verbosity = 2 )
	
