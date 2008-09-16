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
	def __init__( self, workflow , name="SimpleTest"):
		super( TestProcess, self ).__init__( name, "testing simple", workflow )
		
	#{ Implementation 
	
	def getOutput( self, target, is_dry_run ):
		"""@return: target is int instance: return int * 2
					target is float instance: return float * 3, input query 
					target is string cls, return "hello world"""
		if isinstance( target, int ):
			return target * 2
		elif isinstance( target, float ):
			return self.getInput( float ) * target 
		elif self._isCompatibleWith( target, basestring ):
			return "hello world"
		elif self._isCompatibleWith( target, float ):
			return 3.0
		elif self._isCompatibleWith( target, int ):
			return 4
		else:
			raise AssertionError( "Incompatible target %r passed to %s - canOutputTarget method buggy ?" % ( target, self ) )			
	
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		return [ int, float, basestring ]
		
		
	def canOutputTarget( self, target ):
		if isinstance( target, ( float, int ) ):
			return processes.ProcessBase.kPerfect
		
		if self._isCompatibleWith( target, float ):
			return self._getClassRating( target, float )
		
		if self._isCompatibleWith( target, int ):
			return self._getClassRating( target, int )
		
		return self._getClassRating( target, basestring )
		
		
	def needsUpdate( self, target ):
		return True
		
		# generators are always dirty ( as they need to generate their value 
		if self._getClassRating( target, basestring ):
			return True
		
	#}


class OtherTestProcess( TestProcess ):
	"""TestProcess helping to debugging the calles done
	Supported Targets: unicode instances """
	def __init__( self, workflow ):
		super( OtherTestProcess, self ).__init__( workflow, name = "OtherSimpleTest" )
		
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		return [ unicode ]
	
	def canOutputTarget( self, target ):
		if isinstance( target, unicode ):
			return 255
		return 0
	
	def getOutput( self, target, is_dry_run ):
		"""@return: version of target requireing int and float instance"""
		floatinst = self.getInput( float )
		intinst = self.getInput( int )
		
		return target + unicode( floatinst ) + unicode( self.getInput( 10 ) ) * intinst


class WorkflowWrapTestProcess( processes.WorkflowProcessBase ):
	
	def __init__( self, workflow, wflname, **kwargs ):
		"""Wrap the workflow with the given name"""
		wflModImportPath = "byronimotest.byronimo.automation.workflows"
		return super( WorkflowWrapTestProcess, self ).__init__( workflow, wflModImportPath, wflname , **kwargs )
		

#} END processes 




#{ Process Initialization
processes.addProcesses( TestProcess )
processes.addProcesses( OtherTestProcess )
processes.addProcesses( WorkflowWrapTestProcess )

#}
