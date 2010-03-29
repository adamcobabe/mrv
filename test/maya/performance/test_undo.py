# -*- coding: utf-8 -*-
""" Test undo queue performance """
from mrv.test.maya import *
import mrv.maya as mrvmaya
import maya.cmds as cmds
import mrv.maya.undo as undo
from mrv.test.maya.test_undo import TestUndoQueue
import sys

class TestUndoPerformance( unittest.TestCase ):
	"""Test all aspects of the api undo queue"""

	@staticmethod
	@undoable
	def _recurseUndoDeco( numOps, curDepth, maxDepth ):
		"""Recurse and create operations according to args
		:note: decorator used !"""
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
		:note: decorator used !"""
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

	@with_undo
	def test_undoPerformance( self ):
		import time
		iterations = 35
		maxdepth = 3
		totalops = 0

		all_elapsed = [list(),list()]

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

			print >> sys.stderr, "UNDO: DECORATED %s: %i ops in %f s ( %f / s )" % ( undo, numops, elapsed, numops / elapsed )


			starttime = time.time()
			numops = TestUndoPerformance._recurseUndo( iterations, 0, maxdepth )
			totalops += numops
			elapsed_deco = elapsed
			elapsed = time.time() - starttime
			all_elapsed[undoEnabled].append( elapsed )

			print >> sys.stderr, "UNDO: MANUAL %s: %i ops in %f s ( %f / s )" % ( undo, numops, elapsed, numops / elapsed )
			starttime = time.time()

			print >> sys.stderr, "UNDO: DECORATED is %f %% faster than manually implemented functions !" % ( 100 - ( elapsed_deco / elapsed ) * 100 )

			if undoEnabled:
				cmds.undo()
				cmds.undo()
				cmds.redo()
				cmds.redo()
				elapsed = time.time() - starttime

				print >> sys.stderr, "UNDO: CALL TIME: %i operations in %f s ( %f / s )" % ( totalops, elapsed, totalops / elapsed )
			#END if undo enabled
		# END for each undo queue state

		ratio = 100.0 - ( ( all_elapsed[0][0] / all_elapsed[1][0] ) * 100 )
		difference = all_elapsed[1][1] - all_elapsed[0][1]

		# RATIOS between enabled undo system and without
		print >> sys.stderr, "UNDO: RATIO UNDO QUEUE ON/OFF: %f s (on) vs %f s (off) = %f %% speedup on disabled queue ( difference [s] = %f )" % (all_elapsed[1][0], all_elapsed[0][0], ratio, difference )


