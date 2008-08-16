"""B{tests}
Initialize the test framework

@newfield revision: Revision
@newfield id: SVN Id
"""


__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-16 16:08:43 +0200 (Sat, 16 Aug 2008) $"
__revision__="$Revision: 67 $"
__id__="$Id: configuration.py 67 2008-08-16 14:08:43Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest


def get_suite( ):
	"""@return: all tests in this package"""
	import inspect 
	
	import tests.byronimo as byronimo
	import tests.byronimo.maya as maya
	import tests.byronimo.maya.ui as mayaui
	import tests.byronimo.maya.nodes as maya.nodes
	
	testmodules = [ t[1] for t in locals().iteritems() if t[0] != 'inspect' and inspect.ismodule( t[1] ) ]
	
	# gather suites 
	alltests = unittest.TestSuite()
	for module in testmodules:
		try:
			alltests.addTests( module.get_suite( ) )
		except AttributeError:
			print "%s did not define test" % module.__name__
			raise 
	

def run_all( ):
	"""Run all tests modules we know. Currently its a manual process adding the compatible modules
	@todo: Make it find all modules automatically, or implement a recursive approch"""
	# imports
	
	testrunner = unittest.TextTestRunner( verbosity = 2 )
	testrunner.run( get_suite( ) )
	
def main( *args ):
	"""Run all tests by default if started from commandline """
	run_all()
