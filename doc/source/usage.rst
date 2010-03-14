.. _usage-label:

==================
Using MayaRV.Maya
==================
This document gives an overview of the facilities within the Maya portion of MayaReVised which contains classes that require maya to run.

The examples given here can be viewed as one consecutive script which should work of all the code is pasted into a mayarv testcase for instance. The latter one can be found in ``mayarv.test.maya.nodes.test_base`` (test_usage_examples). If you want to be more explorative, adjust the test's code yourself and run it to see the results. For more information on how to run tests, see :ref:`runtestsdoc-label`.

It is advised to start a mayarv enabled ipython shell allowing you to try the examples interactively, see :ref:`imayarv-label`.

To understand some of the terms used here, its a plus if you are familiar with the MayaAPI. If not, it shouldn't be a problem either as knowledge of the MayaAPI is not strictly required.

=====
Nodes
=====
The term *Node* means any Dependency Node or DagNode which has been wrapped for convenient use. It is derived from ``mayarv.maya.nodes.base.Node``.

A Node wraps an underlying *MObject* or an *MDagPath*, and it can be retrieved either by iteration, by using one of the various methods of the MayaRV library or by manually wrapping a maya node whose name is known::
	>>> from mayarv.maya.nodes import *
	>>> import __builtin__		# nodes.set as overwritten the builtin set type
	>>> # wrap a node by name
	>>> p = Node("persp")
	Transform("|persp")
	>>> t = Node("time1")
	
The Node p now represents the transform named 'persp' within the maya scene. You can interact with it natively. It will behave properly within sets and when being compared::
	>>> assert p == p
	>>> assert p != t
	>>> assert p in [p]
	
	>>> s = __builtin__.set()
	>>> s.add(p)
	>>> s.add(t)
	>>> assert p in s and t in s and len(s | s) == 2
	
This will of course work for DAGNodes as well as for DGNodes. As initially stated, a Node wraps the respective API object, which is either of type MDagPath or MObject. These objects can be retrieved from the Node afterwards::
	>>> # getApiObject returns the api object which represents the underlying maya node best
	>>> assert isinstance(p.getApiObject(), api.MDagPath)
	>>> assert isinstance(t.getApiObject(), api.MObject)

You can query the MObject or the DagPath specifically. DagPaths exist in two variants. The DagPath type is derived from MDagPath and contains additional convenience functions to work with it. The MDagPaths is the original unaltered MayaAPI type. The reason for having two types is that MDagPath didn't properly support monkey-patching in all cases.
	>>> assert p.getDagPath() == p.getMDagPath()
	>>> assert isinstance(p.getDagPath(), DagPath) and not isinstance(p.getMDagPath(), DagPath)
	
Although each wrapped node as a python type, which is its capitalized maya type, you may easily query the MayaAPI type representation, being a member of the ``MFn.k...`` enumeration::
	>>> assert isinstance(p, Transform) and p.getApiType() == api.MFn.kTransform
	>>> assert isinstance(t, Time) and t.getApiType() == api.MFn.kTime
	>>> assert p.hasFn(p.getApiType())
	>>> assert isinstance(p.getMObject(), api.MObject) and isinstance(t.getMObject(), api.MObject)
	
.. warning:: Do not keep Nodes cached, but prefer to re-retrieve them on demand as they may become invalid in the meanwhile depending on the operations performed in Maya.

Method Lookup
=============
Calling methods is involves nothing special, you just make the call on your node directly. Its important to know which methods are available and the lookup order. Lets study the method resolution first by checking the first case, a non-existing method::
	>>> # this will raise an AttributeError
	>>> p.doesnt_exist()
	
MayaRV looks up the name in the following order:
 1. Find a method on the instance itself. This would succeed if the method has been implemented on the respective class type, in order to make it easier to use for instance.
 
 2. Find the method name on the top most MFnFunction set, and resort to more general function sets if the name could not be found. If a Node wraps a mesh for example, it would try to find the Method in MFnMesh, then in MFnDagNode, finally in MFnDependencyNode.
 
 3. Try to find an MPlug with the given name, internally using (MFnDependencyNode.)findPlug(name) to achieve this.

This implies that functions will be found *before* an attribute of the same name. If you run into this issue, use the short attribute name instead.

It would be quite expensive to query methods or attributes, but the shown lookup will only be done once per node type, afterwards the type will know that you are looking for a method, or an MPlug respectively, incurring minimal overhead only.

