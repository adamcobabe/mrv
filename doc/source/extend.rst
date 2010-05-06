##########
Extensions
##########
Although MRV is fully usable without any modifications, it was designed with extensibility in mind. This means that you can add custom node types at runtime, extend existing ones with own methods, or provide virtual subclasses that extend an existing type.

MRV's dynamic wrapping engine is based on a simple ascii text file database, which can easily be adjusted if the requirement should arise.

*****************
Plugin Node Types
*****************
Whenever a plugin is loaded, MRV will query the registered node types and create a custom python type for them. The type in question subclasses the actual plugin type, which could be ``MFn.kPluginLocatorNode`` or ``MFn.kPluginDependNode`` for example. The truncated inheritance diagram would look like this::
	
	[...]
	-> DependNode
	--> UnknownPluginDependNode
	---> YourPluginType
	
Registering own node types is simple, and an example of the required techniques is given with the *Persistence* implementation of MRV. For completeness, we outline this case. Please note that the example given here is somewhat constructed, as the persistence system in fact does not need any special registration as it is natively a part of ``mrv.maya.nt``.

The persistence plugin implements a simple Dependency Node which performs no computations, but hosts a set of attributes to store data and connections. Its implementation can be found in ``mrv.maya.nt.persistence``. Once the plugin is loaded, MRV will be notified about the event and add a dummy node type called ``storageNode`` to its internal type hierarchy - the inheritance follows the previous example. This allows the nodes to be created and wrapped, but access to the actual data storage capabilities is not yet available::
	
	# load the plugin
	from mrv.maya.nt import *
	sn = StorageNode()
	sn.dataIDs()		# ERROR: default wraps have no special capabilities
	
The interface to access storage node data conveniently is implemented on the ``StorageNode`` type, located in ``mrv.maya.nt.storage``. To teach MRV your new type, you have to register it. In this case its important to unregister the default type first::
	
	# Lets assume the StorageNode implementation is not yet imported into mrv.maya.nt
	import mrv.maya.nt.storage as modstorage
	import mrv.maya.nt as nt
	
	# remove the previous 'dummy' type
	nt.removeCustomType("StorageNode")
	# add our implementation
	nt.addCustomType(modstorage.StorageNode)
	
Please note that the name of your implemented type, i.e. ``StorageNode`` must match the name of the node registered by your plugin.

The inheritance of your type matters, as it defines your base abilities which should match the actual type of your plugin node. In this case, the class definition of the ``StorageNode`` type looks like this::
	
	# file mrv/maya/nt/storage.py
	class StorageNode( DependNode, StorageBase ):
		[ ... ]
	
