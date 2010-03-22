# -*- coding: utf-8 -*-
"""Test basic node features """
from mrv.test.maya import *
import mrv.maya as bmaya
import mrv.maya.nt as nt
import maya.OpenMaya as api
import maya.cmds as cmds

from mrv.maya.nt import *
from mrv.maya.ns import *
from mrv.maya.ref import FileReference
import mrv.maya as mrv
import mrv.maya.undo as undo
import tempfile
import __builtin__
set = __builtin__.set		# fix set, it was overwritten by the set module when importing nodes *

class TestTransform( unittest.TestCase ):
	
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
		
	def test_usage_examples(self):
		bmaya.Scene.new(force=True)
		# NOTE: If this test fails ( because of name changes for instance ), the 
		# documentation needs to be fixed as well, usage.rst.
		
		# NODES
		#######
		p = Node("persp")
		t = Node("time1")
		assert p == p
		assert p != t
		assert p in [p]
		
		s = set()
		s.add(p)
		s.add(t)
		assert p in s and t in s and len(s | s) == 2
		
		# getApiObject returns the api object which represents the underlying maya node best
		assert isinstance(p.apiObject(), api.MDagPath)
		assert isinstance(t.apiObject(), api.MObject)
		
		assert isinstance(p.dagPath(), api.MDagPath)
		assert isinstance(p.object(), api.MObject)
		
		# api types
		assert isinstance(p, Transform) and p.apiType() == api.MFn.kTransform
		assert isinstance(t, Time) and t.apiType() == api.MFn.kTime
		assert p.hasFn(p.apiType())
		
		# get the MObject representation
		assert isinstance(p.object(), api.MObject) and isinstance(t.object(), api.MObject)
		
		
		# METHODS
		#########
		self.failUnlessRaises(AttributeError, getattr, p, 'doesnt_exist')
		
		assert p.isFromReferencedFile() == p.isReferenced()
		
		assert isinstance(p.getMFnClasses(), list)
		
		# DAG NAVIGATION
		################
		ps = p.children()[0]
		assert ps == p[0]
		assert ps[-1] == p
		
		assert ps == p.shapes()[0]
		assert ps.parent() == p == ps.transform()
		
		# filtering
		assert len(p.childrenByType(Transform)) == 0
		assert p.childrenByType(Camera) == p.childrenByType(Shape)
		assert p.children(lambda n: n.apiType()==api.MFn.kCamera)[0] == ps
		
		# deep and iteration
		assert ps.iterParents().next() == p == ps.root()
		assert ps.parentDeep()[0] == p
		assert p.childrenDeep()[0] == ps
		
		# NODE CREATION
		###############
		cs = createNode("namespace:subspace:group|other:camera|other:cameraShape", "camera")
		assert len(cs.parentDeep()) == 2
		
		m = Mesh()
		assert isinstance(m, Mesh) and m.isValid()
		
		assert m == Mesh(forceNewLeaf=False) 
		
		# NODE DUPLICATION
		##################
		# this duplicated tweaks, set and shader assignments as well
		md = m.duplicate()
		assert md != m
		
		# NAMESPACES
		#############
		ons = cs.namespace()
		assert ons == cs[-1].namespace()	# namespace of parent node
		
		sns = cs[-2].namespace()
		assert sns != ons
		
		pns = sns.parent()
		assert pns.children()[0] == sns
		
		assert len(list(sns.iterNodes())) == 1
		assert len(list(pns.iterNodes())) == 0
		assert len(list(pns.iterNodes(depth=1))) == 1
		
		# DAG MANIPULATION
		##################
		csp = cs.transform()
		cs.setParent(p)
		assert cs.instanceCount(0) == 1
		csi = cs.addParent(csp)
		
		assert csi.isInstanced() and cs.instanceCount(0) == 2
		assert csi != cs
		assert csi.object() == cs.object()
		
		assert cs.parentAtIndex(0) == p
		assert cs.parentAtIndex(1) == csp
		
		p.removeChild(csi)
		assert not cs.isValid() and csi.isValid()
		assert not csi.isInstanced()
		
		
		# reparent
		cspp = csp[-1]
		csi.reparent(cspp)
		
		csp.unparent()
		assert csp.parent() is None and len(csp.children()) == 0
		assert len(cspp.children()) == 1
		assert csi.instanceCount(0) == 1
		
		
		# NODE- AND GRAPH-ITERATION
		###########################
		for dagnode in it.iterDagNodes():
			assert isinstance(dagnode, DagNode)
			
		for dg_or_dagnode in it.iterDgNodes():
			assert isinstance(dg_or_dagnode, DependNode)
		
		rlm = Node("renderLayerManager")
		assert len(list(it.iterGraph(rlm))) == 2
		
		# SELECTIONLISTS
		################
		nl = (p, t, rlm)
		sl = toSelectionList(nl)
		assert isinstance(sl, api.MSelectionList) and len(sl) == 3
		
		sl2 = api.MSelectionList.mfromList(nl)
		sl3 = api.MSelectionList.mfromStrings([str(n) for n in nl])
		
		
		osl = selection()
		select(sl)
		select(p, t)
		# clear the selection
		select()
		assert len(selection()) == 0
		
		for n in sl.mtoIter():
			assert isinstance(n, DependNode)
		
		assert list(sl.mtoIter()) == sl.mtoList()
		assert list(sl.mtoIter()) == list(it.iterSelectionList(sl))
		
		# OBJECTSETS AND PARTITIONS
		###########################
		objset = ObjectSet()
		aobjset = ObjectSet()
		partition = Partition()
		
		assert len(objset) == 0
		objset.addMembers(sl)
		objset.add(csp)
		aobjset.addMember(csi)
		assert len(objset)-1 == len(sl)
		assert len(aobjset) == 1
		assert csp in objset
		
		partition.addSets([objset, aobjset])
		assert objset in partition and aobjset in partition
		partition.discard(aobjset)
		assert aobjset not in partition
		
		assert len(objset + aobjset) == len(objset) + len(aobjset)
		assert len(objset & aobjset) == 0
		aobjset.add(p)
		assert len(aobjset) == 2
		assert len(aobjset & objset) == 1
		assert len(aobjset - objset) == 1
		
		assert len(aobjset.clear()) == 0
		
		
		# COMPONENTS AND COMPONENT ASSIGNMENTS
		######################################
		# create a polycube and pipe its output into our mesh shape
		isb = Node("initialShadingGroup")
		pc = PolyCube()
		pc.output.mconnectTo(m.inMesh)
		assert m.numVertices() == 8
		assert m not in isb                            # it has no shaders on object level
		assert len(m.componentAssignments()) == 0   # nor on component leveld 
		
		# object level
		m.addTo(isb)
		assert m in isb
		
		assert m.sets(m.fSetsRenderable)[0] == isb
		m.removeFrom(isb)
		assert not m.isMemberOf(isb)
		
		# component level
		isb.add(m, m.cf[range(0,6,2)])     # add every second face
		isb.discard(m, m.cf[:])	            # remove all component assignments
		
		isb.add(m, m.cf[:3])				# add faces 0 to 2
		isb.add(m, m.cf[3])					# add single face 3
		isb.add(m, m.cf[4,5])				# add remaining faces
		
		# query assignments
		se, comp = m.componentAssignments()[0]
		assert se == isb
		e = comp.elements()
		assert len(e) == 6					# we have added all 6 faces
		
		
		# Plugs and Attributes
		######################
		# PLUGS #
		assert isinstance(p.translate, api.MPlug)
		assert p.translate == p.findPlug('t')
		assert p.t == p.translate
		
		# connections
		p.tx.mconnectTo(p.ty).mconnectTo(p.tz)
		assert p.tx.misConnectedTo(p.ty)
		assert p.ty.misConnectedTo(p.tz)
		assert not p.tz.misConnectedTo(p.ty)
		
		p.tx.mdisconnectFrom(p.ty).mdisconnectFrom(p.tz)
		assert len(p.ty.minputs()) + len(p.tz.minputs()) == 0
		assert p.tz.minput().isNull()
		
		p.tx.mconnectTo(p.tz, force=False)
		self.failUnlessRaises(RuntimeError, p.ty.mconnectTo, p.tz, force=False)     # tz is already connected
		p.ty.mconnectTo(p.tz)                              # force the connection, force defaults True
		p.tz.mdisconnect()                                    # disconnect all
		
		# query
		assert isinstance(p.tx.asFloat(), float)
		assert isinstance(t.outTime.asMTime(), api.MTime)
		
		ninst = p.instanceNumber()
		pewm = p.worldMatrix.elementByLogicalIndex(ninst)
		
		matfn = api.MFnMatrixData(pewm.asMObject())
		matrix = matfn.matrix()                       # wrap data manually

		dat = pewm.masData()							# or get a wrapped version right away
		assert matrix == dat.matrix()
	
		
		# set values
		newx = 10.0
		p.tx.msetDouble(newx)
		assert p.tx.asDouble() == newx
		
		meshdata = m.outMesh.asMObject()
		meshfn = api.MFnMesh(meshdata)
		meshfn.deleteFace(0)                        # delete one face of copied cube data
		assert meshfn.numPolygons() == 5
		
		mc = Mesh()                                 # create new empty mesh to 
		mc.cachedInMesh.msetMObject(meshdata)        # hold the new mesh in the scene
		assert mc.numPolygons() == 5
		assert m.numPolygons() == 6
		
		# compounds and arrays
		ptc = p.t.mchildren()
		assert len(ptc) == 3
		assert (ptc[0] == p.tx) and (ptc[1] == p.ty)
		assert ptc[2] == p.t.mchildByName('tz')
		assert p.tx.mparent() == p.t
		assert p.t.isCompound()
		assert p.tx.isChild()
		
		assert p.wm.isArray()
		assert len(p.wm) == 1
		
		for element_plug in p.wm:
			assert element_plug.isElement()
			
		# graph traversal
		mihistory = list(m.inMesh.miterInputGraph())
		assert len(mihistory) > 2
		assert mihistory[0] == m.inMesh
		assert mihistory[2] == pc.output		# ignore groupparts
		
		pcfuture = list(pc.output.miterOutputGraph())
		assert len(pcfuture) > 2
		assert pcfuture[0] == pc.output
		assert pcfuture[2] == m.inMesh			# ignore groupparts
		
		# ATTRIBUTES #
		cattr = CompoundAttribute.create("compound", "co")
		cattr.setArray(True)
		if cattr:
			sattr = TypedAttribute.create("string", "str", TypedAttribute.kString)
			pattr = NumericAttribute.createPoint("point", "p")
			mattr = MessageAttribute.create("mymessage", "mmsg")
			mattr.setArray(True)
			
			cattr.addChild(sattr)
			cattr.addChild(pattr)
			cattr.addChild(mattr)
		# END compound attribute
		
		n = Network()
		n.addAttribute(cattr)
		assert n.compound.isArray()
		assert n.compound.isCompound()
		assert len(n.compound.mchildren()) == 3
		assert n.compound.mchildByName('mymessage').isArray()
		
		n.removeAttribute(n.compound.attribute())
		
		
		# MESH COMPONENT ITERATION
		average_x = 0.0
		for vit in m.vtx:                  # iterate the whole mesh
			average_x += vit.position().x
		average_x /= m.numVertices()
		assert m.vtx.iter.count() == m.numVertices()
		
		sid = 3
		for vit in m.vtx[sid:sid+3]:       # iterate subsets
			assert sid == vit.index()
			sid += 1
		
		for eit in m.e:                    # iterate edges
			eit.point(0); eit.point(1)
			
		for fit in m.f:                    # iterate faces
			fit.isStarlike(); fit.isPlanar()
			
		for mit in m.map:                  # iterate face-vertices
			mit.faceId(); mit.vertId() 
		
		
		# SELECTIONS
		#############
		select(p.t, "time1", p, ps)
		assert len(selection()) == 4
		
		# simple filtering
		assert activeSelectionList().miterPlugs().next() == p.t
		assert selection(api.MFn.kTransform)[-1] == p
		
		# adjustments
		sl = activeSelectionList()
		sl.remove(0)		# remove plug
		select(sl)
		assert len(activeSelectionList()) == len(selection()) == 3
		
		assert len(selection(predicate=lambda n: n.isReferenced())) == 0
		
		# COMPONENTS AND PLUGS#
		sl = api.MSelectionList()
		sl.add(m.dagPath(), m.cf[:4])			# first 4 faces
		select(sl)
		assert len(activeSelectionList().miterComponents().next()[1].elements()) == 4
		
		sl.clear()
		sl.add(p.t)
		sl.add(m.outMesh)
		select(sl)
		assert len(selection()) == 2
		
		
		# NAMESPACES
		############
		assert p.namespace() == RootNamespace
		# we created 2 namespaces implicitly with objects
		assert len(RootNamespace.children()) == 2
		
		barns = Namespace.create("foo:bar")
		foons = barns.parent()
		assert len(RootNamespace.children()) == 3
		
		assert len(list(barns.iterNodes())) == 0 and len(list(RootNamespace.iterNodes())) != 0
		
		
		# editing namespaces
		m.setNamespace(barns)
		assert m.namespace() == barns
		
		barns.moveNodes(foons)
		assert foons.iterNodes().next() == m
		
		# deleting / rename
		foons.delete()
		assert not barns.exists() and not foons.exists()
		assert m.namespace() == RootNamespace
		
		subns = Namespace.create("sub")
		subnsrenamed = subns.rename("bar")
		assert subnsrenamed != subns
		assert subnsrenamed.exists() and not subns.exists() 
		
		
		# REFERENCES 
		#############
		refa = FileReference.create(get_maya_file('ref8m.ma'))     # file with 8 meshes
		refb = FileReference.create(get_maya_file('ref2re.ma'))    # two subreferences with subreferences
		
		assert refb.isLoaded()
		assert len(FileReference.ls()) == 2
		
		assert len(refa.children()) == 0 and len(refb.children()) == 2
		subrefa, subrefb = refb.children()
		
		assert subrefa.namespace() != subrefb.namespace()
		assert subrefa.path() == subrefb.path()
		assert subrefa.parent() == refb
		
		refa.setLoaded(False)
		assert not refa.isLoaded()
		assert refa.setLoaded(True).isLoaded()
		
		assert len(list(refa.iterNodes(api.MFn.kMesh))) == 8
		
		refa.remove(); refb.remove()
		assert not refa.exists() and not refb.exists()
		assert len(FileReference.ls()) == 0
		
		
		# SCENE
		#######
		empty_scene = get_maya_file('empty.ma')
		mrv.Scene.open(empty_scene, force=1)
		assert mrv.Scene.name() == empty_scene
		
		files = list()
		def beforeAndAfterNewCB( data ):
			assert data is None
			files.append(mrv.Scene.name())
			
		mrv.Scene.beforeNew = beforeAndAfterNewCB
		mrv.Scene.afterNew = beforeAndAfterNewCB
		
		assert len(files) == 0
		mrv.Scene.new()
		assert len(files) == 2
		assert files[0] == empty_scene
		
		mrv.Scene.beforeNew.remove(beforeAndAfterNewCB)
		mrv.Scene.afterNew.remove(beforeAndAfterNewCB)
		
		
		# UNDO
		######
		@undoable
		def undoable_func( delobj ):
			p.tx.mconnectTo(p.tz)
			delobj.delete()
		
		p = Node("persp")
		t = Transform()
		assert not p.tx.misConnectedTo(p.tz)
		assert t.isValid() and t.isAlive()
		undoable_func(t)
		assert p.tx.misConnectedTo(p.tz)
		assert not t.isValid() and t.isAlive()
		
		cmds.undo()
		assert not p.tx.misConnectedTo(p.tz)
		assert t.isValid() and t.isAlive()
		
		# Advanced Uses #
		ur = undo.UndoRecorder()
		ur.startRecording()
		p.tx.mconnectTo(p.ty)
		p.tx.mconnectTo(p.tz)
		ur.stopRecording()
		p.t.mconnectTo(t.t)
		
		assert p.tx.misConnectedTo(p.ty)
		assert p.tx.misConnectedTo(p.tz)
		assert p.t.misConnectedTo(t.t)
		ur.undo()
		assert not p.tx.misConnectedTo(p.ty)
		assert not p.tx.misConnectedTo(p.tz)
		assert p.t.misConnectedTo(t.t)
		
		
		# PERSISTENCE
		#############
		did = 'dataid'
		sn = StorageNode()
		snn = sn.name()
		pd = sn.pythonData( did, autoCreate = True )
		
		pd[0] = "hello"
		pd['l'] = [1,2,3]
		
		tmpscene = tempfile.gettempdir() + "/persistence.ma"
		mrv.Scene.save(tmpscene)
		mrv.Scene.open(tmpscene)
		
		sn = Node(snn)
		pd = sn.pythonData( did )
		assert len(pd) == 2
		assert pd[0]  == "hello"
		assert pd['l'] == [1,2,3]
		
		objset = sn.objectSet(did, 0, autoCreate=True)
		objset.add(Transform())
		
		mrv.Scene.save(tmpscene)
		mrv.Scene.open(tmpscene)
		
		assert len(Node(snn).objectSet(did, 0)) == 1
		
		os.remove(tmpscene)
		
