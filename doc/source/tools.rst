#################
Commandline Tools
#################
This document contains a full listing of the included commandline tools as well as how to use them.

All production level programs are located in ``mrv/bin``, all testing utilities can be found in ``mrv/test/bin``. 

All examples are given using linux shell semantics, windows users usually only have to substitute '/' with '\\' and prepend the ``python.exe`` interpreter which has to be used to launch the programs.

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
	
Additionally you can prepare the environment and start a default maya session with mrv support. Use the ``--mrv-maya`` flag to accomplish this::
	
	$ # start a default maya 2011 session
	$ bin/mrv 2011 --mrv-maya
	
	$ # start maya 8.5 in prompt mode
	$ bin/mrv --mrv-maya -prompt

.. note::
	The mrv command will use execv on non-windows system, but use spawn on windows to workaround some issues. This implies that scripts on linux/osx can natively use the mrv program, standardchannels are handled automatically. On windows the spawned process will be attached with all standardchannels of the parent python process, but its questionable whether this has the intended effect.
	
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

.. note:: On Windows, paths to the test modules and packages to run must be absolute which appears to be a nose limitation. For example, the *test/maya* becomes something like "c:\projects\mrv\test\maya" on windows.
Additionally, an absolute path must be specified as opposed to the non-windows os's which take the current directory as hint for where to find tests.

**Coverage Sample Usage**::
	
	$ # get a coverage report after running all tests in Maya 2011 
	$ test/bin/tmrv 2011 --mrv-coverage
	
	$ # show the report in a browser
	$ firefox coverage/index.html

	
In order to test user interfaces, you need to run the actual maya executable in UI mode, that is without '-batch' or '-prompt' specified. Using the ``--mrv-maya``flag that ``mrv`` provides, you will get a maya UI session setup to run the specified nose tests with the given options.

**UI Tests Sample Usage**::
	
	$ # Run all UI tests in maya 2011
	$ test/bin/tmrv 2011 --mrv-maya test/maya/ui
	
	$ # Run all tests, including coverage, within maya 8.5
	$ test/bin/tmrv 2011 --mrv-maya --mrv-coverage

.. note:: nose must be installed for mayapy in order for the UI tests to work.
	
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

