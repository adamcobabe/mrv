# -*- coding: utf-8 -*-
"""
Test default report classes

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
import workflows
from mayarv.automation.report import *

class TestReport( unittest.TestCase ):
	"""Test workflow class"""

	def test_plan( self ):
		"""mayarv.automation.report: test plan report"""
		miwfl = workflows.multiinput

		# try as real target - stil very simple
		res = miwfl.makeTarget( unicode( "this" ) )
		plan = miwfl.getReportInstance( Plan )
		r = plan.getReport( headline = "unicode workflow test" )
		self.failUnless( len( r ) == 6 )
		for l in r:
			print l
