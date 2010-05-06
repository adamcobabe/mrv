
.. highlight:: python

*****
Nodes
*****
The term *Node* means any Dependency Node or DagNode which has been wrapped for convenient use. It is derived from ``mrv.maya.nt.base.Node``.

A Node wraps an underlying *MObject* or an *MDagPath*, and it can be retrieved either by iteration, by using one of the various methods of the MRV library or by manually wrapping a maya node whose name is known::
	
	from mrv.maya.nt import *
	# wrap a node by name
	p = Node("persp")
	Transform("|persp")
	t = Node("time1")
	
The Node p now represents the transform named 'persp' within the maya scene. You can interact with it natively. It will behave properly within sets and when being compared::
	
	assert p == p
	assert p != t
	assert p in [p]
	
	s = set()
	s.add(p)
	s.add(t)
	assert p in s and t in s and len(s | s) == 2
	
As initially stated, a Node wraps the respective API object, which is either of type *MDagPath* or *MObject*. These objects can be retrieved from the Node afterwards::
	
	# apiObject returns the api object which represents the underlying maya node best
	assert isinstance(p.apiObject(), api.MDagPath)
	assert isinstance(t.apiObject(), api.MObject)
	
You can query the MObject or the MDagPath specifically::
	
	assert isinstance(p.dagPath(), api.MDagPath)
	assert isinstance(p.object(), api.MObject)
	
Although each wrapped node has a python type, which is its capitalized maya type, you may easily query the MayaAPI type representation, being a member of the ``MFn.k...`` enumeration::
	
	assert isinstance(p, Transform) and p.apiType() == api.MFn.kTransform
	assert isinstance(t, Time) and t.apiType() == api.MFn.kTime
	assert p.hasFn(p.apiType())
	assert isinstance(p.object(), api.MObject) and isinstance(t.object(), api.MObject)
	
.. warning:: Do not keep Nodes cached, but prefer to re-retrieve them on demand as they may become invalid in the meanwhile depending on the operations performed in Maya.

Method Lookup
=============
Nodes represent their respective maya api object, and make all matching MFnFunctionSet methods available directly.
Calling these methods involves nothing special, you just make the call on your node. Its important to know which methods are available and the order in which they are looked up. Lets study the method resolution by checking the first case, a non-existing method::
	
	# this will raise an AttributeError
	p.doesnt_exist()
	
MRV looks up the name in the following order:
 1. Find a method on the instance itself. This would succeed if the method has been implemented on the respective python type or one of its base types, in order to make it easier to use for instance, or to work around limitations.
 
 2. Find the method name on the topmost MFnFunction set, and resort to more general function sets if the name could not be found. If a Node wraps a mesh for example, it would try to find the Method in MFnMesh, then in MFnDagNode.
 
 3. Try to find a MPlug with the given name, internally using ``MFnDependencyNode.findPlug(name)`` to achieve this.

This implies that functions will be found *before* an attribute of the same name. If you need the plug instead, use its short attribute name.

It would be quite expensive to make any call if the shown lookup would be performed anytime, but in fact it will only be done once per node type, afterwards the type will know that you are looking for a method, or an MPlug respectively, and return the requested object right away. MRV types learn what they need to know at runtime.

Even in tight loops, this convenient calling convention may be used without overwhelming performance loss, but if you are interested in optimizing this, have a look at the :ref:`performance-docs-label` paragraph.

MFnFunction Aliases
===================
Methods that map to MFnFunctionSet functions may be aliased such that they better fit or are faster to type. Hence they can be accessed either by their original name or by their alias. For example, (MFnDependencyNode).isFromReferencedFile can also be retrieved using .isReferenced::
	
	assert p.isFromReferencedFile() == p.isReferenced()

If you are interested in knowing which MFnFunction sets your node supports, call the ``getMFnClasses`` method::
	
	p.getMFnClasses()
	[<class 'maya.OpenMaya.MFnTransform'>,
	 <class 'maya.OpenMaya.MFnDagNode'>,
	 <class 'maya.OpenMaya.MFnDependencyNode'>,
	 <class 'maya.OpenMaya.MFnDependencyNode'>]
	 
If you want to learn more about the MFnFunctionSet method aliases, see :ref:`mfnmethodmutator-label`

Static MFn Functions
====================
Static functions on function sets may be accessed through the actual node type natively::
	
	assert DependNode.classification('lambert') == api.MFnDependencyNode.classification('lambert')
	
Return values of static methods are wrapped as well if possible::
	
	import maya.OpenMayaRender as apirender
	rnl = RenderLayer.currentLayer()
	assert isinstance(rnl, Node)
	rnlobj = apirender.MFnRenderLayer.currentLayer()
	assert rnl == rnlobj
	assert isinstance(rnlobj, api.MObject)
	
