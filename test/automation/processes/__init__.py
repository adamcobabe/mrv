# -*- coding: utf-8 -*-
"""B{mayarvtest.mayarv.automation.processes}

Intialize suite checking all processes

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: __init__.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import unittest
import test as common
import mayarv.automation.process as process
import mayarv.automation.processes as processes
from mayarv.dgengine import plug, Attribute as A
from mayarv.path import Path
from mayarv.automation.qa import QAProcessBase, QACheck, QACheckResult

def get_suite( ):
	""" @return: testsuite with all tests of this package
	@note: does some custom setup required for all tests to work"""
	# custom setup
	import test.automation.processes as self
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


#{ Processes

class TestProcess( process.ProcessBase ):
	"""TestProcess helping to debugging the calles done """
	# inputs
	inInt = 		plug( A( int, 0, default = 4 ) )
	inFloat = 		plug( A( float, 0, default = 2.5 ) )
	inText = 		plug( A( str, 0, default = "hello world" ) )
	inChain = 		plug( A( list, 0, default = [5] ) )			# just connectable, will be pulled s
	inObj = 		plug( A( object, A.cls|A.exact_type ) )	# just connectable

	# outputs
	outFloat = 		plug( A( float, A.computable|A.uncached ) )
	outInt = 		plug( A( int, A.computable|A.uncached ) )
	outText = 		plug( A( str, 0, default = "hello world" ) )
	outChain = 		plug( A( list, 0 ) )

	# affects
	inInt.affects( outInt )
	inFloat.affects( outFloat )
	inText.affects( outText )

	inObj.affects( outChain )
	inChain.affects( outChain )

	noun = "TestProcess"
	verb = "computes"


	#{ Implementation

	def evaluateState( self, plug, mode ):
		if plug == TestProcess.outInt:
			return self.inInt.get( ) * 2
		if plug == TestProcess.outFloat:
			return self.inFloat.get( ) * 2.0
		if plug == TestProcess.outText:
			return "hello world"
		elif plug == TestProcess.outChain:
			return [ self.inChain.get()[0] + 10 ]
		else:
			raise AssertionError( "Incompatible target %r passed to %s - canOutputTarget method buggy ?" % ( target, self ) )

	#}


class OtherTestProcess( process.ProcessBase ):
	"""TestProcess helping to debugging the calls done
	Supported Targets: unicode instances """

	# inputs
	inFloat = plug( A( float, 0 ) )
	inInt = plug( A( int, 0 ) )
	inUni = plug( A( unicode, 0 ) )
	inChain = 		plug( A( list, 0, default = [5] ) )

	# outputs
	outString = plug( A( unicode, 0 ) )
	outChain = 		plug( A( list, 0 ) )

	# affects
	inFloat.affects( outString )
	inInt.affects( outString )
	inUni.affects( outString )
	inChain.affects( outChain )

	noun = "OtherTestProcess"
	verb = "computes"


	def evaluateState( self, plug, mode ):
		"""@return: version of plug requireing int and float instance"""
		if plug == OtherTestProcess.outString:
			floatinst = self.inFloat.get()
			intinst = self.inInt.get()
			instr = self.inUni.get()

			return instr + unicode( floatinst ) + unicode( 20 ) * intinst
		elif plug == OtherTestProcess.outChain:
			return [ self.inChain.get()[0] + 10 ]
		# let super handle it
		return super( OtherTestProcess, self ).evaluateState( plug, mode )


class WorkflowWrapTestProcess( process.WorkflowProcessBase ):
	workflow_directory = Path( __file__ ).p_parent.p_parent / "workflows"

	def __init__( self, id, wflname, **kwargs ):
		"""Wrap the workflow with the given name"""
		self.workflow_file = wflname + ".dot"
		return super( WorkflowWrapTestProcess, self ).__init__( id, **kwargs )


	#{ iDuplicatable Interface
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it"""
		return self.__class__( self.id, self.workflowName, wflInstance = self.wgraph )

	#} END iDuplicatable

#} END processes


#{ QA Processes
class QACheckProcess( QAProcessBase ):
	""" Simple test process """

	# tests
	test_alpha = QACheck( "runs test_alpha", has_fix = 1 )
	testBeta = QACheck( "runs testbeta", has_fix = 1 )


	def assureQuality( self, check, mode ):
		if mode == self.eMode.query:
			return QACheckResult( failed_items = [ check ], header = "query" )
		else:
			return QACheckResult( fixed_items = [ check ], header = "fixed" )


#} END QA Processes


#{ Process Initialization
processes.addProcesses( TestProcess, OtherTestProcess, WorkflowWrapTestProcess, QACheckProcess )

#}
