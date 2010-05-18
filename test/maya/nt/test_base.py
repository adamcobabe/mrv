# -*- coding: utf-8 -*-
""" Test general nodes features """
from mrv.test.maya import *
import mrv.maya as mrvmaya
import mrv.maya.env as env
import mrv.maya.ns as nsm
import mrv.maya.nt as nt
import mrv.maya.nt.storage as mstorage
from mrv.maya.util import MEnumeration
from mrv.maya.nt.persistence import PyPickleData
from mrv.test.maya import get_maya_file
from mrv.util import capitalize, uncapitalize
from mrv.path import Path

import maya.cmds as cmds
import maya.OpenMaya as api

import sys

# require persistence
nt.enforcePersistence()

class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """
	
	@with_undo
	def test_tranformation_overrides(self):
		p = nt.Node('persp')
		getters = ('getScale', 'getShear')
		setters = ('setScale', 'setShear')
		def cmp_val(lhs, rhs, loose):
			if loose:
				assert lhs != rhs
			else:
				assert lhs == rhs
		# END util
		
		def assert_values(fgetname, fsetname, loose):
			getter = getattr(p, fgetname)
			v = getter()
			assert isinstance(v, api.MVector)
			
			nv = api.MVector(i+v.x+1.0, i+v.y+2.0, i+v.z+3.0)
			getattr(p, fsetname)(nv)
			
			cmp_val(nv, getter(), loose)
			
			cmds.undo()
			cmp_val(v, getter(), loose)
			cmds.redo()
			cmp_val(nv, getter(), loose)
		# END utility
		
		for i,(fgetname, fsetname) in enumerate(zip(getters, setters)):
			assert_values(fgetname, fsetname, loose=False)
		# END for each fname
		
		setters = ("scaleBy", "shearBy")
		for i,(fgetname, fsetname) in enumerate(zip(getters, setters)):
			assert_values(fgetname, fsetname, loose=True)
		# END for each name
	
	def test_apipatch_not_globally_applied(self):
		p = nt.Node("persp")
		assert hasattr(p.t, 'mconnectTo')	  # has our namespace
		assert not hasattr(p.t, 'connectTo') # but not global namespace
		
	def test_Node_type_has_no_metaclass_members(self):
		# this happens if the metaclass has any members - the typ itself will
		# be of type MetaClas, instead of type, which makes it inherit all attriutes
		assert not hasattr(nt.Node, 'nameToTreeMap')	# has dg and dag nodes
		
	@with_persistence
	@with_scene('empty.ma')
	def test_plugin_handling(self):
		mrp = "Mayatomr"
		pp = 'persistence'
		assert not cmds.pluginInfo(mrp, q=1, loaded=1)
		
		assert not hasattr(nt, 'Transmat')
		cmds.loadPlugin(mrp)
		
		# loading a plugin will add the node types
		assert hasattr(nt, 'Transmat')
		assert nt.typ.nodeTypeTree.has_node('transmat')
		tmat = nt.Transmat()	# mr dep node
		tmat.delete()
		
		dll = nt.MapVizShape()	# mr dag node
		assert isinstance(dll, nt.DagNode)
		dll.delete()
		cmds.flushUndo()	# make sure we get rid of the custom data
		
		
		# custom node types are favored and not overwritten by dummies when 
		# loading
		assert nt.StorageNode is mstorage.StorageNode
		
		# custom node types will remain when unloaded
		cmds.unloadPlugin(pp)
		assert not cmds.pluginInfo(pp, q=1, loaded=1) 
		assert hasattr(nt, 'StorageNode')
		
		# unloading a plugin will remove the nodetypes as well as the hierarchy 
		# entries
		# NOTE: on OSX unloading the plugin beautifully crashes maya, probably
		# a memory exception as MR claims to have had a peak memory of 136 GB
		# As a final goal, this test should be fixed to run here, there 
		# probably is some kind of workaround.
		# http://tracking.byronimo.de/view.php?id=144
		if sys.platform != 'darwin':
			cmds.unloadPlugin(mrp, force=1)
			
			assert not hasattr(nt, 'Transmat')
			assert not hasattr(nt, 'MapVizShape')
			assert not nt.typ.nodeTypeTree.has_node('transmat')
			assert not nt.typ.nodeTypeTree.has_node('mapVizShape')
		
	
			# plugins required by a scene trigger the database to update as well
			assert not cmds.pluginInfo(mrp, q=1, loaded=1)
			mrvmaya.Scene.open(get_maya_file('needsMayatomr.ma'), force=True)
			assert hasattr(nt, 'Transmat')
		# END skip this on osx 
		
		# dynamically added types ( which will not trigger a plugin changed event )
		# can be wrapped as well
		customMI = get_maya_file('customshader.mi')
		csn = "testCustomShader"
		csnc = "TestCustomShader"
		mrvmaya.Mel.mrFactory('-load',customMI)
		
		# it doesnt exist, but can be wrapped nontheless, then it exists
		assert not hasattr(nt, csnc)
		cs = nt.Node(cmds.createNode(csn))
		assert hasattr(nt, csnc)
		
	@with_undo
	def test_create_nodes(self):
		# create all types of nodes, just individual samples, assure createNode
		# gets it right
		pe = nt.PointEmitter()
		assert pe.parent() is None
		
		# a shape with just a shortname works as well
		m = nt.createNode("myMesh", "mesh")
		mp = m.parent()
		assert isinstance(mp, nt.Transform)
		
		cmds.undo()
		cmds.undo()
		
		assert pe.isAlive() and not pe.isValid()
		assert mp.isAlive() and not mp.isValid()
		assert m.isAlive() and not m.isValid()
		
		cmds.redo()
		assert pe.isValid()
		
		cmds.redo()
		assert m.isValid() and mp.isValid()
		
	@with_undo
	def test_createNodes( self ):
		names = ["hello","bla|world","this|world|here","that|this|world|here" ]
		nsnames = ["a:hello","blab|b:world","c:this|b:world","d:that|c:this|b:world|a:b:c:d:here"]
		types = [ "facade", "nurbsCurve", "nurbsSurface", "subdiv" ]

		# SIMPLE CREATION: Paths + nested namespaces
		for i in range( len( names ) ):
			ntype = types[i]
			newnode = nt.createNode( names[i], ntype )
			assert isinstance( newnode, getattr( nt, capitalize( ntype ) ) ) 
			assert newnode.isValid() and newnode.isAlive() 

			# test undo
			cmds.undo()
			assert not newnode.isValid() and newnode.isAlive() 
			cmds.redo()
			assert newnode.isValid() and newnode.isAlive() 

			newnsnode = nt.createNode( nsnames[i], ntype )
			assert isinstance( newnsnode, getattr( nt, capitalize( ntype ) ) ) 
			assert newnsnode.isValid() and newnsnode.isAlive() 

			# test undo
			cmds.undo()
			assert not newnsnode.isValid() and newnsnode.isAlive() 
			cmds.redo()
			assert newnsnode.isValid() and newnsnode.isAlive() 
		# END for each created object

		# EMPTY NAME and ROOT
		self.failUnlessRaises( RuntimeError, nt.createNode, '|', "facade" )
		self.failUnlessRaises( RuntimeError, nt.createNode, '', "facade" )


		# CHECK DIFFERENT ROOT TYPES
		depnode = nt.createNode( "blablub", "facade" )
		self.failUnlessRaises( NameError, nt.createNode, "|blablub|:this", "transform", renameOnClash = False )

		# DIFFERENT TYPES AT END OF PATH
		nt.createNode( "this|mesh", "mesh" )
		self.failUnlessRaises( NameError, nt.createNode, "this|mesh", "nurbsSurface", forceNewLeaf = False )

		# renameOnClash  - it fails if the dep node exists first
		nt.createNode( "node", "facade" )
		self.failUnlessRaises( NameError, nt.createNode, "this|that|node", "mesh", renameOnClash = False )

		# obj exists should match dg nodes with dag node like path ( as they occupy the same
		# namespace after all
		assert nt.objExists( "|node" ) 

		# it also clashes if the dg node is created after a  dag node with the same name
		nt.createNode( "that|nodename", "mesh" )
		self.failUnlessRaises( NameError, nt.createNode, "nodename", "facade", renameOnClash = False )


		# it should be fine to have the same name in several dag levels though !
		newmesh = nt.createNode( "parent|nodename", "transform" )
		newmesh1 = nt.createNode( "parent|nodename|nodename", "mesh" )
		newmesh2 = nt.createNode( "otherparent|nodename|nodename", "mesh" )
		assert newmesh != newmesh1 
		assert newmesh1 != newmesh2 

		# FORCE NEW
		##############
		oset = nt.createNode( "objset", "objectSet", forceNewLeaf = False )
		newoset = nt.createNode( "objset", "objectSet", forceNewLeaf = True )
		assert oset != newoset 

		# would expect same set to be returned
		sameoset = nt.createNode( "objset", "objectSet", forceNewLeaf = False )
		assert sameoset == oset 

		# force new and dag paths
		newmesh3 = nt.createNode( "otherparent|nodename|nodename", "mesh", forceNewLeaf = True )
		assert newmesh3 != newmesh2 



	def test_objectExistance( self ):
		depnode = nt.createNode( "node", "facade" )
		assert nt.objExists( str( depnode ) ) 

		# TEST DUPLICATION
		duplnode = depnode.duplicate( )
		assert duplnode.isValid( ) 

		copy2 = depnode.duplicate( "name2" )
		assert str( copy2 ) == "name2" 
		# NOTE: currently undo is not opetional

		dagnode = nt.createNode( "parent|node", "mesh" )
		assert nt.objExists( str( dagnode ) ) 

		# must clash with dg node ( in maya, dg nodes will block names of dag node leafs ! )
		self.failUnlessRaises( NameError, nt.createNode, "parent|node|node", "mesh", renameOnClash=False )

		# same clash occours if dag node exists first
		dagnode = nt.createNode( "parent|othernode", "transform" )
		self.failUnlessRaises( NameError, nt.createNode, "othernode", "facade", renameOnClash=False )


	def test_dagPathVSMobjects( self ):
		node = nt.createNode( "parent|middle|child", "transform" )
		nodem = nt.Node( "parent|middle" )

		duplnodemiddle = nodem.duplicate( "middle1" )
		instnode = duplnodemiddle.addInstancedChild( node )


		assert instnode.object() == node.object()  # compare mobject
		assert instnode != node 		# compare dag paths

		path = instnode.dagPath( )
		childm1 = nt.Node( "parent|middle1|child" )

		# if it didnt work, he would have returned a "|parent|middle|child"
		assert "|parent|middle1|child" == str(childm1) 

		npath = node.dagPath( )
		ipath = instnode.dagPath( )
		
		assert npath != ipath
		assert node.object() == instnode.object()	# same object after all
		
		# if an MObject is passed in, it should still work
		assert node == instnode.object()
		
		# using an attribute would create a DagNode which corresponds to the first path
		assert not node != instnode.wm.mwrappedNode()
		assert node == instnode.wm.mwrappedNode()


	@with_undo
	def test_convenienceFunctions( self ):
		# SELECTION
		############
		nt.select( "persp" )
		persp = nt.selection()[0]
		assert persp == nt.Node( "persp" ) 

		# clear selection
		nt.select( )
		assert not nt.selection() 
		
		# undo/redo
		cmds.undo()
		assert len(nt.selection()) == 1
		cmds.redo()
		assert len(nt.selection()) == 0

		# select object and selection list
		nt.select( persp )
		assert len( nt.selection( ) ) == 1 
		nt.select( nt.toSelectionList( nt.selection( ) ) )
		assert len( nt.selection( ) ) == 1 

		# select mixed
		nt.select( persp, "front" )
		assert len( nt.selection( ) ) == 2 


		# GET BY NAME
		###############
		persp = nt.findByName( "pers*" )[0]
		assert persp == nt.Node( "persp" ) 
		
		# filter selection
		##################
		nt.select("persp", "perspShape")
		assert len(nt.selection(api.MFn.kCamera)) == 1
		assert len(list(nt.iterSelection(api.MFn.kCamera))) == 1
		
		sl = nt.activeSelectionList()
		assert len(sl) and isinstance(sl, api.MSelectionList)


class TestNodeBase( unittest.TestCase ):
	""" Test node base functionality  """

	def setUp( self ):
		"""Create a new scene to assure we do not resue nodes or configuration"""
		cmds.file( new=1,force=1 )

	def test_customTypes( self ):
		nt.addCustomType( "MyNewCls",parentClsName = "dependNode" )
		# standin class should be there
		cls = nt.MyNewCls
		self.failUnlessRaises( TypeError, cls, "persp" )	# class has incorrect type for persp
		# NOTE: needed actual plugin type for proper test

	def test_hashfunc( self ):
		"""byroimo.maya.nt: should be possible to use objects as keys in hashes"""
		# they must compare their objects for equality, not their own instance
		ddg = dict()
		for i in range( 10 ):		# dg nodes
			ddg[ nt.Node( "initialShadingGroup" ) ] = i

		assert len( ddg ) == 1 

		ddag = dict()
		for i in range( 10 ):		# dg nodes
			ddag[ nt.Node( "persp" ) ] = i

		assert len( ddag ) == 1 

		# merge both together
		dall = dict()
		dall.update( ddg )
		dall.update( ddag )
		assert len( dall ) == 2 


	@with_undo
	def test_wrapDepNode( self ):
		node = nt.Node( "defaultRenderGlobals" )

		# SKIP CHECKS TEST
		self.failUnlessRaises( ValueError, nt.Node, "this" )	# does not exist
		# results inconsitent between maya 8.5 and 2008, thus we skip it as it is not of much value
		# self.failUnlessRaises( TypeError, nt.Node, "this", 1 )  # skip check , maya throws

		# string should be name
		assert str( node ) == node.name( ) 
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
			assert plug == getattr( node, attr )
			assert plug == node.findPlug(attr)
			assert not plug.isNull() 

		# check connection methods
		cons = node.connections( )
		assert len( cons ) 


		# DEPENDENCY INFO
		persp = nt.Node( "persp" )
		affected_attrs = persp.dependencyInfo( "t", by=0 )
		assert len( affected_attrs ) > 1 
		affected_attrs = persp.dependencyInfo( "t", by=1 )
		assert len( affected_attrs ) > 1 
		assert isinstance(affected_attrs[0], nt.Attribute)


		# CHECK LAZY WRAPPING
		# get mfn lazy wrapped attributes
		t = node.attributeCount()
		for state in [1,0]:
			node.setLocked( state )
			assert node.isLocked() == state 

		# ATTRIBUTES
		attr = node.attribute( 0 )
		attr.name( )
		assert not attr.isNull() 

		for i in xrange( node.attributeCount() ):
			attr = node.attribute( i )
			assert not attr.isNull()  and attr.name()

		# CHECK namespaces - should be root namespace
		ns = node.namespace( )
		assert ns == nt.Namespace.rootpath 
		

		# RENAME DEP NODES
		######################
		node = nt.createNode( "mynode", "facade" )
		renamed = node.rename( "myrenamednode" )

		assert renamed.name() == "myrenamednode" 
		assert node == renamed 

		# undo - redo
		cmds.undo()
		assert node.name() == "mynode" 
		cmds.redo()
		assert node.name() == "myrenamednode" 


		# trigger namespace error
		self.failUnlessRaises( RuntimeError, node.rename, "nsdoesnotexist:othername", autocreateNamespace = False )

		# now it should work
		node.rename( "nsdoesnotexist:othername", autocreateNamespace=True )

		# multi undo - namespace is one operation in this one
		cmds.undo()
		assert not nsm.existsNamespace( "nsdoesnotexist" ) 
		cmds.redo()
		assert node.isValid() 


		# rename to same name
		renamed = node.rename( "nsdoesnotexist" )	# should be fine
		assert renamed == node 

		# othernode with different type exists
		othernode = nt.createNode( "othernode", "groupId" )
		self.failUnlessRaises( RuntimeError, node.rename, "othernode", renameOnClash = False )

		# locking
		othernode.setLocked( 1 )
		assert othernode.isLocked()
		cmds.undo( )
		assert not othernode.isLocked()
		cmds.redo()
		assert othernode.isLocked()
		othernode.setLocked( 0 )
		assert not othernode.isLocked()

		# works if rename enabeld though
		node.rename( "othernode" )
		
	def test_namespace_adjustment(self):
		dag = nt.Transform()
		dg = nt.Network()
		
		childns = nsm.Namespace.create(":foo:bar")
		parentns = childns.parent()
		for node in (dag, dg):
			assert node.namespace() == nsm.RootNamespace
			assert isinstance(node.setNamespace(childns), nt.Node)
			
			assert node.namespace() == childns
			assert node.setNamespace(parentns).namespace() == parentns
			assert node.setNamespace(nsm.RootNamespace).namespace() == nsm.RootNamespace
		# END for each node
		

	def test_reparentAndInstances( self ):
		mesh = nt.createNode( "trans|mesh", "mesh" )
		base = nt.createNode( "base|subbase", "transform" )
		obase = nt.createNode( "obase|subbase2", "transform" )
		rbase = nt.createNode( "reparentBase", "transform" )

		# test basic functions
		assert rbase.apiType() == api.MFn.kTransform 
		assert rbase.hasFn( api.MFn.kTransform ) 

		baseinst = base.addInstancedChild( mesh )
		obaseinst = obase.addInstancedChild( mesh )

		# try to re-wrap the instanced items
		assert nt.Node( str( baseinst ) ) == baseinst
		assert nt.Node( str( obaseinst ) ) == obaseinst

		# use partial name
		assert nt.Node( "subbase|mesh" ) == baseinst
		assert nt.Node( "subbase2|mesh" ) == obaseinst

		assert mesh.isValid() and baseinst.isValid() and obaseinst.isValid() 

		# assure we catch this possibly damaage
		self.failUnlessRaises( RuntimeError, mesh.reparent, rbase, raiseOnInstance=True )

		# instances are gone should be gone
		mesh = mesh.reparent( rbase, raiseOnInstance=False )
		assert mesh.isValid() and not baseinst.isValid() and not obaseinst.isValid() 
		
		# try unparent
		meshtrans = mesh.transform()
		meshtrans.setParent(obase)
		assert meshtrans.parent() == obase
		meshtrans.unparent()
		assert meshtrans.parent() is None

	def test_duplicateInstances( self ):
		base = nt.createNode( "base", "transform" )
		obase = nt.createNode( "obase", "transform" )
		basemesh = nt.createNode( "base|mesh", "mesh" )

		obasemeshinst = obase.addInstancedChild( basemesh )

		duplmesh = obasemeshinst.duplicate( "newmeshname" )	# is a separate copy !
		assert duplmesh != obasemeshinst 

		dupltrans = base.duplicate( "duplbase" )
		baseduplmesh = dupltrans.childrenByType( nt.Mesh )[0]
		assert baseduplmesh != basemesh 		# its a separate copy

	def test_wrapping(self):
		# from string
		p = nt.Node("persp")
		
		# it tries to access it like an APIObj - no type checks done here
		self.failUnlessRaises(AttributeError, nt.NodeFromObj, "persp")
		
		# we don't accept other Nodes - it makes no sense and should be fixed
		self.failUnlessRaises(TypeError, nt.Node, p)
		
		# works, but first mfn access fails !
		pfail = nt.NodeFromObj(p)
		
		# oh look, how inconsistent the wrap is :) ... 
		try:
			pfail.findPlug('wm')
		except (RuntimeError, TypeError, NotImplementedError):
			# yes, it actually throws all kinds of different exceptions 
			# depending on the OS and the maya version
			pass
		else:
			self.fail("Expected exception")
		# END exception handling
		

	@with_undo
	def test_wrapDagNode( self ):
		mesh = nt.createNode( "parent|mesh", "mesh" )
		parent = mesh.parent( )

		# simple rename
		mesh.rename( "fancymesh" )


		# simple dupl test
		duplbase = nt.createNode( "parent|this|other|duplbase", "mesh" )
		transcopy = duplbase.transform( ).duplicate()
		copy = duplbase.duplicate( "parent|this|other|duplcopy" )
		assert copy != duplbase 
		assert str( copy ) != str( duplbase ) 
		assert str( copy ) == "|parent|this|other|duplcopy" 

		# TEST ADDITIONAL OPTIONS
		for i in range( 1,3 ):
			ocopy = duplbase.duplicate(  )
			assert str( ocopy ) == str( duplbase ) + str( i ) 

			ocopy = duplbase.duplicate( newTransform=1 )
			assert ocopy.basename( ) == duplbase.basename() 
			assert str( ocopy.parent() ) == str( duplbase.parent() ) + str( i + 1 ) 

			# undo both duplications and redo
			# CRASHES MAYA AFTER REDO
			# and if someone tries to access an object already created
			#cmds.undo()
			#cmds.undo()
			#assert duplbase.isValid() 
			#cmds.redo()
			#cmds.redo()
		# END for each copy


		# simple reparent
		otherparent = nt.createNode( "oparent", "transform" )
		mesh.reparent( otherparent )

		# REPARENT UNDO TEST
		cmds.undo()
		assert mesh.parent() == parent 
		cmds.redo()
		assert mesh.parent() == otherparent 



		# REPARENT RENAME CLASH
		origmesh = nt.createNode( "parent|fancymesh", "mesh" )			#  "|parent|fancymesh"
		self.failUnlessRaises( RuntimeError, mesh.reparent, parent , renameOnClash = False )

		# RENAME CLASH DAG NODE
		othermesh = nt.createNode( "parent|mesh", "mesh" )
		self.failUnlessRaises( RuntimeError, origmesh.rename, "mesh", renameOnClash = False )

		# now it works
		othermesh.rename( "mesh", renameOnClash = True )
		assert othermesh.basename( ) == "mesh" 


		# shape under root
		self.failUnlessRaises( RuntimeError, mesh.reparent, None )

		# REPARENT AGAIN
		# should just work as the endresult is the same
		mesh.reparent( otherparent )	# it will also trigger a new undo event, so undo will react as it should
		mesh.reparent( otherparent )	#  "|otherparent|fancymesh"

		# REPARENT UNDER SELF
		self.failUnlessRaises( RuntimeError, mesh.reparent, mesh )

		# reparent transform to world
		wtrans = nt.createNode( "parent2|worldtrans", "transform" )
		parent = nt.Node( "parent2" )
		oparent = nt.createNode( "oparent2", "transform" )
		wtrans = wtrans.reparent( None )

		wtransnewparent = wtrans.setParent( parent )
		assert wtrans == wtransnewparent
		assert wtransnewparent.instanceCount( 1 ) == 1 
		wtransnewparent.addParent( oparent )
		assert wtransnewparent.instanceCount( 1 ) == 2 
		wtransnewparent.removeParent( oparent )
		assert wtrans.instanceCount( 1 ) == 1 



		# OBJECT NAVIGATION
		#######################
		# TODO: navigate the object properly




		# DUPLICATE ( Dag only )
		#########################
		newmesh = mesh.duplicate( "|duplparent|duplmesh" )
		assert str( newmesh ) == "|duplparent|duplmesh" 
		self.failUnlessRaises( RuntimeError, mesh.duplicate, "|duplparent2|doesntexistns:duplmesh",
							  	autocreateNamespace = False )
		assert newmesh != mesh 
		instbase = nt.createNode( "|duplparent2|newnamespace:instmesh", "transform" )
		meshinst = instbase.addInstancedChild( mesh )
		meshinstname = str( meshinst )

		# UNDO DUPLICATE
		#################
		cmds.undo()

		# this object will end up pointing to the same object , as it came from, use string test
		assert not nt.objExists( meshinstname ) 
		cmds.redo()
		cmds.undo()
		cmds.redo()
		assert meshinst != mesh 
		assert meshinst.isAlive() and meshinst.isValid() and str( meshinst ) == meshinstname 

		# Duplicate TRANSFORM ( just a name given )
		# dag paths should be different although object is the same
		mesh = nt.createNode( "|parent|mybeautifuluniquemeshname", "mesh" )
		meshassert = nt.createNode( "|parent|mesh", "mesh" )
		meshself = nt.Node( "|parent|mybeautifuluniquemeshname" )
		assert mesh == meshself 

		# connect it, to track the instance by connection
		persp = nt.Node( "persp" )
		perspplug = persp.t.mchildByName('tx')
		triplug = meshself.maxTriangles
		perspplug.mconnectTo(triplug)

		# target does exist
		# this is blocking the target instance name with an incorrect type
		nt.createNode( "parent|this|mybeautifuluniquemeshname", "transform" )
		self.failUnlessRaises( RuntimeError, mesh.duplicate, "|parent|this" )

		# if the path is too short ...
		self.failUnlessRaises( NameError, mesh.duplicate, str( mesh.transform() ) )
		self.failUnlessRaises( NameError, mesh.parent().duplicate, '|' )


		meshinstname = mesh.transform().fullChildName( "newns:meshinst" )
		assert isinstance( meshinst, nt.Mesh ) 

	@with_undo
	def test_removeChild( self ):
		base = nt.createNode( "base" , "transform" )
		trans = nt.createNode( "base|trans", "transform" )
		mesh = nt.createNode( "base|mesh", "mesh" )

		for item in [ trans, mesh ]:
			removeditem = base.removeChild( item, allowZeroParents=True )

			# PATHS ARE INVALID NOW - object is nowhere to be found
			assert not removeditem.isValid() and removeditem.isAlive() 

			cmds.undo()
			assert removeditem.isValid() and removeditem.isAlive() 
		# END for each removeChild item


	def test_dependnode_getitem( self ):
		mesh = nt.createNode( "p1|p2|mesh", "mesh" )
		assert len( list( mesh.iterParents() ) ) == 2 
		p2 = mesh.parent()
		p1 = p2.parent()
		assert mesh[-1] == p2 
		assert mesh[-2] == p1 
		self.failUnlessRaises( IndexError, mesh.__getitem__, -3 )

	@with_undo
	def test_childEditing( self ):
		base = nt.createNode( "basenode", "transform" )
		obase = nt.createNode( "otherbasenode", "transform" )

		trans = nt.createNode( "trans", "transform" )
		otrans = nt.createNode( "parent|trans", "transform" )
		mesh = nt.createNode( "meshparent|meshshape", "mesh" )
		curve = nt.createNode( "nurbsparent|ncurve", "nurbsCurve" )
		itemlist = [ trans, mesh, curve ]

		instlist = []

		# MULTIPLE ADDS
		####################
		# Returns the same instance - its what the user wants
		for item in itemlist:
			baseiteminst = base.addInstancedChild( item )
			base.addInstancedChild( item )
			assert item != baseiteminst and baseiteminst.isValid() and item.isValid() 

			instlist.append( baseiteminst )

			# UNDO TEST
			# undo basemesh
			cmds.undo()
			cmds.undo()
			assert not baseiteminst.isValid() and baseiteminst.isAlive() 

			cmds.redo()
			assert baseiteminst.isValid() and baseiteminst.isAlive() 
		# END for each object including undo/redo


		# KEEP PARENT FALSE - USE INSTANCES
		# TODO: this test needs a redo - the original purpose got lost when
		# the addChild method has been changed, additionally it needs to be
		# better documented as this instancing stuff is not easily understood if
		# one just sees the code
		for orig,inst in zip( itemlist, instlist ):
			inst = obase.addChild( inst, keepExistingParent=False )
			obase.addChild( inst, keepExistingParent=False )	 # duplicate adds are not problem

			assert inst.isValid() and inst.isAlive() 
			assert orig.isValid() 			# original may not be influenced by that operation

			# undo / redo
			cmds.undo()
			#cmds.undo()	# just one undo counts
			assert inst.isValid() and orig.isValid() 

			cmds.redo()
		# END for each instance

		# RENAME ON CLASH = False
		self.failUnlessRaises( RuntimeError, obase.addChild, otrans, renameOnClash = False )

		# RENAME ON CLASH = True
		otransname = str( otrans )
		renamedtrans = obase.addChild( otrans, renameOnClash = True )
		assert renamedtrans.isValid() 
		renamedname = str( renamedtrans )
		assert renamedname != otransname 

		cmds.undo( )
		assert nt.objExists( otransname ) and not nt.objExists( renamedname ) 

		cmds.redo()

	def test_instancesAndParenting( self ):
		mrvmaya.Scene.open( get_maya_file( "instancetest.ma" ), force=True )
		m = nt.Node( "m" )			# mesh, two direct and two indirect instances
		c1 = nt.createNode( "|c1", "transform" )

		assert m.instanceCount( 0 ) == 2 
		assert m.instanceCount( 1 ) == 4 

		# test parenting
		mci = c1.addInstancedChild( m )

		assert m.instanceCount( 0 ) == 3 
		assert m.instanceCount( 1 ) == 5 	# direct + indirect

		c1.removeChild( mci )

		assert m.instanceCount( 0 ) == 2 
		assert m.instanceCount( 1 ) == 4 	# direct + indirect

		# check reparent
		d1 = nt.createNode( "|d1", "transform" )
		c1 = c1.reparent( d1 )

		assert m.instanceCount( 0 ) == 2 
		assert m.instanceCount( 1 ) == 4 

		# reparent an instanced transform under d1
		a2 = nt.Node( "a2" )

		a2 = a2.reparent( d1, raiseOnInstance=0 )			# destroys instances
		assert m.instanceCount( 0 ) == 2 
		assert m.instanceCount( 1 ) == 2 


	def test_instanceTraversal( self ):
		base = nt.createNode( "base", "transform" )
		obase = nt.createNode( "obase", "transform" )
		abase = nt.createNode( "abase", "transform" )
		bases = ( base, obase, abase )

		trans = nt.createNode( "trans", "transform" )
		shape = nt.createNode( "meshtrans|mesh", "mesh" )
		instances = ( trans, shape )

		# create instances
		for inst in instances:
			for b in bases:
				b.addInstancedChild( inst )

		# INSTANCE TRAVERSAL
		for inst in instances:
			assert inst.instanceCount( False ) == 4 
			assert inst == inst.instance( inst.instanceNumber( ) ) 
			for instinst in inst.iterInstances( excludeSelf = True ):
				assert instinst != inst 
			foundself = False
			for instinst in inst.iterInstances( excludeSelf = False ):
				if instinst == inst:
					foundself = True
			assert foundself 

			base.removeChild( inst )	# remove one inst
			assert inst.instanceCount( False ) == 3 
			base.addInstancedChild( inst )	# readd it
			# END for each instance path
		# END for each instanced node

		# TRAVERSE NON-INSTANCED  - should have one or 0
		assert len( list(( base.iterInstances( excludeSelf = True ) )) ) == 0 
		assert len( list(( base.iterInstances( excludeSelf = False ) )) ) == 1 

		# TEST DIRECT VS INDIRECT INSTANCES
		baseinst = base.addParent( obase )
		assert base.instanceCount( False ) == 2 
		assert trans.instanceCount( False ) != trans.instanceCount( True ) 

		# iteration is always over all instances
		assert len( list( ( trans.iterInstances(excludeSelf=False))) ) == trans.instanceCount( True ) 


	@with_undo
	def test_displaySettings( self ):
		mrvmaya.Scene.new( force = 1 )
		mesh = nt.createNode( "a1|b1|c1|d1|mesh", "mesh" )
		mesh.tmp.msetInt( 1 )

		# TEMPLATE
		##########
		assert mesh.isTemplate() 
		cmds.undo()
		assert not mesh.isTemplate() 

		a1 = mesh.root()
		a1.v.msetInt( 0 )

		# VISIBLE
		#########
		assert not mesh.isVisible( ) 
		cmds.undo()
		assert mesh.isVisible( ) 

		# DRAWING OVERRIDES
		###################
		a1.do.mchildByName('ove').msetInt( 1 )
		a1.do.mchildByName('ovdt').msetInt( 2 )
		assert mesh.displayOverrideValue( 'ovdt' ) == 2 
		cmds.undo()
		cmds.undo()
		assert mesh.displayOverrideValue( 'ovdt' ) == None 


	def test_addremoveAttr( self ):
		trans = nt.createNode( "trans", "transform" )
		trans2 = nt.createNode( "trans2", "transform" )

		nattr = api.MFnNumericAttribute( )
		attr = nattr.create( "longnumattr", "sna", api.MFnNumericData.kLong, 5 )

		trans.addAttribute( attr )
		attrplug = trans.longnumattr
		attrplug.msetInt( 10 )
		assert attrplug.asInt() == 10 

		# adding same attribute to several objects - DOES NOT WORK
		# CREATE A NEW ONE
		attrnew = nattr.create( "longnumattr", "sna", api.MFnNumericData.kLong, 5 )
		trans2.addAttribute( attrnew )
		trans2.sna.msetInt( 20 )
		assert trans2.sna.asInt() == 20 and trans.sna.asInt() == 10 

		# remove the attribute - with Attribute class this time
		trans.removeAttribute( attrplug.attribute() )

		# have to use find plug as our transform has cached the plug which might
		# have gone out of scope
		self.failUnlessRaises( RuntimeError, trans.findPlug, "sna" )


	def _checkIdentity( self, t ):
		"""Assure that t is identity"""
		for mainattr, val in zip('trs', (0.0, 0.0, 1.0)):
			for subattr in 'xyz':
				assert t.findPlug(mainattr+subattr).asFloat() == val
			# END for each subattr
		# END for each main attr

	@with_undo
	def test_keepWorldSpace( self ):
		g = nt.createNode( "g", "transform" )
		t = nt.createNode( "t", "transform" )
		t.setParent( g )

		mainattrs = ( "t","s" )
		subattrs = ( "x","y","z" )

		count = 0.0
		for ma in mainattrs:
			for sa in subattrs:
				getattr( g, ma ).mchildByName(ma+sa).msetFloat(count)
				count += 1.0
			# END for each sa
		# END for each ma

		# REPARENT TO WORLD
		###################
		t = t.reparent( None, keepWorldSpace = 1 )

		count = 0.0
		for ma in mainattrs:
			for sa in subattrs:
				value = t.findPlug(ma+sa).asFloat( )
				assert value == count 
				count += 1.0
			# END
		# END

		# undo - everything should be back to normal
		cmds.undo()
		self._checkIdentity( t )
		cmds.redo()

		# REPARENT TO PARENT NODE
		###########################
		t = t.setParent( g, keepWorldSpace = 1 )

		self._checkIdentity( t )

	def test_simplified_node_creation( self ):
		# dg node
		os = nt.ObjectSet()
		assert isinstance(os, nt.ObjectSet)
		
		# assure we can still wrap dg nodes
		assert nt.ObjectSet(os.object()) == os
		
		
		# dag nodes
		# come along with a transform
		mesh = nt.Mesh()
		assert isinstance(mesh, nt.Mesh)
		assert len(mesh.parentDeep()) == 1
		
		# multiple calls create multiple shapes, but under the same transform
		mesh2 = nt.Mesh()
		assert mesh2 != mesh
		assert mesh2[-1] == mesh[-1]
		
		# transforms are created plain and under the root
		trans = nt.Transform()
		assert isinstance(trans, nt.Transform)
		assert trans.parent() is None
		
		trans2 = nt.Transform()
		assert trans2 != trans
		
		# kwargs go to createNode
		assert trans == nt.Transform(forceNewLeaf=False)
		
		# cannot create anything below dependnode
		self.failUnlessRaises(TypeError, nt.Node)

	def test_single_indexed_components( self ):
		# check exceptions
		self.failUnlessRaises(IndexError, nt.SingleIndexedComponent)	# no arg
		self.failUnlessRaises(TypeError, nt.Component.create, api.MFn.kMeshEdgeComponent) # invalid type

	@with_persistence
	def test_data(self):
		
		# DATA CREATION
		###############
		# create all implemented data types
		self.failUnlessRaises(TypeError, nt.Data.create)
		
		basic_types = [nt.VectorArrayData, nt.UInt64ArrayData, nt.StringData, 
						nt.StringArrayData, nt.SphereData, nt.PointArrayData,
						nt.NObjectData, nt.MatrixData, nt.IntArrayData, 
						nt.SubdData, nt.NurbsSurfaceData, nt.NurbsCurveData, 
						nt.MeshData, nt.LatticeData, nt.DoubleArrayData, 
						nt.ComponentListData, nt.ArrayAttrsData ]
		
		if env.appVersion()[0] > 2010.0:
			basic_types.append(nt.NIdData)
		# END 2011 special handling
		
		knullobj = nt.api.MObject()
		for bt in basic_types:
			try:
				data = bt.create()
			except:
				print "Failed to create %r with MFn: %r" % (bt, bt._mfncls)
				raise
			# END exception handling for debugging
			assert data != knullobj
			assert isinstance(data, bt)
		# END for each type with a basic constructor
		
		# PLUGIN DATA
		# use storage node data type
		pd = nt.PluginData.create(PyPickleData.kPluginDataId)
		
		
		# NUMERIC DATA
		# these items cannot work or do not work as simple types are not represented
		# by data containers
		forbidden = (	'kLast', 'kDouble', 'kInvalid', 'k4Double', 
						'kBoolean', 'kShort', 'kInt', 'kByte', 'kAddr', 
						'kChar', 'kLong', 'kFloat' )
		types = [ (k, v) for k,v in api.MFnNumericData.__dict__.iteritems() if k.startswith('k') and k not in forbidden ]
		assert types
		for type_name, type_id in types:
			data = nt.NumericData.create(type_id)
			assert not data.isNull() and isinstance(data, nt.NumericData)
		# END for each numeric data type
		
		
		# COMPONENT LIST DATA
		#####################
		# special testing
		mvc = nt.SingleIndexedComponent.create(api.MFn.kMeshVertComponent)
		cd = nt.ComponentListData.create()
		assert cd.length() == 0
		assert mvc not in cd
		cd.add(mvc)
		assert len(cd) == 1
		
		# ERROR: It says our component is NOT contained in the data list, although
		# we just added it and although it says the list has an item
		# assert cd.has(mvc)
		# assert mvc in cd
		assert not cd.has(mvc)	# see above
		assert mvc not in cd	# see above, we keep it to call the functions
		
		cd.remove(mvc)
		assert len(cd) == 0
		
	def test_staticmethods(self):
		# access a static method directly
		rnl = nt.RenderLayer.currentLayer()
		assert isinstance(rnl, nt.Node)
		
	def test_enumerations(self):
		# should exist for nodes, data, components and attributes - we just 
		# take samples
		for enum in (	nt.Node.Type,
						nt.DependNode.MAttrClass, 
						nt.Attribute.DisconnectBehavior,
						nt.Data.Type ):
			assert isinstance(enum, MEnumeration)
		# END for each enumration sample

	@with_persistence
	def test_attributes( self ):
		
		# CREATION 
		##########
		# UNIT ATTRIBUTE # 
		l = "long"
		s = "sh"
		for ut in nt.UnitAttribute.Type:
			try:
				attr = nt.UnitAttribute.create( l, s, ut)
			except RuntimeError:
				# some types cannot be created as they are obsolete
				continue
			# END handle exceptions
			assert isinstance(attr, nt.UnitAttribute)
			assert attr.unitType() == ut
		# END for each unit attribute
		
		
		# TYPED ATTRIBUTE #
		# we create null obj defaults for the sake of simplicity
		for at in nt.Data.Type:
			try:
				attr = nt.TypedAttribute.create(l, s, at)
			except RuntimeError:
				# some types are obsolete
				continue
			# END exception handling 
			assert isinstance(attr, nt.TypedAttribute)
			assert attr.attrType() == at
		# END for each type
		
		# test plugin data type
		attr = nt.TypedAttribute.create(l, s, PyPickleData.kPluginDataId)
		assert isinstance(attr, nt.TypedAttribute)
		assert attr.attrType() == nt.Data.Type.kInvalid	 # its okay, it works, see storage node
		
		
		# NUMERIC DATA #
		for numt in nt.NumericData.Type:
			try:
				attr = nt.NumericAttribute.create(l, s, numt)
			except RuntimeError:
				# some types are absolete
				continue
			# END exception handling 
			assert not attr.isNull()
			assert isinstance(attr, nt.NumericAttribute)
			# skip k4Double - doesnt work
			if numt == nt.NumericData.Type.k4Double:
				continue
			assert attr.unitType() == numt
		# END for each type
		
		# test special constructors
		for method_name in ('createColor', 'createPoint'):
			attr = getattr(nt.NumericAttribute, method_name)(l, s)
			assert attr.unitType() == nt.NumericData.Type.k3Float
		# END for each special constructor
		
		
		# MATRIX ATTRIBUTE # 
		for mt in nt.MatrixAttribute.Type:
			attr = nt.MatrixAttribute.create(l, s, mt)
		# END for each type
		
		# LIGHT DATA ATTRIBUTE # 
		# skipping the work for now 
		
		# GENERIC ATTRIBUTE #
		attr = nt.GenericAttribute.create(l, s)
		
		# ENUM ATTRIBUTE
		attr = nt.EnumAttribute.create(l, s)
		
		# COMPOUND ATTRIBUTE #
		attr = nt.CompoundAttribute.create(l, s)
	
	def test_dagContainer(self):
		# only for maya 2011 and newer
		if env.appVersion()[0] < 2011:
			return
			
		# problem is that the dagContainer node is in fact a valid container 
		# which must be compatible to the MFnContainerNode. It isnt though as 
		# maya's hierarchy system only allows to derive from one parent, officially.
		# Internally it derives from containerBase and hence is compatible. 
		# Just make sure it really is that way, as this is a special tweak.
		assert api.MFnContainerNode in nt.DagContainer.getMFnClasses() 