Enumerations
============
If a MFnFunctionSet associated with a ``NodeType``, ``DataType`` or ``AttributeType`` has enumerations, these are statically available on the type by the name used in the MayaAPI documentation. A utility function allows to map enumeration values back to their name::
	
	assert Node.Type.kMesh == api.MFn.kMesh
	assert Attribute.DisconnectBehavior.kReset == api.MFnAttribute.kReset
	assert Data.Type.kPlugin == api.MFnData.kPlugin
		
	assert Node.Type.nameByValue(api.MFn.kMesh) == 'kMesh'
	
DAG-Navigation
==============
DAG objects are organized in a hierarchy which can be walked and traversed at will. The following example also uses a very handy shortcut, allowing you to access the children and parent nodes by index::
	
	ps = p.children()[0]
	assert ps == p[0]
	assert ps[-1] == p
	assert ps == p.children()[0]
	
Sometimes its required to use filters, only listing shape nodes or transforms are the most common cases and supported specifically::
	
	assert ps == p.shapes()[0]
	assert ps.parent() == p == ps.transform()
	
More specialized filters can be applied as well::
	
	assert len(p.childrenByType(Transform)) == 0
	assert p.childrenByType(Camera) == p.childrenByType(Shape)
	assert p.children(lambda n: n.apiType()==api.MFn.kCamera)[0] == ps
	
Generally, all items that are organized in a hierarchy support the  ``mrv.interface.iDagItem`` interface which provides methods for traversal and query::
	
	assert ps.iterParents().next() == p == ps.getRoot()
	assert ps.parentDeep()[0] == p
	assert p.childrenDeep()[0] == ps

Node Creation
=============
Creating nodes in MRV is simple and maybe a bit slow as you can only create about 1200 to 2500 Nodes per second. There is only one method to accomplish this with plenty of functionality built-in, ``mrv.maya.nt.base.createNode``. This shall only be a brief example::
	
	cs = createNode("namespace:subspace:group|other:camera|other:cameraShape", "camera")
	assert len(cs.parentsDeep()) == 2
	
The short and more convenient way to create nodes is to use the NodeType() call signature, whose ``**kwargs`` will be passed to the ``createNode`` function::
	
	m = Mesh()
	assert isinstance(m, Mesh) and m.isValid()
		
	assert m == Mesh(forceNewLeaf=False)
	
Node Duplication
================
Node duplication is an interesting problem as it might involve many secondary tasks, such as maintaining light-links or shading assignments.

When using the blank duplicate function as provided by the MayaAPI, one will only get a bare copy of the input node, without any connections. Its safe to state that the MayaAPI duplicate is far behind the MEL implementation, as it can take care of much more. Lets just call it a design mistake that they implement functionality in a MEL command instead of in a library so that it can be made accessible in the MayaAPI *and* in MEL.

MRV tackles the problem by providing an interface called ``mrv.interface.iDuplicatable``. It works much like a c++ copy constructor, and anything implementing it correctly is able to be duplicated properly. Node-derived types may implement special duplication routines to assure their are duplicated correctly::
	
	# this duplicated tweaks, set and shader assignments as well
	md = m.duplicate()
	assert md != m
	
If you ever miss anything to be duplicated on a certain node-type, you only need to implement it in the ``copyFrom`` method in the respective type or the most appropriate of its base types.
	
Namespaces
==========
Namespaces in MRV are objects which may create a hierarchy, hence they support the ``mrv.interface.iDagItem`` interface::
	
	ons = cs.namespace()
	assert ons == cs[-1].namespace()	# namespace of parent node
	
	sns = cs[-2].namespace()
	assert sns != ons
	
	pns = sns.parent()
	assert pns.children()[0] == sns
	
	assert len(list(sns.iterNodes())) == 1
	assert len(list(pns.iterNodes())) == 0
	assert len(list(pns.iterNodes(depth=1))) == 1
	
DAG-Manipulation and Instancing
===============================
Change the structure of the DAG, adjust parent-child relation ships and handle instances. DAG manipulation is an interesting topic as it is implemented using the MayaAPI, but it provides a new programming interface unique to MRV in order to be more intuitive and as a workaround to many issues that can occur when using the MayaAPI natively.

Transforms can be parented under the world's root, which is the root of the Directed Acyclic Graph, and under other transforms. Shape nodes may be parented under transforms only. Some special nodes may appear parented under Shape nodes, which effectively puts them into the Shape's ``underworld``.

As long as Transforms and Shapes have only one parent, there is only one DAGPath leading up to the object in question. If you add more parents to them, there are more DAGPaths leading to the same object, which is called ``instancing`` in Maya.

The MRV DAG manipulation API provides multiple methods to adjust the number of children and parents of the individual items, including undo support::
	
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
 
It is worth noting that the only 'real' methods are ``addChild`` and ``removeChild``. All others, such as ``addParent``, ``removeParent``, ``setParent`` and ``addInstancedChild`` are only variations of them.

