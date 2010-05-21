
.. _gendocs-label: 

###########################
The Documentation Generator
###########################

The documentation generally consists of two parts, the manual and API documentation. 

The manual is an 100% handwritten collection of text files using `restructured text`_ markup which are bound together via index files. Index files are special in that they contain ``toctree`` directives to maintain a table of contents.

The API documentation is created automatically from the `restructured text`_ compatible doc strings of packages, modules, classes, methods and functions. 

The layout and conversion of the markup is performed by `sphinx`_. As the way sphinx generates the API documentation involves everything imported into the respective module, not only the defined routines are auto-documented, but also everything else. As this is hard to read and hard to understand at the current time, `epydoc`_ fills the gap and is provided as alternative API documentation.

In order to provide more information to the interested reader about the state of the project, a coverage report can be generated automatically and then linked to by the manual where needed.

*******
makedoc
*******

The previously mentioned features involve multiple tools and passes to compile the final html documentation ( which is currently the only one being directly supported ).

The ``makedoc`` script is located in the ``doc`` directory and needs to be run from there or the ``doc`` directory of your derived project.

The script supports multiple flags to control the usage of individual features. To assure consistency, it will use the :doc:`info module <pinfo>` to retrieve basic project information.

* .. cmdoption:: --sphinx 0|1 (-s)

    If 1, default 1, the `sphinx`_ based manual will be generated. If False, neither that nor the autogen documentation will be built. 

* .. cmdoption:: --sphinx-autogen 0|1 (-a)
    
    If 1, default 1, `sphinx`_ API documentation will be generated. As it usually takes longest of all operations, its worth turning it off when writing the manual.

* .. cmdoption:: --epydoc 0|1 (-e) 
    
    If 1, default 1, `epydoc`_ html API documentation will generated from your projects sources and embedded into the respective API documentation created by `sphinx`_.
    
* .. cmdoption:: --coverage 0|1 (-c)

    If 1, default 1, a nose coverage report is created to which sphinx documents may link as required.
    
* .. cmdoption:: --clean

    If set, instead of generating documentation, previously generated files will be removed. This flag modified all previously mentioned flags, and to clean only the coverage report, your would type::
        
        $ ./makedoc --clean -e 0 -s 0 -c 1

.. note:: In order to generate sphinx or epydoc docuementation, ``sphinx`` and ``epydoc`` need to be installed in the python installation executing ``makedoc``. To generate a coverage report, you will need ``nose`` and ``coverage`` installed in the interpreter matching your latest available maya version.

==================
version_info Files
==================
As building documentation can take a long time, especially if the sphinx API documentation is involved, it is useful to protect it from being regenerated unnecessarily, especially when setting up your project for :doc:`distribution <index>`.

Assuming that it is usually enough to build the documentation once per project version, it only needs to be rebuild if your project version changed relative to the project version stored in the ``*.version_info`` files. One is created for each documentation target, so you will see ``epydoc.version_info``, ``coverage.version_info`` and ``sphinx.version_info`` in your doc directory after a complete build.

Running ``makedoc`` will always regenerate the documentation, but when the script is executed from within the :doc:`setup script <setup>`, documentation generation will be skipped if the version_info matches the version you are currently distributing.

.. note:: This distribution behavior might not always be desired or correct - in the latter case it is up to your judgement to run a ``makedoc --clean`` before redoing the distribution. 

.. _restructured text: http://docutils.sourceforge.net/rst.html
.. _sphinx: http://sphinx.pocoo.org/
.. _epydoc: http://epydoc.sourceforge.net/
