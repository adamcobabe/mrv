
**********
Namespaces
**********
Namespaces provide a separate room for Nodes to exist in, hence they help to reduce the probability of name clashes when handling references or when importing files. Namespaces may be nested, hence they are forming a hierarchy that you may traverse using the ``mrv.interface.iDagItem`` interface.

Handling namespaces is straightforward, you may retrieve the namespace of a node, create and rename namespaces as well as query their objects::
	
	from mrv.maya.ns import *
	assert p.namespace() == RootNamespace
	assert len(RootNamespace.children()) == 2     # we created 2 namespaces implicitly with objects
		
	barns = Namespace.create("foo:bar")
	foons = barns.parent()
	assert len(RootNamespace.children()) == 3
		
	assert len(list(barns.iterNodes())) == 0 and len(list(RootNamespace.iterNodes())) != 0
	
Although you can set the namespace of individual nodes, it is also possible to move all objects in one namespace to another::
	
	m.setNamespace(barns)
	assert m.namespace() == barns
		
	barns.moveNodes(foons)
	assert foons.iterNodes().next() == m 
	
Renaming of namespaces as well as their deletion is supported as well.::
	
	foons.delete()
	assert not barns.exists() and not foons.exists()
	assert m.namespace() == RootNamespace
		
	subns = Namespace.create("sub")
	subnsrenamed = subns.rename("bar")
	assert subnsrenamed != subns
	assert subnsrenamed.exists() and not subns.exists()

.. note:: Its worth noting that namespace objects are immutable, and renaming a namespace will not alter the original instance.


