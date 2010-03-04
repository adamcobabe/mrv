.. _usage-label:

==================
Using MayaRV.Maya
==================
This document gives an overview of the facilities within the Maya portion of MayaReVised which contains classes that require maya to run.

The examples given here can be viewed as one consecutive script which should work of all the code is pasted into a mayarv testcase for instance. The latter one can be found in ``mayarv.test.maya.nodes.test_base`` (test_doc_examples). If you want to be more explorative, adjust the test's code yourself and run it to see the results. For more information on how to run tests, see :ref:`runtestsdoc-label`.

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
	
This will of course work for DAGNodes as well as for DGNodes.
As initially stated, a Node wraps the respective API object, which is either of type MDagPath or MObject. These objects can be retrieved from the Node afterwards::
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
	
.. warning:: Do not keep nodes unless dag-objects, but prefer to reretrieve them as they may become invalid in the meanwhile.

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
	>>> assert ps[-1] == p>>> assert ps == p.getChildren()[0]
	
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
	>>> cs = createNode("namespace:group|other:camera|other:cameraShape")
	>>> assert len(cs.getParentsDeep()) == 2
	
Namespaces
==========
Namespaces in MayaRV are objects which may create a hierarchy, hence they support the ``mayarv.interface.iDagItem`` interface.
	>>> ons = cs.getNamespace()
	>>> assert ons == cs[-1].getNamespace()
	
	>>> sns = cs[-2].getNamespace()
	>>> assert sns != ons
	
	>>> pns = sns.getParent()
	>>> assert pns.getChildren()[0] == sns
	
	>>> assert len(sns.getSelectionList()) == 1
	>>> assert len(pns.listObjectStrings()) == 0
	>>> assert len(pns.getSelectionList(depth=2)) == 1
	
DAG-Manipulation
================

Node- and Graph-Iteration
=========================

Instances
=========

=====================
Attributes and MPlugs
=====================

MPlugs
======
node.findPlug
node.plugname

Connections
-----------

Retrieving Values
-----------------

Setting Values
--------------

Attributes
==========

Add and Delete Attributes
-------------------------




====
Undo
====



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


=========================
Graphical User Interfaces
=========================


===============
Common Mistakes
===============
Lifetime of MObjects/reference count




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
