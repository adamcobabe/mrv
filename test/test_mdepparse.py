# -*- coding: utf-8 -*-
"""Tests for the maya dependency parser"""
from mrv.test.lib import *
from mrv.mdepparse import *


class TestMayaDependencyParsing( unittest.TestCase ):

	def test_base( self ):
		reffile = get_maya_file('ref2re.ma')
		mbfile = get_maya_file('21kcurves.ma')
		
		# two equal refs, each two subrefs - not texture paths
		for parse_all_paths in range(2):
			mfg = MayaFileGraph.createFromFiles([reffile], parse_all_paths=parse_all_paths)
			affectedBy = mfg.depends(reffile, mfg.kAffectedBy)
			assert len(mfg.invalidFiles()) == 0
			
			assert len(mfg.depends(affectedBy[-1], mfg.kAffects)) == 2
			
			# it cannot handle mb yet, but would just skip these
			mfg = MayaFileGraph.createFromFiles([mbfile], parse_all_paths=parse_all_paths)
			assert len(mfg.depends(mbfile, mfg.kAffectedBy)) == 0
		# END for each possible parse_all_paths value
		
		
