
.. _development-label: 

###################
Developing with MRV
###################
MRV is a framework onto which new programs are easily being built, and it provides many tools to facilitate development and to help producing good software quickly.

Setting up your development environment is a first step, which involves cloning the MRV mainline repository, and assuring that some prerequisites are met.

The second part of this guide explains the naming conventions used in MRV, tells you about the development practices employed to produce it.

***********************
Development Environment
***********************
This article describes the required setup and configuration of your system to develop MRV or projects based on MRV.

Prerequisites
=============
The following software packages need to be installed,
* Git 1.6.5 or higher
* Autodesk Maya 8.5 or higher
* Nose 0.11 or higher ( required by Testing Framework )
 
* Documentation Generation (linux and OSX only)

 * Epydoc 3.x or higher
 * Sphinx 0.62 or higher

The following installation guide *assumes you have already installed git and Autodesk Maya* for your platform. For instruction, please see the documentations of the respective package.
 
Installation
============
The basic installation steps are similar in all supported operating systems. Getting MRV to run within a standalone interpreter differs between the platforms.

If a standalone interpreter does not work for you, its absolutely possible to run MRV within the default maya python interpreter, ``mayapy``.

.. _install-label:

1. Install the Prerequisites
----------------------------
The instructions assume you are going to run MRV within a standalone interpreter. If you are planning to use mayapy, the installation may be more complicated, but in general all that needs to be done is to put the required package(s) into the 'site-packages' folder of your python installation.

