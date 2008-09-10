"""B{byronimotest.byronimo.maya.nodes.general}

Test general nodes features

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
import byronimo.maya.nodes as nodes
import maya.cmds as cmds
import maya.OpenMaya as api

import time

class TestDataBase( unittest.TestCase ):
	""" Test data classes  """
	
	def test_primitives( self ):
		"""byronimo.maya.nodes: test primitive types"""
		for apicls in [ api.MTime, api.MDistance, api.MAngle ]:
			inst = apicls( )
			str( inst )
			int( inst )
			float( inst )
			repr( inst )
			
		for apicls in [ api.MVector, api.MFloatVector, api.MPoint, api.MFloatPoint, 
		 				api.MColor, api.MQuaternion, api.MEulerRotation, api.MMatrix, 
						api.MFloatMatrix, api.MTransformationMatrix ]:
			inst = apicls() 
			for item in inst:
				pass 
	
	def test_MPlug( self ):
		"""byronimo.maya.nodes: Test plug abilities( node.attribute ) """
		persp = nodes.Node( "persp" )
		front	 = nodes.Node( "front" )
		side	 = nodes.Node( "side" )
		matworld = persp.worldMatrix
		
		str( matworld )
		repr( matworld )
		
		# CONNECTIONS 
		#######################
		# CHECK COMPOUND ACCESS
		tx = persp.translate.tx	
		
		# DO CONNECTIONS ( test undo/redo )
		persp.translate >> front.translate
		
		self.failUnless( persp.translate & front.translate )	# isConnectedTo
		self.failUnless( persp.translate.p_input.isNull( ) )
		cmds.undo( )
		self.failUnless( not persp.translate.isConnectedTo( front.translate ) )
		cmds.redo( )
		self.failUnless( front.translate in persp.translate.p_outputs )
		
		# CHECK CONNECTION FORCING  
		persp.translate >  front.translate 			# already connected
		self.failUnlessRaises( RuntimeError, persp.scale.__gt__, front.translate )# lhs > rhs 
		
		# overwrite connection 
		side.translate >> front.translate
		self.failUnless( side.translate >= front.translate )
		
		# undo - old connection should be back 
		cmds.undo()
		self.failUnless( persp.translate >= front.translate )
		
		# disconnect input
		front.translate.disconnectInput()
		self.failUnless( not persp.translate >= front.translate )
		
		cmds.undo()
		
		# disconnect output
		persp.t.disconnectOutputs( )
		self.failUnless( len( persp.translate.p_outputs ) == 0 )
		
		cmds.undo()
		self.failUnless( persp.t.isConnectedTo( front.translate ) )
		
		# disconnect from 
		persp.t | front.translate
		self.failUnless( not persp.t & front.t )
		
		cmds.undo()
		self.failUnless( persp.t >= front.t )
		
		# COMPARISONS
		self.failUnless( persp.t != front.t )
		self.failUnless( persp.t.tx != persp.t.ty )
		
		# affected plugs
		affectedPlugs = persp.t.affects( )
		self.failUnless( len( affectedPlugs ) > 1  )
		
		affectedPlugs = persp.t.affected( )
		self.failUnless( len( affectedPlugs ) > 1  )
		
		
		# QUERY
		############################
		# ELEMENT ITERATION
		matworld.evaluateNumElements( )
		for elm in matworld:
			self.failUnless( elm.getParent( ) == matworld )
			
		translate = persp.translate
		
		self.failUnless( len( translate.getChildren() ) == translate.getNumChildren() )
						
		# CHILD ITERATION
		for child in translate.getChildren( ):
			self.failUnless( child.getParent( ) == translate )
		self.failUnless( len( translate.getChildren() ) == 3 )
			
		# SUB PLUGS GENERAL METHOD
		self.failUnless( len( matworld ) == len( matworld.getSubPlugs() ) )
		self.failUnless( translate.numChildren() == len( translate.getSubPlugs() ) )
		self.failUnless( len( translate.getSubPlugs() ) == 3 )
		
		
		# ARRAY CONNECTIONS
		###################
		objset = nodes.createNode( "set1", "objectSet" )
		partition = nodes.createNode( "partition1", "partition" )
		pma = nodes.createNode( "plusMinusAverage1", "plusMinusAverage" )
		destplug = persp.translate.connectToArray( pma.input3D, exclusive_connection = True )
		self.failUnless( persp.translate >= destplug )
		
		# exclusive connection should return exisiting plug
		self.failUnless( persp.translate.connectToArray( pma.input3D, exclusive_connection = True ) == destplug )
		
		# but newones can also be created
		self.failUnless( persp.translate.connectToArray( pma.input3D, exclusive_connection = False ) != destplug )
		#self.failUnless( objset.partition.connectToArray( partition.sets, exclusive_connection = False ) != destplug )

		
		# assure the standin classes are there - otherwise my list there would 
		# bind to the standins as the classes have not been created yet
		plugs = [ matworld, translate ]
		for plug in plugs: plug.getAttribute()

		# CHECK ATTRIBUTES and NODES
		for plug,attrtype in zip( plugs, [ nodes.TypedAttribute, nodes.NumericAttribute ] ):
			attr = plug.getAttribute( )
			
			self.failUnless( isinstance( attr, nodes.Attribute ) )
			self.failUnless( isinstance( attr, attrtype ) )
		                                                           
			node = plug.getNode()
			self.failUnless( isinstance( node, nodes.Node ) )
			self.failUnless( node == persp )
			
		# UNDO / REDO
		##############
		cmds.undoInfo( swf = 1 )
		cam = nodes.createNode( "myTrans", "transform" )
		testdb = [  ( cam.visibility, "Bool", True, False ),
					( cam.translate.tx, "Double", 0.0, 2.0 ) ]
		# TODO: Add all missing types ! 
		for plug, typename, initialval, targetval in testdb:
			getattrfunc = getattr( plug, "as"+typename )
			setattrfunc = getattr( plug, "set"+typename )
			
			self.failUnless( getattrfunc() == initialval )
			setattrfunc( targetval )
			self.failUnless( getattrfunc() == targetval )
			cmds.undo()
			self.failUnless( getattrfunc() == initialval )
			cmds.redo()
			self.failUnless( getattrfunc() == targetval )
		# END for each tuple in testdb 
	
	def test_matrixData( self ):
		"""byronimo.maya.nodes: test matrix data"""
		node = nodes.Node( "persp" )
		matplug = node.getPlug( "worldMatrix" )
		self.failUnless( not matplug.isNull() )
		self.failUnless( matplug.isArray() )
		matplug.evaluateNumElements()			# to assure we have something !
		
		self.failUnless( matplug.getName() == "persp.worldMatrix" )
		self.failUnless( len( matplug ) )
		
		matelm = matplug[0]
		self.failUnless( not matelm.isNull() )
		
		matdata = matelm.asMObject( )
		self.failUnless( isinstance( matdata, nodes.MatrixData ) )
		mmatrix = matdata.matrix( )
		self.failUnless( isinstance( mmatrix, api.MMatrix ) )
		
			
	def test_MPlugArray( self ):
		"""byronimo.maya.nodes: test the plugarray wrapper
		NOTE: plugarray can be wrapped, but the types stored will always be"""
		node = nodes.Node( "defaultRenderGlobals" )
		pa = node.getConnections( )
		
		myplug = pa[0]
		myplug.getName()				# special Plug method not available in the pure api object
		pa.append( myplug )
		pa[-1].getName()
		
		self.failUnless( len( pa ) == 4 )
		
		# SETITEM 
		l = 5
		pa.setLength( l )
		nullplug = pa[0]
		for i in range( l ):
			pa[i] = nullplug
				
		
		# __ITER__
		for plug in pa:			
			plug.getName( )
			self.failUnless( isinstance( plug, api.MPlug ) )
			
		self.failIf( len( pa ) != 5 )
		