Even in tight loops, this convenient calling convention may be used without critical performance loss, but if you are interested in optimizing this, have a look at the :ref:`performance-docs-label` paragraph. 

MFnFunction Aliases
===================
Methods that map to function set functions are aliased such that all getters can be accessed either by their original name or by an alias. For example, (MFnDependencyNode).name can also be retrieved using .getName::
	>>> assert p.getName == p.name

If you are interested in knowing which MFnFunction sets your node supports, call the ``getMFnClasses`` method::
	>>> p.getMFnClasses()
	[<class 'maya.OpenMaya.MFnTransform'>,
	 <class 'maya.OpenMaya.MFnDagNode'>,
	 <class 'maya.OpenMaya.MFnDependencyNode'>,
	 <class 'maya.OpenMaya.MFnDependencyNode'>]
	 
If you want to learn more about the MFnMethod aliases, see :ref:`mfnmethodmutator-label`
	 
DAG-Navigation
==============
DAG objects are organized in a hierarchy which can be walked and traversed at will. The following example also uses a very handy shortcut, allowing you to access the children and parent nodes by index::
	>>> ps = p.getChildren()[0]
	>>> assert ps == p[0]
	>>> assert ps[-1] == p
	>>> assert ps == p.getChildren()[0]
	
Sometimes its required to use filters, only listing shape nodes or transforms are the most common cases::
	>>> assert ps == p.getShapes()[0]
	>>> assert ps.getParent() == p == ps.getTransform()
	
More specialized filters can be applied as well::
	>>> assert len(p.getChildrenByType(Transform)) == 0
	>>> assert p.getChildrenByType(Camera) == p.getChildrenByType(Shape)
	>>> assert p.getChildren(lambda n: n.getApiType()==248)[0] == ps
	
Generally, all items that are organized in a hierarachy support the  ``mayarv.interface.iDagItem`` interface::
	>>> assert ps.iterParents().next() == p == ps.getRoot()
	>>> assert ps.getParentDeep()[0] == p
	>>> assert p.getChildrenDeep()[0] == ps

Node Creation
=============
Creating nodes in MayaRV is simple and possibly slow as you can only create about 1200 Nodes per second. There is only one method to accomplish this with plenty of keyword arguemnts, ``mayarv.maya.nodes.base.createNode``, this shall only be brief example::
	>>> cs = createNode("namespace:subspace:group|other:camera|other:cameraShape", "camera")
	>>> assert len(cs.getParentsDeep()) == 2
	
The short and more convenient way to create nodes is to use the NodeType() call signature, whose ``**kwargs`` will be passed to the ``createNode`` function::
	>>> m = Mesh()
	>>> assert isinstance(m, Mesh) and m.isValid()
		
	>>> assert m == Mesh(forceNewLeaf=False)
	
Node Duplication
================
Node duplication is an interesting problem as it might involve many secondary tasks, such as maintaining light-links or shading assignments. 

When using the blank duplicate function as provided by the MayaAPI, one will only get a bare copy of the input node, without any connections. Its safe to state that the MayaAPI duplicate is far behind the MEL implementation, as it can take care of much more. Lets just call it a design mistake that they implement functionality in a MEL command instead of in a library so that it can be made accessible in the MayaAPI and in MEL.

MayaRV tackles the problem by providing an interface called ``mayarv.interface.iDuplicatable``. It works much like a c++ copy constructor, and anyone who implements it correctly is able to be duplicated. Nodes happen to do so, providing the additional ability to implement special cases for specific node types::
	>>> # this duplicated tweaks, set and shader assignments as well
	>>> md = m.duplicate()
	>>> assert md != m
	
If you ever miss anything to be duplicated on a certain node-type, you only need to implement it in the ``copyFrom`` method in the respective class.
	
Namespaces
==========
Namespaces in MayaRV are objects which may create a hierarchy, hence they support the ``mayarv.interface.iDagItem`` interface.
	>>> ons = cs.getNamespace()
	>>> assert ons == cs[-1].getNamespace()
	
	>>> sns = cs[-2].getNamespace()
	>>> assert sns != ons
	
	>>> pns = sns.getParent()
	>>> assert pns.getChildren()[0] == sns
	
	>>> assert len(list(sns.iterNodes())) == 1
	>>> assert len(list(pns.iterNodes())) == 0
	>>> assert len(list(pns.iterNodes(depth=1))) == 1
	
