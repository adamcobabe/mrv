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

Node Database
=============
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
	 


Iteration
=========
dag iteration, dg iteration, graph iteration

Attribute/Plug Handling
=======================

User Interfaces
===============

Regression Testing
================== 



***********
Performance
***********
Although all performance tests are synthetic and will to give a real indication  of the actual runtime of your scripts, they are able to give a hint about the general performance of certain operations.

The numbers have been produced on a 2Ghz Dual Core Machine running Xubuntu 8.04.  Maya has been preloaded by the systems virtual memory system, and all temporary  directories are RAM disks (tmpfs).

The tests were run one time only. All MRV performance tests can be found in the  ``mrv.test.maya.performance`` module and run using  ``test/bin/tmrv [maya_version] test/maya/performance``.

All PyMel tests can be found on my github fork at  http://github.com/Byron/pymel/tree/performancetests, and run using  ``tests/pymel_test.py tests/performance``.


====================   ================================================== ==================================================
Topic                  MRV 1.0.0 Preview										PyMel 1.0.1
====================   ================================================== ==================================================
later 				    doing tables is a bit of a pain           			will do it once the list of items is complete
====================   ================================================== ==================================================


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
