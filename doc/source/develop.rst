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



.. _performance-docs-label:

=====================================
Performance and Memory Considerations
=====================================

Iterators
=========
Pre-Filter by MFn.type, possibly return unwrapped API nodes wherever feasible.

Undo
=====

_api_ calling convention
=========================

findPlug vs. node.plug
======================

Single vs. Multi
================

Node-Wrapping
==============
