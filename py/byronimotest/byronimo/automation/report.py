"""B{byronimotest.byronimo.automation.report}

Test default report classes

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import workflows
from byronimo.automation.report import * 

class TestReport( unittest.TestCase ):
	"""Test workflow class"""
	
	def test_plan( self ):
		"""byronimo.automation.report: test plan report"""
		miwfl = workflows.multiinput
		
		# try as real target - stil very simple 
		res = miwfl.makeTarget( unicode( "this" ) )
		plan = miwfl.getReportInstance( Plan )
		r = plan.getReport( headline = "unicode workflow test" )
		self.failUnless( len( r ) == 6 )
		for l in r:
			print l
