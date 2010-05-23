	
.. _naming-conventions-label:

******************
Naming Conventions
******************
MRV's primary intention regarding its naming conventions is to fit into the ones already setup by the MayaAPI, while trying not to completely neglect the python heritage and PEP8 which comes with it.

Method Names
============
MRV uses methods named ``setProperty`` to set the given property on an instance, and ``property`` to retrieve that property. ``property`` may take arguments as well to possibly configure the way the property is retrieved.

To indicate non-property values, which are values that have to be generated or produced in some way, the method is prefixed to give a hint on the underlying operation, such as in ``findValue`` or ``createItem``.

If the property is a boolean, and if it equals a state of the instance, the method prefix is chosen to be close to 'natural english', i.e. ``isLocked``, or ``hasCache``.

Public methods which are part of the maya related parts of MRV must obey to this convention. Protected methods, that is methods which are not part of the public interface, may be named according to PEP8 as well. 

Public MRV methods which do not depend on maya in any way may use PEP8, but it is advised to keep the naming consistent with the one employed by the MayaAPI if the interface is used by the maya dependent parts. For example, even though the types in ``mrv.interfaces`` don't depend on Maya, Maya depends on them, so their public methods are camel-cased.

If you derive from a base type which uses PEP8 naming conventions, you must keep that convention alive in the interface methods you add, even if your type is used by the maya related parts of MRV.

Variable Names
==============
Within your method or function, great freedom can be exercised regarding the names of variables. Some like camel-cased variableNames, others prefer PEP8 variable_names, and neither one is right or wrong. Choose what seems most appropriate for you, and whatever you like typing more. Within MRV, you might find passages that use a 'MEL' style variable naming, other parts prefer PEP8. In general, MRV will prefer PEP8 over camel-cases as its easier to type, which in turn increases productivity.

Method Aliases
==============
If MRV overrides native MFnFunctionSet methods, the overriding function will use the same name even if it prefixed with 'get' - that prefix is usually dropped in MRV. In that case though, an alias is provided to conform to MRV's naming conventions. As an example, if the method ``MFnFoo.getBar`` is overridden with ``FooNode.getBar``, an alias called ``FooNode.bar`` would be provided.

If an overridden MFnMethod uses X, no alias is provided for getX. For example, ``MFnFoo.bar`` would be overridden with ``FooNode.bar``, but an alias called ``FooNode.getBar`` will *not* be provided.

Commonly used methods with long names, such as ``MPlug.misConnectedTo`` have an abbreviation alias in order to speed up typing and increase typing convenience. Abbreviations only use lower-case letters, and use the first character of each of the camel-cased words. The abbreviation in this case is be ``MPlug.mict``.


******************
Calling MFnMethods
******************
Return values of overridden MFNMethods return the wrapped type. ( i.e. DagNode.child ). This is the expected behavior as MFnMethods called on wrapped objects should return wrapped objects to stay in the wrapped 'ecosystem'.

At the current time, MFn methods which receive MObjects or MDagPaths will only
allow MObjects or MDagPaths, wrapped nodes must be converted explicitly. At some 
point this should change to allow wrapped nodes as well.

If MFnMethods require the ``MScriptUtil`` to be used from python, and if it has not been overridden by MRV yet, there is no convenient way to call it.

If the MFnMethod alters the object in question, and if there is no MRV override yet, undo will not be implemented. 

Whenever an MRV developer encounters an 'uncallable' method, he is advised to implement the pythonic version of the method directly on the type or base type in question, see the document about :doc:`Extending MRV <../extend>` for more information.

