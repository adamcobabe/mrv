
.. _development-workflow-label:

*********
Workflow
*********
MRV's goal as development framework is to enable the programmer to write reliable, maintainable and well-performing code in less time compared to the conventional methods. 

MRV natively assures that the code is well-performing, but reliability cannot be assured without proper testing. Maintainability comes with a good design, and clean code.

If one wanted to find a development strategy which fits the previously mentioned goals, one would definitely encounter TDD on the way - `Test Driven Development <http://en.wikipedia.org/wiki/Test-driven_development>`_. 

For the sake of brevity, only the most important points will be mentioned here, check the wiki link above for more information.

When developing for python within maya, one generally has the problem that simply 'sourcing' a file is not possible anymore. Instances of your classes which are still floating around somewhere use the code they have been instantiated with, not the new one which you might just have ``reload`` 'ed.

This makes it cumbersome and hard to predict whether you are actually seeing your changes or not.

The only way to be 100% sure that your changes are actually kicking in is to restart the python interpreter ( or maya ), and try again. This of course is not feasible if it is done manually as it takes too much time.

Being aware of this issue, MRV has been developed using TestCases from the ground up. This is why it is possible to rerun a single test every ~3.5s in a standalone interpreter ( as a comparison, maya -batch takes ~5.5 seconds to startup ). The whole test suite can be run in just ~7s, and all regression tests in for Maya 8.5 to 2010 take less than two minutes.

This makes it possible to write code in a test-driven manner, running tests is easy and fast.

Please note that the following examples use a linux shell, but the same development style will work on windows as well provided that you exchange the command-line shown here with a cmd prompt compatible one.

Test-Driven-Development
=======================
When implementing a new MRV feature, it is useful to start by getting a clear idea of what the feature should be like, and who will use it, and how it will be used. Then it is wise to conduct a quick manual test to see whether it is generally possible to do - usually the answer is yes, but its good to get an impression on how difficult it is going to be.

The next step is to find a good place for the code, either it is placed into an existing module, or a new one is created. Before writing a line of code though, a first test case is added into an existing test module, or into a new one.

Ideally you have at least two panes available in your editor, one is for the implementation, the other one for the test. For brevity, lets call the implementation ``lefty``, the test ``righty``.

In ``lefty``, sketch out the design required to implement the feature - do you need a class, or several classes, which member functions do they have, are module level functions reasonable, or do you want to use classmethods instead ?

Once the design has been sketched, its about defining the signature of the methods and functions. Go through them one by one in a suitable order and write the documentation for them - use `restructured Text <http://sphinx.pocoo.org/markup/index.html>`_. 

Write down what the method is supposed to do, think about the possible input arguments and their types, the return type, as well as possible exceptions.
While writing this, you essentially define the domain within which this method is supposed to work. 

Whenever you set a pile for the fence of your domain, switch to ``righty`` and note down what the method can do, or what it can't do to assure you don't forget about the individual things that need to be tested::

    # <feature.py> in lefty
    def makeFoo(bar_iterable, big=False):
        """Create a new Foo instance which contains the Bar instances
        retrieved from the bar_iterable.
    
        :return: ``Foo`` compatible instance. If big was True, it will 
            support the ``BigFoo`` interface
        :param bar_iterable: iterable yielding Bar instances. As Foo's
             cannot exist without Bars, an empty iterable is invalid.
        :param big: if True, change the return type from ``Foo`` to ``BigFoo``
        :raise ValueError: if bar_iterable did not yield any Bar instance"""
        pass # todo implementation
        
::
    
    # <test/test_feature.py> in righty
    # It has been written while putting down the docs for the method
    def test_makeFoo(self):
        pass
        # assure it returns Foo instances, BigFoo if the flag is set
        
        # which contain the bars we passed in
    
        # empty iterables raise

Next up is the implementation of the test case - as it knows the interface of the method to test, it can be fully implemented before writing any actual implementation::
	
	# assure it returns Foo instances, BigFoo if the flag is set
	bars = (Bar(), Bar()) 
	for big in range(2):
		foo = makeFoo(iter(bars), big)
		assert isinstance(foo, Foo)
		if big:
			assert isinstance(foo, BigFoo)
		# END check rval type
		
		# which contain the bars we passed in
		assert foo.bars == bars
		
		# empty iterables raise
		self.failUnlessRaises(ValueError, makeFoo, tuple(), big)
	# END for each value of 'big'

Now you have a full frame for all the boundary cases that you have documented before. Run the test repeatedly while implementing your actual classes. Once the test succeeds, you can at least be quite confident that your code is actually working.

The full implementation of the example can be found in ``mrv.test.maya.nt.test_general`` ( *test_makeFoo* ).

