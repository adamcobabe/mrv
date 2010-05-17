


********
Features
********

Supported Maya Versions
=======================
**PyMel**:

#. 2008 to 2011

* Bundled with Maya 2011
	
**MRV**:

#. 8.5 to 2011

Database
========
Both frameworks organize maya's Nodetypes hierarchically and attach information about compatible MFnFunctionSets to them. This information is retrieved  automatically, but is stored in a cache to speed up loading and to allow manual edits.

**PyMel**:
	1. Stored in one compressed file per maya release, which contains multiple pickled files 
	2. Database file is fully () decompressed at startup, not necessarily using all information.
	3. **Stored Information**
	
	 #. Node Type Hierarchy
	 #. MFnFunctionSet to Nodetype Association
	 #. **Meta Data**
	 
	  #. Method Aliases
	  #. Method Visibility [#mv]_
	  #. Return Value Conversions
	  
	  * Choose between MEL or API Methods (, rephrase maybe)
	 
	 * API Docs 
	 * MEL Docs 
	 * C++ Enumerations
	 * MFnMethod Signatures 
	 
	4. **Database Editing**
	
	 #. Edit many aspects of the database using a custom tool
	 #. edits by hand are not supported 
	
**MRV**: 
	1. Stored in multiple :ref:`human readable text files <database-label>`.
		Additional Information is taken directly from devkit headers located in your 
		maya installation directory.
	2. Two files loaded at startup, all others are loaded on demand.
	3. **Stored Information**
	
	 #. Node Type Hierarchy
	 #. MFnFunctionSet to Nodetype Association
	 #. **Meta Data**
	 
	  #. Method Aliases
	  #. Method Visibility
	  #. Return Value Conversions
	  
	4. **Database Editing**
	
	 #. There is no custom tool to edit the database files
	 #. Database files are edited by hand in a text editor.

Node Types
==========
Both frameworks use their node type hierarchy information to pre-generate all default maya node types and place them in a python module. 

Node instances allow access to related methods, either hand-implemented or as  generated from database information.

Access to a Node instances attributes is supported as well, making code like  ``node.attributename`` possible.