DAG-Manipulation and Instancing
===============================
Change the structure of the DAG easily by adjusting parent-child relation ships and by handling instances. DAG manipulation is an interesting topic as it is implemented using the MayaAPI, but it provides a new programming interface unique to MayaRV in order to be more intuitive and as a workaround to many issues that can occour when using the MayaAPI otherwise.

Transforms can be parented under the world root, which is the root of the dag, and under other transforms. Shape nodes may be parented under transforms only, whereas some special nodes are parented under Shape nodes, which effectively puts them into the Shape's ``underworld``.

As long as Transforms and Shapes have only one parent, there is only one DAGPath leading up to the object in question. If you add more parents to them, there are more DAGPaths leading to the same object, which is called ``instancing`` in Maya.

The MayaRV DAG manipulation API provides multiple methods to adjust the number of children and parents of the individual items, including undo support::
	>>> csp = cs.getTransform()
	>>> cs.setParent(p)
	>>> assert cs.getInstanceCount(0) == 1
	>>> csi = cs.addParent(csp)
	
	>>> assert csi.isInstanced() and cs.getInstanceCount(0) == 2
	>>> assert csi != cs
	>>> assert csi.getMObject() == cs.getMObject()
	
	>>> assert cs.getParentAtIndex(0) == p
	>>> assert cs.getParentAtIndex(1) == csp
	
	>>> p.removeChild(csi)
	>>> assert not cs.isValid() and csi.isValid()
	>>> assert not csi.isInstanced()
 
It is worth noting that the only 'real' methods are ``addChild`` and ``removeChild``. All others, such as ``addParent``, ``removeParent``, ``setParent`` and ``addInstancedChild`` are only variations of them.

``reparent`` and ``unparent`` are different operations than the instance-aware ones presented in the previous section, as they will not only ignore instances, but also enforce the object into a single DAGPath. This effectively removes all instances::
	>>> cspp = csp[-1]
	>>> csi.reparent(cspp)
	
	>>> csp.unparent()
	>>> assert csp.getParent() is None

The MayaAPI provides methods to handle instances and to do mere reparenting, MayaRV makes this more usable by providing own methods. Nonetheless, the general feeling of inconsistency remains these sets of functions are slightly opposing each other.

As a general advice, you should be aware of instances and the methods to use to safely operate on them. ``reparent`` and ``unparent`` can be used safely as well as they will raise by default if instances would be destroyed otherwise.

Node- and Graph-Iteration
=========================
The fastest way to retrieve Nodes is by iterating them. There are three major areas to iterate: DAG Nodes only, DG Nodes only, or the dependency graph which is defined by Plug connections between DG Nodes.

MayaRV iterators are built around their MayaAPI counterparts, but provide a more intuitive and pythonic interface::
	>>> for dagnode in it.iterDagNodes():
	>>> 	assert isinstance(dagnode, DagNode)
		
	>>> for dg_or_dagnode in it.iterDgNodes():
	>>> 	assert isinstance(dg_or_dagnode, DependNode)
	
	>>> rlm = Node("renderLayerManager")
	>>> assert len(list(it.iterGraph(rlm))) == 2
	
Handling Selections with SelectionLists
=======================================
Many methods within the MayaAPI and within MayaRV will take MSelectionLists as input or return them. An MSelectionList is an ordered heterogeneous list which keeps MObjects, MDagPaths, MPlugs as well as ComponentLists, and although the name suggests otherwise, it has nothing to do with the selection within the maya scene.

SelectionLists can easily be created using the ``mayarv.maya.nodes.base.toSelectionList`` function, or the monkey-patched creator functions. It comes in several variants which are more specialized, but will be faster as well. Its safe and mostly performant enough to use the general version though.
	>>> nl = (p, t, rlm)
	>>> sl = toSelectionList(nl)
	>>> assert isinstance(sl, api.MSelectionList) and len(sl) == 3
		
	>>> sl2 = api.MSelectionList.fromList(nl)
	>>> sl3 = api.MSelectionList.fromStrings([str(n) for n in nl])
	
Adjust maya's selection or retrieve it using the ``mayarv.maya.nodes.base.select`` and ``mayarv.maya.nodes.base.getSelection`` functions::
	>>> osl = getSelection()
	>>> select(sl)
	>>> select(p, t)
	
	>>> # clear the selection
	>>> select()
	>>> assert len(getSelection()) == 0
	
