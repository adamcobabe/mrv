###################
Comparison to PyMel
###################
MRV is not the first attempt to make the use of Python within Maya more convenient. PyMel is an excellent feature packed Framework which is, as the name suggests,  more closely affiliated to MEL than to the Maya API, but which allows you to  access the latter one as well.

Wherever applicable, tables have been used. Otherwise a numbered list is provided which allows to match the respective list items one on one. If list items are  presented in an unnumbered fashion, they indicate a feature which is exclusive to the respective framework or cannot be compared because its too different after all.

.. note:: The following comparison was created solely based on a single person's judgment, a person which also happens to be the author of MRV. This is why the comparison may be biased towards MRV, miss important features of PyMel or may even be wrong in parts due to an insufficient insight into the PyMel project. The author does not intent to postulate any outrageously incorrect statements, and will be glad to make adjustments if necessary.  


********
Ideology
********
Both projects have been created with a certain idea in mind

**PyMel**: 
	#. PyMEL originally builds on the cmds module and allows access to compatible MFn methods as well as respective MEL methods which can be accessed in an object oriented manner.
	#. PyMEL uses MEL semantics.
	#. PyMEL is as convenient and easy-to-use as possible, hiding details about the MayaAPI even if it is used. Direct operation of the MayaAPI is not intended.
	#. Smart methods which take multiple of input types make its use easier and more intuitive.
	#. Type-Handling should be convenient.
	

**MRV**
	#. MRV builds on the MayaAPI and allows access to compatible MFn methods in an object oriented manner. The cmds module is not handled at all.
	#. MRV uses MayaAPI semantics.
	#. MRV wants to make using the MayaAPI more productive, trying to keep its own impact on performance as low as possible. It is possible and  valid to operate on the native MayaAPI if beneficial for performance.
	#. Specialized methods take very specific input types. There are some general functions which support multiple input types to ease interactive use.
	#. Type-Handling should be explicit.
	
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
	 * Retrieve the test coverage as html report for the specified maya version ( ``tmrv --mrv-coverage``, linux and osx )
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
Iter Vtx No-Op 			4,96s ( 8.018 vtx/s )								0,019s ( 2.009.699 vtx/s )
Iter Vtx Index 			4,95s ( 8.035 vtx/s )								0,037s ( 1.065.929 vtx/s )
Iter Vtx Position		23,69s ( 1.679 vtx/s )								0,070s ( 565.626 vtx/s )
Iter Edge Position		59,82s ( 665 e/s )									0,329s ( 120.621 e/s )
Iter Poly Position		13,36s ( 2.977 f/s )								0,065s ( 609.627 f/s )
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
Set Vertex Colors 		153,07s ( 259 colors/s )							1,715s ( 23.198 colors/s )
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

 * MRV supports a fast constructor which can be used to construct Node instances from strings only. There is no equivalent in PyMel 
 
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

 * MRV supports fast constructors which get right to the point, and are more specialized. There is no equivalent in PyMel 
 
 * **MRV**::
 	 
 	>>> for apiobj in nodes_apiobjects:
	>>> 	NodeFromObj(apiobj)
 	 
====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Wrap from String 		1,84s ( 5.928 Nodes/s )								0,469s ( 15.553 nodes/s )
Wrap from String2 		xxxxxxxxxxxxxxxxxxxxxxx								0,426s ( 17.539 nodes/s )
Wrap from API Obj		0,727s ( 15.068 nodes/s)							0,112s ( 67.264 nodes/s )
Wrap from API Obj2		xxxxxxxxxxxxxxxx									0,079s ( 94.665 nodes/s )
====================   ================================================== ==================================================


Node Handling
=============
Nodes can be created, renamed, and their DAG relationships may change through parenting and instancing.

The following test creates 1000 dg nodes ( ``network`` ) as well as 1000 dag nodes ( ``transform`` ) and renames them afterwards. The code shown here is only comprised of the lines which are of actual importance, some boilerplate code is omitted.

* **Create DG Nodes** and **Create DAG Nodes**

 * **PyMel**::
 	 
 	>>> for node_type in ('network', 'transform'):
 	>>> 	for number in xrange(nn):
	>>> 		createNode(node_type)

 * **MRV**::
 	 
 	>>> for node_type in ('network', 'transform'):
 	>>> 	for number in xrange(nn):
	>>> 		createNode(node_type, node_type) 

* **Rename DG Nodes** and ** Rename DAG Nodes**