Using easy_install, which comes with the python setuptools ( http://pypi.python.org/pypi/setuptools ) the installation is as easy as the name suggests::
	
	$ easy_install<python_version> nose sphinx epydoc

Please note that the version of easy_install is important as you need to install the prerequisites for each python version that is used by the maya version you are going to run:
* Maya 8.5 -> Python 2.4
* Maya 2008|2009 -> Pyhthon 2.5
* Maya 2010 -> Python 2.6

Please note that the generation of the docs currently only works on linux and OSX assuming that easy_install is installed. You don't strictly need sphinx and epydoc to develop in MRV.

Mayapy
^^^^^^
On Windows, MRV currently uses mayapy only ( although there have been experiments which proved that it can run in a standalone interpreter there as well ).

The only package that you need to install to run the tests is nose. Its recommended to retrieve the package using easy_install for your standalone interpreter and to copy it to *"C:\Program Files\Autodesk\Maya<version>\Python\Lib\site-packages"* afterwards.

If you want to use mayapy on other system, copy the ``nose`` package either into *"/usr/autodesk/maya<version>/lib/python<pyversion>/site-packages"* ( linux ) or into *"/Applications/Autodesk/maya<version>/Maya.app/Contents/Frameworks/Python.framework/Versions/<pyversion>/lib/python<pyversion>/site-packages"* (OSX).

2. Get A or Your Repository Clone
---------------------------------
Clone the MRV mainline repository from gitorious.org. Either fork your own on [www.gitorious.org/mrv] or [www.github.com/Byron/mrv] and clone from your fork, or clone from the mainline repository as shown here.

Execute the following::

 $ git clone git://gitorious.org/mrv/mainline.git mrv
 $ git submodule update --init
 
On linux and OSX, you would have done this in a shell of your choice. On windows, you would have retrieved a shell using the "Git Bash Here" menu entry in your RMB explorer menu when clicking on a folder of your choice.

3. Run the tests
----------------
By running the tests, you verify that the installation actually succeeded as you are able to run MRV in a standalone interpreter. 

Linux and OSX
^^^^^^^^^^^^^
In your shell, you should now be able to execute the ``tmrv`` tool, such as follows::
	
	$ cd mrv
	$ # start the tests for the given maya version, 2011 in this case
	$ test/bin/tmrv 2011

All tests are expected to succeed. Please note that ``tmrv`` just executes ``mrv/bin/mrv`` and launches nosetest afterwards, hence all parameters supported ``nosetests`` in your particular installation will work here as well.

On OSX, the default installation will not work if you intend to run Maya2010 or later. Please see the ``Troubleshooting`` guide for a solution.

Windows
^^^^^^^
On Windows, make sure that the MRV repository has at least one folder between itself and the drive letter. Otherwise you are not able to run tests properly due to some issue with nose on windows (apparently). 

* This is wrong:

 * c:\\mrv\\[.git]
 
* This would work:

 * c:\\projects\\mrv\\[.git]

Set your **MAYA_LOCATION** environment variable to the location of the maya version to use. MRV will be run using ''mayapy'' of the specified version, you cannot choose between the versions as on Linux / OSX.

Additionally, set the **MRV_MAYA_VERSION** variable to the version you use, i.e. "8.5" or "2011". This variable is required only by one test, which would fail otherwise.  

In a command prompt, execute::
	
	$ cd mrv
	$ test\bin\tmrv

All tests are expected to succeed.
	
Troubleshooting
---------------
This paragraph informs about possible issues which have already been resolved, but which may be quite distracting at first.

OSX and 64bit Executables
^^^^^^^^^^^^^^^^^^^^^^^^^
Starting with Maya2010, maya is delivered as 64 bit binary. The default interpreter in your path should be 64 bits as well, but if it is not, you have to make some adjustments. 

To allow the mrv startup script to find a python interpreter compiled for 64 bit, it will be sufficient to put a symbolic link to ``python2.6`` into your /usr/bin directory which points to the interpreter in question. 

``mayapy`` in your maya installation directory will work in case you don't want to build your own one, using macports for instance. In that case you need to put a symbolic link named ``python2.6`` into your ``/Applications/Autodesk/maya2010/Maya.app/Contents/bin`` directory which needs to be inserted to the first position of your PATH. To run the unit tests, you will have to install ``nose`` into maya's site-packages directory::
	
	$ mayabin=/Applications/Autodesk/maya<version>/Maya.app/Contents/bin
	$ ln -s $mayabin/mayapy python<pyversion>
	$ export PATH=$mayabin:$PATH

The reason for this extra-effort is that the ``mrv`` executable wants to start ``python<pyversion>`` which needs to be in the path. In order to use mayapy without dropping dynamic version support, the respective python<version> symlinks need to be in the PATH. On OSX its additionally required to put it into the same location as mayapy as mayapy will not find its prerequisites otherwise and fails to start.

Still troubled ? Use mayapy
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the standalone interpreter just doesn't want to work on your platform or with your particular configuration, you may always use ``mayapy``, which can be found in the *<maya_install_directory>/bin* folder. It will setup a  standalone interpreter which automatically pulls in the packages required for Maya to work.

As a side-effect, ``nose`` needs to be installed in mayapy's *site-packages* directory, as indicated in the :ref:`installation section<install-label>`.

*********************
MRV Naming Convention
*********************
MRV's primary intention regarding its naming conventions is to fit into the ones already setup by the MayaAPI, while trying not to completely neglect the python heritage and PEP8 which comes with it.

Method Names
============
MRV uses methods named ``setProperty`` to set the given property on an instance, and ``property`` to retrieve that property. ``property`` may take arguments as well to possibly configure the way the property is retrieved.

To indicate non-property values, which are values that have to be generated or retrieved in some way, the method is prefixed to give a hint on the underlying operation, such as in ``findValue`` or ``createItem``.

If the property is a boolean, and if it equals a state of the instance, the method prefix is chosen to be close to 'natural english', i.e. ``isLocked``, or ``hasCache``.

Public methods which are part of the maya related parts of MRV must obey to this convention. Protected methods, that is methods which are not part of the public interface, may be named according to PEP8 as well. 

Public MRV methods which do not depend on maya in any way may use PEP8, but it is advised to keep the naming consistent with the one employed by the MayaAPI if the interface is used by the maya dependent parts. For example, even though the types in ``mrv.interfaces`` don't depend on Maya, Maya depends on them, so their public methods are camel-cased. 

Variable Names
==============
Within your method or function, great freedom can be exercised regarding the names of variables. Some like camel-cased variableNames, others prefer PEP8 variable_names, and neither one is right or wrong. Choose what seems most appropriate for you, and whatever you like typing more. Within MRV, you might find passages that use a 'MEL' style variable naming, other parts prefer PEP8. In general, MRV will prefer PEP8 over camel-cases as its easier to type, which in turn increases productivity.

Method Aliases
==============
If MRV overrides native MFnFunctionSet methods, the overriding function will use the same name even if it prefixed with 'get' - that prefix is dropped in MRV. In that case though, an alias is provided to conform to MRV's naming conventions. As an example, if the method ``MFnFoo.getBar`` is overridden with ``FooNode.getBar``, an alias called ``FooNode.bar`` would be provided.

If an overridden MFnMethod uses X, no alias is provided for getX. For example, ``MFnFoo.bar`` would be overridden with ``FooNode.bar``, but an alias called ``FooNode.getBar`` will *not* be provided.

Commonly used methods with long names, such as ``MPlug.isConnectedTo`` have an abbreviation alias in order to speed up typing and typing convenience. Abbreviations only use lower-case letters, and use the first character of each of the camel-cased words. The abbreviation in this case is be ``MPlug.mict``.


******************
Calling MFnMethods
******************
Return values of overridden MFNMethods return the wrapped type. ( i.e. DagNode.child ). This is the expected behavior as MFnMethods called on wrapped objects should return wrapped objects to stay in the wrapped 'ecosystem'.

At the current time, MFn methods which receive MObjects or MDagPaths will only
allow MObjects or MDagPaths, wrapped nodes must be converted explicitly. At some 
point this should change to allow wrapped nodes as well.

If MFnMethods require the ``MScriptUtil`` to be used from python, and if it has not been overridden by MRV yet, there is no convenient way to call it.

If the MFnMethod alters the object in question, and if there is no MRV override yet, undo will not be implemented. 

Whenever an MRV developer encounters an 'uncallable' method, he is advised to implement the pythonic version of the method directly on the type or base type in question, see the document about :doc:`Extending MRV<extend>` for more information.

.. _development-workflow-label:

********************
Development Workflow
********************
suggest TDD, BTD
Cloning, rebasinng, etc, default git stuff, but put it here to convince non-git people as well.


.. _runtestsdoc-label:

Running Tests
=============

Debugging
=========
-> Utilities
pdb
utiltiies
imrv

Common Mistakes
===============
Lifetime of MObjects/reference count
mat == p.wm.getByLogicalIndex(0).asData().matrix()	# matrix is ref, parent goes out of scope

***************
Making Releases
***************

Building Docs
=============


************************************************
Avoiding Trouble - A Word about Reference Counts
************************************************
TODO: MObject ref counts vs. python wrapper refcounts
masData performance consderation ( add below )

.. _performance-docs-label:

*************************************
Performance and Memory Considerations
*************************************
MRV has been created with performance in mind. Core code as gone through several iteration in order to be as fast as it can possibly be within python. This is beneficial to the developer as he can be sure that conveniently written code will run at a high pace. 
Usually this kind of code is the most readable and the most maintainable which is why it is preferred. Nonetheless there are situations when performance outweights code convenience, this article explains what to look out for and how to improve the performance of your programs.

The respective tips are listed in the order of simplicity and effect, hence simler and more effective ways to enhance performance come first.

Iterators
=========
When operating in large scenes, its important to limit the amount of nodes that are returned by iterators. The fastest way to do this is to use an MFn.kType pre-filter to limit the yielded Nodes to certain types. As the pre-filtering will happen in C++, it will be very fast::
	>>> iterDagNodes(api.MFn.kTransform, api.MFn.kShape)		# Fast !
	>>> iterDagNodes(predicate=lambda n: isinstance(n, (Transform, Shape)))	# slow and wasteful

Undo
=====
Turn off the undo queue completely by setting the MRV_UNDO_ENABLED=0 in your environment. This will reduce overhead by at least 10% and increase the performance of many core methods. As a positive side-effect, you have more memory at runtime as the undoqueue will not store the history of operations.

Turning off the undo queue is feasible if you run in maya batch mode and a very easy way to speed up programs.

Single vs. Multi
================
Many programs operate on multiple objects of the same type, as a lot of work needs to be done. Interestingly, many API's seem to embrace the 'single object operation'  paradigm which means that you have to call a single method on all objects individually. 

Considering that some boilerplate is involved with each call, which may even weigh more than the actual operation you intend to apply, it obvious that methods that operate on multiple objects at the same time are preferable in many cases.

The Maya API actually does well here in many cases, and even though you will find many single object operations, there are many multi object operations as well. 

This implies that it might be worth accumulating the objects you want to work on before sending it to a multi method, which will ideally process the bunch within c++. This costs memory, but will be faster ( memory <-> performance tradeoffs are very common in general ).

There are times when you may use iterators instead of lists, they combine the benefits of passing in multiple objects ( at a slight overhead ) without notable memory consumption.

A method worth noting at this point is ``MPlug.connectMultiToMulti``, which connects multiple source to multiple destination plugs. It also adds the benefit that it will more efficiently deal with the undo queue, effectively boosting the performance by factor 8 to 14.


Convenience Methods
===================
Use specialized methods instead of generic ones. Generic methods that accept different types of inputs have to figure out what these types are in order to handle them correctly, each time you call. This is very wasteful especially if your input types do not change in that 20k iteration loop of yours.

That kind of code will perform better if the specialized version of the method is used instead - it only takes a specific input type and comes right to the point.

An example for this would be the overridden ``__getitem__`` method of the patched ``MPlug``::
	>>> for node in iterDagNodes(api.MFn.kTransform):
	>>> 	node.translate['tx']					# slow
	>>> 	# node.tx would be even better, but its not the point here
	>>>		node.translate.getChildByName('tx')	# better 
	

findPlug vs. node.plug
======================
In fact, using the ``node.plug`` convention is a convenience method as well. Internally some processing is needed figure out that you actually want a plug. A more direct way to retrieve plugs is by using the ``findPlug('plug')`` method which boost plug lookup performance by quite exactly 7%. The previous example could be written like this::
	>>> for node in iterDagNodes(api.MFn.kTransform):
	>>> 	node.findPlug('translate').getChildByName('tx')
	

_api_ calling convention
=========================
What happens whenever you call a method on a wrapped node is the following::
	>>> node.findPlug('plugname')
	>>> # this is equivalent to ...
	>>> mfninst = api.MFnDependencyNode(node.getMObject())
	>>> mfninst.findPlug('plugname')
	
As you see, you get a temporary function set which gets wrapped around the MObject or MDagPath associated with your node. This is costly as it involves the instantiation of a function set with an API object as well as an API function call. This will happen each time you call the function, even though it would be possible and better to reuse an existing function set.

The ``_api_`` calling convention does two things.
 * For patched API types, like MPlug, you receive the original, unpatched instance method.
 * For Node types, _api_ will return a method which reuses its initialized function set. This will cache the function set, the associated api object as well as the function object itself directly on your node.

To illustrate this, lets have a look at the examples::
	>>> assert isinstance(node.tx.node(), Node)		# node() returns wrapped Node
	>>> assert isinstance(node.tx._api_node(), api.MObject)	# _api_node() returns original MObject
	
The _api_ calling convention on patched types is possibly faster as the implementation does not do anything special. As always allows you to operate on unwrapped nodes though, the previous example could natively be rewritten like this::
	>>> assert isinstance(node.tx.getNodeMObject(), api.MObject)
	

To illustrate the _api_ convention on Node types, see the next example::
	>>> for i in xrange(10000):
	>>> 	perspShape.focalLength()               # slow after first call
	>>> 	topShape._api_focalLength()                 # very fast after first call
	
Its good to know about the _api_convention, but it clearly does *not* mean that you should preventively make all calls using this convention. This is because the performance gain shows up after the first call only, and only on that specific node. First the cache is built, and used in subsequent calls. In practice, it is unlikely that you are going to repeatetly call the same function on the same node in a tight loop.

Also its worth considering that the cache consumes additional memory, an MFn function set is instantiated and cached for each _api_ call on a Node.

Last but not least, its worth noting that maya controls the lifetime of your API Objects, hence these should not be cached. The _api_ cache usually is very short-lived though and should not make trouble.

If you find yourself using _api_ method calls all the time, you might consider using the respective function set directly::
	>>> mfncamera = api.MFnCamera(topShape.getMObject())
	>>> for i in xrange(10000):
	>>> 	mfncamera.focalLength()
	>>> 	# ... make additional calls at no additional overhead. 


Python Method Caching
=====================
Generally within python, each attribute access costs time, time that shows up to matter in tight loops. You can gain a lot of performance by caching the methods and attributes you have to use in local variables. The previous example could be rewritten like this, maximizing the examples performance::
	>>> mfncamera = api.MFnCamera(topShape.getMObject())
	>>> getFocalLength = mfncamera.focalLength
	>>> for i in xrange(10000):
	>>> 	getFocalLength()			# as fast as it gets

Node-Wrapping
==============
MRV is very aware of the fact that the added convenience comes at a cost. Where programming convenience and programmer's efficiency is improved, its likely that the runtime of the resulting programs is much less than optimal.

Here its important to make a tradeoff by keeping the code convenient and readable in most spots, but to optimize it only where it matters.

The wrapping of Nodes takes a considerable amount of time. On a 2 Ghz dual core machine you will get no more than 80k wrapped nodes per second. Turning the wrapping off and going bare API is supported by all methods which automatically wrap nodes, the kwarg is always named ``asNode`` which should be set to False in order to get bare MObjects or MDagPaths. This implies that you have to use MFn function sets explicitly::
	>>> mfndag = api.MFnDagNode()
	>>> for mdagpath in iterDagNodes(api.MFn.kTransform, asNode=False):		# uses pre-filter as well
	>>> 	mfndag.setObject(mdagpath)		# initialize the function set ...
	>>> 	mfndag.findPlug('translate')	# ... and use it

Combining this example with the Python Method Caching, you can maximize the performance of the given example by writing::
	>>> mfndag = api.MFnDagNode()
	>>> setObject = mfndag.setObject
	>>> findPlug = mfndag.findPlug
	>>> for mdagpath in iterDagNodes(api.MFn.kTransform, asNode=False):		# uses pre-filter as well
	>>> 	setObject(mdagpath)
	>>> 	findPlug('translate')
	
The only way to make the previous example even faster is to use the dag node iterator directly with cached methods. This is usually not worth the effort though and will add even more boilerplate code which at some point might just not be worth the maintenance effort anymore.




