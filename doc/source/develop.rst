=======================
Development Environment
=======================
*NOTE*: This article is still under development

This article describes the required setup and configuration of your system to develop MayaRV.

Prerequesites
=============
* Test Framework
 * Nose 0.11 or higher
* Documentation Generation
 * Epydoc 3.x or higher
 * Sphinx 0.62 or higher

Installation
============
Clone the repository to get all data. Either fork your own on [www.gitorious.org] or [www.github.com] and clone from there, or clone from the main repository.

 git clone git://gitorious.org/mayarv/mainline.git mayarv
 git submodule update --init --recursive

Windows
=======
On Windows, make sure that the maya revised repository has at least one folder between itself and the drive letter. Otherwise you are not able to run tests properly due to some issue with nose on windows. 

* This is wrong: 
 * c:\\mayarv\\[.git]
* This would work:
 * c:\\projects\\mayarv\\[.git]

Set your '''MAYA_LOCATION''' environment variable to the location of the maya version to use. MayaRV will be run using ''mayapy'' of the specified version.

Install nose in maya's python site-libararies.

'''TODO: Detail this'''

OSX
==== 
'''TODO: Detail this, it uses the default system interpreter, any of its sitelibraries will work.'''

Maya2011 and onward
-------------------
Starting with Maya2010, maya is delivered as 64 bit birnary. The default interpreter in your path should be 64 bits as well, but if it is not, you have to make some adjustments. 

To allow the mrv startup script to find a python interpreter compiled for 64 bit, it will be sufficient to put a symbolic link to ``python2.6`` into your /usr/bin directory which points to the interpreter in question. 

``mayapy`` in your maya installation directory will work in case you don't want to build your own one, using macports for instance. In that case you need to put a symbolic link named ``python2.6`` into your ``/Applications/Autodesk/maya2010/Maya.app/Contents/bin`` directory which needs to be inserted to the first position of your PATH. To run the unit tests, you might have to install ``nose`` into maya's site-packages directory.


.. _runtestsdoc-label:
=============
Running Tests
=============

=============
Building Docs
=============

====================
Development Workflow
====================
suggest TDD, BTD

====================
Debugging Utilitites
====================
pdb
utiltiies
imrv

===============
Common Mistakes
===============
Lifetime of MObjects/reference count
mat == p.wm.getByLogicalIndex(0).asData().matrix()	# matrix is ref, parent goes out of scope


======
Naming
======
X and setX
If overridden MFnMethod uses getX, an alias X is provided, the method itself is overridden as getX.
isSomething, but issometh	# abbreviations lower case


.. _performance-docs-label:

=====================================
Performance and Memory Considerations
=====================================
MayaReVised has been created with performance in mind. Core code as gone through several iteration in order to be as fast as it can possibly be within python. This is beneficial to the developer as he can be sure that conveniently written code will run at a high pace. 
Usually this kind of code is the most readable and the most maintainable which is why it is preferred. Nonetheless there are situations when performance outweights code convenience, this article explains what to look out for and how to improve the performance of your programs.

The respective tips are listed in the order of simplicity and effect, hence simler and more effective ways to enhance performance come first.

Iterators
=========
When operating in large scenes, its important to limit the amount of nodes that are returned by iterators. The fastest way to do this is to use an MFn.kType pre-filter to limit the yielded Nodes to certain types. As the pre-filtering will happen in C++, it will be very fast::
	>>> iterDagNodes(api.MFn.kTransform, api.MFn.kShape)		# Fast !
	>>> iterDagNodes(predicate=lambda n: isinstance(n, (Transform, Shape)))	# slow and wasteful

Undo
=====
Turn off the undo queue completely by setting the MAYARV_UNDO_ENABLED=0 in your environment. This will reduce overhead by at least 10% and increase the performance of many core methods. As a positive side-effect, you have more memory at runtime as the undoqueue will not store the history of operations.

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
MayaRV is very aware of the fact that the added convenience comes at a cost. Where programming convenience and programmer's efficiency is improved, its likely that the runtime of the resulting programs is much less than optimal.

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




