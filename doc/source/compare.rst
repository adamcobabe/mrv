###################
Comparison to PyMel
###################
MRV is not the first attempt to make the use of Python within Maya more convenient. PyMel is an excellent feature packed Framework which is, as the name suggests,  more closely affiliated to MEL than to the Maya API, also it also allows you to  access the latter one conveniently.

Together with Chad Dombrova, the original Author and Maintainer of PyMel, the  following overview has been compiled to provide an overview of the similarities and differences of the two frameworks regarding their features, performance and coding convenience.

Wherever applicable, tables have been used. Otherwise a numbered list is provided which allows to match the respective list items one on one. If list items are  presented in an unnumbered fashion, they indicate a feature which is exclusive to the respective framework.

********
Ideology
********
TODO: This section needs to be improved, and clarified

**PyMel**: **?**
	#. PyMEL builds on the cmds module and allows access to compatible MayaAPI functions as well as respective MEL methods which can be accessed in an object oriented manner.
	#. PyMEL uses MEL semantics.
	#. PyMEL is as convenient and easy-to-use as possible, hiding details about the MayaAPI even if it is used. Direct operation of the MayaAPI is not intended.
	#. Smart methods which take multiple of input types make its use easier and more intuitive.
	#. Type-Handling should be convenient
	

**MRV**
	#. MRV builds on the MayaAPI and allows access to compatible MFn methods. The cmds module is not handled at all.
	#. MRV uses MayaAPI semantics.
	#. MRV wants to make using the MayaAPI more productive, trying to keep its own impact on performance as low as possible. It is possible and  valid to operate on the native MayaAPI if beneficial for performance.
	#. Specialized methods take very specific input types. There are some general functions which support multiple input types to ease interactive use.
	#. Type-Handling should be explicit.
	
********
Features
********

Supported Maya Versions
=======================
PyMel:
	2008 to 2011
	
MRV:
	8.5 to 2011

Database
========
Both frameworks organize maya's Nodetypes hierarchically and attach information about compatible MFnFunctionSets to them. This information is retrieved  automatically, but is stored in a cache to speed up loading and to allow manual edits.

