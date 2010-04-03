
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

* *Testing Framework*

 * Nose 0.11 or higher
 * Coverage ( optional )
 
* *Documentation Generation (linux and OSX only)*

 * Epydoc 3.x
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
	
	$ easy_install<python_version> nose coverage sphinx epydoc

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

.. _repo-clone-label: 

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
MRV's goal as development framework is to enable the programmer to write reliable, maintainable and well-performing code in less time compared to the conventional methods. 

MRV natively assures that the code is well-performing, but reliability cannot be assured without proper testing. Maintainability comes with a good design, and clean code.

If one wanted to find a development strategy which fits the previously mentioned goals, one would definitely find TDD - `Test Driven Development <http://en.wikipedia.org/wiki/Test-driven_development>`_. 

For the sake of brevity, only the most important points will be mentioned here, check the wiki link above for more information.

When developing for python within maya, one generally has the problem that simply 'sourcing' a file is not possible anymore. Instances of your classes which are still floating around somewhere use the code they have been instantiated with, not the new one which you might just have ``reload`` 'ed.

This makes it cumbersome and hard to predict whether you are actually seeing your changes or not.

The only way to be 100% sure that your changes are actually kicking in is to restart maya, and try again. This of course is not feasible if it is done manually as it takes much too long.

Being aware of this issue, MRV has been developed using TestCases from the ground up. This is why it is possible to rerun a single test every ~3.5s in a standalone interpreter ( as a comparison, maya -batch takes ~5.5 seconds to startup ). The whole test suite can be run in just ~7s, and all regression tests in for Maya 8.5 to 2010 take less than two minutes.

This makes it actually possible to write in a test-driven manner, running tests is easy and fast.

Please note that the following examples use a linux shell, but the same development style will work on windows as well provided that you exchanges the commandline shown here with a cmd prompt compatible one.

MRV TDD
=======
When implementing a new MRV feature, it is useful to start by getting a clear idea of what the feature should be like, and who will use it, and how it will be used. Then it is wise to conduct a quick manual test to see whether it is generally possible to do - usually the answer is yes, but its good to get an impression on how difficult it is going to be.

The next step is to find a good place for the code, either it is placed into an existing module, or a new one is created. Before writing a line of code though, a first test case is added into an existing test module, or into a new one.

Ideally you have at least two panes available in your editor, one is for the implementation, the other one for the test. For brevity, lets call the implementation ``lefty``, the test ``righty``.

In ``lefty``, sketch out the design required to implement the feature - do you need a class, or several classes, which member functions do they have, are module level functions reasonable, or do you want to use classmethods instead ?

Once the design has been sketched, its about defining the signature of the methods and function. Go through them one by one in a suitable order and write the documentation for them - use restructured Text. 

Write down what the method is supposed to do, think about the possible input arguments and their types, the return type, as well as possible exceptions.
While writing this, you essentially define the domain within which this method is supposed to work. 

Whenever you set a pile for the fence of your domain, switch to ``righty`` and note down what the method can do, or what it can't do to assure you don't forget about the individual things that need to be tested::
	
	>>> # <feature.py>
	>>> def makeFoo(bar_iterable, big=False):
	>>>     """Create a new Foo instance which contains the Bar instances
	>>>     retrieved from the bar_iterable.
	>>>
	>>>     :return: ``Foo`` compatible instance. If big was True, it will 
	>>>         support the ``BigFoo`` interface
	>>>     :param bar_iterable: iterable yielding Bar instances. As Foo's
	>>>          cannot exist without Bars, an empty iterable is invalid.
	>>>     :param big: if True, change the type from ``Foo`` to ``BigFoo``
	>>>     :raise ValueError: if bar_iterable did not yield any Bar instance
	>>>          pass # todo implementation"""

	>>> # <test/test_feature.py>
	>>> # It has been written while putting down the docs for the method
	>>> def test_makeFoo(self):
	>>>     # assure it returns Foo instances, BigFoo if the flag is set
	>>>     
	>>>     # which contain the bars we passed in
	>>>
	>>>     # empty iterables raise