Please be aware of the fact that ``getSelection`` as well as ``select`` are high-level functions that emphasize convenience over performance. If this matters, use the respective functions in MGlobal instead.

SelectionLists can be iterated natively, or explicitly be converted into lists::
	>>> for n in sl:
	>>> 	assert isinstance(n, DependNode)
		
	>>> assert list(sl) == sl.toList()
	>>> assert list(sl.toIter()) == list(it.iterSelectionList(sl))

ObjectSets and Partitions
=========================
Sets and Partitions are a major feature of Maya, which uses ObjectSets and their derivatives in many locations of the program. Partitions allow to enforce exclusive membership among sets. 

ObjectSets in MayaRV can be controlled much like ordinary python sets, but they in fact correspond to an ObjectSet compatible node with your scene::
	>>> objset = ObjectSet()
	>>> aobjset = ObjectSet()
	>>> partition = Partition()
		
	>>> assert len(objset) == 0
	>>> objset.addMembers(sl)
	>>> objset.add(csp)
	>>> aobjset.addMember(csi)
	>>> assert len(objset)-1 == len(sl)
	>>> assert len(aobjset) == 1
	>>> assert csp in objset
		
	>>> partition.addSets([objset, aobjset])
	>>> assert objset in partition and aobjset in partition
	>>> partition.discard(aobjset)
	>>> assert aobjset not in partition
		
	>>> assert len(objset + aobjset) == len(objset) + len(aobjset)
	>>> assert len(objset & aobjset) == 0
	>>> aobjset.add(p)
	>>> assert len(aobjset) == 2
	>>> assert len(aobjset & objset) == 1
	>>> assert len(aobjset - objset) == 1

	>>> assert len(aobjset.clear()) == 0
	
ShadingEngines work the same, except that they are attached to the renderParition by default, and that you usually assign components to them.
	
Components and Component-Level Shader Assignments
=================================================
The following examples operate on a simple mesh, representing a polygonal cube with 6 faces, 8 vertices and 12 edges::
	isb = Node("initialShadingGroup")
	pc = PolyCube()
	pc.output > m.inMesh
	assert m.numVertices() == 8
	assert m not in isb                            # it has no shaders on object level
	assert len(m.getComponentAssignments()) == 0   # nor on component leveld 
	
Shader assignments on object level can simply be created and broken by adding or removing items from the respective shading group::
	>>> m.addTo(isb)
	>>> assert m in isb
	
Component Assignments are mutually exclusive to the object level assignments, but maya will just allow the object level assignments to take priority. If you want component level assignments to become effective, make sure you have no object level assignments left::
	>>> assert m.getSets(m.fSetsRenderable)[0] == isb
	>>> m.removeFrom(isb)
	>>> assert not m.isMemberOf(isb)
	
	>>> isb.add(m, m.cf[range(0,6,2)])     # add every second face
	>>> isb.discard(m, m.cf[:])	            # remove all component assignments
		
	>>> isb.add(m, m.cf[:3])				# add faces 0 to 2
	>>> isb.add(m, m.cf[3])					# add single face 3
	>>> isb.add(m, m.cf[4,5])				# add remaining faces
	
To query component assignments, use the ``mayarv.maya.nodes.base.Shape.getComponentAssignments`` function::
	>>> se, comp = m.getComponentAssignments()[0]
	>>> assert se == isb
	>>> e = comp.getElements()
	>>> assert len(e) == 6					# we have added all 6 faces
	
====================
Plugs and Attributes 
====================
People coming from MEL might be confused at first as MEL always uses the term ``attr`` when dealing with plugs and attributes. The MayaAPI, as well as MayaRV differentiate these.

 * Attributes define the type of data to be stored, its name and a suitable default value. They do not hold any data themselves.
 
 * Plugs allow accessing Data as identified by an Attribute on a given Node. Plugs are valid only if they refer to a valid Node and one of the Node's Attributes. Plugs can be connected to each other, input connections are exclusive, hence a Plug may have multiple output connection, but only one input connection.

Plugs
======
To access data on a node, you need to retrieve a Plug to it, represented by the monkey-patched API type ``MPlug``. Whenever you deal with data and connections within MayaRV, you deal with Plugs::
	>>> assert isinstance(p.translate, api.MPlug)
	>>> assert p.translate == p.findPlug('translate')
	>>> assert p.t == p.translate 
	