**PyMel**:
	1. **Basic Node Type: ``PyNode``**
	
	 #. Create from: StringNames, MObject, MDagPath, MObjectHandle
	 #. PyNodes are (Pseudo)``unicode``-Strings, supporting string methods
	 #. All PyNode types are located in the ``pymel.core.nodetypes`` module
	 #. MayaAPI objects are an implementation detail, and are internally accessed through the PyNode's ``.__api*__`` methods and properties, where applicable. Keeps the most appropriate API Object and an initialized function set as well as an MObjectHandle at all times.
	 #. A PyNode type is provided for any type available in maya, including plugin types. As plugins load and unload, respective types are added and removed.
	 #. Docstrings provide additional information, these are retrieved from the respective MEL command docs if no hand-written doc string exists 
	 #. The string name of DagNodes is the node's partial name, the shortest unique name.
	 #. PyNodes can be used in PyMel provided versions of MEL commands natively.
	 
	2. **Methods**
	
	 1. Attributes hide MFnMethods
	 2. MFnMethods are available by only one name which may be aliased, possibly making the original name unavailable. [#mapymel]_
	 3. MFnMethods return PyNodes where applicable 
	 4. MFnMethods originally taking MObjects or MDagPaths also take PyNodes, handling the type conversion internally. The type handling is automated.
	 5. MFnMethods normally support undo if a 'setter' method has a corresponding 'getter' method. This functionality is automated.
	 6. MFnMethods that would require referenced parameter types which would receive the output of the method are called without them. The output parameters are returned instead [#moppymel]_. MScriptUtil is never used.
	 
	  1. If there are several overloaded signatures, one of them is choosen using the database editing tool 
	  
	 7. Docstrings correspond to the respective MFnMethod's documentation, the documentation of the underlying MEL command, or hand-written documentation if the method was implemented by hand.
	 8. Methods follow the ``getX`` and ``setX`` conventions. MFnMethods are not altered to fit this convention, but may be renamed to be more intuitive.
	 9. All MFnMethods are attached to the node type when the type is created  
	 
	3. **Plugs/Attributes**
	
	 #. ``node.plugname`` returns an ``Attribute`` instance, a custom PyMel type.
	 #. Attributes can be accessed by their short and long attribute name.
	 #. Attributes will be tried first when looking up name, methods are looked up afterwards. This happens on every access 
	 #. There is no differentiation between Plugs and Attributes, MEL semantics are used.
	 #. **Data Access**
	 
	  #. Access primitive numeric data types and strings. 
	  #. Full undo is implemented for all modifying methods.
	
**MRV**:
	1. **Basic Node Type: ``Node``**
	
	 1. Create from: StringNames, MObject, MDagPath
	 
	  * ``NodeFromObj`` creates Node instances from API objects only - used internally for performance.
	  * ``NodeFromStr`` creates Node instances from strings only
	  
	 2. Nodes are ``object`` s
	 3. All Node types are located in the ``mrv.maya.nt`` package
	 4. MayaAPI objects can be retrieved using the ``.object()`` and ``.dagPath()`` methods, where applicable. The respective MObject and MDagPath instances are permanently stored on the Node. DagNodes store the API object which was used to create them and retrieve their MObject representation on demand.
	 5. A Node type is provided for any type available in maya, including plugin types. As plugins load and unload, respective node types are added and removed.
	 6. Docstrings are handwritten on basic Node types, and do not exist on auto-generated ones.
	 7. The string name of DagNodes is the full absolute path name.
	 8. Nodes require explicit conversion to string before being passed to maya.cmds.
	 
	2. **Methods**
	
	 1. MFnMethods hide Plugs
	 2. MFnMethods are available by their original name, but may have an alias to make it available under a more intuitive name.
	 3. MFnMethods return Nodes where applicable
	 4. MFnMethods take their original types only, the user must extract the actual MObject or MDagPath explicitly.
	 5. MFnMethods do not support undo if it was not explicitly implemented.
	 6. MFnMethods are called exactly as stated in the MayaAPI documentation. (Referenced) output parameters are maintained. If the use of MScriptUtil is required, there is usually no way around it unless someone has hand-implemented the method in question.
	 
	  1. Overloaded signatures are natively available, as you call the actual MFnMethod effectively. 
	  
	 7. Docstrings are either the name of the original MFnMethod to help you finding the actual documentation in the default maya api docs, or hand-written documentation on hand-written documentation if it was implemented by hand.
	 8. Methods are following the :ref:`'X' and 'setX' <naming-conventions-label>` convention, but keep the current MFnMethodNames unaltered.
	 9. MFnMethods are attached to the node type once it is accessed by the first instance. The lookup will only happen once.
	 
	3. **Plugs/Attributes**
	
	 #. ``node.plugname`` returns an ``MPlug`` instance which contains additional methods that have been patched into the 'm' namespace. [#mmnsmrv]_
	 #. Plugs can be accessed by their short and long attribute name.
	 #. As methods are found first, once a name does not correspond to a method but a plug, this information is stored on the type to make the next plug access less costly for all instances of the given type.
	 #. Plugs are not Attributes. Attributes define the type of data and a name for it, Plugs are handles to access the data and to define data flow through connections. MayaAPI semantics are used.
	 #. **Data Access** 
	 
	  #. Access primitive data types and strings, all other data types using the ``MPlug.asMObject`` and ``MPlug.masData`` methods.
	  #. Full undo is only implemented for the MRV methods which reside in the 'm' namespace. [#mpmmrv]_
	

Node Iteration/Node Listing
===========================
This section covers the differences in the interface to retrieve nodes. 

**PyMel**:
	#. Retrieve PyNodes as lists **no iterators ?**
	#. Get all DAG nodes using ``ls(dag=1)``
	#. Get all DG nodes using ``ls()``
	#. List all input or output nodes using ``node.history`` and ``node.future``, there no easy way to traverse actual plugs  
	
**MRV**:
	#. Retrieve iterators yielding Nodes (default), MObjects or MDagPaths
	#. Iterate DAG nodes using ``iterDagNodes()``
	#. Iterate all DG nodes using ``iterDgNodes()``
	#. Iterate the dependency graph using ``iterGraph()``, or ``MPlug.miterGraph``.
	

User Interfaces
===============
Both frameworks provide wrappers for maya's user interface MEL commands, allowing them to be used in an object oriented fashion.

**PyMel**:
	1. **UI Types**
	
	 #. Common base type for all UI elements is ``PyUI``, which is a unicode object.
	 #. PyUI instances can be created from the name of maya's UI element. If no name is given, all flags supported by the underlying MEL command can be passed in as keyword argument.
	 #. Each UI MEL comamnd has a corresponding capitalized PyUI type
	 #. PyUI type hierarchy is solely based on the actual type inheritance in the ``uitypes`` module. 
	 #. PyUI types may inherit from hand-implemented base classes to add custom functionality. 
	 #. Fully auto-generated UI types derive from PyUI. 
	 
	 
	2. **Property Access**
	
	 #. Database information is used to provide ``getX`` methods for all long MEL command flags ``X`` which can be queried, and ``setX``  methods for all long editable command flags ``X`` .
	 
	  * i.e. ``x, y = win.getWidthHeight()`` or ``win.setWidthHeight((x, y))`` to get and set the dimension of a window. 
	
	3. **Callback/Event Handling**
	
	 1. Callbacks are set using the respective property, usually named ``setXCommand``.
	 
	  * i.e. ``button.setCommand(stringOrCallable)`` sets the command to be called once a button is pressed.
	  
	 2. As callbacks correspond to the underlying MEL callback, each one may have zero or one receivers.
	 3. Maya callbacks which provide additional arguments return Python types, not just strings like 'true', 'false' or ''.

**MRV**:
	1. **UI Types**
		#. Common base type for all UI elements is ``BaseUI``, which is an object. All UI elements with names derive from ``NamedUI``, which is a ``BaseUI``, and a unicode object, among others.
		#. NamedUI instances can be created from the name of maya's UI element. If no name is given, all flags supported by the underlying MEL command can be passed in as keyword argument. BaseUI instances will always instantiate the actual maya UI element ( i.e. modal dialogs ).
		#. Each UI MEL command has a corresponding capitalized BaseUI type
		#. The BaseUI type hierarchy is defined in the database according to the commonalities of the flags of the respective MEL commands.
		#. Types within that hierarchy are hand-implemented to provide common functionality to all derived types. Abstract bases are used as well. 
		#. Fully auto-generated UI types derive from their base type as defined in the database.
		
	2. **Property Access**
	
	 #. A list of short and long property names as manually extracted from the MEL command documentation is kept on the respective UI type, which will be used by the type's metaclass to generate python properties prefixed with ``p_``. The property can be queried, but may not necessarily be edited, which is when a RuntimeError will be produced.
	 
	  * i.e. ``x, y = win.p_wh`` or ``x, y = win.p_widthHeight``, ``win.p_wh = (x, y)`` or ``win.p_widthHeight = (x, y)`` to get and set the dimensions of a window. 
	
	3. **Callback Handling**
	
	 1. Callbacks are called Events. A list of short and long event names as manually extracted from the MEL command documentation is kept on the respective UI type, which will be used by the type's metaclass to create UIEvent descriptors prefixed with ``e_``.
	 
	  * i.e. ``button.e_pressed = callable1`` and ``button.e_pressed = callable2`` to register two receivers with the button pressed event.
	  
	 2. An event may have any amount of receivers.
	 3. Maya callbacks with arguments provide them as strings only. The receiver has to deal with it itself. The first argument of each sent event is the  event's sender.
	 
	 * Custom Signals may be created to facilitate QT-like modular user interfaces. 
	 
Regression Testing
==================
Both frameworks feature nose compatible test cases.

**PyMel**:
	#. Test modules are organized in a flat list of files
	#. Tests can be run in the maya version in your PATH.
	#. There are no utilities to facilitate user interface testing.
	
**MRV**:
	#. Test modules are organized in a hierarchy, matching the name and hierarchical location of the modules they test.
	#. Tests can be run easily in all installed maya versions
	#. User interfaces may be tested by the default nose based test system. Maya will be started in minimal GUI mode and runs the specified UI tests.


Interfaces and Utilities
========================
Both frameworks provide additional utilities and interface to handle common problems that arise within maya. The actual implementation varies greatly though, this comparison merely lists the major ones.

**PyMel**:
	#. File handling through procedural interface
	#. Reference handling through custom Type ( ``FileReference`` )
	#. Namespace handling through custom Type ( ``Namespace`` )
	#. OptionVar handling through custom dict type ( ``OptionVarDict`` )
	
	* **Probably many more**
	
**MRV**:
	#. File handling though custom Type ( ``Scene`` )
	#. Reference handling through custom Type ( ``FileReference`` )
	#. Namespace handling through custom Type ( ``Namespace`` )
	#. OptionVar handling through custom dict type ( ``OptionVarDict`` )
	
	
	
	
Standalone Tools
================
Both frameworks offer standalone tools to provide additional functionality. These are listed here by their functionality, including the available platforms. 

**PyMel**:
	1. **Tools**
	
	 #. IPython shell with PyMel support, some Maya specific convenience functions like Node name completion and Attribute completion. A dag command lists the scene dag as ascii art. ( ``ipymel``, all platforms )
	 
	 * Convert MEL to Python ( ``mel2py``, all platforms )
	 
	2. **Testing**
	
	 #. Run tests in current maya version ( ``pymel_test``, Linux, OSX )
	 
	3. **Maintenance**
	
	 #. Compile full documentation  ( ``make_pymel_docs``, linux and osx )
	 
	 * Make a new release ( ``makerelease``, linux and OSX )
	 * Rebuild the database caches ( ``rebuildcaches.py``, OSX )
	 

**MRV**:
	1. **Tools**
	
	 #. IPython shell with MRV support, all MFnFunctions take part in tab completion, but nothing more.
	 
	 * Prepare a python standalone interpreter to run MRV and maya ( ``mrv``, All platforms, on windows it uses only the predefined maya version )
	 
	2. **Testing**
	
	 #. Run tests in current and specified maya versions ( ``tmrv``, all platforms, on windows the same limitations apply as for ``mrv`` )
	 
	 * Run UI specific tests in a slimmed down maya UI session ( ``tmrv --mrv-maya test/maya/ui``, all platforms )
	 * Retrieve the test coverage as html report for the specified maya version ( ``tmrv --tmrv-coverage``, linux and osx )
	 * Full regression testing against all installed maya versions ( ``tmrvr``, linux and osx )
	 
	3. **Maintenance**
	
	 #. Compile full documentation ( ``make clean html``, Linux and OSX )
	 

	 
--------------------------------------------------------------------------------

.. [#mv] Whether a method can be called through a Node or not 
.. [#moppymel] MFnCamera.getFilmFrustrum( double distance, MPointArray clipPlanes ) can be called like Camera.getFilmFrustrum( 10.0 ), returning a tuple of 4
.. [#mapymel] ``MFnDagNode::child`` becomes ``DagNode.childAtIndex``, and is not available under ``DagNode.child``.
.. [#mmnsmrv] All patches applied to globally available MayaAPI types, such as MPlug or MSelection list reside in the 'm' namespace to prevent clashes with possibly existing patched methods.
.. [#mpmmrv] This is potentially dangerous as ``MPlug.msetFloat(...)`` supports undo, whereas the original MPlug.setFloat(...) does not. There is a debugging environment variable which helps to find these kind of bugs.