Next up is the implementation of the test case - as it knows the interface of the method to test, it can be fully implemented before write any actual implementation::
	
	>>> # assure it returns Foo instances, BigFoo if the flag is set
	>>> bars = (Bar(), Bar()) 
	>>> for big in range(2):
	>>>		foo = makeFoo(iter(bars), big)
	>>>		assert isinstance(foo, Foo)
	>>>		if big:
	>>>			assert isinstance(foo, BigFoo)
	>>>		# END check rval type
	>>>		
	>>>		# which contain the bars we passed in
	>>>		assert foo.bars == bars
	>>>		
	>>>		# empty iterables raise
	>>>		self.failUnlessRaises(ValueError, makeFoo, tuple(), big)
	>>>	# END for each value of 'big'

Now you have a full frame for all the boundary cases that you have documented before. Run the test repeatedly while implementing your actual classes. Once the test succeeds, you can at least be quite confident that your code is actually working.

The full implementation of the example can be found in ``mrv.test.maya.nt.test_general``.

The case presented here is of course nothing more than a constructed example, in many cases the flow of the development will be much less 'predefined' and more flexible, and it is usually iterative as well. The basic steps are the same though::
	#. Understand the problem to solve
	#. Design your Interface, Class or Method by sketching it - write documentation to get an even clearer understanding of the problem, as well as the limits within which you will solve it.
	
	 * Track the sub-tests that you will need while writing the documentation
	 
	#. Implement the test case(s)
	#. Write your actual implementation.
	
Of course it is totally valid to switch order, or jump back and forth between the steps - but the list presented here gives a good outline on how MRV is being developed.

Running Tests
=============
In Test-Driven-Development, running the test is a major part of the workflow, which is why this sections presents a few commonly used strategies to test efficiently and conveniently.

Nose is the main test driver, it offers pretty much everything you ever wanted and allows to be extended using plugins rather easily - the following presentation shows only some of the vast amount of features available, you can read more on the `official homepage <http://somethingaboutorange.com/mrl/projects/nose>`_, the examples should work on linux, OSX and windows.

If your working directory is the MRV root directory, the following command will run all tests ( in about ~7s )::
	
	$ test/bin/tmrv <mayaversion>
	
Run individual test packages or module by specifying there paths::
	
	$ # runs the Path test, as well as all maya related tests of the given maya version
	$ test/bin/tmrv <mayaversion> test/test_path.py test/maya

Running tests outside of the maya test package will not startup maya, hence it will return much quicker::
	
	$ test/bin/tmrv <mayaversion> test/test_enum.py
	
If an exception is raised in the tests, you will see it in the final output, as well as the caught standard output. The ``-d`` flag resolves symbols to their actual values. In case you want to jump right into the exception when it occurs, specify ``--pdb``. If you just have a failing test and want to inspect the variable values yourself, use ``--pdb-failure``::
	
	$ test/bin/tmrv <mayaversion> test/test_fails.py -d
	$ test/bin/tmrv <mayaversion> test/test_fails.py --pdb
	$ test/bin/tmrv <mayaversion> test/test_fails.py --pdb-failure
	
As nose will by default catch all standard output of your program, it may also suppress messages you print during the first import of your program. To show all of these as they occur, use the ``-s`` flag::
	
	$ test/bin/tmrv <mayaversion> test/test_startup_issues.py -s
	
Testing User Interfaces
-----------------------
Testing user interfaces is a very manual process. The tests currently available in the ``mrv.test.maya.ui`` package are showing a few windows, the knowing user may also click a few buttons to verify that callbacks work alright.

These tests at least show that the UI system is not fundamentally broken, and that Callbacks and Signals work - nonetheless the manual nature of these tests causes them not to be run very often.

The commandline required to run the tests is the following ( all platforms )::
	
	$ test/bin/tmrvUI <path/to/maya/bin/maya>
	
In future, this testing system is likely to be improved, also considering that QT offers a `test library <http://qt.nokia.com/doc/4.2/qtestlib-manual.html>`_ which can virtualize mouse clicks and keyboard input, in order to fully automate user interface testing.

More information about this is to follow, but own experiences have to be made first.
	
Verifying Test Coverage
-----------------------
In statically typed languages, one benefits from the great blessing of having a compiler which is able to check types and their compatibility, as well as to verify names at compile time.

Unfortunately, Python will only be able to discover this big class of errors at runtime, which essentially is too late. Test cases help to run your code, but are you sure it is running every line of it ?

Nose comes with an excellent tool which verifies the tests code coverage. As it needs a few options, there is a utility ( Linux + OSX ) which runs all or the specified tests with coverage output::
	
	$ test/bin/tmrvc <mayaversion> 
	$ firefox coverage/index.html
	