The ``MPlug`` type has been extended with various convenience methods which are well worth an extended study, here we focus on the most important functionality.
	
Connections
-----------
Connect and disconnect plugs using simple, chainable functions. The most common connection related methods can be called using overloaded operators::
	>>> ( p.tx > p.ty ) > p.tz		# parantheses enforce connection order in this case
	>>> assert p.tx >= p.ty
	>>> assert p.ty.isConnectedTo(p.tz)
	>>> assert not p.tz >= p.ty
		
	>>> ( p.tx | p.ty ) | p.tz		# disconnect all
	>>> assert len(p.ty.p_inputs) + len(p.tz.getInputs()) == 0
	>>> assert p.tz.getInput().isNull()
	
	>>> p.tx > p.tz
	>>> p.ty > p.tz              # raises as tz is already connected
	>>> p.ty >> p.tz             # force the connection
	>>> p.tz.disconnect()        # disconnect all

Querying Values
---------------
Primitive values, like ints, floats, values with units as well as strings can easily be retrieved using one of the dedicated ``MPlug.asType`` functions::
	>>> assert isinstance(p.tx.asFloat(), float)
	>>> assert isinstance(t.outTime.asMTime(), api.MTime)
	
All other data is returned as an MObject serving as a container for the possibly copied data. Data-specific function sets can operate on this data. You need to know which function set is actually compatible with the ``MObject``, or use a MayaRV data wrapper::
	>>> ninst = p.getInstanceNumber()
	>>> pewm = p.worldMatrix.elementByLogicalIndex(ninst)
		
	>>> matfn = api.MFnMatrixData(pewm.asMObject())
	>>> matrix = matfn.matrix()                       # wrap data manually
		
	>>> assert matrix == pewm.asData().matrix()       # or get a wrapped version right away
	
Setting Values
--------------
Primitive value types can be handled easily using their corresponding ``MPlug.setType`` functions::
	>>> newx = 10.0
	>>> p.tx.setDouble(newx)
	>>> assert p.tx.asDouble() == newx
	
All other types need to be created and adjusted using their respective data function sets. The following example extracts mesh data defining a cube, deletes a face, creates a new mesh shape to be filled with the adjusted data so that it shows in the scene::
	>>> meshdata = m.outMesh.asMObject()
	>>> meshfn = api.MFnMesh(meshdata)
	>>> meshfn.deleteFace(0)                        # delete one face of copied cube data
	>>> assert meshfn.numPolygons() == 5
		
	>>> mc = Mesh()                                 # create new empty mesh to 
	>>> mc.cachedInMesh.setMObject(meshdata)        # hold the new mesh in the scene
	>>> assert mc.numPolygons() == 5
	>>> assert m.numPolygons() == 6
	
	
Compound Plugs and Plug-Arrays
-------------------------------------
Compound Attributes are attributes which by themselves only serve as a parent for one or more child aattributes. Array attributes are Attributes which can have any amount of homogeneous elements. Compound- and Array Attributes can be combined to create complex special purpose Attribute types.

The ``MPlug`` type has functions to traverse the Plugs to the corresponding attributes

A simple example for a compound plug is the translate attribute of a transform, which has 3 child plugs, translateX, translateY and translatZ.

Array plugs are used to access the transform's worldMatrix data, which contains one world matrix per direct instance of the transform.

The following example shows the traversal of these attribute types::
	>>> ptc = p.t.getChildren()
	>>> assert len(ptc) == 3
	>>> assert (ptc[0] == p.tx) and (ptc[1] == p.ty)
	>>> assert ptc[2] == p.t['tz']
	>>> assert p.tx.getParent() == p.t
	>>> assert p.t.isCompound()
	>>> assert p.tx.isChild()
		
	>>> assert p.wm.isArray()
	>>> assert len(p.wm) == 1
		
	>>> for element_plug in p.wm:
	>>> 	assert element_plug.isElement()

Graph Travseral
-----------------
Using the ``iter(Input|Output)Graph`` methods, complex and fast traversals of the dependency graph are made easy::
	>>> mihistory = list(m.inMesh.iterInputGraph())
	>>> assert len(mihistory) > 2
	>>> assert mihistory[0] == m.inMesh
	>>> assert mihistory[2] == pc.output		# ignore groupparts
		
	>>> pcfuture = list(pc.output.iterOutputGraph())
	>>> assert len(pcfuture) > 2
	>>> assert pcfuture[0] == pc.output
	>>> assert pcfuture[2] == m.inMesh			# ignore groupparts 
	
