# -*- coding: utf-8 -*-
"""Tests for the maya dependency parser"""
from mayarv.test.lib import *
from mayarv.mdepparse import *

class TestMayaDependencyParsing( unittest.TestCase ):

	def test_base( self ):
		reffile = get_maya_file('ref2re.ma')
		
		# two equal refs, each two subrefs 
		mfg = MayaFileGraph.createFromFiles([reffile])
		affectedBy = mfg.depends(reffile, mfg.kAffectedBy)
		print mfg.invalidFiles()
		assert len(mfg.invalidFiles()) == 0
		 
		
		# it cannot handle mb yet
		