The case presented here is of course nothing more than a constructed example, in many cases the flow of the development will be much less 'predefined' and more fluid, and it is usually iterative as well. The basic steps are the same though:

	1. Understand the problem to solve
	2. Design your Interface, Class or Method by sketching it - write documentation to get an even clearer understanding of the problem, as well as the limits within which you will solve it.
	
	 * Track the sub-tests that you will need while writing the documentation
	 
	3. Implement the test case(s)
	4. Write your actual implementation.
	
Of course it is totally valid to switch order, or jump back and forth between the steps - but the list presented here gives a good outline on how MRV is being developed.

.. _runtestsdoc-label:

Running Tests
=============
In Test-Driven-Development, running the test is a major part of the workflow, which is why this section presents a few commonly used strategies to test efficiently and conveniently.

Nose is the main test driver, it offers pretty much everything you ever wanted and allows to be extended using plugins rather easily - the following presentation shows only some of the vast amount of features available, you can read more on the `official homepage <http://somethingaboutorange.com/mrl/projects/nose>`_, the examples should work on linux, OSX and windows.

If your working directory is the MRV root directory, the following command will run all tests ( in about ~7s )::
	
	$ test/bin/tmrv <mayaversion>
	
Run individual test packages or module by specifying their paths::
	
	$ # runs the Path test, as well as all maya related tests of the given maya version
	$ test/bin/tmrv <mayaversion> test/test_path.py test/maya

Running tests outside of the maya test package will not startup maya, hence it will return much quicker::
	
	$ test/bin/tmrv <mayaversion> test/test_enum.py
	
If an exception is raised in the tests, you will see it in the final output, as well as the caught standard output generated when the test case ran. The ``-d`` flag resolves traceback symbols to their actual values. In case you want to jump right into the exception when it occurs, specify ``--pdb``. If you just have a failing test and want to inspect the variable values yourself, use ``--pdb-failure``::
	
	$ test/bin/tmrv <mayaversion> test/test_fails.py -d
	$ test/bin/tmrv <mayaversion> test/test_fails.py --pdb
	$ test/bin/tmrv <mayaversion> test/test_fails.py --pdb-failure
	
As nose will by default catch all standard output of your program, it may also suppress messages you print during the first import of your program. To show all of these as they occur, use the ``-s`` flag::
	
	$ test/bin/tmrv <mayaversion> test/test_startup_issues.py -s
	
Testing User Interfaces
-----------------------
Testing of user interfaces used to be a manual process, which clearly degrades the reliability of software as its user interface will only be tested occasionally in an unrepeatable and possibly incomplete manner. 

Using python, it became far easier to automate user interface testing as your interface elements may provide a clear interface to interact with them. Within certain limits - you will most probably not get around testing a few things manually - you  can at least outline the expected functionality and verify the functionality within these bounds. 

The tests currently available in the ``mrv.test.maya.ui`` package are showing a few windows, the knowing user may also click a few buttons to verify that callbacks work alright. Considering the possibilities, the tests are rather primitive and are assumed to be working if there is no exception - there are `other tools <http://gitorious.org/animio>`_ which do much better in that respect.

These tests currently only show that the UI system is not fundamentally broken, and that Callbacks and Signals work - nonetheless the manual nature of them causes them not to be run very often.

The commandline required to run the tests is the following ( all platforms )::
	
	$ test/bin/tmrv [maya_version] --mrv-maya [ nose arguments ]
	
In future, this testing system is likely to be improved, also considering that QT offers a `test library <http://qt.nokia.com/doc/4.2/qtestlib-manual.html>`_ which can virtualize mouse clicks and keyboard input, in order to fully automate user interface testing.

Other techniques may be used to allow automated tests on default Maya user interfaces, for more information, please see the :ref:`template-project-label` section.  

.. note:: For UI tests to work, ``mayapy`` needs to be able to import ``nose`` to run the actual tests.

Verifying Test Coverage
-----------------------
In statically typed languages, one benefits from the great blessing of having a compiler which is able to check types and their compatibility, as well as to verify names at compile time.

Unfortunately, Python will only be able to discover this big class of errors at runtime, which essentially is too late. Test cases help to run your code, but are you sure it is running every line of it ?

Nose comes with an excellent tool which verifies the tests code coverage. As it needs a few options, there is a tmrv flag which configures nose to run all or the specified tests with coverage output::
	
	$ test/bin/tmrv <mayaversion> --tmrv-coverage 
	$ firefox coverage/index.html
	
The resulting web page highlights all lines that ran, and shows the ones that did not run, which enables you to adjust your tests to run all the lines.

At the time of writing (|today|), MRV had a :download:`test coverage of 90% <../download/coverage/index.html>`, but of course `test coverage is not everything <http://www.infoq.com/news/2007/05/100_test_coverage>`_.

Regression Testing
------------------
As MRV is meant to be useful in all Maya Releases which support python, namely 8.5 till X where X is the latest release, it must be verified that all tests indeed succeed in all available Maya versions, ideally on all platforms.

