# -*- coding: utf-8 -*-
"""B{mayarvtest.mayarv.maya.benchmark.undo}

Test undo queue performance

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
import mayarv.maya as bmaya
import maya.cmds as cmds
import mayarv.maya.undo as undo
from test.maya.undo import TestUndoQueue
import sys
import test.maya.benchmark as bcommon

class TestUndoPerformance( unittest.TestCase ):
	"""Test all aspects of the api undo queue"""

	@staticmethod
	@undoable
	def _recurseUndoDeco( numOps, curDepth, maxDepth ):
		"""Recurse and create operations according to args
		@note: decorator used !"""
		if curDepth == maxDepth:
			return 0
		numops = 0
		for i in xrange( numOps ):
			op = TestUndoQueue.TestOperation()
			op.doIt( )			# apply operation
			numops += TestUndoPerformance._recurseUndo( numOps, curDepth+1, maxDepth )
			numops += 1
		# END for each op
		return numops

	@staticmethod
	def _recurseUndo( numOps, curDepth, maxDepth ):
		"""Recurse and create operations according to args
		@note: decorator used !"""
		if curDepth == maxDepth:
			return 0
		undo.startUndo()

		numops = 0
		for i in xrange( numOps ):
			op = TestUndoQueue.TestOperation()
			op.doIt( )			# apply operation
			numops += TestUndoPerformance._recurseUndo( numOps, curDepth+1, maxDepth )
			numops += 1
		# END for each op

		undo.endUndo()
		return numops

	def test_undoPerformance( self ):
		"mayarv.maya.undo: recursive undo including decorator"
		if not bcommon.mayRun( "undo" ): return
		print "\n"			# new line to create some space
		import time
		iterations = 35
		maxdepth = 3
		totalops = 0

		all_elapsed = [[],[]]

		for undoEnabled in range( 2 ):

			undo = ""
			if not undoEnabled:
				undo = "Undo disabled"

			cmds.undoInfo( st=undoEnabled )

			# decorated !
			starttime = time.time()
			numops = TestUndoPerformance._recurseUndoDeco( iterations, 0, maxdepth )
			totalops += numops
			elapsed = time.time() - starttime
			all_elapsed[undoEnabled].append( elapsed )

			print "UNDO: DECORATED %s: %i ops in %f s ( %f / s )" % ( undo, numops, elapsed, numops / elapsed )


			starttime = time.time()
			numops = TestUndoPerformance._recurseUndo( iterations, 0, maxdepth )
			totalops += numops
			elapsed_deco = elapsed
			elapsed = time.time() - starttime
			all_elapsed[undoEnabled].append( elapsed )

			print "UNDO: MANUAL %s: %i ops in %f s ( %f / s )" % ( undo, numops, elapsed, numops / elapsed )
			starttime = time.time()

			print "UNDO: DECORATED is %f %% faster than manually implemented functions !" % ( 100 - ( elapsed_deco / elapsed ) * 100 )

			if undoEnabled:
				cmds.undo()
				cmds.undo()
				cmds.redo()
				cmds.redo()
				elapsed = time.time() - starttime

				print "UNDO: CALL TIME: %i operations in %f s ( %f / s )" % ( totalops, elapsed, totalops / elapsed )
			#END if undo enabled
		# END for each undo queue state

		ratio = 100.0 - ( ( all_elapsed[0][0] / all_elapsed[1][0] ) * 100 )
		difference = all_elapsed[1][1] - all_elapsed[0][1]

		# RATIOS between enabled undo system and without
		print "UNDO: RATIO UNDO QUEUE ON/OFF: %f s (on) vs %f s (off) = %f %% speedup on disabled queue ( difference [s] = %f )" % (all_elapsed[1][0], all_elapsed[0][0], ratio, difference )


