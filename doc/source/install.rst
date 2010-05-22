
############
Installation
############
MRV can be installed in multiple flavors and in multiple ways. At first the mere amount of combinations might be staggering, but this guide will help you to narrow the options down according to your specific needs and permission level.

Another good news is, that this guide in fact explains how to install new python software in general, and can be applied not only to mrv, but to most other pure python package out there. If you know one, you know 'em all.

First of all, if you want to develop using MRV, its recommended to jump right to the `Developer Installation`_. This guide continues with installation instructions for those who seek a quick look or those who want to install MRV based software.

Basically, installing the Package [1]_ is as simple as putting it into your python interpreter's ``PYTHONPATH``, this guide only makes the effort trying to show you the most common ways to do it.

To allow you to skip reading and jump right to the installation method which will work for all, you will want to read the `Manual Installation using PYTHONPATH <manual-pythonpath-label>`_ section.

**************************
Preliminary Considerations
**************************
All you need to use the Package [1]_ is a python interpreter compatible to your maya version. There you may choose between using the system's python interpreter, or the one shipped with maya, called *mayapy*.

======================================
System's Python Interpreter vs. Mayapy
======================================
MRV's recommended development interpreter is the **system's python interpreter** because:

* it start up ~0.6 seconds faster (as tested on linux) than mayapy
* its easier to install auxiliary packages using `easy_install`_ or your platforms package manager (linux and OSX).
* you can flexibly choose the maya version to run if you have multiple installed

Disadvantages on non-linux platforms are that:

* it must be compiled for the same architecture as your maya version. Maya 64 will need a 64 bit version of the interpreter for instance. 

If the latter statement is an issue for you, you will just want to go with ``mayapy`` instead, which is a bit more restricted and less flexible, but fully functional as well.

Compatibility
-------------
Besides the fact that your system interpreter must be compiled for the same architecture as your maya installation, i.e. 32bit or 64bit, it must also be compatible with maya's python binding.

* Python **2.4** will work with **Maya 8.5**
* Python **2.5** will work with **Maya 2008 and 2009**
* Python **2.6** will work with **Maya 2010 and 2011**

================================
Finding your Installation Method
================================
The best way to install the Package [1]_ differs depending on the target audience. The following list of statements will resolve to viable options sorted by convenience if you follow down the branch that matches your situation:

* Install it just for me

 * I have root/administrator permissions
 
  * I want to use the system's interpreter
  
   #. `Easy Install with Setuptools`_
   #. `Auto-Install with Distutils`_
   #. `Manual Installation`_
  
  * I want/have to use Mayapy
  
   #. `Auto-Install with Distutils`_
   #. `Manual Installation`_
 
 * I may not change the system
 
  * `Manual Installation (PYTHONPATH) <manual-pythonpath-label>`_
 
* Install it for several people at once

 * `Manual Installation (PYTHONPATH) <manual-pythonpath-label>`_
 
****************************
Easy Install with Setuptools
****************************
System Interpreter Only
root permissions


**************
Retrieving MRV
**************
git clone
archive ( pipy, github )

The following topics assume you have MRV downloaded and extracted.

===========================
Auto-Install with Distutils
===========================
root permissions
mention --no-compile

===================
Manual Installation
===================


.. _manual-pythonpath-label:

PYTHONPATH
----------
no root permissions
mention: several users

Site-Packages
-------------
root permissions

****
IMRV
****

*********
Upgrading
*********
easy_install -U package
otherwise git fetch + merge
re-extract from archive

**********************
Developer Installation
**********************
As a (future) developer, please have a look at the dedicated development section for detailed information on how to :ref:`get MRV (Preview) up and running <development-label>`.

-------

.. [1] The package may be MRV itself or a 'derived' package that uses MRV as framework.
.. _easy_install: http://pypi.python.org/pypi/setuptools