* **PyMel**::
 	 
 	>>> for node in nodes:
	>>> 	node.rename(node.name()[:-1])

 * **MRV**::
 	 
 	>>> for node in node_list:
	>>> 	node.rename(node.basename()[:-1])

====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Create DG Nodes 		0,456s ( 2.190 Nodes/s )							0,436s ( 2.290 nodes/s )
Create DAG Nodes 		0,425s ( 2.348 Nodes/s )							0,504s ( 1.983 nodes/s )
Rename DG Nodes 		0,553s ( 1.807 Nodes/s )							0,290s ( 3.437 nodes/s )
Rename DAG Nodes 		0,465s ( 2.148 Nodes/s )							0,339s ( 2.941 nodes/s )
====================   ================================================== ==================================================
	
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

 * In MRV, one can access the plug using an MFn method. In PyMel, its not possible to receive the plug 

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
Get Anim Nodes 			10,26s ( 2.086 nodes/s )							0,393s ( 54.357 nodes/s )
Access Plug/Attr		3,99s ( 5.363 attrs/s )								0,309s ( 69.872 plugs/s )
Access Plug				xxxxxxxxxxxxxxxxxxxxxxx								0,275s ( 77.771 plugs/s )
Access Plug/Attr 2		6,51s ( 7.671 attrs/s )								0,718s ( 69.579 plugs/s )
Get Plug/Attr Data		14,04 ( 3.559 values/s )							1,03s ( 48.483 values/s )
MFnMethod Access		0,0079s( 6.260.342 accesses/s )					0,0061s ( 8.184.646 accesses/s )
MFnMethod Call			0,470s ( 106.234 calls/s )							0,286 ( 174.749 calls/s )
Plug/Attr Connection	1,35s ( 3698 connections/s )						1,072 ( 4662 connections/s )
====================   ================================================== ==================================================
	
Startup Time and Memory Consumption
===================================
When using a framework, it should ideally unfold its capabilities as fast as possible thanks to minimal loading times, and be as small as possible in main memory to keep more available for the actual task.

This test regards two different scenarios: Usage in the script editor in gui mode and usage as part of a program running in a standalone python interpreter. The version running in the script editor should have all functionality available in the root namespace and imports everything, whereas the program will only import core functionality.

In Gui mode, the time actually measured is the time it takes to import the respective modules from a freshly started maya with no plugins loaded. 

In standalone mode, the time it takes to startup the interpreter and import the core framework modules is measured - they are assumed to initialize maya standalone. In MRV, undo is enabled even in standalone mode to be more comparable to PyMel which doesn't allow that. In MRVs case, the time and memory it takes to load a plugin could be saved otherwise.

The memory consumption is measure by checking the resident memory of the program before and after the import of the respective modules.

All GUI tests are performed in Maya 2011 on OSX - I could not activate my trial on linux. The OSX machine is a 2ghz dual core with 4GB of RAM. 
All standalone tests are performed on Maya 2011 on Xubuntu linux as it nicely shows how fast maya can be startup.

All tests have been performed at least two times, the best time was used.

* **GUI Import Time**

 * **PyMel**::
 	 
 	 >>> from pymel.all import *
	
 * **MRV**::
 	 
 	 >>> from mrv.maya.all import *
 	 
* **OpenMaya Memory/Time**

 * As both frameworks use OpenMaya and import all modules, the memory it takes to do so as well as the time it takes to load is included in the measurements::
 	 
 	>>> import maya.OpenMaya
 	>>> import maya.OpenMayaMPx
 	>>> import maya.OpenMayaRender
 	>>> import maya.OpenMayaFX
 	>>> import maya.OpenMayaAnim
 	 
* **GUI Memory**

 * The memory was measured once before importing the modules using the code above, and once after the import.

* **Standalone Startup**

 * **PyMel**::
 	 
 	$ time mrv 2011 -c "import pymel.core"
 	 
 * Please note that the line above always crashed while deflating the database using zip ( for some strange reason ), so I had to use another line which worked::
 		
 	$ time mrv 2011 -c "import pymel.all"
 	
 * The line above did not terminate maya correctly, but it was at least started up so a time could be extracted.
 
 * **MRV**::
 	 
 	$ time mrv 2011 -c "import mrv.maya.nt"
 
