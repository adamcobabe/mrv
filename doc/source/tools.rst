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
This tool will setup the environment to allow running MRV and Maya Standalone within your system interpreter, mayapy, or maya.bin. The system interpreter will be used by default and is expected to be in your path. On Linux and OSX, it must be named ``python2.x``. On Windows, the python interpreter's executable is expected to be ``python2x``.**x** can be 4,5 and 6 and depends on the maya version you would like to run.

If no python interpreter can be found in your path, ``mrv`` will fallback to using ``mayapy``.

The first optional argument passed in to the tool names the Maya version you would like to run, these can be *8.5* to X, where X denotes the latest release.

All additional arguments are passed to the python interpreter or maya.bin directly.

It can easily be used to write standalone tools with maya support.

**Sample Usage**::
	
	$ # start a python interpreter with maya 2011
	$ bin/mrv 2011
	
	$ # show the tools help
	$ bin/mrv --help
	
	$ # show the help of the underlying python interpreter
	$ bin/mrv 2011 -h
	
The --mrv-maya flag
-------------------
	
Additionally you can prepare the environment and start a default maya session with mrv support. Use the ``--mrv-maya`` flag to accomplish this::
	
	$ # start a default maya 2011 session
	$ bin/mrv 2011 --mrv-maya
	
	$ # start maya 8.5 in prompt mode
	$ bin/mrv --mrv-maya -prompt

The --mrv-mayapy flag
---------------------
By default, mrv will try to use the system's python interpreter first, and mayapy if it could not be found. This can be problematic if the system' python interpreter is not suitable to run the given maya version. In that case, you may force mrv to use maya's builtin python interpreter using the ``--mrv-mayapy`` flag.

**Enforce Mayapy Sample Usage**::
	
	$ # start mrv for maya 2010 using mayapy
	$ bin/mrv 2010 --mrv-mayapy
	

	
The --mrv-no-maya flag
----------------------
There may be occasions when you want to use mrv facilities which are not specific to maya at all, and the ``mrv.maya`` module is not used. In this case you may specifiy which code to run using the default python ``-c`` and ``-m`` arguments. All remaining arguments will be set to ``sys.argv`` which can be read by your code subsequently.

**Use the current python interpreter without maya support**::
	
	$ bin/mrv --mrv-no-maya -c "import mrv; print mrv" -given -via=sys.argv

.. note::
	The mrv command will use execv on non-windows system, but use spawn on windows to workaround some issues. This implies that scripts on linux/osx can natively use the mrv program, standardchannels are handled automatically. On windows the spawned process will be attached with all standardchannels of the parent python process, but its questionable whether this has the intended effect.

.. _imrv-label:

imrv
====
This program is effectively nothing more than a customized IPython shell which provides a fully initialized MRV development environment. Additionally, it will attach all available functions to all types to aid auto-completion of methods - under normal conditions methods are only added to a type as you call the function.

``imrv`` can be seen as the python version of ``maya -prompt``.

An introduction to using the tool can be found in :doc:`develop`::

	$ # get ipython with a fully initialized MRV in Maya 2011
	$ imrv 2011

.. note:: Will only work if you have the ipython package available in your python installation.


**************
Test Utilities
**************

tmrv
====
A MRV specific replacement for the ``nosetests`` utility which supports all arguments of ``nosetests``, whereas the first argument may be the Maya release you want to run the tests in.

**Sample Usage**::
	
	$ # run all tests in Maya 2011
	$ test/bin/tmrv 2011
	
	$ # run the given tests in Maya 2008
	$ test/bin/tmrv 2008 test/test_path.py test/maya
	
	$ # show all arguments supported by nosetests
	$ test/bin/tmrv --help
	
The --mrv-coverage flag[=packagename]
-------------------------------------
To generate a **coverage report**, use the ``--mrv-coverage`` flag. Such a  :download:`coverage report <download/coverage/index.html>` is generated using  nose coverage which must be available in your local nose installation. If you specify a package name, only code that ran within the given package will be included in the coverage report. It defaults to ``mrv``.

As it is essentially a reconfigured nose, it supports all nose specific arguments as well::

	$ # get a coverage report after running all tests in Maya 2011 
	$ test/bin/tmrv 2011 --mrv-coverage
	
	$ # show the report in a browser
	$ firefox coverage/index.html

.. note:: On Windows when using cmd.exe, paths to the test modules and packages to run must be absolute. For example, the *test/maya* becomes something like "c:\projects\mrv\test\maya" on windows. Additionally, an absolute path must be specified as opposed to the non-windows os's which take the current directory as hint for where to find tests.

Testing User Interfaces
-----------------------
In order to test user interfaces, you need to run the actual maya executable in UI mode, that is without '-batch' or '-prompt' specified. Using the ``--mrv-maya``flag that ``mrv`` provides, you will get a maya UI session setup to run the specified nose tests with the given options::

	$ # Run all UI tests in maya 2011
	$ test/bin/tmrv 2011 --mrv-maya test/maya/ui
	
	$ # Run all tests, including coverage, within maya 8.5
	$ test/bin/tmrv 2011 --mrv-maya --mrv-coverage

.. note:: nose must be installed for ``mayapy`` in order for the UI tests to work.
	
tmrvr
=====
This tools allows automated full regression testing by running all tests for all available or specified maya versions. Use the ``--help`` flag for additional options.

**Sample Usage**::
	
	$ # Run all tests for all available maya versions
	$ test/bin/tmrvr
	
	$ # Run all tests only for the given maya versions
	$ test/bin/tmrvr 8.5 2008
	
The --skip-single flag
----------------------
If you would like to shorten the regression test, you can skip the single tests which perform only one tests per maya session as they have to be run in an isolated fashion. In case you decide to do so, the final result of the regression test will be failure though.
	
	$ # Run all tests, but skip the single tests
	$ test/bin/tmrvr --skip-single

	
*************
Release Tools
*************
A list of tools which are used mainly to do new releases.

makedoc
=======
Create and update the MRV documentation or parts thereof. By default, all parts will be built. Use the ``--help`` flag to see a full list of viable options::
	
	$ # make all docs
	$ cd mrv/doc
	$ ./makedoc
	
.. note:: In order for the documentation to be generated, the python interpreter of your latest installed maya version needs to have sphinx installed. If a coverage report should be generated, nose and coverage are a prerequesite as well for the python interpreter matching your latest installed maya version. If epydoc documentation should be generated, the interpreter *executing* ``makedoc`` needs to have epydoc available.
