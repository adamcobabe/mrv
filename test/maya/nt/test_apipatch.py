# -*- coding: utf-8 -*-
""" Test general nodes features """
from mrv.test.maya import *
import mrv.maya.nt as nt

import maya.cmds as cmds
import maya.OpenMaya as api

from itertools import izip

class TestDataBase( unittest.TestCase ):
	""" Test data classes  """

	def test_primitives( self ):
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
			
			str(inst) != repr(inst)

	@with_undo
	def test_MPlug( self ):
		persp = nt.Node( "persp" )
		front	 = nt.Node( "front" )
		side	 = nt.Node( "side" )
		matworld = persp.worldMatrix
		assert isinstance(matworld.mfullyQualifiedName(), basestring)

		str( matworld )
		repr( matworld )

		# CONNECTIONS
		#######################
		# CHECK COMPOUND ACCESS
		tx = persp.translate.mchildByName('tx')
		
		# can access attributes twice
		persp.translate

		# DO CONNECTIONS ( test undo/redo )
		persp.translate.mconnectTo(front.translate, force=True)

		assert persp.translate.misConnectedTo(front.translate) 	# misConnectedTo
		assert persp.translate.minput().isNull( ) 
		cmds.undo( )
		assert not persp.translate.misConnectedTo( front.translate ) 
		cmds.redo( )
		assert front.translate in persp.translate.moutputs() 

		# check moutput
		assert persp.translate.moutput() == front.translate 
		assert persp.rotate.moutput().isNull()		# unconnected return nullPlus as minput does

		# CHECK CONNECTION FORCING
		persp.translate.mconnectTo(front.translate, force=False) 			# already connected
		self.failUnlessRaises( RuntimeError, persp.s.mconnectTo, front.translate, force=False )

		# overwrite connection
		side.translate.mconnectTo(front.translate)	# force default True
		assert side.translate.misConnectedTo(front.translate) 

		# undo - old connection should be back
		cmds.undo()
		assert persp.translate.misConnectedTo(front.translate) 

		# disconnect input
		front.translate.mdisconnectInput()
		assert not persp.translate.misConnectedTo(front.translate) 

		cmds.undo()

		# disconnect output
		persp.t.mdisconnectOutputs( )
		assert len( persp.translate.moutputs() ) == 0 

		cmds.undo()
		assert persp.t.misConnectedTo( front.translate ) 

		# disconnect from
		persp.t.mdisconnectFrom(front.translate)
		assert not persp.t.misConnectedTo(front.t) 

		cmds.undo()
		assert persp.t.misConnectedTo(front.t) 

		# COMPARISONS
		assert persp.t != front.t 
		assert persp.t.mchildByName('tx') != persp.t.mchildByName('ty') 

		# affected plugs
		affectedPlugs = persp.t.maffects( )
		assert len( affectedPlugs ) > 1  

		affectedPlugs = persp.t.maffected( )
		assert len( affectedPlugs ) > 1  
		
		
		# test multi connections
		sn = nt.createNode("network1", "network")
		sn2 = nt.createNode("network2", "network") 
		tn = nt.createNode("network3", "network")
		
		def pir(array_plug, range_iter):
			for index in range_iter:
				yield array_plug.elementByLogicalIndex(index)
			# END for each item in range
		# END plugs-in-range
		
		# connect 10 to 10 
		r = range(10)
		api.MPlug.mconnectMultiToMulti(	izip(pir(sn.a, r), pir(tn.affectedBy, r)), force=False) 
		for i in r:
			assert sn.a.elementByLogicalIndex(i).misConnectedTo(tn.affectedBy.elementByLogicalIndex(i))
		# END make connection assertion
		
		# connection of overlapping range fails without force
		r = range(5, 15)
		self.failUnlessRaises(RuntimeError, api.MPlug.mconnectMultiToMulti, izip(pir(sn2.a, r), pir(tn.affectedBy, r)), force=False)
		
		# there no connection should have worked ( its atomic )
		# hence slot 10 is free
		persp.tx > tn.affectedBy.elementByLogicalIndex(10)
		
		# force connection works
		api.MPlug.mconnectMultiToMulti(izip(pir(sn2.a, r), pir(tn.affectedBy, r)), force=True)
		
		for i in r:
			assert sn2.a.elementByLogicalIndex(i).misConnectedTo(tn.affectedBy.elementByLogicalIndex(i))
		# END make connection assertion

		# ATTRIBUTES AND UNDO
		#######################
		funcs = ( 	( "isLocked", "msetLocked" ), ( "isKeyable", "msetKeyable" ),
					( "isCachingFlagSet", "msetCaching" ), ( "isChannelBoxFlagSet", "msetChannelBox" ) )

		plugnames =( "t", "tx", "r","rx", "s", "sy" )
		for p in plugnames:
			plug = persp.findPlug(p)

			for ( getname, setname ) in funcs:
				fget = getattr( plug, getname )
				fset = getattr( plug, setname )

				curval = fget()
				oval = bool( 1 - curval )
				fset( oval )

				# SPECIAL HANDLING as things cannot be uncached
				if setname == "msetCaching":
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
			assert elm.mparent( ) == matworld 

		translate = persp.translate

		assert len( translate.mchildren() ) == translate.numChildren() 

		# CHILD ITERATION
		for child in translate.mchildren( ):
			assert child.mparent( ) == translate 
		assert len( translate.mchildren() ) == 3 

		# SUB PLUGS GENERAL METHOD
		assert len( matworld ) == len( matworld.msubPlugs() ) 
		assert translate.numChildren() == len( translate.msubPlugs() ) 
		assert len( translate.msubPlugs() ) == 3 


		# ARRAY CONNECTIONS
		###################
		objset = nt.createNode( "set1", "objectSet" )
		partition = nt.createNode( "partition1", "partition" )
		pma = nt.createNode( "plusMinusAverage1", "plusMinusAverage" )
		destplug = persp.translate.mconnectToArray( pma.input3D, exclusive_connection = True )
		assert persp.translate.misConnectedTo(destplug) 

		# exclusive connection should return exisiting plug
		assert persp.translate.mconnectToArray( pma.input3D, exclusive_connection = True ) == destplug 

		# but newones can also be created
		assert persp.translate.mconnectToArray( pma.input3D, exclusive_connection = False ) != destplug 
		#assert objset.partition.mconnectToArray( partition.sets, exclusive_connection = False ) != destplug 


		# assure the standin classes are there - otherwise my list there would
		# bind to the standins as the classes have not been created yet
		plugs = [ matworld, translate ]
		for plug in plugs: plug.mwrappedAttribute()

		# CHECK ATTRIBUTES and NODES
		for plug, attrtype in zip( plugs, [ nt.TypedAttribute, nt.CompoundAttribute ] ):
			attr = plug.mwrappedAttribute( )
			assert isinstance( attr, nt.Attribute ) 
			assert isinstance( attr, attrtype ) 

			node = plug.mwrappedNode()
			assert isinstance( node, nt.Node ) 
			assert node == persp 

		# UNDO / REDO
		##############
		cam = nt.createNode( "myTrans", "transform" )
		testdb = [ ( cam.visibility, "Bool", True, False ),
					( cam.tx, "Double", 0.0, 2.0 ) ]
		# TODO: Add all missing types !
		for plug, typename, initialval, targetval in testdb:
			getattrfunc = getattr( plug, "as"+typename )
			setattrfunc = getattr( plug, "mset"+typename )

			assert getattrfunc() == initialval 
			setattrfunc( targetval )
			assert getattrfunc() == targetval 
			cmds.undo()
			assert getattrfunc() == initialval 
			cmds.redo()
			assert getattrfunc() == targetval 
		# END for each tuple in testdb
		
		
		# TEST EVERYTHING
		#################
		# This part has been written to be very sure every customized method gets 
		# called at least once. I don't trust my 'old'  tests, although they do 
		# something and are valuable to the testing framework. 
		nwnode = nt.Network()
		persp.msg.mct(nwnode.affectedBy.elementByLogicalIndex(0))
		front.msg.mct(nwnode.affectedBy.elementByLogicalIndex(1))
		
		t = persp.translate
		tx = persp.tx
		wm = persp.wm
		a = nwnode.affectedBy
		
		a.evaluateNumElements()
		assert len(wm) == 1 and len(a) == 2
		assert isinstance(iter(wm).next(), api.MPlug)
		assert len(list(a)) == 2
		
		# test str/repr
		assert str(wm) != str(a)
		assert repr(wm) != str(wm)
		assert wm != a
		
		# is it really necessary to apply custom handling here ? Check __eq__ method
		# test comparison
		assert a[0] == a[0]
		assert a[0] != a[1]
		
		# mparent 
		assert tx.mparent() == t
		assert a[0].mparent() == a
		
		# mchildren
		assert len(a[0].mchildren()) == 0
		assert len(t.mchildren()) == 3
		
		# mchildByName
		assert t.mchildByName('tx') == tx
		self.failUnlessRaises(TypeError, tx.mchildByName, 'something')
		self.failUnlessRaises(AttributeError, t.mchildByName, 'doesntexist')
		
		# msubPlugs
		assert len(t.msubPlugs()) == 3
		assert len(a.msubPlugs()) == 2
		assert len(tx.msubPlugs()) == 0
		
		# msetLocked
		tx.msetLocked(1)
		assert tx.isLocked()
		tx.msetLocked(0)
		assert not tx.isLocked()
		
		# msetKeyable
		tx.msetKeyable(0)
		assert not tx.isKeyable()
		tx.msetKeyable(1)
		assert tx.isKeyable()
		
		# msetCaching
		tx.msetCaching(0)
		#assert not tx.isCachingFlagSet()	# for some reason, the caching cannot be changed here
		tx.msetCaching(1)
		assert tx.isCachingFlagSet() == 1
		
		# msetChannelBox
		tx.msetChannelBox(0)
		assert not tx.isChannelBoxFlagSet()
		tx.msetChannelBox(1)
		assert tx.isChannelBoxFlagSet() == 1
		
		# mconnectMultiToMulti
		# is tested elsewhere
		
		# connectTo
		self.failUnlessRaises(RuntimeError, persp.msg.mconnectTo, a[1], force=False)	# already connected
		front.msg.mconnectTo(a[1], force=False)		# already connected
		front.msg.mconnectTo(a[0], force=True)		# force breaks connections
		persp.msg.mconnectTo(a[0])					# default is force
		
		# mconnectToArray
		# sufficiently tested ( -> st )
		
		# mdisconnect
		# st
		
		# mdisconnectInput
		# st
		
		# mdisconnectOutputs
		# st
		
		# mdisconnectFrom
		# st
		
		# mdisconnectNode
		# st
		
		# mhaveConnection
		assert api.MPlug.mhaveConnection(front.msg, a[1]) and api.MPlug.mhaveConnection(a[1], front.msg)
		assert not api.MPlug.mhaveConnection(persp.msg, a[1]) and not api.MPlug.mhaveConnection(a[1], persp.msg)
		
		# misConnectedTo
		# st
		
		# moutputs
		assert len(front.msg.moutputs()) == 1 and front.msg.moutputs()[0] == a[1]
		assert len(a[0].moutputs()) == 0
		
		# moutput
		# st
		
		# minputs
		assert len(a.minputs()) == 2
		assert len(a[1].minputs()) == 1
		
		
		# miterGraph 
		# st
		
		# miterInputGraph
		# st
		
		# miterOutputGraph
		# st
		
		# minput
		# st
		
		# mconnections
		assert len(front.msg.mconnections()) == 2
		assert len(a[1].mconnections()) == 2
		
		
		# mdependencyInfo
		m = nt.Mesh()
		assert len(m.outMesh.maffected())
		assert isinstance(m.outMesh.maffected()[0], api.MPlug)
		assert m.outMesh.maffected() == m.outMesh.mdependencyInfo(by=True)
		assert isinstance(m.inMesh.maffects(), list)	# no affected items for some reason
		assert m.inMesh.maffects() == m.inMesh.mdependencyInfo(by=False)
		
		
		# mnextLogicalIndex|plug
		assert a.mnextLogicalIndex() == 2
		assert a.mnextLogicalPlug().logicalIndex()
		
		# mwrappedAttribute
		assert isinstance(a.mwrappedAttribute(), nt.Attribute)
		
		# mwrappedNode
		assert isinstance(a.mwrappedNode(), nt.Node)
		
		# masData
		nt.PolyCube().output.mconnectTo(m.inMesh)	# need data here
		assert isinstance(m.outMesh.masData(), nt.Data)
		
		# mfullyQualifiedName
		assert a.mfullyQualifiedName() != a.partialName()
		
	@with_scene('empty.ma')
	def test_plug_itertools(self):
		p = nt.Node('persp')
		p.tx.mconnectTo(p.ty).mconnectTo(p.tz)
		
		# check future
		pxf = list(p.tx.miterOutputGraph())
		assert len(pxf) == 3
		assert pxf[0] == p.tx and pxf[1] == p.ty and pxf[2] == p.tz
		
		# check history
		pzh = list(p.tz.miterInputGraph())
		assert len(pzh) == 3
		assert pzh[0] == p.tz and pzh[1] == p.ty and pzh[2] == p.tx 

	def test_matrixData( self ):
		node = nt.Node( "persp" )
		matplug = node.findPlug( "worldMatrix" )
		assert not matplug.isNull() 
		assert matplug.isArray() 
		matplug.evaluateNumElements()							# to assure we have something !

		assert matplug.name() == "persp.worldMatrix" 
		assert len( matplug ) 

		matelm = matplug[0]
		assert matelm == matplug.elementByLogicalIndex(0)		# get by logical index
		assert not matelm.isNull() 

		matdata = matelm.masData( )
		assert isinstance( matdata, nt.MatrixData ) 
		mmatrix = matdata.matrix( )
		assert isinstance( mmatrix, api.MMatrix ) 

	def test_matrix( self ):
		tmat = api.MTransformationMatrix()

		tmat.msetScale( ( 2.0, 4.0, 6.0 ) )

		s = tmat.mgetScale()
		assert s.x == 2.0 
		assert s.y == 4.0 
		assert s.z == 6.0 

		t = api.MVector( 1.0, 2.0, 3.0 )
		tmat.setTranslation( t )
		assert t == tmat.getTranslation( ) 

	def test_MPlugArray( self ):
		node = nt.Node( "defaultRenderGlobals" )
		pa = node.connections( )

		myplug = pa[0]
		myplug.name()				# special Plug method not available in the pure api object
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
			plug.name( )
			assert isinstance( plug, api.MPlug ) 

		self.failIf( len( pa ) != 5 )

	def test_MSelectionList( self ):
		sl = nt.toSelectionList(nt.it.iterDgNodes())
		nodeset = set()
		
		# can be handled like a list
		assert len(sl) > 3
		
		# provides unique wrapped nodes
		for node in sl.mtoIter():
			assert isinstance(node, nt.Node)
			nodeset.add(node)
		# END for each node
		assert len(nodeset) == len(sl)
		
		# test creation functions
		node_list = list(sl.mtoIter())
		nls = node_list[4:15]
		for slsnodesgen, selfun in ((lambda : [str(n) for n in nls], api.MSelectionList.mfromStrings),
									(lambda : nls, api.MSelectionList.mfromList),
									(lambda : [(n, api.MObject()) for n in node_list[-5:] if isinstance(n, nt.DagNode)], api.MSelectionList.mfromComponentList) ):
			slsnodes = slsnodesgen()
			sls = selfun(iter(slsnodes))
			assert isinstance(sls, api.MSelectionList) and len(sls) == len(slsnodes) 
		# END for each variant
		
		# from multiple
		assert len(api.MSelectionList.mfromMultiple(*nls)) == len(nls)
		
		# from iter
		assert len(api.MSelectionList.mfromIter(iter(nls))) == len(nls)
		

		# test conversion methods
		assert list(sl.mtoIter()) == sl.mtoList()
		assert hasattr(sl.mtoIter(), 'next')
		
		# test contains
		dagnode = nt.Node("persp")
		dgnode = nt.Node("time1")
		plug = dgnode.o
		
		sls = api.MSelectionList.mfromList((dagnode, dgnode, plug))
		assert len(sls) == 3
		
		nc = 0
		for item in sls.mtoIter():
			assert sls.mhasItem(item)
			nc += 1
		# END for each item
		assert nc == len(sls)
		
		# COMPONENT ITERATION
		m = nt.Mesh()
		nt.PolyCube().output > m.inMesh
		sl = api.MSelectionList()
		sl.add(m.dagPath())
		sl.add(m.dagPath(), m.cf[:])
		assert len(list(sl.miterComponents())) == 1
		
		
		# PLUG ITERATION
		p = nt.Node("persp")
		sl = api.MSelectionList()
		sl.add(p.dagPath())
		sl.add(p.t)
		sl.add(p.rx)
		assert len(list(sl.miterPlugs())) == 2

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
			ar = cls.mfromMultiple(*items)
			assert_matches(ar, items)
			
			# from iter
			ar = cls.mfromIter(iter(items))
			assert_matches(ar, items)
			
			# from list
			ar = cls.mfromList(items)
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
		self.failUnlessRaises(ValueError, api.MIntArray.mfromRange, 3, 2)
		self.failUnlessRaises(ValueError, api.MIntArray.mfromRange, 3, -5)
		ia = api.MIntArray.mfromRange(2,4)
		assert len(ia) == 2 and ia[0] == 2 and ia[1] == 3
		
