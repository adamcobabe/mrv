# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo.maya.undo}

Test ALL features of the undo queue

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
import byronimo.maya as bmaya
import maya.cmds as cmds
import byronimo.maya.undo as undo
from byronimo.maya.nodes import *
import maya.OpenMaya as om
import sys

class TestUndoQueue( unittest.TestCase ):
	"""Test all aspects of the api undo queue"""

	class TestOperation( undo.Operation ):
		def __init__( self ):
			undo.Operation.__init__( self )
			self.numDoit = 0
			self.numUndoIt = 0

		def doIt( self ):
			self.numDoit += 1

		def undoIt( self ):
			self.numUndoIt += 1



	def test_undoBasics( self ):
		"""byronimo.maya.undo: basic assertions"""
		undo.startUndo()

		# put some undoable operation
		op = TestUndoQueue.TestOperation()
		op.doIt( )			# apply operation

		self.failUnless( len( sys._maya_stack ) == 1 )
		self.failUnless( sys._maya_stack_depth == 1 )


		undo.endUndo()

		# STACK MUST BE EMPTY#
		# as it has been taken by the command
		self.failUnless( len( sys._maya_stack ) == 0 )

		# UNDO
		cmds.undo()
		self.failUnless( op.numDoit == op.numUndoIt )

		# REDO
		cmds.redo()
		self.failUnless( op.numDoit - 1 == op.numUndoIt )

		# OP WITHOUT PUSH
		self.failUnlessRaises( AssertionError, TestUndoQueue.TestOperation )


		bmaya.Mel.flushUndo()

		# handle undo ourselves
		persp = Node( "persp" )
		curvalue = persp.tx.asFloat()
		newvalue = curvalue + 1.0

		undo.startUndo()
		persp.tx.setFloat( newvalue )
		assert persp.tx.asFloat() == newvalue

		undo.undoAndClear( )		# end undo must come afterwards, otherwise the comand takes the queue
		undo.endUndo()
		assert persp.tx.asFloat() == curvalue	# its back to normal without an official undo

		# UNDO AND FILE FLUSHES
		########################
		# Our stack must be flused once maya's undo queue gets flushed
		# This is critical if an undoable method causes undo flushes, but also
		# built up our own intermediate stack which might now contain entries from
		# a non-existing scene
		# NOTE: Currently this is a known limitation that could be circumvented
		# with some pre-scene-callbacks
		trans = nodes.createNode( "mytrans", "transform" )

		undo.startUndo()
		trans.tx.setFloat( 10.0 )
		assert len( sys._maya_stack ) == 1
		bmaya.Scene.new( force = 1 )
		assert len( sys._maya_stack ) == 0, "Known Undo-Limitation"
		undo.endUndo()



	def test_dgmod( self ):
		"""byronimo.maya.undo: test dg modifier capabilities
		@note: DGmod is intensively used by MPlug """
		persp = Node( "persp" )
		front = Node( "front" )
		side = Node( "side" )

		# SIMPLE CONNECTION
		################
		# start undo
		uobj = undo.StartUndo( )
		dgmod = undo.DGModifier( )
		self.failUnless( len( sys._maya_stack ) == 1 )

		dgmod.connect( persp.message, front.isHistoricallyInteresting )
		dgmod.doIt( )

		# create undo step
		del( uobj )

		self.failUnless( len( sys._maya_stack ) == 0 )
		cmds.undo()	# undo connection
		# check connection - should be undone
		self.failUnless( not persp.message.isConnectedTo( front.isHistoricallyInteresting ) )

		cmds.redo()
		# redo it and check connection
		self.failUnless( persp.message.isConnectedTo( front.isHistoricallyInteresting ) )

		# connect and break existing conenction
		uobj = undo.StartUndo( )
		dgmod = undo.DGModifier( )
		dgmod.disconnect( persp.message, front.isHistoricallyInteresting )
		dgmod.connect( side.message, front.isHistoricallyInteresting )
		dgmod.doIt( )
		del( uobj )

		self.failUnless( side.message.isConnectedTo( front.isHistoricallyInteresting ) )
		cmds.undo()

		# old connection should be back
		self.failUnless( persp.message.isConnectedTo( front.isHistoricallyInteresting ) )


		# undo first change
		cmds.undo()

		# EMPTY DOIT
		################
		undo.startUndo( )
		dgmod = undo.DGModifier( )
		dgmod.doIt( )
		undo.endUndo( )

		cmds.undo()


	def test_dagmod( self ):
		"""byronimo.maya.undo: test DAG modifier capabilities"""
		undo.startUndo()
		dagmod = undo.DagModifier()
		obj = dagmod.createNode( "transform" )
		dagmod.renameNode( obj, "thisnewnode" )
		dagmod.doIt()

		handle = om.MObjectHandle( obj )
		self.failUnless( handle.isValid() and handle.isAlive() )

		undo.endUndo()

		cmds.undo()
		self.failUnless( not handle.isValid() and handle.isAlive() )

		cmds.redo()
		self.failUnless( handle.isValid() and handle.isAlive() )

