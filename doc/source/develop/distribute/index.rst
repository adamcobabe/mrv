
.. _distribution-label: 

############
Distribution
############
Besides providing a framework for writing your software efficiently, software needs ways to be distributed to reach the end-user. The MRV distribution system is written such that it cannot only distribute MRV, but also projects using it.

The main features are:

* Manage version and project information non-redundantly
* Compile documentation using Sphinx_ and/or Epydoc_
* Create source or binary distributions and provide tag-management facilities using git.
* Bake external dependencies into your distribution 
* Incorporate your test-suite to verify the products function with full pre-release regression testing and post-release testing, which runs unit-tests in the package you are actually going to distribute.
* Easy basic customization
* Compatible to default python distutils_ and working with easy_install.
* Operational on Linux, OSX and Windows

The following guide will explain the individual MRV distribution facilities, how MRV uses them, and how you can use them easily. 

********
Contents
********

.. toctree::
   :maxdepth: 2
   
   workflow
   pinfo
   docs
   setup
   
   
.. _distutils: http://docs.python.org/distutils
.. _Sphinx: http://sphinx.pocoo.org/
.. _Epydoc: http://epydoc.sourceforge.net/
