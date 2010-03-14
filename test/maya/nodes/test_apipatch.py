# -*- coding: utf-8 -*-
""" Test general nodes features """
from mayarv.test.maya import *
import mayarv.maya.nodes as nodes
import maya.cmds as cmds
import maya.OpenMaya as api
import mayarv.test.maya.nodes as ownpackage
from itertools import izip

class TestDataBase( unittest.TestCase ):
	""" Test data classes  """

	def test_primitives( self ):
		"""mayarv.maya.nodes: test primitive types"""
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
		"""mayarv.maya.nodes: Test plug abilities( node.attribute ) """
		persp = nodes.Node( "persp" )
		front	 = nodes.Node( "front" )
		side	 = nodes.Node( "side" )
		matworld = persp.worldMatrix

		str( matworld )
		repr( matworld )

		# CONNECTIONS
		#######################
		# CHECK COMPOUND ACCESS
		tx = persp.translate['tx']
		
		# can access attributes twice
		persp.translate

		# DO CONNECTIONS ( test undo/redo )
		persp.translate >> front.translate

		assert persp.translate & front.translate 	# isConnectedTo
		assert persp.translate.p_input.isNull( ) 
		cmds.undo( )
		assert not persp.translate.isConnectedTo( front.translate ) 
		cmds.redo( )
		assert front.translate in persp.translate.p_outputs 

		# check p_output
		assert persp.translate.p_output == front.translate 
		self.failUnlessRaises( IndexError, persp.rotate.getOutput )

		# CHECK CONNECTION FORCING
		persp.translate >  front.translate 			# already connected
		self.failUnlessRaises( RuntimeError, persp.scale.__gt__, front.translate )# lhs > rhs

		# overwrite connection
		side.translate >> front.translate
		assert side.translate >= front.translate 

		# undo - old connection should be back
		cmds.undo()
		assert persp.translate >= front.translate 

		# disconnect input
		front.translate.disconnectInput()
		assert not persp.translate >= front.translate 

		cmds.undo()

		# disconnect output
		persp.t.disconnectOutputs( )
		assert len( persp.translate.p_outputs ) == 0 

		cmds.undo()
		assert persp.t.isConnectedTo( front.translate ) 

		# disconnect from
		persp.t | front.translate
		assert not persp.t & front.t 

		cmds.undo()
		assert persp.t >= front.t 

		# COMPARISONS
		assert persp.t != front.t 
		assert persp.t['tx'] != persp.t['ty'] 

		# affected plugs
		affectedPlugs = persp.t.affects( )
		assert len( affectedPlugs ) > 1  

		affectedPlugs = persp.t.affected( )
		assert len( affectedPlugs ) > 1  
		
		
		# test multi connections
		sn = nodes.createNode("network1", "network")
		sn2 = nodes.createNode("network2", "network") 
		tn = nodes.createNode("network3", "network")
		
		def pir(array_plug, range_iter):
			for index in range_iter:
				yield array_plug.getByLogicalIndex(index)
			# END for each item in range
		# END plugs-in-range
		
		# connect 10 to 10 
		r = range(10)
		api.MPlug.connectMultiToMulti(	izip(pir(sn.a, r), pir(tn.affectedBy, r)), force=False) 
		for i in r:
			assert sn.a.getByLogicalIndex(i).isConnectedTo(tn.affectedBy.getByLogicalIndex(i))
		# END make connection assertion
		
		# connection of overlapping range fails without force
		r = range(5, 15)
		self.failUnlessRaises(RuntimeError, api.MPlug.connectMultiToMulti, izip(pir(sn2.a, r), pir(tn.affectedBy, r)), force=False)
		
		# there no connection should have worked ( its atomic )
		# hence slot 10 is free
		persp.tx > tn.affectedBy.getByLogicalIndex(10)
		
		# force connection works
		api.MPlug.connectMultiToMulti(izip(pir(sn2.a, r), pir(tn.affectedBy, r)), force=True)
		
		for i in r:
			assert sn2.a.getByLogicalIndex(i).isConnectedTo(tn.affectedBy.getByLogicalIndex(i))
		# END make connection assertion

		# ATTRIBUTES AND UNDO
		#######################
		funcs = ( 	( "isLocked", "setLocked" ), ( "isKeyable", "setKeyable" ),
					( "isCachingFlagSet", "setCaching" ), ( "isChannelBoxFlagSet", "setChannelBox" ) )

		plugnames =( "t", "tx", "r","rx", "s", "sy" )
		for p in plugnames:
			plug = getattr( persp, p )

			for ( getname, setname ) in funcs:
				fget = getattr( plug, getname )
				fset = getattr( plug, setname )

				curval = fget()
				oval = bool( 1 - curval )
				fset( oval )

				# SPECIAL HANDLING as things cannot be uncached
				if setname == "setCaching":
					continue

				assert fget() == oval 

				cmds.undo()
				assert fget() == curval 

				cmds.redo()
				assert fget() == oval 

				fset( curval )	# reset
			# END for each function
		# END for each plugname

		# QUERY
		############################
		# ELEMENT ITERATION
		matworld.evaluateNumElements( )
		for elm in matworld:
			assert elm.getParent( ) == matworld 

		translate = persp.translate

		assert len( translate.getChildren() ) == translate.getNumChildren() 

		# CHILD ITERATION
		for child in translate.getChildren( ):
			assert child.getParent( ) == translate 
		assert len( translate.getChildren() ) == 3 

		# SUB PLUGS GENERAL METHOD
		assert len( matworld ) == len( matworld.getSubPlugs() ) 
		assert translate.numChildren() == len( translate.getSubPlugs() ) 
		assert len( translate.getSubPlugs() ) == 3 


		# ARRAY CONNECTIONS
		###################
		objset = nodes.createNode( "set1", "objectSet" )
		partition = nodes.createNode( "partition1", "partition" )
		pma = nodes.createNode( "plusMinusAverage1", "plusMinusAverage" )
		destplug = persp.translate.connectToArray( pma.input3D, exclusive_connection = True )
		assert persp.translate >= destplug 

		# exclusive connection should return exisiting plug
		assert persp.translate.connectToArray( pma.input3D, exclusive_connection = True ) == destplug 

		# but newones can also be created
		assert persp.translate.connectToArray( pma.input3D, exclusive_connection = False ) != destplug 
		#assert objset.partition.connectToArray( partition.sets, exclusive_connection = False ) != destplug 


		# assure the standin classes are there - otherwise my list there would
		# bind to the standins as the classes have not been created yet
		plugs = [ matworld, translate ]
		for plug in plugs: plug.getAttribute()

		# CHECK ATTRIBUTES and NODES
		for plug,attrtype in zip( plugs, [ nodes.TypedAttribute, nodes.NumericAttribute ] ):
			attr = plug.getAttribute( )

			assert isinstance( attr, nodes.Attribute ) 
			assert isinstance( attr, attrtype ) 

			node = plug.getNode()
			assert isinstance( node, nodes.Node ) 
			assert node == persp 

		# UNDO / REDO
		##############
		cmds.undoInfo( swf = 1 )
		cam = nodes.createNode( "myTrans", "transform" )
		testdb = [  ( cam.visibility, "Bool", True, False ),
					( cam.translate['tx'], "Double", 0.0, 2.0 ) ]
		# TODO: Add all missing types !
		for plug, typename, initialval, targetval in testdb:
			getattrfunc = getattr( plug, "as"+typename )
			setattrfunc = getattr( plug, "set"+typename )

			assert getattrfunc() == initialval 
			setattrfunc( targetval )
			assert getattrfunc() == targetval 
			cmds.undo()
			assert getattrfunc() == initialval 
			cmds.redo()
			assert getattrfunc() == targetval 
		# END for each tuple in testdb
		
	@with_scene('empty.ma')
	def test_plug_itertools(self):
		p = nodes.Node('persp')
		( p.tx > p.ty ) > p.tz
		
		# check future
		pxf = list(p.tx.iterOutputGraph())
		assert len(pxf) == 3
		assert pxf[0] == p.tx and pxf[1] == p.ty and pxf[2] == p.tz
		
		# check history
		pzh = list(p.tz.iterInputGraph())
		assert len(pzh) == 3
		assert pzh[0] == p.tz and pzh[1] == p.ty and pzh[2] == p.tx 

	def test_matrixData( self ):
		"""mayarv.maya.nodes: test matrix data"""
		node = nodes.Node( "persp" )
		matplug = node.getPlug( "worldMatrix" )
		assert not matplug.isNull() 
		assert matplug.isArray() 
		matplug.evaluateNumElements()			# to assure we have something !

		assert matplug.getName() == "persp.worldMatrix" 
		assert len( matplug ) 

		matelm = matplug[0]
		assert matelm == matplug[0.0]		# get by logical index
		assert not matelm.isNull() 

		matdata = matelm.asData( )
		assert isinstance( matdata, nodes.MatrixData ) 
		mmatrix = matdata.matrix( )
		assert isinstance( mmatrix, api.MMatrix ) 

	def test_matrix( self ):
		"""mayarv.maya.nodes: Test the matrices"""
		tmat = api.MTransformationMatrix()

		tmat.setScale( ( 2.0, 4.0, 6.0 ) )

		s = tmat.getScale()
		assert s.x == 2.0 
		assert s.y == 4.0 
		assert s.z == 6.0 

		t = api.MVector( 1.0, 2.0, 3.0 )
		tmat.setTranslation( t )
		assert t == tmat.getTranslation( ) 

		tmat.setRotate( ( 20, 40, 90, 1.0 ) )

	def test_MPlugArray( self ):
		"""mayarv.maya.nodes: test the plugarray wrapper
		NOTE: plugarray can be wrapped, but the types stored will always be"""
		node = nodes.Node( "defaultRenderGlobals" )
		pa = node.getConnections( )

		myplug = pa[0]
		myplug.getName()				# special Plug method not available in the pure api object
		pa.append( myplug )

		assert len( pa ) == 4 

		# SETITEM
		l = 5
		pa.setLength( l )
		nullplug = pa[0]
		for i in range( l ):
			pa[i] = nullplug


		# __ITER__
		for plug in pa:
			plug.getName( )
			assert isinstance( plug, api.MPlug ) 

		self.failIf( len( pa ) != 5 )

	def test_MSelectionList( self ):
		sl = nodes.toSelectionList(nodes.it.iterDgNodes())
		nodeset = set()
		
		# can be handled like a list
		assert len(sl) > 3
		
		# provides unique wrapped nodes
		for node in sl:
			assert isinstance(node, nodes.Node)
			nodeset.add(node)
		# END for each node
		assert len(nodeset) == len(sl)
		
		# test creation functions
		node_list = list(sl)
		nls = node_list[4:15]
		for slsnodesgen, selfun in ((lambda : [str(n) for n in nls], api.MSelectionList.fromStrings),
									(lambda : nls, api.MSelectionList.fromList),
									(lambda : [(n, api.MObject()) for n in node_list[-5:] if isinstance(n, nodes.DagNode)], api.MSelectionList.fromComponentList) ):
			slsnodes = slsnodesgen()
			sls = selfun(iter(slsnodes))
			assert isinstance(sls, api.MSelectionList) and len(sls) == len(slsnodes) 
		# END for each variant
		
		# from multiple
		assert len(api.MSelectionList.fromMultiple(*nls)) == len(nls)
		
		# from iter
		assert len(api.MSelectionList.fromIter(iter(nls))) == len(nls)
		

		# test conversion methods
		assert list(sl) == sl.toList()
		assert hasattr(sl.toIter(), 'next')
		
		# test contains
		dagnode = nodes.Node("persp")
		dgnode = nodes.Node("time1")
		plug = dgnode.o
		
		sls = api.MSelectionList.fromList((dagnode, dgnode, plug))
		assert len(sls) == 3
		
		nc = 0
		for item in sls:
			assert item in sls
			nc += 1
		# END for each item
		assert nc == len(sls)
		
		# access nodes by index
		slitems = list()
		for index in xrange(len(sl)):
			slitems.append(sl[index])
		# END for each index
		assert slitems and slitems[-1] == sl[-1]
		
		# COMPONENT ITERATION
		m = nodes.Mesh()
		nodes.PolyCube().output > m.inMesh
		sl = api.MSelectionList()
		sl.add(m.getMDagPath())
		sl.add(m.getMDagPath(), m.cf[:])
		assert len(list(sl.iterComponents())) == 1
		
		
		# PLUG ITERATION
		p = nodes.Node("persp")
		sl = api.MSelectionList()
		sl.add(p.getMDagPath())
		sl.add(p.t)
		sl.add(p.rx)
		assert len(list(sl.iterPlugs())) == 2
		
		
		

	def test_array_creation(self):
		def assert_matches(ar, items):
			assert len(ar) == len(items)
			for i in xrange(len(ar)):
				assert ar[i] == items[i]
			# END assert array entry matches item entry
		# END assert items
			
		# test all random access types
		def assert_creation(cls, items):
			# from multiple
			ar = cls.fromMultiple(*items)
			assert_matches(ar, items)
			
			# from iter
			ar = cls.fromIter(iter(items))
			assert_matches(ar, items)
			
			# from list
			ar = cls.fromList(items)
			assert_matches(ar, items)
			
			# test iteration
			ne = 0
			for elm in ar:
				ne += 1
			assert len(ar) == ne
		# END assert items
		
		col1 = api.MColor(1.0, 1.0)
		col2 = api.MColor(1.0, 2.0)
		col3 = api.MColor(1.0, 3.0)
		
		p1 = api.MPoint(1.0, 1.0)
		p2 = api.MPoint(1.0, 2.0)
		p3 = api.MPoint(1.0, 3.0)
		
		fp1 = api.MFloatPoint(1.0, 1.0)
		fp2 = api.MFloatPoint(1.0, 2.0)
		fp3 = api.MFloatPoint(1.0, 3.0)
		
		fv1 = api.MFloatVector(1.0, 1.0)
		fv2 = api.MFloatVector(1.0, 2.0)
		fv3 = api.MFloatVector(1.0, 3.0)
		
		v1 = api.MVector(1.0, 1.0)
		v2 = api.MVector(1.0, 2.0)
		v3 = api.MVector(1.0, 3.0)
		
		for cls, items in ((api.MIntArray, (4,6,7)),
							(api.MDoubleArray, (4.0,6.0,7.0)),
							(api.MFloatArray, (4.0,6.0,7.0)),
							(api.MColorArray, (col1, col2, col3)),
							(api.MPointArray, (p1, p2, p3)), 
							(api.MFloatPointArray, (fp1, fp2, fp3)), 
							(api.MFloatVectorArray, (fv1, fv2, fv3)),
							(api.MVectorArray, (v1, v2, v3))):
			assert_creation(cls, items)
		# END for each cls/items

	def test_intarray_creation(self):
		# from range
		self.failUnlessRaises(ValueError, api.MIntArray.fromRange, 3, 2)
		self.failUnlessRaises(ValueError, api.MIntArray.fromRange, 3, -5)
		ia = api.MIntArray.fromRange(2,4)
		assert len(ia) == 2 and ia[0] == 2 and ia[1] == 3
		
