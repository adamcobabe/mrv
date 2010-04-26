#################
Commandline Tools
#################
This document contains a full listing of the included commandline tools as well as how to use them.

All production level programs are located in ``mrv/bin``, all testing utilities can be found in ``mrv/test/bin``. 

All examples are given using linux shell semantics, windows users usually only have to substitute '/' with '\\', and be aware of possible limitations.

****************
Production Tools
****************

mrv
===
This tool will setup the environment to allow running MRV and Maya Standalone within your system interpreter. The latter one is expected to be in your PATH.

The first argument passed in to the tool names the Maya release you would like to run, these can be *8.5* to X, where X denotes the latest release.

All additional arguments are passed to the python interpreter directly.

It can easily be used to write standalone tools with maya support.

**Sample Usage**::
	
	$ # start a python interpreter with maya 2011
	$ bin/mrv 2011
	
	$ # show the tools help
	$ bin/mrv --help
	
	$ # show the help of the underlying python interpreter
	$ bin/mrv 2011 -h

**Availability**: Linux, OSX and Windows

.. note:: The windows version of the tool currently does not allow the maya version to be specified.

.. _imrv-label:

imrv
====
This program is effectively nothing more than a customized IPython shell which provides a fully initialized MRV development environment. Additionally, it will attach all available functions to all types to aid auto-completion of methods - under normal conditions methods are only added to a type as you call the function.

``imrv`` can be seen as the python version of ``maya -prompt``.

An introduction to using the tool can be found in :doc:`develop`.

**Sample Usage**::
	
	$ # get ipython with a fully initialized MRV in Maya 2011
	$ imrv 2011

**Availability**: Linux and OSX

.. note:: Will only work if you have the ipython package available in your python installation.


**************
Test Utilities
**************

tmrv
====
A MRV specific replacement for the ``nosetests`` utility which supports all arguments of ``nosetests``, whereas the first argument may be the Maya release you want to run the tests in.

Arguments specific to mrv are prefixed with ``--mrv-``.

**Sample Usage**::
	
	$ # run all tests in Maya 2011
	$ test/bin/tmrv 2011
	
	$ # run the given tests in Maya 2008
	$ test/bin/tmrv 2008 test/test_path.py test/maya
	
	$ # show all arguments supported by nosetests
	$ test/bin/tmrv --help
	
To generate a **coverage report**, use the ``--mrv-coverage`` flag. Such a  :download:`coverage report <download/coverage/index.html>` is generated using  nose coverage which must be available in your local nose installation. As it is essentially a reconfigured nose, it supports all nose specific arguments as well.

**Coverage Sample Usage**::
	
	$ # get a coverage report after running all tests in Maya 2011 
	$ test/bin/tmrv 2011 --mrv-coverage
	$ # show the report in a browser
	$ firefox coverage/index.html

**Availability**: Linux, OSX and Windows

tmrvr
=====
This tools allows automated full regression testing by running all tests for all available or specified maya versions. Use the ``--help`` flag for additional options.

**Sample Usage**::
	
	$ # Run all tests for all available maya versions
	$ test/bin/tmrvr
	
	$ # Run all tests only for the given maya versions
	$ test/bin/tmrvr 8.5 2008
	
	$ # Run all tests, but skip the single tests
	$ test/bin/tmrvr --skip-single

tmrvUI
======
Runs UI specific tests. For this to work, you must supply a path to the maya binary which should run the specified or default User Interface. If no test modules are given as either relative or absolute paths, all test cases reachable from the current working directory will be run.

**Sample Usage** ( Linux and OSX )::
	
	$ # run all tests reachable from the current directory ( even non-ui )
	$ test/bin/tmrvUI <path/to/maya/bin/maya>
	
	$ # run all UI tests
	$ test/bin/tmrvUI <path/to/maya/bin/maya> test/maya/ui
	
	$ # run only the specified module, verbosely 
	$ test/bin/tmrvUI <path/to/maya/bin/maya> test/maya/ui/test_base.py -v
	
**Sample Usage** ( Windows )::
	
	$ test\\bin\\tmrvUI.bat [ nose args ]
	
Please note that the windows version currently requires the maya \bin directory to be in your PATH so that maya can be started by just typing 'maya'. This is due to the fact as the batch file is currently in a relatively poor state of development, and as it doesn't allow any spaces in the paths, its impossible to specify a path like "C:\\program files\autodesk" to the actual maya binary.
	
**Availability**: Linux, OSX, Windows

.. note:: This tools interface is slightly different from ``tmrv`` as you currently may not specify the maya version to run by release, but by the full path to the executable. However, it is likely to be improved, together with the User Interface testing utilities.