Here we see two interesting concepts:
	First is that we make our StorageNode type a real DependencyNode ( in the context of MRV's type system ) simply by deriving from the type ``mrv.maya.nt.base.DependNode``.
	
	Secondly we will find the actual implementation in a type named ``StorageBase`` which allows further customizations in its initializer, which effectively allows you to create own custom types with ``StorageNode``-Capabilities, by inheriting the default implementation.
	
As we previously registered our type, we are now able to access additional functionality. Please note that we need a new wrap to the existing node - the previously created instance still uses the dummy type::
	
	# create a new wrap, using the new type this time
	snnew = Node(sn.object())
	snnew.dataIDs()
	[]
	
As a summary:
	#. Split your implementation into at least two modules, one for the maya plugin, one for the MRV interface ( see ``mrv.maya.nt.persistence`` and ``mrv.may.nt.storage`` )
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

In case you find yourself adding convenience to basic maya types that way, you might consider putting your code directly onto the respective MRV node type and :ref:`contribute it <contribute-label>` to the project, so everyone will benefit from your improvements.


****************************
Replacing Default Node Types
****************************
In case Virtual Subtypes do not quite cut it and you wish to alter the behavior of existing node types, you may easily and permanently substitute in your own type. This implies that calls to ``Node`` and ``NodeFromObj`` will automatically return your type.

This can be required if you are not able or willing to contribute code to MRV, but still want to completely override (parts) of the default implementation:
	#. Derive your own Type ( directly or indirectly ) from the MRV node type to override and make sure your type has the same name, i.e. ``class Mesh(nt.Mesh) [...]``. This is all you have to do as your derived type inherits a metaclass which takes care of the details. 
	#. Override existing methods or add your own ones. Its important to bare in mind that you must not restrict the existing interface so that code which doesn't expect your type continues to work properly.

For a complete example, see ``mrv.test.maya.nt.test_general.test_replacing_default_node_types``.

This procedure is not recommended for software that is distributed into uncontrolled environments as you can never be sure that you don't affect existing code negatively.
	
Please note that this technique can only be used to replace leaf node types, that is types with no additional child types. As all of the foundation classes, from which each node type inherits, are already implemented in MRV, replacing these foundation classes would not affect the existing leaf node types as they have been created with the previous base classes already - these cannot be changed anymore.

If you need to override existing base functionality, for example to customize the ``__str__`` representation of nodes, consider using monkey patching techniques, which may only be done in highly controlled code environments.

For an example of the presented aspects, see ``mrv.test.maya.nt.test_general.test_replace_non_leaf_node_types``.


***************************
Plugin Node Types Revisited
***************************
Considering that a simple type deriving from a MRV node type already creates a valid MRV type that will be returned by ``Node`` and ``NodeFromObj``, the ``addCustomType`` method might seem dispensable.

In fact this is True as the plugin-changed event carried out by MRV once your plugin loaded will never overwrite existing types, hence it does not matter whether your custom types gets imported before or after your plugin was loaded. If it was imported beforehand, your custom type will not be overwritten, if it is imported afterwards, your custom type will overwrite the dummy type automatically. 

The only difference compared to using ``addCustomType`` is that the internal node inheritance tree will be updated with your custom type. This does not happen if the type is automatically added to the ``nt`` package by the metaclass. The tree is used by the ``createNode`` method to predetermine whether the node to be created is a dag or a dg node. In the general case, this will work even if ``addCustomType``
was not used as the default type added to the tree already identifies it ( assuming it was not removed using ``removeCustomType`` ). If it was removed, ``createNode`` will still work although it might do slightly more work. 
	
***************************
Convenience by Contribution
***************************
In case you find yourself writing certain convenience methods over and over again, you might as well consider to contribute you code to the MRV project.

In the most common case, convenience can be added directly to the node type in question. This requires you to find the implementation of the type. There it is totally valid to add new methods according to your liking. An example for this would be the ``Mesh`` implementation, which can be found in the ``mrv.maya.nt.geometry`` module::
	
	class Mesh(SurfaceShape):
		def getTweaks(self):
			[ implementation ]
	
If the type in question has not been implemented yet, it can be added to an existing or new module in the ``mrv.maya.nt`` package. As this package is only being accessed as a whole, its absolutely valid and common practice to reorganize the types within the modules as the modules grow.

If you intend to adjust MRVs code base, please have a closer look at the :ref:`development-workflow-label` section. In short words, its important to use git during development as it keeps you connected to the mainline of the development, and once you have cloned the MRV repository hosted at http://www.gitorious.com/mrv, you are ready to go.

Even if you don't want to ( or cannot ) contribute it is highly advised to work on a git clone of the MRV mainline as git will allow you to rebase your changes onto the latest version.

.. _database-label:

############
The Database
############
MRV provides python wrappers for the MObjects and MDagPaths used by the maya API. These wrappers come in a massive amount of Types - each maya node type, DataType, AttributeType and ComponentType has a representation within python - although within maya, these are only MObjects or MDagPaths respectively.

MRVs type system is defined in a database which allows to define all of these types automatically. Auto-created types are complemented by hand-written code whenever required, or based on hand-implemented base types.

**********
File Types
**********
The database consists of simple text files which come in two formats, *P.ipe S.eparated F.ile* and *H.ierarchy F.ile*. Both types are human readable, human editable, and extremely easy to parse.

Hierarchy File
==============
As the name suggest, the hierarchy file represents a simple hierarchy of items. Items are encoded in ascii and may contain all characters but <tab> or <newline>. Each tab-indentation in the file increases the level at which the following item is set::

	root
	    parent
		    child
			    subchild
	    parent2
	    [...]


Pipe Separated File
===================
This file format is somewhat similar to the CSV file standard, the separator is a pipe in this case. It has a fixed amount of columns and any amount of rows. The items separated by the pipe may contain ascii characters, excluding a pipe and newline::

	Project | Maintainer | Nationality  
	MRV     | Sebastian  | German
	
It is up to the implementor which information is put into the actual rows - in this example, we have a dedicated header line. MRV does not use a header line though as the column's meaning is predefined in code.

*******************
Node Type Hierarchy
*******************
MRV keeps the hierarchy of all built-in maya node types, data types, attribute types and component types in files called ``nodeHierarchy<mayaversion>.hf``, hence each maya release has its own file. This is because with each maya release, at least one built-in type base changes name, or moves in the hierarchy, which makes the tree incompatible between the releases.

The tree is generated automatically, and does not contain any plugin nodes. Plugin nodes are supported by providing plugin base types, such as ``unknownPluginDependNode`` or ``unknownPluginLocatorNode``, which serve as base class for dynamically generated plugin wrapper types added when the plugin loads.

************************************
Mapping MFnFunctionSets to NodeTypes
************************************
Maya node types may be compatible to one or more function sets, which are prefixed with ``MFn`` within the Maya API. Information about which function set can be attached to which node type is held in a file called ``nodeTypeToMfnCls.map``, defining a simple one-on-one mapping.

As node types derive from each other, all sub types are automatically compatible to the function sets of their base types. All Dag Nodes support the ``MFnDagNode`` function set for example. 

As MRV also provides custom ( but fully maya API compatible ) types for Data, Components and Attributes, their function set mappings are listed in that file as well.

As maya only adds new function sets between the versions, but does not alter the compatibility of existing ones, it is possible to have one file for all maya versions. It will always represent the state of the latest available release. 

.. _mfnmethodmutator-label:

******************
MFn Database Files
******************
Each node type may call any method on any of its compatible function sets. The way how these methods are called, and more, is defined in the pipe separated files of the MFn Database. Each function set has its own database file in the following format::
	
	flags | methodname      | rvalue conversion function | alias
	      | parentNamespace | Namespace                  | namespace
	  x   | setName         | None                       | 
	  

* **flags**	  
	Currently supported method flags are **x** which makes the method in question unavailable for calls. This is done if there is a more specialized method available in MRV. ``setName`` for example will change the name of the node without undo support, the corresponding ``rename`` method implemented by MRV supports undo and more.
	
* **methodname**
	The original name of the function set method.
	
* **rval value conversion function**
	If set, the return value of the method in question will be passed to the conversion function, which in turn returns a converted type compatible to the inserted one. Its used mainly to automatically convert return values of MFn methods into the respective MRV type.

* **alias**
	An optional alias for the MFn method. If set, the method can be called using the original *or* the alias name. The method ``parentNamespace`` for instance can just be called using ``namespace`` for convenience.
	MRV will only provide an alias if the new name is significantly more convenient to use, easier to remember, or just less 'out-of-place' than the original method name, but it will not be used to try to fix perceived maya API method naming inconsistencies.

Please note that the database is manually maintained at the current time - future releases will add functionality to auto-set certain values according to reasonable rules. This means the database will continue to be hand-editable to stay in maximum control, but maintenance will become easier.

As the Maya API never changes the signature of existing methods, or removes them completely, its valid to keep only one MFn Database for all maya releases.

*******************************
Upgrading to a new Maya Release
*******************************
Whenever a new major maya release hits the scene, it is required to update the database with the latest additions and more importantly, changes to the node hierarchy.

To achieve this proceed as follows:

	#. Create the new branch 'release_upgrade' and check it out.
	#. In ``mrv/bin/mrv`` add a new mayaversion|pyversion string matching your maya and python version. You cannot start bin/mrv <mayaversion> if this was not adjusted.
	#. In ``mrv/maya/__init__.py`` add the new maya version to the list of supported ones. Trying to import ``mrv.maya`` would fail otherwise.
	#. In ``mrv.test.maya.test_mdb``, remove the *_DISABLED_* portion in front of the ``test_init_new_maya_release``
	#. Run the test using the new maya release, for example::
		
		Runs the upgrade procedure for maya 2020 from the root of the repository.
		test/bin/tmrv 2020 test/maya/test_mdb.py -s
		
	#. Go through the list of instructions printed on screen, commit your changes and merge your branch into master.

	

