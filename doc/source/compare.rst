###################
Comparison to PyMel
###################
MRV is not the first attempt to make the use of Python within Maya more
convenient.
PyMel is an excellent feature packed Framework which is, as the name suggests, 
more closely affiliated to MEL than to the Maya API, also it also allows you to 
access the latter one conveniently.

Together with Chad Dombrova, the original Author and Maintainer of PyMel, the 
following overview has been compiled to provide an overview of the similarities and 
differences of the two frameworks regarding their features, performance and coding
convenience.

********
Features
********


==================== ================================================== ==================================================
Topic                MRV 1.0.0 Preview										PyMel 1.0.1
==================== ================================================== ==================================================
this 				  hello            								       hi
that 				  hello           								       hi
==================== ================================================== ==================================================


***********
Performance
***********
Although all performance tests are synthetic and will to give a real indication 
of the actual runtime of your scripts, they are able to give a hint about the
general performance of certain operations.

The numbers have been produced on a 2Ghz Dual Core Machine running Xubuntu 8.04. 
Maya has been preloaded by the systems virtual memory system, and all temporary 
directories are RAM disks (tmpfs).

The tests were run one time only. All MRV performance tests can be found in the 
``mrv.test.maya.performance`` module and run using 
``test/bin/tmrv [maya_version] test/maya/performance``.

All PyMel tests can be found on my github fork at 
http://github.com/Byron/pymel/tree/performancetests, and run using 
``tests/pymel_test.py tests/performance``.


***********
Basic Tasks
***********
The following table concentrates on the code required to perform everyday and 
simple tasks. It assumes that all required classes and functions have been 
imported into the module where the code is run.

# sets handling
# components and sets


.. rubric:: Footnotes

.. [#f1] 
.. [#f2] 