``tmrvr`` greatly facilitates running these tests::
	
	$ test/bin/tmrvr 
	$ test/bin/tmrv [maya version] --mrv-maya test/maya/ui

IPython and IMRV
================
During development, it is unlikely that one remembers all methods available on instances of a certain type, sometimes its required to just quickly test or verify something, or to pull up the docs on a basic but rarely used python built-in function. Searching the Web is possible, but using ``ipython`` is much more convenient.

``imrv``, one of MRVs :doc:`../tools`,  essentially is an ipython shell which has been setup to load a specialized version of the MRV runtime to provide you with a fully initialized MRV runtime environment::
	
	$ bin/imrv
	
::
	
	>>> p = Node("persp")
	>>> Transform("|persp")
	>>> 
	>>> List all available methods on the perspective transform:
	>>> p.<tab-key>
	>>> 
	>>> Show the doc-string of a method:
	>>> p.name?
	>>> 
	>>> Jump into the debugger next time an exception occurs:
	>>> pdb
	
	>>> Disable the debugger
	>>> pdb
	
Avoiding Trouble - A Word about Reference Counts
================================================
As MRV nearly exclusively uses the API to do work, it also allows you to use the underlying API types, MObject and MDagPath, directly.

If used correctly, the benefit is performance and ease of use, but in the worst case, maya will crash - this happens more easily when using the Maya API than when using MEL for example.

To understand the source of the issue, one has to understand what an MObject is: MObjects are containers with a reference count, a type and a pointer to the actual data. This in fact is very similar to the ``object`` base type in python.

If you see an MObject in python, such as in the following snippet ... ::
	
	p = Node("persp")
	po = p.object()
	<maya.OpenMaya.MObject; proxy of <Swig Object of type 'MObject *' at 0x36a2ee0> >
	
... what you actually see is a proxy object which serves as a python handle to the actual C++ MObject. The reference count of that proxy object is 1, as it is stored in only one named variable, ``po``. The caveat here is that this does not affect the reference count of the underlying MObject at all - its reference count is the same as it was before. The only one who actually holds a reference to it is Maya, and it is allowed to drop it at any time, or copy its memory to a different location. If that would happen, any access to ``p`` or ``po`` may cause a crash or destabilize Maya to cause a crash later, which is even worse.

The only way to forcibly increment the reference count is by copying the MObject explicitly::

	poc = api.MObject(po)
	po, poc
	(<maya.OpenMaya.MObject; proxy of C++ MObject instance at _f0d5050500000000_p_MObject>,
	<maya.OpenMaya.MObjectPtr; proxy of C++ MObject instance at _1008460200000000_p_MObject>)
 
This invoked the C++ copy constructor, and incremented the reference count on the MObject. Copying MObjects might come at additional costs though in case the MObject encapsulates data.

When adding attributes with the bare python Maya API, this situation can easily occur::
	
	p.addAttribute(api.MFnTypedAttribute().create("sa", "stringarray", api.MFnData.kStringArray, api.MFnStringArrayData().create()))
	
In this example, we created two temporary function sets, ``MFnTypedAttribute`` and ``MFnStringArrayData``. The ``create`` methods of the respective sets return newly created MObjects - the only one who keeps a reference is the actual function set. Two bad things happened in the example:

#. ``MFnStringArrayData`` returned an MObject encapsulating an empty string array, then it goes out of scope, and decrements its reference count on the returned MObject during its destruction sequence. The MObject has no one referencing it anymore, so it will destroy itself and its data. Python still has a handle onto the memory location that once kept the MObject, and it is passed to ``MFnTypedAttribute.create``.
#. ``MFnTypedAttribute.create`` produces a new attribute ``MObject`` with (possibly) invalid default data, returns it and destroys itself as it goes out of scope. Again, the reference count of the newly created Attribute MObject decrements to 0, which destroys the Attribute and its data. The python handle you got will be passed to the ``p.addAttribute`` method, which tries to create an attribute from deleted data.

If you try that line, you will see that it apparently works, but its not guaranteed to do so, nor will you be able to tell whether the caused memory corruption will crash Maya at a later point.

The alternative to the line above is to use the Attribute wrappers that MRV provides::
	
	p.addAttribute(TypedAttribute.create("sa", "stringarray", Data.Type.kStringArray, StringArrayData.create()))
	
In the version above, both create methods implicitly copy the returned MObject, which forcibly increments its reference count. Once the underlying MFnFunctionSet goes out of scope, it will decrement the MObject's reference counts to 1, keeping it alive and healthy.

Generally, when dealing with MObjects directly, keep the reference count in mind especially in case of MObjects that have just been created.

In c++, this is not a problem as MObjects are copied automatically when being assigned to a variable for instance or when being passed into functions ( most of the time ). If you have a proper compiler though, the above line would be invalid as well as you return temporary objects and pass them in as reference. 

In python, there is no compiler who would be able to check for this. 
