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
import byronimo.maya.namespace as namespace
import byronimo.maya.nodes as nodes
import byronimo.maya.nodes.types as types
from byronimotest.byronimo.maya import get_maya_file
from byronimo.util import capitalize
from byronimo.maya.util import StandinClass
import maya.cmds as cmds

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
				node = nodes.Node( nodename )
			except TypeError:
				failedList.append( ( nodename, cmds.nodeType( nodename ) ) )
			except:
				raise 
				
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


	def test_createNodes( self ):
		"""byronimo.maya.nodes: create nodes with long names and namespaces"""
		names = ["hello","bla|world","this|world|here","that|this|world|here" ]
		nsnames = ["a:hello","blab|b:world","c:this|b:world","d:that|c:this|b:world|a:b:c:d:here"]
		types = [ "facade", "nurbsCurve", "nurbsSurface", "subdiv" ]
		
		# SIMPLE CREATION: Paths + nested namespaces
		for i in range( len( names ) ):
			ntype = types[i]
			newnode = nodes.createNode( names[i], ntype )
			self.failUnless( isinstance( newnode, getattr( nodes, capitalize( ntype ) ) ) )
			self.failUnless( newnode.isValid() and newnode.isAlive() )
			
			# test undo 
			cmds.undo()
			self.failUnless( not newnode.isValid() and newnode.isAlive() )
			cmds.redo()
			self.failUnless( newnode.isValid() and newnode.isAlive() )
		
			newnsnode = nodes.createNode( nsnames[i], ntype )
			self.failUnless( isinstance( newnsnode, getattr( nodes, capitalize( ntype ) ) ) )
			self.failUnless( newnsnode.isValid() and newnsnode.isAlive() )
			
			# test undo 
			cmds.undo()
			self.failUnless( not newnsnode.isValid() and newnsnode.isAlive() )
			cmds.redo() 
			self.failUnless( newnsnode.isValid() and newnsnode.isAlive() )
		# END for each created object 
		
		# EMPTY NAME and ROOT 
		self.failUnlessRaises( RuntimeError, nodes.createNode, '|', "facade" ) 
		self.failUnlessRaises( RuntimeError, nodes.createNode, '', "facade" )
		
		
		# CHECK DIFFERENT ROOT TYPES 
		depnode = nodes.createNode( "blablub", "facade" )
		self.failUnlessRaises( NameError, nodes.createNode, "|blablub|:this", "transform", renameOnClash = False )
		
		# DIFFERENT TYPES AT END OF PATH
		nodes.createNode( "this|mesh", "mesh" )
		self.failUnlessRaises( NameError, nodes.createNode, "this|mesh", "nurbsSurface" )
		
		# renameOnClash  - it fails if the dep node exists first
		nodes.createNode( "node", "facade" )
		self.failUnlessRaises( NameError, nodes.createNode, "this|that|node", "mesh", renameOnClash = False )
		
		# obj exists should match dg nodes with dag node like path ( as they occupy the same 
		# namespace after all
		self.failUnless( nodes.objExists( "|node" ) )
		
		# it also clashes if the dg node is created after a  dag node with the same name
		nodes.createNode( "that|nodename", "mesh" )
		self.failUnlessRaises( NameError, nodes.createNode, "nodename", "facade", renameOnClash = False )	
		
		
		# it should be find to have the same name in several dag levels though !
		nodes.createNode( "parent|nodename", "transform" )
		nodes.createNode( "parent|nodename|nodename", "mesh" )
		nodes.createNode( "otherparent|nodename|nodename", "mesh" )
		
		
	def test_objectExistance( self ):
		"""byronimo.maya.nodes: check whether we can properly handle node exist checks"""
		depnode = nodes.createNode( "node", "facade" )
		self.failUnless( nodes.objExists( str( depnode ) ) )
		
		dagnode = nodes.createNode( "parent|node", "mesh" )
		self.failUnless( nodes.objExists( str( dagnode ) ) )
		
		# must clash with dg node ( in maya, dg nodes will block names of dag node leafs ! )
		self.failUnlessRaises( NameError, nodes.createNode, "parent|node|node", "mesh", renameOnClash=False )
		
		# same clash occours if dag node exists first 
		dagnode = nodes.createNode( "parent|othernode", "transform" )
		self.failUnlessRaises( NameError, nodes.createNode, "othernode", "facade", renameOnClash=False )
		
		
	def test_dagPathVSMobjects( self ):
		"""byronimo.maya.nodes: if mobjects where used internally, this test would fail"""
		node = nodes.createNode( "parent|middle|child", "transform" )
		nodem = nodes.Node( "parent|middle" )
		
		instargs = { 'asInstance' : 1, 'instanceLeafOnly' : 1 }
		instnode = node.duplicate( "child", **instargs )
		instnodem = nodem.duplicate( "middle", **instargs )
		
		path = instnode.getDagPath( )
		childm1 = nodes.Node( "parent|middle1|child" )
		
		# if it didnt work, he would have returned a "|parent|middle|child" 
		self.failUnless( "|parent|middle1|child" == str(childm1) ) 
		
		npath = node.getDagPath( )
		ipath = instnode.getDagPath( )
		
		