Please note that the traversal can be configured in many ways to meet your specific requirements.
	
Attributes
==========
As attributes are just describing the type and further meta information of data, their most interesting purpose is to create new attributes which can be customized to fully suit your specific needs. 

The following example will use facilities of MayaRV to create a complex attribute.
 * master ( Compound, Array )
 
  * String
  
  * Point ( double3 compound )
  
   * x ( double )
   
   * y ( double )
   
   * z ( double )
   
  * message ( Message Array )

The code looks like this::
	>>> cattr = CompoundAttribute.create("compound", "co")
	>>> cattr.setArray(True)
	>>> if cattr:
	>>> 	sattr = TypedAttribute.create("string", "str", TypedAttribute.kString)
	>>> 	pattr = NumericAttribute.createPoint("point", "p")
	>>> 	mattr = MessageAttribute.create("message", "msg")
	>>> 	mattr.setArray(True)
			
	>>> 	cattr.addChild(sattr)
	>>> 	cattr.addChild(pattr)
	>>> 	cattr.addChild(mattr)
	>>> # END compound attribute

Now the only thing left to do is to add the newly created attribute to a node::
	>>> 
	

To delete an attribute, remove the attribute which works as long as it was dynamically added before::
	>>> n = Network()
	>>> n.addAttribute(cattr)
	>>> assert n.compound.isArray()
	>>> assert n.compound.isCompound()
	>>> assert len(n.compound.getChildren()) == 3
	>>> assert n.compound['mymessage'].isArray()
	
Finally, remove the attribute - either using the attribute we kept, ``cattr`` or by finding the attribute::
	>>> n.removeAttribute(n.compound.getAttribute())


========================
Mesh Component Iteration
========================
Meshes can be handled nicely through their wrapped ``MFnMesh`` methods, but in addition it is possible to quickly iterate its components using very pythonic syntax::
	>>> from mayarv.maya.nodes import *
	
	>>> m = Mesh()
	>>> PolyCube().output > m.inMesh
	>>> average_x = 0.0
	>>> for vit in m.vtx:                  # iterate the whole mesh
	>>> 	average_x += vit.position().x
	>>> average_x /= m.numVertices()
	>>> assert m.vtx.iter.count() == m.numVertices()
		
	>>> sid = 3
	>>> for vit in m.vtx[sid:sid+3]:       # iterate subsets
	>>> 	assert sid == vit.index()
	>>> 	sid += 1
		
	>>> for eit in m.e:                    # iterate edges
	>>> 	eit.point(0); eit.point(1)
			
	>>> for fit in m.f:                    # iterate faces
	>>> 	fit.isStarlike(); fit.isPlanar()
			
	>>> for mit in m.map:                  # iterate face-vertices
	>>> 	mit.faceId(); mit.vertId() 
	
As it has only been hinted at in the example, all shortcuts supported by Components, i.e. ``m.cf[1,3,5]`` will work with iterators as well.
	
==========
Selections
==========
There are several utility methods to aid in handling selections. They are mostly used during interactive sessions, although general utilities like ``select`` and ``getSelectionList`` may also proove practical in scripts. 

The following examples show some of the most common functions::
	>>> select(p.t, "time1", p, ps)
	>>> assert len(getSelection()) == 4
		
	>>> # simple filtering
	>>> assert getSelectionList().iterPlugs().next() == p.t
	>>> assert getSelection(api.MFn.kTransform)[-1] == p
		
	>>> # adjustments
	>>> sl = getSelectionList()
	>>> sl.remove(0)                                 # remove plug
	>>> select(sl)
	>>> assert len(getSelectionList()) == len(getSelection()) == 3
	
Please note that many of the selection utilities operate on wrapped Nodes by default, which may not be desired in performance critical areas.  

Advanced filtering can be implemented using the ``predicate`` of iterators, allowing to return only these items which produce a True value in the predicate function. Something like ``ls -ro`` would look like this::
	>>> assert len(getSelection(predicate=lambda n: n.isReferenced())) == 0

Expanders, such as in ``ls -sl -dag`` could be implemented with adapter iterators, which expande dag nodes to the list of their children recursively.

