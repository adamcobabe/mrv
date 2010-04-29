# -*- coding: utf-8 -*-
"""Test basic node features """
from mrv.test.maya import *
import mrv.maya as mrvmaya
import mrv.maya.nt.persistence as persistence
import mrv.maya.nt as mrvnt
from mrv.maya.nt import *
from mrv.maya.ns import *
from mrv.maya.ref import FileReference
import mrv.maya as mrv
import mrv.maya.undo as undo

import mrv.maya.nt as nt

import maya.OpenMaya as api
import maya.OpenMayaRender as apirender
import maya.cmds as cmds

import tempfile

class StorageNetworkNodeWrong(nt.Network):
	# misses the __mrv_virtual_subtype__ attribute
	pass 
	
	
class StorageNetworkNode(nt.Network, nt.StorageBase):
	"""Implements a wrapper for a specially prepared Network node which has 
	StorageNode capabilities"""
	__mrv_virtual_subtype__ = 1
	
	def __init__(self, node):
		"""The overloaded initializer assures we do not wrap incompatible types"""
		if not hasattr(self, 'data'):
			raise TypeError("%r node is missing its data attribute" % self)
		# END handle type
		# assure we initialize our base - it requires some information to work
		super(StorageNetworkNode, self).__init__(node)
		
	@classmethod
	def create(cls):
		"""Create a new Network node with storage node capabilities"""
		n = nt.Network()
		n.addAttribute(persistence.createStorageAttribute(persistence.PyPickleData.kPluginDataId))
		return StorageNetworkNode(n.object())
		
	@classmethod
	def iter_instances(cls):
		for n in nt.iterDgNodes(nt.Node.Type.kAffect, asNode=False):
			try:
				yield StorageNetworkNode(n)
			except TypeError:
				continue
			# END try to wrap our type around
		# END for each network node
	
	
class Bar(object):
	pass 


class Foo(object):
	"""A Foo containing Bars
	:note: Documentation Example"""
	def __init__ (self, bars):
		self.bars = tuple(bars)
		if not self.bars:
			raise ValueError("Need bars")


class BigFoo(Foo):
	"""A BigFoo is a better Foo"""
	pass

		
def makeFoo(bar_iterable, big=False):
	"""Create a new Foo instance which contains the Bar instances
	retrieved from the bar_iterable.
	
	:return: ``Foo`` compatible instance. If big was True, it will 
		support the ``BigFoo`` interface
	:param bar_iterable: iterable yielding Bar instances. As Foo's
		cannot exist without Bars, an empty iterable is invalid.
	:param big: if True, change the return type from ``Foo`` to ``BigFoo``
	:raise ValueError: if bar_iterable did not yield any Bar instance"""
	if big:
		return BigFoo(bar_iterable)
	return Foo(bar_iterable)


