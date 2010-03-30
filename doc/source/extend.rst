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
	
Registering own node types is simple, and an example of the required techniques are given with the *Persistence* implementation of MRV. For completeness, we outline this case. Please note that the example given here is somewhat constructed, as the persistence system in fact does not need any special registration as it is natively a part of ``mrv.maya.nt``.

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

******************
Virtual Subtypes
******************
*Virtual Subclassing* is a technique allowing to bring custom implementations into MRV without the need to write a plugin in order to get a custom node type. 

In the case of the simple ``StorageNode`` maya type, the plugin does (nearly) nothing more than defining a set of attributes that the ``StorageNode`` type implementation can operate on. There is no objection against dynamically adding these attributes to any maya node at runtime, and using the ``StorageBase`` interface to operate on it. A **Virtual Subtype** can be used to operate on the attributes.

The most significant difference between using a custom Plugin and Virtual Subtypes is that MRV will not automatically create these for you when they are encountered, instead you have to use your own methods to wrap the Virtual Subtypes around existing nodes.

The process of doing so is outlined here, for a fully working example, see ``mrv.test.maya.nt.test_general.StorageNetworkNode`` and ``mrv.test.maya.nt.test_general.test_virtual_subtype``:
	#. Derive your Virtual Subtype from an existing MRV node type, it is *not* required to be a leaf-leve type.
	#. Define the ``__mrv_virtual_subtype__`` class member and set it to a True value.
	#. Create a new instance of your Virtual Subtype by wrapping an existing node of the correct maya type - your constructor (``__new__``) by default supports everything that ``mrv.maya.nt.base.Node`` supports, i.e. ``MyVirtualType(node.object())`` is just fine.
	
Using Virtual Subtypes is a very convenient way to non-intrusively extend maya types.

In case you find yourself adding convenience to basic maya types that way, you might consider putting your code directly onto the respective MRV node type and contribute it to the project, so everyone will benefit from your improvements.


****************************
Replacing Default Node Types
****************************
In case Virtual Subtypes and you wish to alter the behavior of existing node types, you may easily and permanently substitute in your own type. This implies that calls to ``Node`` and ``NodeFromObj`` will automatically return your type.

This can be required if you are not able or willing to contribute code to MRV, but still want to completely override (parts) of the default implementation:
	#. Derive your own Type ( directly or indirectly ) from the MRV node type to override and make sure your type has the same name, i.e. ``class Mesh(nt.Mesh) [...]``. This is all you have to do as your derived type inherits a metaclass which takes care of the details. 
	#. Override existing methods or add your own ones. Its important to bare in mind that you must not restrict the existing interface so that code which doesn't expect your type continues to work properly.

For a complete example, see ``mrv.test.maya.nt.test_general.test_replacing_default_node_types``.

This procedure is not recommended for software that is distributed into uncontrolled environments as you can never be sure that you don't affect existing code negatively.
	
Please note that this technique can only be used to replace leaf node types, that is types with no additional children. As all of the foundation classes, from which each node type inherits, are already implemented in MRV, replacing these foundation classes would not affect the existing leaf node types as they have been created with the previous base classes already.

If you need to override existing base functionality, for example to customize the ``__str__`` representation of nodes, consider monkey patching, which may only be done in highly controlled code environments.

For an example of the presented aspects, see ``mrv.test.maya.nt.test_general.test_replace_non_leaf_node_types``.


***************************
Plugin Node Types Revisited
***************************
Considering that a simple type deriving from a MRV node type already creates a valid MRV type that will be returned by ``Node`` and ``NodeFromObj``, the ``addCustomType`` method might seem dispensable.

In fact this is True as the plugin-changed event carried out by MRV once your plugin loaded will never overwrite existing types, hence it does not matter whether your custom types gets imported before or after your plugin was loaded.

The only difference in a type using the ``addCustomType`` is that the internal node inheritance tree will be updated with your custom type. This does not happen if the type is automatically added by the metaclass. The tree is used by the ``createNode`` method to pre-determine whether the node to be created is a dag or a dg node. In the general case, this will work even if ``addCustomType``
was not used as the default type added to the tree already identifies it ( considering it was not removed using ``removeCustomType`` ). If it was removed, ``createNode`` will still work although it will do slightly more work. 
	
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
