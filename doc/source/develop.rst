=======================
Development Environment
=======================
*NOTE*: This article is still under development

This article describes the required setup and configuration of your system to develop MayaRV.

---------------
Prerequesites
---------------
* Test Framework
 * Nose 0.11 or higher
* Documentation Generation
 * Epydoc 3.x or higher
 * Sphinx 0.62 or higher

--------------
Installation
--------------
Clone the repository to get all data. Either fork your own on [www.gitorious.org] or [www.github.com] and clone from there, or clone from the main repository.

 git clone git://gitorious.org/mayarv/mainline.git mayarv
 git submodule update --init --recursive

-------
Windows
-------
On Windows, make sure that the maya revised repository has at least one folder between itself and the drive letter. Otherwise you are not able to run tests properly due to some issue with nose on windows. 

* This is wrong: 
 * c:\\mayarv\\[.git]
* This would work:
 * c:\\projects\\mayarv\\[.git]

Set your '''MAYA_LOCATION''' environment variable to the location of the maya version to use. MayaRV will be run using ''mayapy'' of the specified version.

Install nose in maya's python site-libararies.

'''TODO: Detail this'''

---
OSX
---
As MayaRV will be run using ''mayapy'' on this system, it is required to install nose in the maya site libraries. 

'''TODO: Detail this'''

.. _runtestsdoc-label:
Running Tests
=============

Building Docs
=============

Windows
=======