class TestCases( unittest.TestCase ):
	
	def test_makeFoo(self):
		# assure it returns Foo instances, BigFoo if the flag is set
		bars = (Bar(), Bar()) 
		for big in range(2):
			foo = makeFoo(iter(bars), big)
			assert isinstance(foo, Foo)
			if big:
				assert isinstance(foo, BigFoo)
			# END check rval type
			
			# which contain the bars we passed in
			assert foo.bars == bars
			
			# empty iterables raise
			self.failUnlessRaises(ValueError, makeFoo, tuple(), big)
		# END for each value of 'big'
	
	@with_persistence
	def test_virtual_subtype(self):
		n = nt.Network()
		
		# types must define the __mrv_virtual_subtype__ attribute
		self.failUnlessRaises(TypeError, StorageNetworkNodeWrong, n.object())
		
		# make a StorageNetwork node 
		sn = StorageNetworkNode.create()
		assert isinstance(sn, StorageNetworkNode)
		
		# it cannot wrap ordinary network nodes - we implemented it that way
		self.failUnlessRaises(TypeError, StorageNetworkNode, n.object())
		
		# iteration works fine as well
		sns = list(StorageNetworkNode.iter_instances())
		assert len(sns) == 1 and isinstance(sns[0], StorageNetworkNode)
		assert sns[0] == sn
		
		# be sure we can use the storage interface
		assert isinstance(sn.dataIDs(), list)
		
	@with_persistence
	def test_replacing_default_node_types(self):
		n = nt.Network()
		sn = StorageNetworkNode.create()
		
		# REPLACING BUILTIN NODE TYPES
		##############################
		# if we want to play crazy, we can make all network nodes our special
		# storage node, be replacing the existing Network node type.
		# Any instantiation will fail as if its not one of our specialized nodes, 
		# but this is implementation defined of course.
		# Defining a new derived Type automatically puts it into the nt module
		OldNetwork = nt.Network
		class Network(StorageNetworkNode):
			def sayhello(self):
				print "hello"
		# yes, the official Network node is now our own one, automatically
		assert nt.Network is Network
		
		sn2 = nt.Node(str(sn))
		assert isinstance(sn2, StorageNetworkNode)
		assert isinstance(sn2.dataIDs(), list)
		
		# and it can say something
		sn2.sayhello()
		
		# we cannot wrap normal nodes as our initializer on StorageNetworkNode barks 
		# if the vital data plug cannot be found.
		self.failUnlessRaises(TypeError, nt.Node, str(n))
		
		# reset the old one, we affect everything within MRV now
		nt.removeCustomType(Network)
		nt.addCustomType(OldNetwork)
		
		# everything back to normal - we get plain old network nodes
		sn_network = nt.Node(sn.object())
		assert type(sn_network) is OldNetwork
		assert type(sn_network) is nt.Network
		
		# REPLACING BUILTIN NODES PROPERLY
		##################################
		class Network(OldNetwork, nt.StorageBase):
			def __init__(self, node):
				"""Implement the initializer such that we only initialize our base
				if we have the 'data' attribute. Otherwise we keep it uninitialized, so it 
				will not be functional"""
				try:
					super(Network, self).__init__(node)
				except TypeError:
					pass
				# END handle input type
				
			def sayaloha(self):
				print "aloha"
				
		# END better Super-Network implementation
		assert nt.Network is Network
		
		# now plain network nodes will be new Network nodes, but we are allowed
		# to create them
		# NodeFromObj works as well, just to be sure
		n2 = nt.NodeFromObj(n.object())
		assert type(n2) is Network
		
		# as the storage base has not been initialized, we cannot do anything 
		# with it. The actual point here though is that users who don't know the
		# interface will get a fully functional network node at least.
		# As we do not 'tighten' the interface, code that doesn't expect our type
		# will not get into trouble.
		self.failUnlessRaises(AttributeError, n2.dataIDs)
		assert isinstance(n2, OldNetwork)
		n2.sayaloha()
		
		# and storage network nodes will be 'Network' nodes whose additional
		# functions we can use
		sn2 = nt.Node(sn.object())
		assert type(sn2) is Network
		sn2.sayaloha()
		sn2.dataIDs()
		
		# once again, get rid of our custom type, reset the old one 
		nt.removeCustomType(Network)
		nt.addCustomType(OldNetwork)
		assert nt.Network is OldNetwork
		
	def test_replace_non_leaf_node_types(self):
		# keep the previous type as we want to restore it
		OldDependNode = nt.DependNode
		
		nold = nt.Network()
		assert str(nold).startswith("network")
		
		# overwriting the foundation of all nodes will not change anything 
		# for existing node types, as they have bound the previous type already.
		class DependNode(nt.Node):
			"""This type cannot do anything, we have removed functionality"""
			def __str__(self):
				return 'me_as_string'
		# END custom DependNode
		
		assert str(nold).startswith('network')
		
		# new instances still use the default implementation
		nnew = nt.Network()
		assert str(nnew).startswith('network')
		
		# also we cannot instatiate it explicitly as we are not inheriting 
		# from the type that MRV wants to create, Network
		self.failUnlessRaises(TypeError, DependNode, nnew.object())
		
		# we could get away with this, but we clean it up anyway
		nt.removeCustomType(DependNode)
		nt.addCustomType(OldDependNode)
		
		
		# MONKEY PATCHING
		#################
		# The only way to get custom method implementation directly into the non-leaf  
		# node types is monkey patching, hence existing methods will be overwritten
		# with your implementation
		# Using the dict for retrieval as one would get class methods otherwise, these
		# check for the actual type passed in which would fail in our case.
		old_str = nt.DependNode.__dict__['__str__']
		nt.DependNode.__str__ = DependNode.__dict__['__str__']
		
		assert str(nold) == 'me_as_string'
		# undo our changes
		nt.DependNode.__str__ = old_str
		
	@with_scene('empty.ma')
	def test_usage_sets(self):
		# NOTE: This test is part of the pymel comparison
		p, t, f = Node('persp'), Node('top'), Node('front')
		s = ObjectSet()
		
		# add single - set centric or object centric
		s.add(p)
		p.addTo(s)
		assert p in s
		
		# add multiple
		s.add((t, f))
		
		# remove single - set or object centric
		s.discard(p)
		p.removeFrom(s)
		
		# remove multiple 
		s.discard((t, f))
		
		assert len(s) == 0
		
	@with_scene('empty.ma')
	def test_usage_shading_engines(self):
		# NOTE: this test is part of the pymel comparison
		isg = Node("initialShadingGroup")
		rp = Node("renderPartition")
		
		# assign new shading engine to the render partition
		sg = ShadingEngine()
		sg.setPartition(rp)
		
		
		# create a poly sphere
		m = Mesh()
		PolySphere().output.mconnectTo(m.inMesh)
		
		# assign all faces to the initial shading group
		# Cannot use the m.cf[:] shortcut to get a complete component as 
		# shading engines apparently don't deal with it properly
		m.addTo(isg, m.cf[:m.numPolygons()])
		
		# force the first 200 faces into another shading engine
		m.addTo(sg, m.cf[:200], force=True)
		
		
	def test_add_and_retrieve_complex_datatype_using_api(self):
		sellist = api.MSelectionList()
		sellist.add("persp")
		p = api.MDagPath()
		sellist.getDagPath(0, p)
		
		mfndag = api.MFnDagNode(p)
		mfnattr = api.MFnTypedAttribute()
		mfndata = api.MFnStringArrayData()
		attr = mfnattr.create("stringArray", "sa", api.MFnData.kStringArray, mfndata.create())
		mfndag.addAttribute(attr)
		
		# all this to add an attribute, now retrieve the value
		# this is rather short as we reuse the function set.
		mfndata.setObject(mfndag.findPlug("sa").asMObject())
		mfndata.array()
		
	@with_scene('empty.ma')
	def test_add_and_retrieve_complex_datatype_using_mrv(self):
		p = nt.Node("persp")
		p.addAttribute(nt.TypedAttribute.create('stringarray', 'sa', Data.Type.kStringArray, nt.StringArrayData.create()))
		p.sa.masData().array()
		
	@with_undo
	@with_persistence
	@with_scene('empty.ma')
	def test_usage_examples(self):
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
		
		# static methods #
		assert DependNode.classification('lambert') == api.MFnDependencyNode.classification('lambert')
		rnl = RenderLayer.currentLayer()
		assert isinstance(rnl, Node)
		rnlobj = apirender.MFnRenderLayer.currentLayer()
		assert rnl == rnlobj
		assert isinstance(rnlobj, api.MObject)
		
		# enumerations #
		assert Node.Type.kMesh == api.MFn.kMesh
		assert Attribute.DisconnectBehavior.kReset == api.MFnAttribute.kReset
		assert Data.Type.kPlugin == api.MFnData.kPlugin
		
		assert Node.Type.nameByValue(api.MFn.kMesh) == 'kMesh'
		
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
		assert p.children(lambda n: n.apiType()==Node.Type.kCamera)[0] == ps
		
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
		assert p.isInstancedAttribute(p.attribute('wm')) 
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
		assert p.tx.parent() == p.t
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
			sattr = TypedAttribute.create("string", "str", Data.Type.kString)
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
		assert selection(Node.Type.kTransform)[-1] == p
		
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
		
		assert len(list(refa.iterNodes(Node.Type.kMesh))) == 8
		
		refa.remove(); refb.remove()
		assert not refa.exists() and not refb.exists()
		assert len(FileReference.ls()) == 0
		
		
		# SCENE
		#######
		empty_scene = get_maya_file('empty.ma')
		mrv.Scene.open(empty_scene, force=1)
		assert mrv.Scene.name().tonative() == empty_scene
		
		files = list()
		def beforeAndAfterNewCB( data ):
			assert data is None
			files.append(mrv.Scene.name())
			
		mrv.Scene.beforeNew = beforeAndAfterNewCB
		mrv.Scene.afterNew = beforeAndAfterNewCB
		
		assert len(files) == 0
		mrv.Scene.new()
		assert len(files) == 2
		assert files[0].tonative() == empty_scene
		
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
		
		tmpscene = tempfile.gettempdir() + "/persistence.mb"
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
		
		# ABOUT METHODS AND TYPES
		#########################
		p = Node("persp")
		ps = p.child(0)			# method originally on MFnDagNode
		assert isinstance(ps, DagNode)
		
		self.failUnlessRaises(TypeError, ps.hasSamePerspective, ps)
		assert ps.hasSamePerspective(ps.dagPath())		# method on MFnCamera
		
