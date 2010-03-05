# -*- coding: utf-8 -*-
""" Test general nodes features """
import unittest
import mayarv.maya as bmaya
import mayarv.maya.env as env
import mayarv.maya.ns as nsm
import mayarv.maya.nodes as nodes
from mayarv.test.maya import get_maya_file
from mayarv.util import capitalize, uncapitalize
from mayarv.maya.util import StandinClass
import maya.cmds as cmds
import mayarv.test.maya as common
import mayarv.test.maya.nodes as ownpackage
import maya.OpenMaya as api
from mayarv.path import Path


class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """
	
	def test_testWrappers( self ):
		"""mayarv.maya.nodes: test wrapper class creation
		@note: we coulld dynamically create the nodes for testing using ls -nt,
		but using a filecache is much faster - speed matters"""
		if not ownpackage.mayRun( "general" ): return

		filename = get_maya_file( "allnodetypes_%s.mb" % env.getAppVersion( )[0] )
		if not Path( filename ).isfile():
			raise AssertionError( "File %s not found for loading" % filename )
		bmaya.Scene.open( filename, force=True )
		
		missingTypesList = []
		invalidInheritanceList = []
		seen_types = set()		# keeps class names that we have seen already 
		for nodename in cmds.ls( ):
			try:
				node = nodes.Node( nodename )
				node.getMFnClasses()
			except (TypeError,AttributeError):
				missingTypesList.append( ( nodename, cmds.nodeType( nodename ) ) )
				continue
			except:
				raise

			self.failUnless( not node._apiobj.isNull() )
			
			# skip duplicate types - it truly happens that there is the same typename
			# with a different parent class - we cannot handle this 
			nodetypename = node.getTypeName()
			if nodetypename in seen_types:
				continue
			seen_types.add( nodetypename )

			# assure we have all the parents we need
			parentClsNames = [ capitalize( typename ) for typename in cmds.nodeType( nodename, i=1 ) ]
			
			for pn in parentClsNames:
				token = ( node, parentClsNames )
				try:
					pcls = getattr( nodes, pn )
				except AttributeError:
					invalidInheritanceList.append( token )
					break
				# END AttributeError
				
				# if its a standin class, try to create it 
				try:
					pcls = pcls.createCls()
				except AttributeError:
					pass 
					
				if not isinstance( node, pcls ):
					invalidInheritanceList.append( token )
					break
				# END if a parent class is missing
			# END for each parent class name 
		# END for each type in file

		if len( missingTypesList ):
			nodecachefile = "nodeHierarchy%s.html" % env.getAppVersion( )[0]
			for fn in missingTypesList:
				print fn
			
			print "Add these lines to the hierarchy file" 
			for fn in missingTypesList:
				print '<tt> >  >  > </tt><a href="%s.html" target="subFrame">%s</a><br />' % ( uncapitalize( fn[1] ), uncapitalize( fn[1] ))
			raise TypeError( "Add the following node types to the %r cache file at the respective post in the hierarchy:" % ( nodecachefile ) )
		# END missing types handling 
		
		if len( invalidInheritanceList ):
			for ( node, parentClsNames ) in invalidInheritanceList:
				print "Invalid inheritance of type %s, must be %s" % ( node.typeName(), parentClsNames )
			# END for each item tuple 
			raise AssertionError( "Class(es) with invalid inheritance found - see stdout" )
		# END invalid inheritance handling 

		# try to just use a suberclass directly
		for transname in cmds.ls( type="transform" ):
			node = nodes.DagNode( transname )
			self.failUnless( hasattr( node, "__dict__" ) )


	def test_createNodes( self ):
		"""mayarv.maya.nodes: create nodes with long names and namespaces"""
		if not ownpackage.mayRun( "general" ): return
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
		self.failUnlessRaises( NameError, nodes.createNode, "this|mesh", "nurbsSurface", forceNewLeaf = False )

		# renameOnClash  - it fails if the dep node exists first
		nodes.createNode( "node", "facade" )
		self.failUnlessRaises( NameError, nodes.createNode, "this|that|node", "mesh", renameOnClash = False )

		# obj exists should match dg nodes with dag node like path ( as they occupy the same
		# namespace after all
		self.failUnless( nodes.objExists( "|node" ) )

		# it also clashes if the dg node is created after a  dag node with the same name
		nodes.createNode( "that|nodename", "mesh" )
		self.failUnlessRaises( NameError, nodes.createNode, "nodename", "facade", renameOnClash = False )


		# it should be fine to have the same name in several dag levels though !
		newmesh = nodes.createNode( "parent|nodename", "transform" )
		newmesh1 = nodes.createNode( "parent|nodename|nodename", "mesh" )
		newmesh2 = nodes.createNode( "otherparent|nodename|nodename", "mesh" )
		self.failUnless( newmesh != newmesh1 )
		self.failUnless( newmesh1 != newmesh2 )

		# FORCE NEW
		##############
		oset = nodes.createNode( "objset", "objectSet", forceNewLeaf = False )
		newoset = nodes.createNode( "objset", "objectSet", forceNewLeaf = True )
		self.failUnless( oset != newoset )

		# would expect same set to be returned
		sameoset = nodes.createNode( "objset", "objectSet", forceNewLeaf = False )
		self.failUnless( sameoset == oset )

		# force new and dag paths
		newmesh3 = nodes.createNode( "otherparent|nodename|nodename", "mesh", forceNewLeaf = True )
		self.failUnless( newmesh3 != newmesh2 )



	def test_objectExistance( self ):
		"""mayarv.maya.nodes: check whether we can properly handle node exist checks"""
		if not ownpackage.mayRun( "general" ): return
		depnode = nodes.createNode( "node", "facade" )
		self.failUnless( nodes.objExists( str( depnode ) ) )

		# TEST DUPLICATION
		duplnode = depnode.duplicate( )
		self.failUnless( duplnode.isValid( ) )

		copy2 = depnode.duplicate( "name2" )
		self.failUnless( str( copy2 ) == "name2" )
		# NOTE: currently undo is not opetional

		dagnode = nodes.createNode( "parent|node", "mesh" )
		self.failUnless( nodes.objExists( str( dagnode ) ) )

		# must clash with dg node ( in maya, dg nodes will block names of dag node leafs ! )
		self.failUnlessRaises( NameError, nodes.createNode, "parent|node|node", "mesh", renameOnClash=False )

		# same clash occours if dag node exists first
		dagnode = nodes.createNode( "parent|othernode", "transform" )
		self.failUnlessRaises( NameError, nodes.createNode, "othernode", "facade", renameOnClash=False )


	def test_dagPathVSMobjects( self ):
		"""mayarv.maya.nodes: if mobjects where used internally, this test would fail"""
		if not ownpackage.mayRun( "general" ): return
		node = nodes.createNode( "parent|middle|child", "transform" )
		nodem = nodes.Node( "parent|middle" )

		duplnodemiddle = nodem.duplicate( "middle1" )
		instnode = duplnodemiddle.addInstancedChild( node )


		self.failUnless( instnode._apiobj == node._apiobj ) # compare mobject
		self.failUnless( instnode != node )		# compare dag paths

		path = instnode.getDagPath( )
		childm1 = nodes.Node( "parent|middle1|child" )

		# if it didnt work, he would have returned a "|parent|middle|child"
		self.failUnless( "|parent|middle1|child" == str(childm1) )

		npath = node.getDagPath( )
		ipath = instnode.getDagPath( )


	def test_convenienceFunctions( self ):
		"""mayarv.maya.nodes: test convenience and conversion functions"""
		if not ownpackage.mayRun( "util" ): return

		# SELECTION
		############
		nodes.select( "persp" )
		persp = nodes.getSelection()[0]
		self.failUnless( persp == nodes.Node( "persp" ) )

		# clear selection
		nodes.select( )
		self.failUnless( not nodes.getSelection() )

		# select object and selection list
		nodes.select( persp )
		self.failUnless( len( nodes.getSelection( ) ) == 1 )
		nodes.select( nodes.toSelectionList( nodes.getSelection( ) ) )
		self.failUnless( len( nodes.getSelection( ) ) == 1 )

		# select mixed
		nodes.select( persp, "front" )
		self.failUnless( len( nodes.getSelection( ) ) == 2 )


		# GET BY NAME
		###############
		persp = nodes.getByName( "pers*" )[0]
		self.failUnless( persp == nodes.Node( "persp" ) )


class TestNodeBase( unittest.TestCase ):
	""" Test node base functionality  """

	def setUp( self ):
		"""Create a new scene to assure we do not resue nodes or configuration"""
		if not ownpackage.mayRun( "general" ): return
		cmds.file( new=1,force=1 )

	def test_customTypes( self ):
		"""mayarv.maya.nodes: add a custom type to the system"""
		if not ownpackage.mayRun( "general" ): return
		nodes.addCustomType( "MyNewCls",parentClsName = "dependNode" )
		# standin class should be there
		cls = nodes.MyNewCls
		self.failUnlessRaises( TypeError, cls, "persp" )	# class has incorrect type for persp
		# NOTE: needed actual plugin type for proper test

	def test_hashfunc( self ):
		"""byroimo.maya.nodes: should be possible to use objects as keys in hashes"""
		# they must compare their objects for equality, not their own instance
		ddg = dict()
		for i in range( 10 ):		# dg nodes
			ddg[ nodes.Node( "initialShadingGroup" ) ] = i

		self.failUnless( len( ddg ) == 1 )

		ddag = dict()
		for i in range( 10 ):		# dg nodes
			ddag[ nodes.Node( "persp" ) ] = i

		self.failUnless( len( ddag ) == 1 )

		# merge both together
		dall = dict()
		dall.update( ddg )
		dall.update( ddag )
		self.failUnless( len( dall ) == 2 )


	def test_wrapDepNode( self ):
		"""mayarv.maya.nodes: create and access dependency nodes ( not being dag nodes )"""
		if not ownpackage.mayRun( "general" ): return
		node = nodes.Node( "defaultRenderGlobals" )

		# SKIP CHECKS TEST
		self.failUnlessRaises( ValueError, nodes.Node, "this" )	# does not exist
		# results inconsitent between maya 8.5 and 2008, thus we skip it as it is not of much value
		# self.failUnlessRaises( TypeError, nodes.Node, "this", 1 )  # skip check , maya throws

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
			assert plug == getattr( node, attr )
			assert plug == node.findPlug(attr)
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
		t = node.type()
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
		self.failUnless( not nsm.exists( "nsdoesnotexist" ) )
		cmds.redo()
		self.failUnless( node.isValid() )


		# rename to same name
		renamed = node.rename( "nsdoesnotexist" )	# should be fine
		self.failUnless( renamed == node )

		# othernode with different type exists
		othernode = nodes.createNode( "othernode", "groupId" )
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

	def test_reparentAndInstances( self ):
		"""mayarv.maya.nodes: see of reparenting is responding when instances are involved"""
		if not ownpackage.mayRun( "general" ): return
		mesh = nodes.createNode( "trans|mesh", "mesh" )
		base = nodes.createNode( "base|subbase", "transform" )
		obase = nodes.createNode( "obase|subbase2", "transform" )
		rbase = nodes.createNode( "reparentBase", "transform" )

		# test basic functions
		self.failUnless( rbase.getApiType() == api.MFn.kTransform )
		self.failUnless( rbase.hasFn( api.MFn.kTransform ) )

		baseinst = base.addInstancedChild( mesh )
		obaseinst = obase.addInstancedChild( mesh )

		# try to re-wrap the instanced items
		assert nodes.Node( str( baseinst ) ) == baseinst
		assert nodes.Node( str( obaseinst ) ) == obaseinst

		# use partial name
		assert nodes.Node( "subbase|mesh" ) == baseinst
		assert nodes.Node( "subbase2|mesh" ) == obaseinst

		self.failUnless( mesh.isValid() and baseinst.isValid() and obaseinst.isValid() )

		# assure we catch this possibly damaage
		self.failUnlessRaises( RuntimeError, mesh.reparent, rbase, raiseOnInstance=True )

		# instances are gone should be gone
		mesh = mesh.reparent( rbase, raiseOnInstance=False )
		self.failUnless( mesh.isValid() and not baseinst.isValid() and not obaseinst.isValid() )
		
		# try unparent
		meshtrans = mesh.getTransform()
		meshtrans.setParent(obase)
		assert meshtrans.getParent() == obase
		meshtrans.unparent()
		assert meshtrans.getParent() is None

	def test_duplicateInstances( self ):
		"""mayarv.maya.nodes: handle duplication of instances"""
		if not ownpackage.mayRun( "dagnode" ): return
		base = nodes.createNode( "base", "transform" )
		obase = nodes.createNode( "obase", "transform" )
		basemesh = nodes.createNode( "base|mesh", "mesh" )

		obasemeshinst = obase.addInstancedChild( basemesh )

		duplmesh = obasemeshinst.duplicate( "newmeshname" )	# is a separate copy !
		self.failUnless( duplmesh != obasemeshinst )

		dupltrans = base.duplicate( "duplbase" )
		baseduplmesh = dupltrans.getChildrenByType( nodes.Mesh )[0]
		self.failUnless( baseduplmesh != basemesh )		# its a separate copy

	def test_wrapDagNode( self ):
		"""mayarv.maya.nodes: create and access dag nodes"""
		if not ownpackage.mayRun( "dagnode" ): return
		mesh = nodes.createNode( "parent|mesh", "mesh" )
		parent = mesh.getParent( )

		# simple rename
		mesh.rename( "fancymesh" )


		# simple dupl test
		duplbase = nodes.createNode( "parent|this|other|duplbase", "mesh" )
		transcopy = duplbase.getTransform( ).duplicate()
		copy = duplbase.duplicate( "parent|this|other|duplcopy" )
		self.failUnless( copy != duplbase )
		self.failUnless( str( copy ) != str( duplbase ) )
		self.failUnless( str( copy ) == "|parent|this|other|duplcopy" )

		# TEST ADDITIONAL OPTIONS
		for i in range( 1,3 ):
			ocopy = duplbase.duplicate(  )
			self.failUnless( str( ocopy ) == str( duplbase ) + str( i ) )

			ocopy = duplbase.duplicate( newTransform=1 )
			self.failUnless( ocopy.getBasename( ) == duplbase.getBasename() )
			self.failUnless( str( ocopy.getParent() ) == str( duplbase.getParent() ) + str( i + 1 ) )

			# undo both duplications and redo
			# CRASHES MAYA AFTER REDO
			# and if someone tries to access an object already created
			#cmds.undo()
			#cmds.undo()
			#self.failUnless( duplbase.isValid() )
			#cmds.redo()
			#cmds.redo()
		# END for each copy


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

		# reparent transform to world
		wtrans = nodes.createNode( "parent2|worldtrans", "transform" )
		parent = nodes.Node( "parent2" )
		oparent = nodes.createNode( "oparent2", "transform" )
		wtrans = wtrans.reparent( None )

		wtransnewparent = wtrans.setParent( parent )
		assert wtrans == wtransnewparent
		self.failUnless( wtransnewparent.getInstanceCount( 1 ) == 1 )
		wtransnewparent.addParent( oparent )
		self.failUnless( wtransnewparent.getInstanceCount( 1 ) == 2 )
		wtransnewparent.removeParent( oparent )
		self.failUnless( wtrans.getInstanceCount( 1 ) == 1 )



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
		instbase = nodes.createNode( "|duplparent2|newnamespace:instmesh", "transform" )
		meshinst = instbase.addInstancedChild( mesh )
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

		# Duplicate TRANSFORM ( just a name given )
		# dag paths should be different although object is the same
		mesh = nodes.createNode( "|parent|mybeautifuluniquemeshname", "mesh" )
		meshassert = nodes.createNode( "|parent|mesh", "mesh" )
		meshself = nodes.Node( "|parent|mybeautifuluniquemeshname" )
		self.failUnless( mesh == meshself )

		# connect it, to track the instance by connection
		persp = nodes.Node( "persp" )
		perspplug = persp.t['tx']
		triplug = meshself.maxTriangles
		perspplug >> triplug

		# target does exist
		# this is blocking the target instance name with an incorrect type
		nodes.createNode( "parent|this|mybeautifuluniquemeshname", "transform" )
		self.failUnlessRaises( RuntimeError, mesh.duplicate, "|parent|this" )

		# if the path is too short ...
		self.failUnlessRaises( NameError, mesh.duplicate, str( mesh.getTransform() ) )
		self.failUnlessRaises( NameError, mesh.getParent().duplicate, '|' )


		meshinstname = mesh.getTransform().getFullChildName( "newns:meshinst" )
		self.failUnless( isinstance( meshinst, nodes.Mesh ) )

	def test_removeChild( self ):
		"""mayarv.maya.nodes: test how remove child responds"""
		if not ownpackage.mayRun( "general" ): return
		base = nodes.createNode( "base" , "transform" )
		trans = nodes.createNode( "base|trans", "transform" )
		mesh = nodes.createNode( "base|mesh", "mesh" )

		for item in [ trans, mesh ]:
			removeditem = base.removeChild( item, allowZeroParents=True )

			# PATHS ARE INVALID NOW - object is nowhere to be found
			self.failUnless( not removeditem.isValid() and removeditem.isAlive() )

			cmds.undo()
			self.failUnless( removeditem.isValid() and removeditem.isAlive() )
		# END for each removeChild item


	def test_dependnode_getitem( self ):
		"""mayarv.nodes.maya: DependeNode.__getitem__"""
		if not ownpackage.mayRun( "general" ): return
		mesh = nodes.createNode( "p1|p2|mesh", "mesh" )
		self.failUnless( len( list( mesh.iterParents() ) ) == 2 )
		p2 = mesh.getParent()
		p1 = p2.getParent()
		self.failUnless( mesh[-1] == p2 )
		self.failUnless( mesh[-2] == p1 )
		self.failUnlessRaises( IndexError, mesh.__getitem__, -3 )

	def test_childEditing( self ):
		"""mayarv.maya.nodes: tests the add and remove children"""
		if not ownpackage.mayRun( "general" ): return
		base = nodes.createNode( "basenode", "transform" )
		obase = nodes.createNode( "otherbasenode", "transform" )

		trans = nodes.createNode( "trans", "transform" )
		otrans = nodes.createNode( "parent|trans", "transform" )
		mesh = nodes.createNode( "meshparent|meshshape", "mesh" )
		curve = nodes.createNode( "nurbsparent|ncurve", "nurbsCurve" )
		itemlist = [ trans, mesh, curve ]

		instlist = []

		# MULTIPLE ADDS
		####################
		# Returns the same instance - its what the user wants
		for item in itemlist:
			baseiteminst = base.addInstancedChild( item )
			base.addInstancedChild( item )
			self.failUnless( item != baseiteminst and baseiteminst.isValid() and item.isValid() )

			instlist.append( baseiteminst )

			# UNDO TEST
			# undo basemesh
			cmds.undo()
			cmds.undo()
			self.failUnless( not baseiteminst.isValid() and baseiteminst.isAlive() )

			cmds.redo()
			self.failUnless( baseiteminst.isValid() and baseiteminst.isAlive() )
		# END for each object including undo/redo


		# KEEP PARENT FALSE - USE INSTANCES
		# TODO: this test needs a redo - the original purpose got lost when
		# the addChild method has been changed, additionally it needs to be
		# better documented as this instancing stuff is not easily understood if
		# one just sees the code
		for orig,inst in zip( itemlist, instlist ):
			inst = obase.addChild( inst, keepExistingParent=False )
			obase.addChild( inst, keepExistingParent=False )	 # duplicate adds are not problem

			self.failUnless( inst.isValid() and inst.isAlive() )
			self.failUnless( orig.isValid() )			# original may not be influenced by that operation

			# undo / redo
			cmds.undo()
			#cmds.undo()	# just one undo counts
			self.failUnless( inst.isValid() and orig.isValid() )

			cmds.redo()
		# END for each instance

		# RENAME ON CLASH = False
		self.failUnlessRaises( RuntimeError, obase.addChild, otrans, renameOnClash = False )

		# RENAME ON CLASH = True
		otransname = str( otrans )
		renamedtrans = obase.addChild( otrans, renameOnClash = True )
		self.failUnless( renamedtrans.isValid() )
		renamedname = str( renamedtrans )
		self.failUnless( renamedname != otransname )

		cmds.undo( )
		self.failUnless( nodes.objExists( otransname ) and not nodes.objExists( renamedname ) )

		cmds.redo()

	def test_instancesAndParenting( self ):
		"""mayarv.maya.nodes.base: test instances and parenting, also instanced attributes"""
		if not ownpackage.mayRun( "general" ): return
		bmaya.Scene.open( get_maya_file( "instancetest.ma" ), force=True )
		m = nodes.Node( "m" )			# mesh, two direct and two indirect instances
		c1 = nodes.createNode( "|c1", "transform" )

		self.failUnless( m.getInstanceCount( 0 ) == 2 )
		self.failUnless( m.getInstanceCount( 1 ) == 4 )

		# test parenting
		mci = c1.addInstancedChild( m )

		# common._saveTempFile( "instancetest.ma" )
		self.failUnless( m.getInstanceCount( 0 ) == 3 )
		self.failUnless( m.getInstanceCount( 1 ) == 5 )	# direct + indirect

		c1.removeChild( mci )

		self.failUnless( m.getInstanceCount( 0 ) == 2 )
		self.failUnless( m.getInstanceCount( 1 ) == 4 )	# direct + indirect

		# check reparent
		d1 = nodes.createNode( "|d1", "transform" )
		c1 = c1.reparent( d1 )

		self.failUnless( m.getInstanceCount( 0 ) == 2 )
		self.failUnless( m.getInstanceCount( 1 ) == 4 )

		# reparent an instanced transform under d1
		a2 = nodes.Node( "a2" )

		a2 = a2.reparent( d1, raiseOnInstance=0 )			# destroys instances
		self.failUnless( m.getInstanceCount( 0 ) == 2 )
		self.failUnless( m.getInstanceCount( 1 ) == 2 )


	def test_instanceTraversal( self ):
		"""mayarv.maya.nodes.base: traverse instances"""
		if not ownpackage.mayRun( "general" ): return
		base = nodes.createNode( "base", "transform" )
		obase = nodes.createNode( "obase", "transform" )
		abase = nodes.createNode( "abase", "transform" )
		bases = ( base, obase, abase )

		trans = nodes.createNode( "trans", "transform" )
		shape = nodes.createNode( "meshtrans|mesh", "mesh" )
		instances = ( trans, shape )

		# create instances
		for inst in instances:
			for b in bases:
				b.addInstancedChild( inst )

		# INSTANCE TRAVERSAL
		for inst in instances:
			self.failUnless( inst.getInstanceCount( False ) == 4 )
			self.failUnless( inst == inst.getInstance( inst.getInstanceNumber( ) ) )
			for instinst in inst.iterInstances( excludeSelf = True ):
				self.failUnless( instinst != inst )
			foundself = False
			for instinst in inst.iterInstances( excludeSelf = False ):
				if instinst == inst:
					foundself = True
			self.failUnless( foundself )

			base.removeChild( inst )	# remove one inst
			self.failUnless( inst.getInstanceCount( False ) == 3 )
			base.addInstancedChild( inst )	# readd it
			# END for each instance path
		# END for each instanced node

		# TRAVERSE NON-INSTANCED  - should have one or 0
		self.failUnless( len( list(( base.iterInstances( excludeSelf = True ) )) ) == 0 )
		self.failUnless( len( list(( base.iterInstances( excludeSelf = False ) )) ) == 1 )

		# TEST DIRECT VS INDIRECT INSTANCES
		baseinst = base.addParent( obase )
		self.failUnless( base.getInstanceCount( False ) == 2 )
		self.failUnless( trans.getInstanceCount( False ) != trans.getInstanceCount( True ) )

		# iteration is always over all instances
		self.failUnless( len( list( ( trans.iterInstances(excludeSelf=False))) ) == trans.getInstanceCount( True ) )


	def test_displaySettings( self ):
		"""mayarv.maya.nodes.base: test how display type and display overrides work hierarchically"""
		if not ownpackage.mayRun( "general" ): return
		bmaya.Scene.new( force = 1 )
		mesh = nodes.createNode( "a1|b1|c1|d1|mesh", "mesh" )
		mesh.tmp.setInt( 1 )

		# TEMPLATE
		##########
		self.failUnless( mesh.isTemplate() )
		cmds.undo()
		self.failUnless( not mesh.isTemplate() )

		a1 = mesh.getRoot()
		a1.v.setInt( 0 )

		# VISIBLE
		#########
		self.failUnless( not mesh.isVisible( ) )
		cmds.undo()
		self.failUnless( mesh.isVisible( ) )

		# DRAWING OVERRIDES
		###################
		a1.do['ove'].setInt( 1 )
		a1.do['ovdt'].setInt( 2 )
		self.failUnless( mesh.getDisplayOverrideValue( 'ovdt' ) == 2 )
		cmds.undo()
		cmds.undo()
		self.failUnless( mesh.getDisplayOverrideValue( 'ovdt' ) == None )


	def test_addremoveAttr( self ):
		"""mayarv.maya.nodes.base: add and remove attributes with undo"""
		if not ownpackage.mayRun( "general" ): return
		trans = nodes.createNode( "trans", "transform" )
		trans2 = nodes.createNode( "trans2", "transform" )

		nattr = api.MFnNumericAttribute( )
		attr = nattr.create( "longnumattr", "sna", api.MFnNumericData.kLong, 5 )

		trans.addAttribute( attr )
		attrplug = trans.longnumattr
		attrplug.setInt( 10 )
		self.failUnless( attrplug.asInt() == 10 )

		# adding same attribute to several objects - DOES NOT WORK
		# CREATE A NEW ONE
		attrnew = nattr.create( "longnumattr", "sna", api.MFnNumericData.kLong, 5 )
		trans2.addAttribute( attrnew )
		trans2.sna.setInt( 20 )
		self.failUnless( trans2.sna.asInt() == 20 and trans.sna.asInt() == 10 )

		# remove the attribute - with Attribute class this time
		trans.removeAttribute( attrplug.getAttribute() )

		# have to use find plug as our transform has cached the plug which might
		# have gone out of scope
		self.failUnlessRaises( RuntimeError, trans.findPlug, "sna" )


	def _checkIdentity( self, t ):
		"""Assure that t is identity"""
		self.failUnless( t.t['tx'].asFloat() == 0.0 )
		self.failUnless( t.t['ty'].asFloat() == 0.0 )
		self.failUnless( t.t['tz'].asFloat() == 0.0 )
		self.failUnless( t.r['rx'].asFloat() == 0.0 )
		self.failUnless( t.r['ry'].asFloat() == 0.0 )
		self.failUnless( t.r['rz'].asFloat() == 0.0 )
		self.failUnless( t.s['sx'].asFloat() == 1.0 )
		self.failUnless( t.s['sy'].asFloat() == 1.0 )
		self.failUnless( t.s['sz'].asFloat() == 1.0 )

	def test_keepWorldSpace( self ):
		"""mayarv.maya.nodes.base: keep ws transformation when reparenting"""
		if not ownpackage.mayRun( "general" ): return
		g = nodes.createNode( "g", "transform" )
		t = nodes.createNode( "t", "transform" )
		t.setParent( g )

		mainattrs = ( "t","s" )
		subattrs = ( "x","y","z" )

		count = 0.0
		for ma in mainattrs:
			for sa in subattrs:
				getattr( g, ma )[ma+sa].setFloat( count )
				count += 1.0
			# END for each sa
		# END for each ma

		# REPARENT TO WORLD
		###################
		t = t.reparent( None, keepWorldSpace = 1 )

		# common._saveTempFile( "afterreparentw.ma" )
		count = 0.0
		for ma in mainattrs:
			for sa in subattrs:
				value = getattr( t, ma )[ma+sa].asFloat( )
				self.failUnless( value == count )
				count += 1.0
			# end
		#end

		# undo - everything should be back to normal
		cmds.undo()
		self._checkIdentity( t )
		cmds.redo()

		# REPARENT TO PARENT NODE
		###########################
		t = t.setParent( g, keepWorldSpace = 1 )
		# common._saveTempFile( "afterreparentg.ma" )

		self._checkIdentity( t )

	def test_simplified_node_creation( self ):
		# dg node
		os = nodes.ObjectSet()
		assert isinstance(os, nodes.ObjectSet)
		
		# assure we can still wrap dg nodes
		assert nodes.ObjectSet(os.getMObject()) == os
		
		
		# dag nodes
		# come along with a transform
		mesh = nodes.Mesh()
		assert isinstance(mesh, nodes.Mesh)
		assert len(mesh.getParentDeep()) == 1
		
		# multiple calls create multiple shapes, but under the same transform
		mesh2 = nodes.Mesh()
		assert mesh2 != mesh
		assert mesh2[-1] == mesh[-1]
		
		# transforms are created plain and under the root
		trans = nodes.Transform()
		assert isinstance(trans, nodes.Transform)
		assert trans.getParent() is None
		
		trans2 = nodes.Transform()
		assert trans2 != trans
		
		# kwargs go to createNode
		assert trans == nodes.Transform(forceNewLeaf=False)
		
		# cannot create anything below dependnode
		self.failUnlessRaises(ValueError, nodes.Node)

	def test_single_indexed_components( self ):
		# check exceptions
		self.failUnlessRaises(ValueError, nodes.SingleIndexedComponent)	# no arg
		self.failUnlessRaises(TypeError, nodes.Component.create, api.MFn.kMeshEdgeComponent) # invalid type

	def test_data(self):
		# DATA CREATION
		###############
		# create all implemented data types
		self.failUnlessRaises(TypeError, nodes.Data.create)
		
		basic_types = (	nodes.VectorArrayData, nodes.UInt64ArrayData, nodes.StringData, 
						nodes.StringArrayData, nodes.SphereData, nodes.PointArrayData,
						nodes.NObjectData, nodes.MatrixData, nodes.IntArrayData, 
						nodes.SubdData, nodes.NurbsSurfaceData, nodes.NurbsCurveData, 
						nodes.MeshData, nodes.LatticeData, nodes.DoubleArrayData, 
						nodes.ComponentListData, nodes.ArrayAttrsData )
		
		knullobj = nodes.api.MObject()
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
		pd = nodes.PluginData.create(nodes.PyPickleData.kPluginDataId)
		
		
		# NUMERIC DATA
		# these items cannot work or do not work as simple types are not represented
		# by data containers
		forbidden = (	'kLast', 'kDouble', 'kInvalid', 'k4Double', 
						'kBoolean', 'kShort', 'kInt', 'kByte', 'kAddr', 
						'kChar', 'kLong', 'kFloat' )
		types = [ (k, v) for k,v in api.MFnNumericData.__dict__.iteritems() if k.startswith('k') and k not in forbidden ]
		assert types
		for type_name, type_id in types:
			data = nodes.NumericData.create(type_id)
			assert not data.isNull() and isinstance(data, nodes.NumericData)
		# END for each numeric data type
		
		
		# COMPONENT LIST DATA
		#####################
		# special testing
		mvc = nodes.SingleIndexedComponent.create(api.MFn.kMeshVertComponent)
		cd = nodes.ComponentListData.create()
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
		

	def test_mfncachebuilder( self ):
		"""byroniom.maya.nodes.base: write a generated cache using the builder function
		should be redone for maya 8.5 perhaps ... or in fact its enough to have one for all maya versions
		and just merge them
		@todo: do it """
		# nodes.typ.writeMfnDBCacheFiles( )


