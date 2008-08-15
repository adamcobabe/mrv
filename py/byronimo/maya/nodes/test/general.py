"""B{byronimo.maya.nodes.test}

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
from byronimo.maya.test import get_maya_file
from byronimo.util import capitalize
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
		"""byronimo.maya.nodes: Test plug ( node.attribute ) """
		node = nodes.MayaNode( "defaultRenderGlobals" )
		# for attr in [ "resolution" ]:
	
	def test_matrixData( self ):
		"""byronimo.nodes: test matrix data"""
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
		
		l = 5
		pa.setLength( l )
		for i in range( l ):
			try:
				pa[i] = api.MPlug()
			except TypeError:
				pass # happens because of bug
			else:
				raise ValueError( "Wow, MPlugArray.set now works" )
		
		for plug in pa:			# test iterator
			plug.getName( )
			self.failUnless( isinstance( plug, api.MPlug ) )
			
		self.failIf( len( pa ) != 5 )
		
			
class TesNodeBase( unittest.TestCase ):
	""" Test node base functionality  """
	
	def test_wrapDepNode( self ):
		"""byronimo.maya.nodes: create and access dependency nodes ( not being dag nodes )"""
		node = nodes.MayaNode( "defaultRenderGlobals" )
		
		# string should be name		
		self.failUnless( str( node ) == node.getName( ) )
		repr( node )
		
		#node.object()
		
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
			
		
	def test_wrapDagNode( self ):
		"""byronimo.maya.nodes: create and access dag nodes"""


	def test_mfncachebuilder( self ):
		"""byroniom.maya.nodes.base: write a generated cache using the builder function"""
		#types.writeMfnDBCacheFiles( )
		
		