* **Standalone Memory**

 * The memory is measured in a python interactive shell due to its persistent nature. The base memory is measured after manually initializing maya standalone. Afterwards, the respective core modules are imported::
 	 
 	>>> import maya.standalone
 	>>> maya.standalone.initialize()
 	
 * **PyMel**::
 	 
 	>>> import pymel.core
 	
 * Please note that the above line would crash at the same spot as it did during the startup test, so the following line worked so far::
 
 	>>> import pymel.all
 	 
 * **MRV**::
 	 
 	>>> import mrv.maya.nt

=====================  ================================================== ==================================================
Test                   PyMel 1.0.1                                        MRV 1.0.0 Preview
=====================  ================================================== ==================================================
OpenMaya Memory/Time   203,5 MB -> 215,7 MB == 12,2 MB in 0,22s           see left side
GUI Import Time        2,37s                                              0.62s
GUI Memory             203,5 MB -> 291,1 MB == 87,6 MB                    203,5 MB -> 224,5 MB == 21,0 MB
Standalone  Startup    8,24s (*invalid run due to repeatable crash*)      5,74s
Standalone Memory      123,7 MB -> 253,9 MB == 130,2 MB (*invalid run*)   123,7 MB -> 153,1 MB == 29,4 MB
=====================  ================================================== ==================================================

.. note:: During testing, it is recommended to use maya 8.5 or 2008 as they will be ready in 3,2s (8.5) to 3,8s (2008).

**************
Usage Examples
**************
The listing concentrates on the code required to perform everyday and  simple tasks. It assumes that all required classes and functions have been  imported into the module where the code is run. This is done most easily using ``from pymel.all import *`` (``PyMel``) or ``from mrv.maya.all import *`` (``MRV``).

As a general difference you will notice that PyMel is very convenient to use through a variety of smart methods which handle many details behind the scenes.

MRV is derived from the MayaAPI, and uses its interface. Compared to MayaAPI code, its like a short hand writing style, yet it remains verbose compared to PyMel and very explicit.


Set Handling
============
Sets are a very nice feature in Maya, as well as their implementation. Handling of sets should be easy and intuitive in the framework you use.

* **PyMel**::
	
	>>> p, t, f = PyNode('persp'), PyNode('top'), PyNode('front')
	>>> s = sets()
	
	>>> # add single
	>>> s.add(p)
	>>> assert p in s
	
	>>> # add multiple - need sets command for undo support
	>>> sets(s, add=(t,f))
	>>> # same in MEL, argument meaning changed in PyMel
	>>> cmds.sets(str(t), str(f), add=str(s))
	
	>>> # remove single 
	>>> s.remove(p)
	
	>>> # remove multiple
	>>> sets(s, rm=(t,f))
	>>> assert sets(s, q=1, size=1) == 0

* **MRV**::
	
	>>> p, t, f = Node('persp'), Node('top'), Node('front')
	>>> s = ObjectSet()
	
	>>> # add single - set centric or object centric
	>>> s.add(p)
	>>> p.addTo(s)
	>>> assert p in s
	
	>>> # add multiple
	>>> s.add((t, f))
	
	>>> # remove single - set or object centric
	>>> s.discard(p)
	>>> p.removeFrom(s)
	
	>>> # remove multiple 
	>>> s.discard((t, f))
	
	>>> assert len(s) == 0
	
	
Shading Engine Handling
=======================
ShadingEngines are ObjectSets, but are specialized for the purpose of rendering. The renderPartition assures that one object or face is only handled by exactly one shading engine.

* **PyMel**::
	
	>>> isg = PyNode("initialShadingGroup")
	>>> rp = PyNode("renderPartition")
	
	>>> # assign new shading engine to the render partition
	>>> sg = createNode('shadingEngine')
	>>> rp.sets.evaluateNumElements()
	
	>>> # the partition plug is overridden by the 'partition' function of the 
	>>> # underlying pseudostring
	>>> # sg.partition > rp.sets[rp.sets.getNumElements()]
	>>> sg.pa > rp.sets[rp.sets.getNumElements()]
	
	>>> m = polySphere()[0].getShape()
	
	>>> # assign all faces to the initial shading group
	>>> # m is automatically part of the default shading engine
	>>> isg.remove(m)
	>>> isg.add(m.f)
	
	>>> # assign 200 faces to another shading group
	>>> # Cannot use object as it does not allow to force the membersship
	>>> # sg.add(m.f[0:199])
	>>> sets(sg, fe=m.f[0:199])
	
