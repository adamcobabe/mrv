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
from byronimo.automation.processes.plug import *
from byronimo.dgengine import plug, Attribute as A

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
	"""TestProcess helping to debugging the calles done """
	# inputs
	inInt = 		plug( "inInt", 		A( int, A.writable, default = 4 ) )
	inFloat = 		plug( "inFloat", 	A( float, A.writable, default = 2.5 ) )
	
	# outputs 
	outFloat = 		plug( "outFloat", 	A( float, A.computable ) )
	outInt = 		plug( "outInt", 	A( int, A.computable ) )
	outFloatGen = 	plug( "outFloatGen", A( float, A.computable ) )
	outIntGen = 	plug( "outIntGen", 	A( int, A.computable ) )
	outText = 		plug( "outText", 	A( str, 0, default = "hello world" ) )
	
	# affects 
	inInt.affects( outInt )
	inFloat.affects( outFloat )
	
	
	def __init__( self, workflow , name="TestProcess"):
		super( TestProcess, self ).__init__( name, "testing simple", workflow )
		
	#{ Implementation 
	
	def evaluateState( self, plug, mode ):
		if plug == TestProcess.outInt:
			return self.inInt.get( ) * 2
		if plug == TestProcess.outFloat:
			return self.inFloat.get( ) * 2.0 
		if plug == TestProcess.outText:
			return "hello world"
		elif plug == TestProcess.outFloatGen:
			return 3.0
		elif plug == TestProcess.outIntGen:
			return 4
		else:
			raise AssertionError( "Incompatible target %r passed to %s - canOutputTarget method buggy ?" % ( target, self ) )			
		
	#}


class OtherTestProcess( TestProcess ):
	"""TestProcess helping to debugging the calles done
	Supported Targets: unicode instances """
	
	# inputs 
	inFloat = plug( "inFloat", A( float, A.writable ) )
	inInt = plug( "inInt", A( int, A.writable ) )
	inUni = plug( "inUnicode", A( unicode, A.writable ) )
	
	# outputs 
	outString = plug( "outString", A( unicode, 0 ) )
	
	# affects 
	inFloat.affects( outString )
	inInt.affects( outString )
	inUni.affects( outString )
	
	
	def __init__( self, workflow ):
		super( OtherTestProcess, self ).__init__( workflow, name = "OtherTestProcess" )
	
	def evaluateState( self, target, mode ):
		"""@return: version of target requireing int and float instance"""
		floatinst = self.inFloat.get()
		intinst = self.inInt.get()
		instr = self.inUni.get()
		
		return instr + unicode( floatinst ) + unicode( 20 ) * intinst


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