**PyMel**:
	1. Stored in one compressed file per maya release, which contains multiple pickled files **?**
	2. Database file is fully (**?**) decompressed at startup, not necessarily using all information.
	3. **Stored Information**
	
	 #. Node Type Hierarchy
	 #. MFnFunctionSet to Nodetype Association
	 #. **Meta Data**
	 
	  #. Method Aliases
	  #. Method Visibility [#mv]_
	  #. Return Value Conversions
	  
	  * Choose between MEL or API Methods (**?**, rephrase maybe)
	 
	 * API Docs **?**
	 * MEL Docs **?**
	 * C++ Enumerations
	 * MFnMethod Signatures **?**
	 
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
	 #. Docstrings provide additional information, these are retrieved from the respective MEL command docs if no hand-written doc string exists **?**
	 #. The string name of DagNodes is the node's partial name, the shortest unique name.
	 #. PyNodes can be used in PyMel provided versions of MEL commands natively.
	 
	2. **Methods**
	
	 1. Attributes hide MFnMethods
	 2. MFnMethods are available by only one name which may be aliased, possibly making the original name unavailable. [#mapymel]_
	 3. MFnMethods return PyNodes where applicable **?**
	 4. MFnMethods originally taking MObjects or MDagPaths also take PyNodes, handling the type conversion internally. The type handling is automated.
	 5. MFnMethods normally support undo if a 'setter' method has a corresponding 'getter' method. This functionality is automated.
	 6. MFnMethods that would require referenced parameter types which would receive the output of the method are called without them. The output parameters are returned instead [#moppymel]_. MScriptUtil is never used.
	 
	  1. If there are several overloaded signatures, one of them is choosen using the database editing tool **?**
	  
	 7. Docstrings correspond to the respective MFnMethod's documentation, the documentation of the underlying MEL command, or hand-written documentation if the method was implemented by hand.
	 8. Methods follow the ``getX`` and ``setX`` conventions. MFnMethods are not altered to fit this convention, but may be renamed to be more intuitive.
	 9. All MFnMethods are attached to the node type when the type is created **?** 
	 
	3. **Plugs/Attributes**
	
	 #. ``node.plugname`` returns an ``Attribute`` instance, a custom PyMel type.
	 #. Attributes can be accessed by their short and long attribute name.
	 #. Attributes will be tried first when looking up name, methods are looked up afterwards. This happens on every access **?**
	 #. There is no differentiation between Plugs and Attributes, MEL semantics are used.
	 #. **Data Access**
	 
	  #. Access primitive numeric data types and strings. **?**
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
	#. List all input or output nodes using ``node.history`` and ``node.future``, there no easy way to traverse actual plugs **?** 
	
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
	 #. PyUI type hierarchy is solely based on the actual type inheritance in the ``uitypes`` module. **?**
	 #. PyUI types may inherit from hand-implemented base classes to add custom functionality. 
	 #. Fully auto-generated UI types derive from PyUI. **?**
	 
	 
	2. **Property Access**
	
	 #. Database information is used to provide ``getX`` methods for all long MEL command flags ``X`` which can be queried, and ``setX``  methods for all long editable command flags ``X`` **?**.
	 
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
	#. **many more to add, go ahead**
	
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
	
	 #. Compile full documentation **?** ( ``make_pymel_docs``, linux and osx )
	 
	 * Make a new release ( ``makerelease``, linux and OSX )
	 * Rebuild the database caches ( ``rebuildcaches.py``, OSX )
	 

**MRV**:
	1. **Tools**
	
	 #. IPython shell with MRV support, all MFnFunctions take part in tab completion, but nothing more.
	 
	 * Prepare a python standalone interpreter to run MRV and maya ( ``mrv``, All platforms, on windows it uses only the predefined maya version )
	 
	2. **Testing**
	
	 #. Run tests in current and specified maya versions ( ``tmrv``, all platforms, on windows the same limitations apply as for ``mrv`` )
	 
	 * Run UI specific tests in a slimmed down maya UI session, maya executable must be specified ( ``tmrvUI``, all platforms )
	 * Retrieve the test coverage as html report for the specified maya version ( ``tmrvc``, linux and osx )
	 * Full regression testing against all installed maya versions ( ``tmrvr``, linux and osx )
	 
	3. **Maintenance**
	
	 #. Compile full documentation ( ``make clean html``, Linux and OSX )
	 
	 

***********
Performance
***********
Although all performance tests are synthetic and will not give a real indication  of the actual runtime of your scripts, they are able to give a hint about the general performance of certain operations.

The numbers have been produced on a 2Ghz Dual Core Machine running Xubuntu 8.04.  Maya 2010 [#perfm10]_ has been preloaded by the systems virtual memory system, and all temporary  directories are RAM disks (tmpfs).

The tests were run one time only. All MRV performance tests can be found in the  ``mrv.test.maya.performance`` module and run using  ``test/bin/tmrv [maya_version] test/maya/performance``.

All PyMel tests can be found on the github fork at  http://github.com/Byron/pymel/tree/performancetests, and run using  ``tests/pymel_test.py tests/performance``.

All test cases are presented with their actual code, omitting the code needed to measure the actual time. The final results are presented in a table.

Mesh Iteration
===============
MRV mesh iteration tests can be found in ``mrv/test/maya/performance/test_geometry.py``.

PyMel mesh iteration tests can be found in ``pymel/tests/performance/test_geometry.py``.

* **Iter Vtx No-Op**

 * The test provides a basis to compute the pure iteration overhead.
 * **PyMel**::
 	 
 	>>> m = PyNode('mesh40k')
 	>>> nc = 0
	>>> for it in m.vtx:
	>>> 	nc += 1
	
 * **MRV**::
 	 
 	>>> m = Node('mesh40k')
 	>>> nc = 0
	>>> for it in m.vtx:
	>>> 	nc += 1
	
* **Iter Vtx Index**

 * Iterate vertices and query the index. It show how a very light operation affects iteration performance
 * **PyMel**::
 	 
 	>>> for it in m.vtx:
	>>> 	it.index()

 * **MRV**::
 	 
 	>>> for it in m.vtx:
	>>> 	it.getIndex()
	
* **Iter Vtx Position**

 * Iterate vertices and query their local space position. This operation is more costly due to the potential space transformation.
 * **PyMel**::
 	 
 	>>> for it in m.vtx:
	>>> 	it.getPosition() 
 	 
 * **MRV**::
 	 
 	>>> for it in m.vtx:
	>>> 	it.position()
	
* **Iter Edge Position**

 * Iterate edges and query their vertice's positions in local space
 * **PyMel**::
 	 
 	>>> for it in m.e:
	>>> 	it.getPoint(0)
	>>> 	it.getPoint(1) 
 	 
 * **MRV**::
 	 
 	>>> for it in m.e:
	>>> 	it.point(0)
	>>> 	it.point(1)

* **Iter Poly Position**

 * Iterate polygons and query all the polygon's vertex positions in localspace
  
 * **PyMel**::
 	 
 	>>> for it in m.f:
	>>> 	it.getVertices()
 	 
 * **MRV**::
 	 
 	>>> ia = api.MIntArray()
 	>>> for it in m.f:
	>>> 	it.getVertices(ia)

====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Iter Vtx No-Op 			4.96s ( 8.018 vtx/s )								0.019s ( 2.009.699 vtx/s )
Iter Vtx Index 			4.95s ( 8.035 vtx/s )								0.037s ( 1.065.929 vtx/s )
Iter Vtx Position		23.69s ( 1.679 vtx/s )								0.070s ( 565.626 vtx/s )
Iter Edge Position		59.82s ( 665 e/s )									0.329s ( 120.621 e/s )
Iter Poly Position		13.36s ( 2.977 f/s )								0.065s ( 609.627 f/s )
====================   ================================================== ==================================================

Set Vertex Colors
=================
This more complex example performs an actual computation. It will set the verex color relative to the average length of the edges connected to the vertex in question.

* **PyMel**::

	>>> obj = PyNode('mesh40k')
		
	>>> cset = 'edgeLength'
	>>> obj.createColorSet(cset)
	>>> obj.setCurrentColorSetName(cset)
	>>> colors = []
	>>> el = api.MIntArray()
	>>> el.setLength(obj.numVertices())
	>>> maxLen = 0.0
	>>> for vid, vtx in enumerate(obj.vtx):
	>>> 	edgs = vtx.connectedEdges()
	>>> 	totalLen=0
	>>> 	for edg in edgs:
	>>> 		totalLen += edg.getLength()
	>>>
	>>> 	avgLen=totalLen / len(edgs)
	>>> 	maxLen = max(avgLen, maxLen)
	>>> 	el[vid] = avgLen
	>>> 	colors.append(Color.black)
	>>>
	>>> for vid, col in enumerate(colors):
	>>> 	col.b = el[vid] / maxLen
	>>>
	>>> obj.setColors( colors )
 
* **MRV**::
	
	>>> cset = 'edgeLength'
	>>> m = Node('mesh40k')
	>>> 
	>>> m.createColorSetWithName(cset)
	>>> m.setCurrentColorSetName(cset)
	>>> 
	>>> lp = api.MPointArray()
	>>> m.getPoints(lp)
	>>> 
	>>> colors = api.MColorArray()
	>>> colors.setLength(m.numVertices())
	>>> 
	>>> vids = api.MIntArray()
	>>> vids.setLength(len(colors))
	>>> 
	>>> el = api.MFloatArray()
	>>> el.setLength(len(colors))
	>>> cvids = api.MIntArray()
	>>> 
	>>> # compute average edge-lengths
	>>> max_len = 0.0
	>>> for vid, vit in enumerate(m.vtx):
	>>> 	vit.getConnectedVertices(cvids)
	>>> 	cvp = lp[vid]
	>>> 	accum_edge_len=0.0
	>>> 	for cvid in cvids:
	>>> 		accum_edge_len += (lp[cvid] - cvp).length()
	>>> 	avg_len = accum_edge_len / len(cvids)
	>>> 	max_len = max(avg_len, max_len)
	>>> 	el[vid] = avg_len
	>>> 	vids[vid] = vid
	>>> 
	>>> for cid in xrange(len(colors)):
	>>> 	c = colors[cid]
	>>> 	c.b = el[cid] / max_len
	>>> 	colors[cid] = c
	>>> 
	>>> m.setVertexColors(colors, vids, api.MDGModifier())


====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Set Vertex Colors 		153.07s ( 259 colors/s )							1.715s ( 23.198 colors/s )
====================   ================================================== ==================================================
	

Node Wrapping
=============
Both frameworks rely on custom types which wrap the underlying API object to provide a more convenient programming interface. The process of wrapping an API object in an instance of a custom type can be costly, and as both frameworks return these by default, node wrapping performance directly affects the performance of all operations.

The scene loaded for the test contains more than 2500 DAG and DG nodes which are to be wrapped.

As preparation, strings of all nodes in the scene are stored in the node_strings list. All (Py)Nodes are stored for later extraction of the API objects.

* **Wrap from String**

 * **PyMel**::
 	 
 	>>> for name in nodes_strings:
 	>>> 	PyNode(name)
 
 * **MRV**::
 	 
	>>> for name in nodenames:
	>>> 	Node( name )
	
* **Wrap from String2**

 * MRV supports a fast constructor which can be used to construct Node instances from strings only. There is no equivalent in PyMel **?**
 
 * **MRV**::
 	 
 	>>> for name in nodenames:
	>>> 	tmplist.append(NodeFromStr(name))

* **Wrap from API Obj**

 * **PyMel**::
 	 
 	>>> for apiobj in nodes_apiobjects:
	>>> 	PyNode(apiobj)
	
 * **MRV**::
 	 
 	>>> for apiobj in nodes_apiobjects:
	>>> 	Node(apiobj)
 
* **Wrap from API Obj2**

 * MRV supports fast constructors which get right to the point, and are more specialized. There is no equivalent in PyMel **?**
 
 * **MRV**::
 	 
 	>>> for apiobj in nodes_apiobjects:
	>>> 	NodeFromObj(apiobj)
 	 
====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Wrap from String 		1.84s ( 5.928 Nodes/s )								0.469s ( 15.553 nodes/s )
Wrap from String2 		xxxxxxxxxxxxxxxxxxxxxxx								0.426s ( 17.539 nodes/s )
Wrap from API Obj		0.727 ( 15.068 )									0.112 ( 67.264 nodes/s )
Wrap from API Obj2		xxxxxxxxxxxxxxxx									0.079 ( 94.665 nodes/s )
====================   ================================================== ==================================================


Node Handling
=============
Nodes can be created, renamed, and their DAG relationships may change through parenting and instancing.


Attributes and Plugs
====================
Whether you want to access data, or make new connections to alter the data flow, MPlugs (MRV) and Attributes (PyMel) are required to do it.

The following tests take part in a scene with more than 21000 animation nodes and plenty of corresponding animated DAG and DG nodes of different types. The animation nodes are first retrieved, then their output plugs are accessed.

* **Get Anim Nodes**

 * **PyMel**::
 	 
 	>>> anim_nodes = ls(type="animCurve")

 * **MRV**::
 	 
 	>>> anim_nodes = list(iterDgNodes(Node.Type.kAnimCurve))


* **Access Plug/Attr**

 * **PyMel**::
 	 
 	>>> for anode in anim_nodes:
	>>> 	anode.output

 * **MRV**::
 	 
 	>>> for anode in anim_nodes:
	>>> 	anode.output
		
* **Access Plug**

 * In MRV, one can access the plug using an MFn method. In PyMel, its not possible to receive the plug **?**

 * **MRV**::
 	 
 	>>> for anode in anim_nodes:
	>>> 	anode.findPlug('output')

	
The following tests are to determine the performance of the retrieval of simple floating point data, using the plug/attribute as well as an MFnMethod.

The variable ``p`` is a PyNode/Node of the perspective camera ( shape ). The loop is set to 50000 iterations.

* **Access Plug/Attr 2**

 * Access the same plug/attribute repeatedly on the same node
 
 * **PyMel**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.fl

 * **MRV**::
 	 
	>>> for iteration in xrange(na):
	>>> 	p.fl

* **Get Plug/Attr Data**

 * **PyMel**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.fl.get()
	
 * **MRV**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.fl.asFloat()
	
* **MFnMethod Access**

 * **PyMel**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.getFocalLength
	
 * **MRV**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.focalLength

* **MFnMethod Call**

 * **PyMel**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.getFocalLength()
	
 * **MRV**::
 	 
 	>>> for iteration in xrange(na):
	>>> 	p.focalLength()
	
* **Plug/Attr Connection**

 * The test contains two network nodes which feature multi-message plugs/attributes. 5000 of these are connected with each other, from one network node to another. A utility is used to produce the required element plugs/attributes. 
 * Please note that single connecting plugs is inefficient, in case of MRV its better to use ``MPlug.mconnectMultiToMulti`` to get 10x the performance.
 
 * **PyMel**::
 	 
 	>>> for source, dest in zip(pir(sn.a, r), pir(tn.ab, r)):
	>>> 	source > dest
	
 * **MRV**::
 	 
 	>>> for source, dest in zip(pir(sn.a, r), pir(tn.ab, r)):
	>>> 	source.mconnectTo(dest)
	
====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Get Anim Nodes 			10.26s ( 2.086 nodes/s )							0.393s ( 54.357 nodes/s )
Access Plug/Attr		3.99s ( 5.363 attrs/s )								0.309s ( 69.872 plugs/s )
Access Plug				xxxxxxxxxxxxxxxxxxxxxxx								0.275s ( 77.771 plugs/s )
Access Plug/Attr 2		6.51s ( 7.671 attrs/s )								0.718s ( 69.579 plugs/s )
Get Plug/Attr Data		14.04 ( 3.559 values/s )							1.03s ( 48.483 values/s )
MFnMethod Access		0.0079s( 6.260.342 accesses/s )					0.0061s ( 8.184.646 accesses/s )
MFnMethod Call			0.470s ( 106.234 calls/s )							0.286 ( 174.749 calls/s )
Plug/Attr Connection	1.35s ( 3698 connections/s )						1.072 ( 4662 connections/s )
====================   ================================================== ==================================================
	
Startup Time and Memory Consumption
===================================
todo.
	

***********
Basic Tasks
***********
The following table concentrates on the code required to perform everyday and  simple tasks. It assumes that all required classes and functions have been  imported into the module where the code is run.

# ( perhaps work through the usage examples , or write little scripts which show how to solve certain common problems )
# sets handling
# components and sets
# add attributes ( show benefits of having separate access to attributes )

.. rubric:: Footnotes

.. [#mv] Whether a method can be called through a Node or not 
.. [#moppymel] MFnCamera.getFilmFrustrum( double distance, MPointArray clipPlanes ) can be called like Camera.getFilmFrustrum( 10.0 ), returning a tuple of 4
.. [#mapymel] ``MFnDagNode::child`` becomes ``DagNode.childAtIndex``, and is not available under ``DagNode.child``.
.. [#mmnsmrv] All patches applied to globally available MayaAPI types, such as MPlug or MSelection list reside in the 'm' namespace to prevent clashes with possibly existing patched methods.
.. [#mpmmrv] This is potentially dangerous as ``MPlug.msetFloat(...)`` supports undo, whereas the original MPlug.setFloat(...) does not. There is a debugging environment variable which helps to find these kind of bugs.
.. [#perfm10] Maya 2010 is the fastest release so far regarding the python performance. Maya 2011 is about 7% slower.
