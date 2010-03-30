#############
Extending MRV
#############
Although MRV is fully usable without any modifications, it was designed with extensibility in mind. This means that you can add custom node types at runtime, extend existing ones with own methods, or provide virtual subclasses that extend an existing type.

MRV's dynamic wrapping engine is based on a simple ascii text file database, which can easily be adjusted if the requirement should arise.

*****************
Plugin Node Types
*****************
Whenever a plugin is loaded, MRV will query the registered node types and assign create a custom (python) type for them. The type in question subclasses the actual plugin type, which can be ``MFn.kPluginLocatorNode`` or ``MFn.kPluginDependNode`` for example. The truncated inheritance diagram would look like this::
	
	[...]
	-> DependNode
	--> UnknownPluginDependNode
	---> YourPluginType
	
Registering own node types is simple, and a perfect example of the required techniques are given with the *Persistence* implementation of MRV. For completeness, we outline this case. Please note that the example given here is somewhat constructed, as the persistence system in fact does not need any special registration as it is natively a part of ``mrv.maya.nt``.

The persistence plugin implements a simple Dependency Node which performs no computations, but hosts a set of attributes to store actual data an connections. Its implementation can be found in ``mrv.maya.nt.persistence``. Once the plugin is loaded, MRV will be notified about the event and add a dummy node type called ``storageNode`` to its internal type hierarchy - the inheritance follows the previous example. This allows the nodes to be created and wrapped, but access to the actual data storage capabilities is not yet available on such a node::
	>>> # load the plugin
	>>> from mrv.maya.nt import *
	>>> sn = StorageNode()
	>>> sn.dataIDs()		# ERROR: default wraps have no special capabilities
	
The interface to access storage node data conveniently is implemented on the ``StorageNode`` type, located in ``mrv.maya.nt.storage``. To teach MRV your new type, you have to register it. In this case its important to deregister the default type first::
	>>> # Lets assume the StorageNode implenentation is not yet imported into mrv.maya.nt
	>>> import mrv.maya.nt.storage as modstorage
	>>> import mrv.maya.nt as nt
	
	>>> # remove the previous 'dummy' type
	>>> nt.removeCustomType("StorageNode")
	>>> # add our implementation
	>>> nt.addCustomType(modstorage.StorageNode)
	
Please note that the name of your implemented type, i.e. ``StorageNode`` must match the name of the node registered by your plugin.

The inheritance of your type matters, as it defines your base abilities which should match the actual type of your plugin node. In this case, the class definition of the ``StorageNode`` type looks like this::
	>>> # file mrv/maya/nt/storage.py
	>>> class StorageNode( DependNode, StorageBase ):
	>>>		[ ... ]
	
Here we see two interesting concepts:
	First is that we make our StorageNode type a real DependencyNode ( in the context of MRV's type system ) simply by deriving from the type ``mrv.maya.nt.base.DependNode``.
	
	Secondly we will find the actual implementation in a type named ``StorageBase`` which allows further customizations in its initializer, which effectively allows you to create own custom types with ``StorageNode``-Capabilities, inheriting the default implementation.
	
As we previously registered our type, we are now able to access additional functionality. Please note that we need a new wrap to the existing node - the previously created instance still uses the dummy type::
	>>> # create a new wrap, using the new type this time
	>>> snnew = Node(sn.object())
	>>> snnew.dataIDs()
	>>> []
	
As a summary:
	#. Split your implementation into at least two modules, one for the maya plugin, one for the MRV interface ( see ``mrv.maya.nt.persistence`` and ``mrv.may.nt.storage``
	#. Once your plugin is loaded, remove the dummy type MRV creates for you using ``mrv.maya.nt.removeCustomType``, and add your own one instead using ``mrv.maya.nt.addCustomType``.
	
You can automate the process of registering your implementation by putting the MRV type registration into your ``initializePlugin`` method.

Although it is technically not required, you could consider it good style to unregister your own types once your plugin unloads. It should naturally be done once the ``uninitializePlugin`` method of your plugin is executed.  

.. note:: The add|removeCustomType workflow also allows to remove existing **leaf** level types completely, which enables you to provide a very custom implementation for node types without monkey-patching MRV or altering its source code.
	
******************
Virtual Subclasses
******************
*Virtual Subclassing* is a technique allowing to bring custom implementations into MRV without the need to write a plugin in order to get a custom node type. 

In the case of the simple ``StorageNode`` maya type, the plugin does (nearly) nothing more than defining a set of attributes that the ``StorageNode`` type implementation can operate on. There is no objection against dynamically adding these attributes to any maya node at runtime, and using the ``StorageBase`` interface to operate on it. A **Virtual Subclass** can be used to operate on the attributes.

The most significant difference between using a custom Plugin and Virtual Subclasses is that MRV will not automatically create these for you when they are encountered, instead you have to use your own methods to wrap the Virtual Subclasses around existing nodes.

The process of doing so is outlined here, for a fully working example, see ``mrv.test.maya.nt.test_storage``::
	>>> todo

******************
Adding Convenience
******************



The Database
============

Hierarchy Files
---------------
UI and Node hierarchy

Mapping MFnFunctionSets to Nodetypes
------------------------------------

MFn to NodeTypeMap
------------------

.. _mfnmethodmutator-label:

MFn Method Mutators
-------------------

Attribute creation, reference counts, point out possible problems
