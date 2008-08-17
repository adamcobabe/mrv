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
import byronimo.maya as bmaya
import byronimo.maya.env as env
import byronimo.maya.nodes as nodes
import byronimo.maya.nodes.types as types
from byronimotest.byronimo.maya import get_maya_file
from byronimo.util import capitalize,getPythonIndex
from byronimo.maya.util import StandinClass
import maya.cmds as cmds
import maya.OpenMaya as api

import time

class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """
	
	def test_testWrappers( self ):
		"""byronimo.maya.nodes: test wrapper class creation
		@note: we coulld dynamically create the nodes for testing using ls -nt, 
		but using a filecache is much faster - speed matters"""
		filename = "allnodetypes_%s.mb" % env.getAppVersion( )[0] 
		bmaya.Scene.open( get_maya_file( filename ), force=True )
		
		failedList = []
		for nodename in cmds.ls( ):
			try: 
				node = nodes.MayaNode( nodename )
			except TypeError:
				failedList.append( ( nodename, cmds.nodeType( nodename ) ) )
				
			self.failUnless( not node._apiobj.isNull() )
			
			# assure we have all the parents we need 
			parentClsNames = [ capitalize( typename ) for typename in cmds.nodeType( nodename, i=1 ) ]
			for pn in parentClsNames:
				pcls = getattr( nodes, pn )
				self.failUnless( isinstance( node, pcls ) )
			
		# END for each type in file 	
		
		if len( failedList ):
			nodecachefile = "nodeHierarchy_%s.html" % env.getAppVersion( )[0]
			raise TypeError( "Add the following node types to the %r cache file at the respective post in the hierarchy: %r" % ( nodecachefile, failedList ) )
		
		# try to just use a suberclass directly 
		for transname in cmds.ls( type="transform" ):
			node = nodes.DagNode( transname )
			self.failUnless( hasattr( node, "__dict__" ) )


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
		persp = nodes.MayaNode( "persp" )
		front	 = nodes.MayaNode( "front" )
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
		
		# CHECK CONNECTION FORCING  - already connected 
		persp.translate >  front.translate
		self.failUnlessRaises( RuntimeError, persp.scale.__gt__, front.translate )# lhs > rhs 
		
		
		
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
			
			
		# SUB PLUGS GENERAL METHOD
		self.failUnless( len( matworld ) == len( matworld.getSubPlugs() ) )
		self.failUnless( translate.numChildren() == len( translate.getSubPlugs() ) )


		# CHECK ATTRIBUTES and NODES
		for plug,attrtype in zip( [ matworld, translate ], [ nodes.TypedAttribute, nodes.NumericAttribute ] ):
			attr = plug.getAttribute( )
			self.failUnless( isinstance( attr, nodes.Attribute ) )
			self.failUnless( isinstance( attr, attrtype ) )
		                                                           
			node = plug.getNode()
			self.failUnless( isinstance( node, nodes.MayaNode ) )
			self.failUnless( node == persp )
			
		
	
	def test_matrixData( self ):
		"""byronimo.maya.nodes: test matrix data"""
		node = nodes.MayaNode( "persp" )
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
		node = nodes.MayaNode( "defaultRenderGlobals" )
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
		
			
class TesNodeBase( unittest.TestCase ):
	""" Test node base functionality  """
	
	def test_customTypes( self ):
		"""byronimo.maya.nodes: add a custom type to the system"""
		nodes.addCustomType( "MyNewCls",parentClsName = "dependNode" )
		# standin class should be there 
		cls = nodes.MyNewCls
		self.failUnless( isinstance( cls, StandinClass ) )
		self.failUnlessRaises( TypeError, cls, "persp" )	# class has incorrect type for persp 
		# NOTE: needed actual plugin type for proper test
	
	def test_wrapDepNode( self ):
		"""byronimo.maya.nodes: create and access dependency nodes ( not being dag nodes )"""
		node = nodes.MayaNode( "defaultRenderGlobals" )
		
		# string should be name		
		self.failUnless( str( node ) == node.getName( ) )
		repr( node )
		
		
		# must not have methods that require undo
		try: 
			node.create( "this" )
			node.setName( "this" )
		except AttributeError:
			pass
		except:
			raise		# could fail, but raise is better 
		
		# get simple attributes
		for attr in [ "preMel", "postMel" ]:
			plug = getattr( node, attr )
			self.failUnless( not plug.isNull() )
		
		# check connection methods 
		cons = node.getConnections( )
		self.failUnless( len( cons ) )
		
		
		# CHECK LAZY WRAPPING 
		# get mfn lazy wrapped attributes 
		t = node.getType()
		for state in [1,0]:			
			node.setLocked( state )
			self.failUnless( node.isLocked() == state )
		
		# ATTRIBUTES
		attr = node.getAttribute( 0 )
		attr.getName( )
		self.failUnless( not attr.isNull() )
		
		for i in xrange( node.attributeCount() ):
			attr = node.getAttribute( i )
			self.failUnless( not attr.isNull() )
			
		# CHECK namespaces - should be root namespace 
		ns = node.getNamespace( )
		self.failUnless( ns == nodes.Namespace.rootNamespace )
		
			
		
	def test_wrapDagNode( self ):
		"""byronimo.maya.nodes: create and access dag nodes"""


	def test_mfncachebuilder( self ):
		"""byroniom.maya.nodes.base: write a generated cache using the builder function"""
		#types.writeMfnDBCacheFiles( )
		
		