Its worth noting though that very complex filters could possibly be faster if they are handled by ``ls`` directly instead of reprogramming them using the python MayaAPI.

Selecting Components and Plugs
==============================
Selecting components is comparable to component assignments of sets and shading engines. In case of selections, one first creates a selection list to be selected, and adds the mesh as well as the components::
	>>> sl = api.MSelectionList()
	>>> sl.add(m.getMDagPath(), m.cf[:4])			# first 4 faces
	>>> select(sl)
	>>> assert len(getSelectionList().iterComponents().next()[1].getElements()) == 4

Plugs are can be selected exactly the same way as nodes::
	>>> sl.clear()
	>>> sl.add(p.t)
	>>> sl.add(m.outMesh)
	>>> select(sl)
	>>> assert len(getSelection()) == 2

==========
Namespaces
==========
Namespaces provide a separate room for Nodes to exist in, hence they help to reduce the probability of name clashes when handling references or when importing files. Namespaces may be nested, hence they are forming a hierarchy that you may traverse freely using the ``mayarv.interface.iDagItem`` interface.

Handling namespaces is straightforward, you may retrieve the namespace of a node, create and rename namespaces as well as query their objects.
	>>> from mayarv.maya.ns import *
	>>> assert p.getNamespace() == RootNamespace
	>>> assert len(RootNamespace.getChildren()) == 2     # we created 2 namespaces implicitly with objects
		
	>>> barns = Namespace.create("foo:bar")
	>>> foons = barns.getParent()
	>>> assert len(RootNamespace.getChildren()) == 3
		
	>>> assert len(list(barns.iterNodes())) == 0 and len(list(RootNamespace.iterNodes())) != 0
	
Although you can set the namespace of individual nodes, it is also possible to move all objects in one namespace to another::
	>>> m.setNamespace(barns)
	>>> assert m.getNamespace() == barns
		
	>>> barns.moveNodes(foons)
	>>> assert foons.iterNodes().next() == m 
	
Renaming of namespaces as well as their deletion is supported as well::
	>>> foons.delete()
	>>> assert not barns.exists() and not foons.exists()
	>>> assert m.getNamespace() == RootNamespace
		
	>>> subns = Namespace.create("sub")
	>>> subnsrenamed = subns.rename("bar")
	>>> assert subnsrenamed != subns
	>>> assert subnsrenamed.exists() and not subns.exists()

==========
References
==========
References within maya can be referred to by Path or by Reference Node. The latter one is a stable entity in your scene, whereas the first one is dependent on the amount of references as well as the actual reference file.

Dealing with references correctly can be complex in times, but the ``FileReference`` type in MayaRV greatly facilitates this.

Maya organizes its references hierarchically, which can be queried using the ``iDagItem`` interface of the FileReference type. Additional functionality includes reference creation, import, removal as well as to query information and iterate its contained nodes.

The example uses files from the test system and respective utilities::
	>>> from mayarv.maya.ref import FileReference
	>>> refa = FileReference.create(get_maya_file('ref8m.ma'))     # file with 8 meshes
	>>> refb = FileReference.create(get_maya_file('ref2re.ma'))    # two subreferences with subreferences
		
	>>> assert refa.p_loaded and refb.isLoaded()
	>>> assert len(FileReference.ls()) == 2
		
	>>> assert len(refa.getChildren()) == 0 and len(refb.getChildren()) == 2
	>>> subrefa, subrefb = refb.getChildren()
		
	>>> assert subrefa.p_namespace != subrefb.getNamespace()
	>>> assert subrefa.p_path == subrefb.getPath()
	>>> assert subrefa.getParent() == refb
		
	>>> refa.p_loaded = False
	>>> assert not refa.p_loaded
	>>> assert refa.setLoaded(True).isLoaded()
		
	>>> assert len(list(refa.iterNodes(api.MFn.kMesh))) == 8
		
	>>> refa.remove(); refb.remove()
	>>> assert not refa.exists() and not refb.exists()
	>>> assert len(FileReference.ls()) == 0 


