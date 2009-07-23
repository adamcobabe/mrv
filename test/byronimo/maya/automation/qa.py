# -*- coding: utf-8 -*-
"""B{mayarvtest.mayarv.maya.automation.qa}

Test the quality assurance framework and it's mel bindings

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import mayarv.maya.automation.qa as qa
import mayarv.automation.processes as processes
import byronimotest.mayarv.automation.workflows as workflows
import byronimotest.mayarv.automation.processes as processes
from mayarv.maya.util import Mel
import maya.mel as mmel

#  create test methods
index_proc_create = """global proc string[] b_test_index( )
{
	return { "test1", "test1descr", 1, "test2", "test2descr", 1 };
}"""
mmel.eval( index_proc_create )

check_proc_create = """global proc string[] b_test_check( string $cname, int $should_fix )
{
	string $rval[] = { (string) 0, $cname };
	// have failed items if we do not fix it
	if( ! $should_fix )
		$rval[ size( $rval ) ] = "persp";
	return $rval;
}"""
mmel.eval( check_proc_create )


class TestMELQAProcess( processes.QACheckProcess, qa.QAMELAdapter ):
	"""Test class providing some configuration"""
	mel_index_proc = "b_test_index"
	mel_check_proc = "b_test_check"

	def assureQuality( self, check, mode, *args, **kwargs ):
		"""Run mel checks"""
		assert self.isMELCheck( check )
		return self.handleMELCheck( check, mode )

class TestMELQAProcessDynamic( TestMELQAProcess ):

	static_mel_plugs = False

	# implement the method returning the checks
	def getPlugs( self, predicate = lambda p: True ):
		checks = self.getMelChecks( predicate )
		checks.extend( super( TestMELQAProcessDynamic, self ).getPlugs( predicate ) )
		return checks

# add instance to the workflow
workflows.qualitychecking.addNode( TestMELQAProcess( id="TestMELProcess" ) )
workflows.qualitychecking.addNode( TestMELQAProcessDynamic( id="TestMELProcessDynamic" ) )


class TestQualityAssurance( unittest.TestCase ):
	"""Test qa framework"""

	def test_melqa_workflow( self ):
		"""mayarv.maya.automation.qa: test mel processes"""

		wfl = workflows.qualitychecking
		tprocess = wfl.TestMELProcess
		tprocessDynamic = wfl.TestMELProcessDynamic

		assert len( tprocess.listChecks() ) == 4
		assert len( tprocess.listMELChecks() ) == 2
		assert len( tprocessDynamic.listChecks() ) == 6
		assert len( tprocessDynamic.listMELChecks() ) == 4

		# run mel checks
		melchecks = tprocess.listMELChecks( )
		for mode in qa.QAProcessBase.eMode:
			results = wfl.runChecks( melchecks, mode = mode )
			assert len( results ) == len( melchecks )

			for shell, result in results:
				if mode == tprocess.eMode.fix:
					assert result.isSuccessful()
					assert not result.getFailedItems()
				else:
					assert not result.isSuccessful()
					assert result.getFailedItems()
			# END for each shell's result
		# END for each mode