class TestNodeBase( unittest.TestCase ):
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
		node = nodes.Node( "defaultRenderGlobals" )
		
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
		
		
		# DEPENDENCY INFO
		persp = nodes.Node( "persp" )
		affected_attrs = persp.affects( "t" )
		self.failUnless( len( affected_attrs ) > 1 )
		affected_attrs = persp.affected( "t" )
		self.failUnless( len( affected_attrs ) > 1 )
		
		
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
		
		
		# RENAME DEP NODES
		######################
		node = nodes.createNode( "mynode", "facade" )
		renamed = node.rename( "myrenamednode" )
		
		self.failUnless( renamed == "myrenamednode" )
		self.failUnless( node == renamed )
		
		# undo - redo
		cmds.undo()
		self.failUnless( node == "mynode" )
		cmds.redo()
		self.failUnless( node == "myrenamednode" )
		
		
		# trigger namespace error
		self.failUnlessRaises( RuntimeError, node.rename, "nsdoesnotexist:othername", autocreateNamespace = False )
		
		# now it should work
		node.rename( "nsdoesnotexist:othername", autocreateNamespace=True )
		
		# multi undo - namespace is one operation in this one 
		cmds.undo()
		self.failUnless( not namespace.exists( "nsdoesnotexist" ) )
		cmds.redo()
		self.failUnless( node.isValid() )
		
		
		# rename to same name 
		renamed = node.rename( "nsdoesnotexist" )	# should be fine
		self.failUnless( renamed == node )
		
		# othernode with different type exists
		othernode = nodes.createNode( "othernode", "groupId" )
		self.failUnlessRaises( RuntimeError, node.rename, "othernode", renameOnClash = False )
		
		# works if rename enabeld though
		node.rename( "othernode" )
		
		
		
	def test_wrapDagNode( self ):
		"""byronimo.maya.nodes: create and access dag nodes"""
		mesh = nodes.createNode( "parent|mesh", "mesh" )
		parent = mesh.getParent( )
		
		# simple rename 
		mesh.rename( "fancymesh" )
		
		
		# simple dupl test 
		duplbase = nodes.createNode( "parent|this|other|duplbase", "mesh" )
		copy = duplbase.duplicate( "parent|this|other|duplcopy" )
		self.failUnless( copy != duplbase )
		self.failUnless( str( copy ) != str( duplbase ) )
		self.failUnless( str( copy ) == "|parent|this|other|duplcopy" )
		
		
		# simple reparent 
		otherparent = nodes.createNode( "oparent", "transform" )
		mesh.reparent( otherparent )
		
		# REPARENT UNDO TEST
		cmds.undo()
		self.failUnless( mesh.getParent() == parent )
		cmds.redo()
		self.failUnless( mesh.getParent() == otherparent )
		
		
		
		# REPARENT RENAME CLASH  
		origmesh = nodes.createNode( "parent|fancymesh", "mesh" )			#  "|parent|fancymesh"
		self.failUnlessRaises( RuntimeError, mesh.reparent, parent , renameOnClash = False ) 
		
		# RENAME CLASH DAG NODE 
		othermesh = nodes.createNode( "parent|mesh", "mesh" )
		self.failUnlessRaises( RuntimeError, origmesh.rename, "mesh", renameOnClash = False )
		
		# now it works
		othermesh.rename( "mesh", renameOnClash = True )
		self.failUnless( othermesh.getBasename( ) == "mesh" )
		
		
		# shape under root 
		self.failUnlessRaises( RuntimeError, mesh.reparent, None )
		
		# REPARENT AGAIN
		# should just work as the endresult is the same 
		mesh.reparent( otherparent )	# it will also trigger a new undo event, so undo will react as it should
		mesh.reparent( otherparent )	#  "|otherparent|fancymesh"
		
		# REPARENT UNDER SELF
		self.failUnlessRaises( RuntimeError, mesh.reparent, mesh )
		
		
		# OBJECT NAVIGATION
		#######################
		# TODO: navigate the object properly 
		
		
		
		
		# DUPLICATE ( Dag only )
		#########################
		newmesh = mesh.duplicate( "|duplparent|duplmesh" )
		self.failUnless( str( newmesh ) == "|duplparent|duplmesh" )
		self.failUnlessRaises( RuntimeError, mesh.duplicate, "|duplparent2|doesntexistns:duplmesh", 
							  	autocreateNamespace = False )
		self.failUnless( newmesh != mesh )
		meshinst = mesh.duplicate( "|duplparent2|newnamespace:instmesh", asInstance=True )
		meshinstname = str( meshinst )
		
		# UNDO DUPLICATE
		#################   
		cmds.undo()
		
		# this object will end up pointing to the same object , as it came from, use string test
		self.failUnless( not nodes.objExists( meshinstname ) )		 
		cmds.redo()
		cmds.undo()
		cmds.redo()
		self.failUnless( meshinst != mesh )
		self.failUnless( meshinst.isAlive() and meshinst.isValid() and str( meshinst ) == meshinstname )
		
		# Duplicate TRANSFORM ( just a name givne )
		# dag paths should be different although object is the same
		mesh = nodes.createNode( "|parent|mybeautifuluniquemeshname", "mesh" )
		meshassert = nodes.createNode( "|parent|mesh", "mesh" )
		meshself = nodes.Node( "|parent|mybeautifuluniquemeshname" )
		self.failUnless( mesh == meshself )
		
		# connect it, to track the instance by connection 
		persp = nodes.Node( "persp" )
		perspplug = persp.t.tx
		triplug = meshself.maxTriangles
		perspplug >> triplug 
		
		# shapes must have full paths
		self.failUnlessRaises( NameError, mesh.duplicate, "newns:meshinst" , asInstance=True, instanceLeafOnly=True )
		
		# cannot parent instance under itself
		self.failUnlessRaises( NameError, mesh.duplicate, str( mesh.getTransform() ), asInstance=True, instanceLeafOnly=True )
		
		# but should work if not an instance
		meshdupl = mesh.duplicate( str( mesh.getTransform() ) )
		
		meshinstname = mesh.getTransform().getFullChildName( "newns:meshinst" )
		meshinst = mesh.duplicate( meshinstname  , asInstance=True, instanceLeafOnly=True )
		self.failUnless( isinstance( meshinst, nodes.Mesh ) )
		self.failUnless( mesh != meshinst )
		
		# instance should have the persp.t connected
		self.failUnless( perspplug >= triplug )
		self.failUnless( perspplug >= meshinst.maxTriangles )
		self.failUnless( meshinst._apiobj == mesh._apiobj )
		


	def test_mfncachebuilder( sself ):
		"""byroniom.maya.nodes.base: write a generated cache using the builder function"""
		pass
		#types.writeMfnDBCacheFiles( )
		
		
