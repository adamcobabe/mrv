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
from byronimo.maya.nodes.modifiers import *
import maya.OpenMaya as om
import sys



class TestModifiers( unittest.TestCase ):
	"""Test all aspects of the api undo queue"""
	
	def test_dgmod( self ):
		"""byronimo.maya.nodes.modifiers: test dg modifier capabilities"""
		persp = MayaNode( "persp" )
		front = MayaNode( "front" )
		
		dgmod = om.MDGModifier()
		# SIMPLE CONNECTION
		################
		# start undo 
		undo.startUndo( )
		dgmod = DGModifier( )
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
		
		cmds.undo()
		
		# EMPTY DOIT
		################
		undo.startUndo( )
		dgmod = DGModifier( )
		dgmod.doIt( )
		undo.endUndo( )
		
		cmds.undo()
		
		
	def test_dagmod( self ):
		"""byronimo.maya.nodes.modifiers: test DAG modifier capabilities"""
		dagmod = DagModifier()