* **MRV**::
	
	>>> # NOTE: this test is part of the pymel comparison
	>>> isg = Node("initialShadingGroup")
	>>> rp = Node("renderPartition")
	
	>>> # assign new shading engine to the render partition
	>>> sg = ShadingEngine()
	>>> sg.setPartition(rp)
	
	
	>>> # create a poly sphere
	>>> m = Mesh()
	>>> PolySphere().output.mconnectTo(m.inMesh)
	
	>>> # assign all faces to the initial shading group
	>>> # Cannot use the m.cf[:] shortcut to get a complete component as 
	>>> # shading engines apparently don't deal with it properly
	>>> m.addTo(isg, m.cf[:m.numPolygons()])
	
	>>> # force the first 200 faces into another shading engine
	>>> m.addTo(sg, m.cf[:200], force=True)


Mixed
=====

The following example was taken from the PyMel homepage at http://code.google.com/p/pymel/ as it goes through a few general tasks.

* **PyMel**::

	>>> for x in ls( type='transform'):
	>>> 	print x.longName()                # object oriented design
	>>> 
	>>> 	x.sx >> x.sy                      # connection operator
	>>> 	x.sx >> x.sz
	>>> 	x.sx // x.sy                      # disconnection operator
	>>> 	x.sx.disconnect()                 # smarter methods -- (automatically disconnects all inputs and outputs when no arg is passed)
	
	>>> # add and set a string array attribute with the history of this transform's shape
	>>> 	x.setAttr( 'newAt', x.getShape().history(), force=1 )
	
	>>> 	# get and set some attributes
	>>> 	x.rotate.set( [1,1,1] )
	>>> 	trans = x.translate.get()
	>>> 	trans *= x.scale.get()           # vector math
	>>> 	x.translate.set( trans )         # ability to pass list/vector args
	>>> 	# mel.myMelScript(x.type(), trans) # automatic handling of mel procedures

* **MRV**::
	
    >>> import mrv.maya as mrvmaya                  # required for some utilities
    >>> # later we query the shape, hence we must assure we actually have one
    >>> # and setup a custom predicate
    >>> for x in iterDagNodes(Node.Type.kTransform, predicate=lambda n: n.childCount()):
    >>>     print x.name()                          # name() always returns the full path name
    >>> 
    >>>     x.sx.mconnectTo(x.sy)                   # Convenience methods are located in the 'm' namespace of the MPlug type
    >>>     x.sx.mconnectTo(x.sz)
    >>>     x.sx.mdisconnectFrom(x.sy)
    >>>     x.sx.mdisconnect()
    >>>     
    >>>     default = StringArrayData.create(list())
    >>>     shapehistory = [n.name() for n in iterGraph(x[0], input=True)]
    >>>     x.addAttribute(TypedAttribute.create('newAt', 'na', Data.Type.kStringArray, default)).masData().set(shapehistory)
    >>>     
    >>>     x.rx.msetFloat(1.0)                     # using individual plugs to have undo support, otherwise you would use MFn methods, like setRotation(...)
    >>>     x.ry.msetFloat(1.0)
    >>>     x.rz.msetFloat(1.0)
        
    >>>     trans = x.getTranslation(api.MSpace.kTransform)
    >>>     dot = trans * x.getScale()                   # the dot product is a single float, MVector has no in-place dot-product as the type changes
    >>>     x.tx.msetFloat(dot)                   # have to use child plugs for undo support
    >>>     x.ty.msetFloat(dot)
    >>>     x.tz.msetFloat(dot)
        
    >>>     # mrvmaya.Mel.myScript(x.typeName(), trans) # its essentially the pymel implementation which is used here.
	

.. rubric:: Footnotes

.. [#mv] Whether a method can be called through a Node or not 
.. [#moppymel] MFnCamera.getFilmFrustrum( double distance, MPointArray clipPlanes ) can be called like Camera.getFilmFrustrum( 10.0 ), returning a tuple of 4
.. [#mapymel] ``MFnDagNode::child`` becomes ``DagNode.childAtIndex``, and is not available under ``DagNode.child``.
.. [#mmnsmrv] All patches applied to globally available MayaAPI types, such as MPlug or MSelection list reside in the 'm' namespace to prevent clashes with possibly existing patched methods.
.. [#mpmmrv] This is potentially dangerous as ``MPlug.msetFloat(...)`` supports undo, whereas the original MPlug.setFloat(...) does not. There is a debugging environment variable which helps to find these kind of bugs.
.. [#perfm10] Maya 2010 is the fastest release so far regarding the python performance. Maya 2011 is about 7% slower.
