"""B{byronimotest.byronimo.automation.processes}

Intialize suite checking all processes 

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
import byronimotest as common
import byronimo.automation.processes as processes

def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import byronimotest.byronimo.automation.processes as self	
	return common.get_package_suite( self )
	
def run( **runner_args ):
	"""Run all the tests  """
	testrunner = unittest.TextTestRunner( **runner_args )
	return testrunner.run( get_suite() )
	
	
def main( args ):
	""" Run the tests if called with the start script """
	run( verbosity = 2 )
	

if __name__ == '__main__':
	""" run all tests if run directly """
	main( [] )
	
	
#{ Processes 

class TestProcess( processes.ProcessBase ):
	"""TestProcess helping to debugging the calles done 
	
	Supported Targets: int instance, basestring class
	Thus it is a generator for strings, and a processor for ints"""
	def __init__( self, workflow ):
		super( TestProcess, self ).__init__( "Test", "testing", workflow )
		self._intPrequesite = False		 # int depends on true value of this one to be valid 
		
	#{ Implementation 
	
	def getOutput( self, target, is_dry_run ):
		"""@return: target is int instance: return int * 2
					target is string cls, return "hello world"""
		if isinstance( target, int ):
			return target * 2
		elif self._isCompatibleWith( target, basestring ):
			return "hello world"
		else:
			raise AssertionError( "Incompatible target %r passed to %s - canOutputTarget method buggy ?" % ( target, self ) )			
	
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		return [ int, basestring ]
		
		
	def canOutputTarget( self, target ):
		if isinstance( target, int ):
			return processes.ProcessBase.kPerfect
			
		return self._getClassRating( target, basestring )
		
		
	def needsUpdate( self, target ):
		if isinstance( target, int ):
			return not self._intPrequesite
	
		# generators are always dirty ( as they need to generate their value 
		if self._getClassRating( target, basestring ):
			return True
		
	#}


class OtherTestProcess( TestProcess ):
	"""TestProcess helping to debugging the calles done
	Supported Targets: unicode instances """
	
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		return [ unicode ]
	
	def canOutputTarget( self, target ):
		if isinstance( target, unicode ):
			return 255
		return 0
	


#} END processes 


#{ Process Initialization
processes.addProcesses( TestProcess )
processes.addProcesses( OtherTestProcess )

#}