==============
Scene Handling
==============
The 'Scene' is a singleton class which may be used to interact with the scene and to manage scene messages. It is a mix of functionality from the ``file`` MEL command and the ``MSceneMessage`` API class. The following example uses utilities and scenes from the test system::
	>>> import mayarv.maya as mrv
	>>> empty_scene = get_maya_file('empty.ma')
	>>> mrv.Scene.open(empty_scene, force=1)
	>>> assert mrv.Scene.getName() == empty_scene
		
	>>> files = list()
	>>> def beforeAndAfterNewCB( data ):
	>>> 	assert data is None
	>>> 	files.append(mrv.Scene.getName())
			
	>>> mrv.Scene.beforeNew = beforeAndAfterNewCB
	>>> mrv.Scene.afterNew = beforeAndAfterNewCB
		
	>>> assert len(files) == 0
	>>> mrv.Scene.new()
	>>> assert len(files) == 2
	>>> assert files[0] == empty_scene
	
It is important to remove callbacks once you are done with them to allow the maya callbacks to be cleaned up properly::
	>>> mrv.Scene.beforeNew.remove(beforeAndAfterNewCB)
	>>> mrv.Scene.afterNew.remove(beforeAndAfterNewCB)
	
====
Undo
====
The MayaAPI, the very basis of MayaReVised, has limited support for undo as it clearly focuses on performance. Changes to the dependency graph can only be made through a utility which supports undo, but changes to values through plugs for instance  are not covered by that. To allow MayaRV to be used within user scripts, full undo was implemented whereever needed. This is indicated by the ``undoable`` decorator. Whenever a method which changes the state cannot be undone for whichever reason, it is decorated with ``notundoable``.

As you are unlikely to need undo support when running in batch mode or standalone, you can disable the undo system by setting MAYARV_UNDO_ENABLED to 0, which causes the undo implementation to completely disappear in many cases, which reduces the overhead considerably and reduces the memory usage.

In case your method or function uses an undoable method, it must be decorated with ``undoable`` as well. If you fail doing so, undo will pick up your individual undoable calls, and a single invocation of maya's undo will just undo one of them ( instead of your complete method ).

To implement a simple undoable function yourself, you create a functor of type ``GenericOpertion`` which knows what to do to apply your operation, and to undo it.

The following example shows how multiple undoable operations are bundled into a single undoable operation::
	>>> import maya.cmds as cmds
	>>> @undoable
	>>> def undoable_func( delobj ):
	>>> 	p.tx > p.tz
	>>> 	delobj.delete()
		
	>>> t = Transform()
	>>> assert not p.tx.isConnectedTo(p.tz)
	>>> assert t.isValid() and t.isAlive()
	>>> undoable_func(t)
	>>> assert p.tx >= p.tz
	>>> assert not t.isValid() and t.isAlive()
		
	>>> cmds.undo()
	>>> assert not p.tx.isConnectedTo(p.tz)
	>>> assert t.isValid() and t.isAlive()

Advanced Uses
=============
MayaRV keeps an own undo stack for its undoable commands which integrates itself with maya's undo queue using a custom MEL command. Effectively it records every change on that stack, once the main undoable method completes, the stack is moved onto maya's own undo queue.

This allows for interesting uses considering that you can, at any time undo, your own doing in a controlled and safe fashion. This can be very useful to prepare a scene for export by changing it, and then undo your changes once you are done. This way, the user wouldn't have to reload the scene::
	>>> import mayarv.maya.undo as undo
	>>> ur = undo.UndoRecorder()
	>>> ur.startRecording()
	>>> p.tx > p.ty
	>>> p.tx > p.tz
	>>> ur.stopRecording()
	>>> p.t > t.t
		
	>>> assert p.tx >= p.ty
	>>> assert p.tx >= p.tz
	>>> assert p.t >= t.t
	>>> ur.undo()
	>>> assert not p.tx >= p.ty
	>>> assert not p.tx >= p.tz
	>>> assert p.t >= t.t

==========
Extensions
==========

Custom Node Types
=================

Virtual Subclasses
==================

Adding Convenience
==================

Improving the Database
======================

====================
Debugging Utilitites
====================
pdb
utiltiies
imrv

====================
Development Workflow
====================
suggest TDD, BTD

===============
Common Mistakes
===============
Lifetime of MObjects/reference count
mat == p.wm.getByLogicalIndex(0).asData().matrix()	# matrix is ref, parent goes out of scope



.. _performance-docs-label:

=====================================
Performance and Memory Considerations
=====================================

Iterators
=========
Pre-Filter by MFn.type, possibly return unwrapped API nodes wherever feasible.

Undo
=====

_api_ calling convention
=========================

findPlug vs. node.plug
======================

Single vs. Multi
================

Node-Wrapping
==============
