
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
* Incorporate your test-suite to verify the products functionality before and after the distribution was generated.
* Easy basic customization
* Compatible to default python distutils_ and working with `easy_install`_.
* Operational on Linux, OSX and Windows

The following guide will explain the individual MRV distribution facilities, how MRV uses them, and how you can use them easily. 


----

.. toctree::
   :maxdepth: 2
   
   pinfo
   setup
   docs
   workflow
   
   
.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _distutils: http://docs.python.org/distutils
.. _Sphinx: http://sphinx.pocoo.org/
.. _Epydoc: http://epydoc.sourceforge.net/