The resulting web page highlights all lines that ran, and shows the ones that did not run, which enables you to adjust your tests to run all the lines.

At the time of writing (|today|), MRV had a :download:`test coverage of 90% <download/coverage/index.html>`, but of course `test coverage is not everything <http://www.infoq.com/news/2007/05/100_test_coverage>`_.

Regression Testing
------------------
As MRV is meant to be useful in all Maya Releases which support python, namely 8.5 till X where X is the latest release, it must be verified that all tests indeed succeed in all available Maya versions, ideally on all platforms.

On Linux and OSX, a tool is available to facilitate running these tests. If it succeeds, it will give instructions to manually run the user interface tests and to complete the regression testing::
	
	$ test/bin/tmrvr 
	$ test/bin/tmrvUI <path/to/maya/bin/maya>

IPython and IMRV
================
During development, it is unlikely that one remembers all methods available on instances of a certain type, sometimes its required to just quickly test or verify something, or to pull up the docs on a basic but rarely used python built-in function. Searching the Web is possible, but using ``ipython`` is much more convenient.

``imrv``, one of MRVs :doc:`tools`,  essentially is an ipython shell which has been setup to load a specialized version of the MRV runtime to provide you with a fully initialized MRV runtime environment::
	
	$ bin/imrv
	>>> p = Node("persp")
	Transform("|persp")
	
	List all available methods on the perspective transform:
	>>> p.<tab-key>
	
	Show the doc-string of a method:
	>>> p.name?
	
	Jump into the debugger next time an exception occurs:
	>>> pdb
	
	Disable the debugger
	>>> pdb
	
Avoiding Trouble - A Word about Reference Counts
================================================
As MRV nearly exclusively uses the API to do work, it also allows you to use the underlying API types, MObject and MDagPath, directly.

If used correctly, the benefit is performance and ease of use, but in the worst case, maya will crash - this happens more easily when using the Maya API than when using MEL for example.

To understand the source of the issue, one has to understand what an MObject is: MObjects are containers with a reference count, a type and a pointer to the actual data. This in fact is very similar to the ``object`` base type in python.

If you see an MObject in python, such as in the following snippet ... ::
	
	>>> p = Node("persp")
	>>> po = p.object()
	<maya.OpenMaya.MObject; proxy of <Swig Object of type 'MObject *' at 0x36a2ee0> >
	
... what you actually see is a proxy object which serves as a python handle to the actual C++ MObject. The reference count of that proxy object is 1, as it is stored in only one named variable, ``po``. The caveat here is that this does not affect the reference count of the underlying MObject at all - its reference count is the same as it was before. The only one who actually holds a reference to it is Maya, and it is allowed to drop it at any time, or copy its memory to a different location. If that would happen, any access to ``p`` or ``po`` may cause a crash or destabilize Maya to cause a crash later, which is even worse.

The only way to forcibly increment the reference count is by copying the MObject explicitly::
	
	>>> poc = api.MObject(po)
	>>> po, poc
	(<maya.OpenMaya.MObject; proxy of C++ MObject instance at _f0d5050500000000_p_MObject>,
 <maya.OpenMaya.MObjectPtr; proxy of C++ MObject instance at _1008460200000000_p_MObject>)
 
This invoked the C++ copy constructor, and incremented the reference count on the MObject. Copying MObjects might come at additional costs though in case the MObject encapsulates data.