``reparent`` and ``unparent`` are different operations than the instance-aware ones presented in the previous section, as they will not only ignore instances, but also force the object into a single DAGPath. This effectively removes all instances::
	
	cspp = csp[-1]
	csi.reparent(cspp)
	
	csp.unparent()
	assert csp.parent() is None and len(csp.children()) == 0
	assert len(cspp.children()) == 1
	assert csi.instanceCount(0) == 1

The MayaAPI provides methods to handle instances and to accomplish fundamental re-parenting, MRV makes them more usable by providing own methods. Nonetheless, the general feeling of inconsistency remains as these sets of functions are slightly opposing each other, some are instance aware, some are not.

As a general advice, you should be aware of instances and the methods to use to safely operate on them. ``reparent`` and ``unparent`` in MRV can be used safely as well as they will raise by default if instances would be destroyed otherwise.

Node- and Graph-Iteration
=========================
The fastest way to retrieve Nodes is by iterating them. There are three major areas to iterate: DAG Nodes only, DG Nodes ( which includes DAG Nodes ), or the dependency graph which is defined by plug connections between DG Nodes.

MRV iterators are built around their MayaAPI counterparts, but provide a more intuitive and pythonic interface::
	
	for dagnode in it.iterDagNodes():
		assert isinstance(dagnode, DagNode)
		
	for dg_or_dagnode in it.iterDgNodes():
		assert isinstance(dg_or_dagnode, DependNode)
	
	rlm = Node("renderLayerManager")
	assert len(list(it.iterGraph(rlm))) == 2
	
Handling Selections with SelectionLists
=======================================
Many methods within the MayaAPI and within MRV will take MSelectionLists as input or return them. An MSelectionList is an ordered heterogeneous list which keeps MObjects, MDagPaths, MPlugs as well as ComponentLists. Although the name may suggest it, ``MSelectionList`` instances have nothing to do with Maya's active selection.

MSelectionLists can easily be created using the ``mrv.maya.nt.base.toSelectionList`` function, or the monkey-patched creator functions. Conversion functions come in several variants, some are more specialized, but faster, than others. Its safe and usually fast enough to use the general version though::
	
	nl = (p, t, rlm)
	sl = toSelectionList(nl)
	assert isinstance(sl, api.MSelectionList) and len(sl) == 3
		
	sl2 = api.MSelectionList.mfromList(nl)
	sl3 = api.MSelectionList.mfromStrings([str(n) for n in nl])
	
Adjust maya's selection or retrieve it using the ``mrv.maya.nt.base.select`` and ``mrv.maya.nt.base.selection`` functions::
	
	osl = selection()
	select(sl)
	select(p, t)
	
	# clear the selection
	select()
	assert len(selection()) == 0
	
Please be aware of the fact that ``selection`` as well as ``select`` are high-level functions that emphasize convenience over performance. If this matters, use the respective functions in MGlobal instead.

SelectionLists can be iterated natively, or can explicitly be converted into lists::
	
	for n in sl.mtoIter():
		assert isinstance(n, DependNode)
		
	assert list(sl.mtoIter()) == sl.mtoList()
	assert list(sl.mtoIter()) == list(it.iterSelectionList(sl))

ObjectSets and Partitions
=========================
Sets and Partitions are a major feature of Maya, which uses ObjectSets and their derivatives in many locations of the program. Partitions allow to enforce exclusive membership among sets. 

ObjectSets in MRV can be controlled much like ordinary python sets, but they in fact correspond to an ObjectSet compatible node with your scene::
	
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
	
ShadingEngines work the same, except that they are attached to the renderParition by default.
	
Components and Component-Level Shader Assignments
=================================================
The following examples operate on a simple mesh, representing a polygonal cube with 6 faces, 8 vertices and 12 edges::
	
	isb = Node("initialShadingGroup")
	pc = PolyCube()
	pc.output.mconnectTo(m.inMesh)
	assert m.numVertices() == 8
	assert m not in isb                         # it has no shaders on object level
	assert len(m.componentAssignments()) == 0   # nor on component leveld 
	
Shader assignments on object level can simply be created and broken by adding or removing items from the respective shading group::
	
	m.addTo(isb)
	assert m in isb
	
Component Assignments are mutually exclusive to the object level assignments, but maya will just allow the object level assignments to take priority. If you want component level assignments to become effective, make sure you have no object level assignments left::
	
	assert m.sets(m.fSetsRenderable)[0] == isb
	m.removeFrom(isb)
	assert not m.isMemberOf(isb)
	
	isb.add(m, m.cf[range(0,6,2)])     # add every second face
	isb.discard(m, m.cf[:])            # remove all component assignments
		
	isb.add(m, m.cf[:3])				# add faces 0 to 2
	isb.add(m, m.cf[3])					# add single face 3
	isb.add(m, m.cf[4,5])				# add remaining faces
	
To query component assignments, use the ``mrv.maya.nt.base.Shape.componentAssignments`` function::
	
	se, comp = m.componentAssignments()[0]
	assert se == isb
	e = comp.elements()
	assert len(e) == 6					# we have added all 6 faces

