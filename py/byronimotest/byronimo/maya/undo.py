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
		bmaya.Mel.eval( "byronimoUndo -psh" )
		
		# put some undoable operation
		op = TestUndoQueue.TestOperation()
		op.doIt( )			# apply operation
		
		self.failUnless( len( sys._maya_stack ) == 1 )
		self.failUnless( sys._maya_stack_depth == 1 )
		
		
		bmaya.Mel.eval( "byronimoUndo -pop" )
		
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
		self.failUnlessRaises( ValueError, TestUndoQueue.TestOperation )
			
		
		bmaya.Mel.flushUndo()
		
		
	def test_dgmod( self ):
		"""byronimo.maya.undo: test dg modifier capabilities
		@note: DGmod is intensively used by MPlug """
		persp = Node( "persp" )
		front = Node( "front" )
		side = Node( "side" )
		
		# SIMPLE CONNECTION
		################
		# start undo 
		undo.startUndo( )
		dgmod = undo.DGModifier( )
		self.failUnless( len( sys._maya_stack ) == 1 )
		
		dgmod.connect( persp.message, front.isHistoricallyInteresting )
		dgmod.doIt( )
		
		# create undo step
		undo.endUndo( )
		
		self.failUnless( len( sys._maya_stack ) == 0 )
		cmds.undo()	# undo connection
		# check connection - should be undone 
		self.failUnless( not persp.message.isConnectedTo( front.isHistoricallyInteresting ) )
		
		cmds.redo()
		# redo it and check connection 
		self.failUnless( persp.message.isConnectedTo( front.isHistoricallyInteresting ) )
		
		# connect and break existing conenction
		undo.startUndo( )
		dgmod = undo.DGModifier( )
		dgmod.disconnect( persp.message, front.isHistoricallyInteresting )
		dgmod.connect( side.message, front.isHistoricallyInteresting )
		dgmod.doIt( )
		undo.endUndo( )
		
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
		