When adding attributes with the bare python Maya API, this situation can easily occur::
	>>> p.addAttribute(api.MFnTypedAttribute().create("sa", "stringarray", api.MFnData.kStringArray, api.MFnStringArrayData().create())
	
In this example, we created two temporary function sets, ``MFnTypedAttribute`` and ``MFnStringArrayData``. The ``create`` methods of the respective sets return newly create MObjects - the only one who keeps a reference is the actual function set. Two bad things happen:

#. ``MFnStringArrayData`` returned an MObject encapsulating an empty string array to you, then it goes out of scope, and decrements its reference count on the returned MObject during its destruction sequence. The MObject has no one referencing it anymore, so it will destroy itself and its data. Python still has a handle onto the memory location that once kept the MObject, and it is passed to ``MFnTypedAttribute.create``.
#. ``MFnTypedAttribute.create`` produces a new attribute ``MObject`` with invalid default data, returns it and destroys itself as it goes out of scope. Again, the reference count of the newly created Attribute decrements to 0, which destroys the Attribute and its data. The python handle you see will be passed to the ``p.addAttribute`` method, which tries to create an attribute from deleted data.

If you try that line, you will see that it apparently works, but its not guaranteed to do so, nor will you be able to tell whether the caused memory corruption will crash Maya at a later point.

The alternative to the line above is to use the Attribute wrappers that MRV provides::
	
	>>> p.addAttribute(TypedAttribute.create("sa", "stringarray", Data.Type.kStringArray, StringArrayData.create()))
	
In the version above, both create methods implicitly copy the returned MObject, which forcibly increments its reference count. Once the underlying MFnFunctionSet goes out of scope, it will decrement the MObject's reference counts to 1, keeping it alive and healthy.

Generally, when dealing with MObjects directly, keep the reference count in mind especially in case of MObjects that have just been created.

In c++, this is not a problem as MObjects are copied automatically when being assigned to a variable for instance or when being passed into functions ( most of the time ). If you have a proper compiler though, the above line would be invalid as well as you return temporary objects and pass them in as reference. 

In python, there is no compiler who would be able to check for this. 

************
Contributing
************
MRV is an open source project based on the work of just one person ( for now ), which doesn't only mean that this person must be slightly crazy, but also that MRV was written from just one perspective. There is a `gource video <http://vimeo.com/10611158>`_ which illustrates that ... pretty lonely situation.

Many convenience methods, for instance the ones in ``mrv.maya.nt.geometry`` have been written because there was a specific need for it. Many areas that would need additional implementations have not seen any attention yet.

The solution to this problem is to make MRV accessible by providing a solid documentation, and to actually make contribution easy. With traditional SCM's, this is not the case as you may not do anything with the repository unless special permissions are granted.

With `git <http://git-scm.com>`_ though, or any distributed version control system for that matter, this is a problem of the past as your clone of the repository contains all information you need to , theoretically, found your very own version of the software. Make your own branches, apply your own patches, commit whenever you want, and rebase your changes onto the latest version of the mainline repository that you originally cloned from.

With contributions, the scene you have seen in the first video, `might soon look more like this <http://vimeo.com/10617731>`_.
 
Using Git
=========
Once you have cloned your initial copy from the mainline repository ( see :ref:`repo-clone-label` ), you stay up-to-date by fetching ( ``git fetch`` ) the latest changes from mainline and by merging them into your master branch ( ``git merge`` ).

In order to contribute though, the by far easiest workflow is to create your own MRV fork on either `www.gitorious.com <http://gitorious.org/mrv>`_ or on `www.github.com <http://www.github.com/Byron/mrv>`_. 

When creating own features or patches, you just put them into a separate branch ( using ``git co -b myfeature`` ), commit your changes using ``git commit ...`` and finally push everything into your public repository ( ``git push ...`` ) and create a merge request. Once it has been merged into the mainline repository, your change automatically makes it into the next MRV release. 

The workflow presented here is only a rough introduction to the multitude of possible git workflows, and more concrete examples will be added as the need arises.

.. _runtestsdoc-label:


***************
Making Releases
***************
TODO: Although there is a build and release sysetm, at the time of writing ( |today| ), it was not used to create the release you have. It will be revised and documented for 1.0.0.


Building Docs
=============
Currently, building of the docs is only supported on linux and on OSX provided that sphinx and epydoc have been installed properly. 

If that is the case, the following line will build the docs you are currently reading, in the version you have checked out locally::
	
	$ cd doc
	$ make html
	$ # to redo existing docs from scratch
	$ make clean html

The built documentation can be found in ``mrv/doc/build/html``.

.. _performance-docs-label:


*****************************************
Integrating MRV into Production-Pipelines
*****************************************
MRV sole purpose of existence originally was to serve as foundation of a Maya based 3D production pipeline, details about that can be read in a :doc:`designated article <history>`.

Nowadays, and after many improvements, it should be even more useful when applied in the context of pipelines. MRV doesn't weigh much, neither in memory, nor on the CPU, is very well documented and very well tested.

Besides that, you are able to :doc:`extend <extend>` it to suit your needs, and :doc:`configure <conf>` it to suit your needs even better.

Finally, if - after a thorough study of the documentation - there are any questions or doubts left that would prevent its use, I will be glad to help personally.

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




