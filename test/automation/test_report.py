# -*- coding: utf-8 -*-
""" Test default report classes """
import unittest
import workflows
from mayarv.automation.report import *

class TestReport( unittest.TestCase ):
	"""Test workflow class"""

	def test_plan( self ):
		miwfl = workflows.multiinput

		# try as real target - stil very simple
		res = miwfl.makeTarget( unicode( "this" ) )
		plan = miwfl.createReportInstance( Plan )
		r = plan.makeReport( headline = "unicode workflow test" )
		self.failUnless( len( r ) == 6 )
		for l in r:
			print l
