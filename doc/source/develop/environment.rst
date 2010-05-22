

************
Environment
************
This paragraph describes the required setup and configuration of your system to develop MRV or projects based on MRV.

Prerequisites
=============
The following software packages need to be installed,

* Git 1.6.5 or higher

* Autodesk Maya 8.5 or higher

* *Testing Framework*

 * Nose 0.11 or higher
 * Coverage ( optional )
 
* *Documentation Generation*

 * Epydoc 3.x
 * Sphinx 0.65 or higher

The following installation guide *assumes you have already installed git and Autodesk Maya* for your platform. For instruction, please see the documentations of the respective software package.
 
Installation
============
The basic installation steps are similar in all supported operating systems. Getting MRV to run within a standalone interpreter differs between the platforms.

If a standalone interpreter does not work for you, its absolutely possible to run MRV within the default maya python interpreter, ``mayapy``.

.. _install-label:

1. Install the Prerequisites
----------------------------
The instructions assume you are going to run MRV within a standalone interpreter. If you are planning to use mayapy, the installation may be more complicated, but in general all that needs to be done is to put the required package(s) into the 'site-packages' folder of your python installation.

Using easy_install, which comes with the `python setuptools <http://pypi.python.org/pypi/setuptools>`_ the installation is as easy as the name suggests::
	
	$ easy_install<python_version> nose coverage sphinx epydoc

Please note that the version of easy_install is important as you need to install the prerequisites for each python version that is used by the maya version you are going to run:

* Maya 8.5 -> Python 2.4
* Maya 2008|2009 -> Pyhthon 2.5
* Maya 2010|2011 -> Python 2.6

Mayapy
^^^^^^
The only package that you need to install to run the tests is ``nose``. Its recommended to retrieve the package using easy_install for your standalone interpreter and to alter your ``PYTHONPATH`` to include the ``site-packages`` directory of your local python installation. 

Alternatively, copy the ``nose`` package into *"C:\\Program Files\\Autodesk\\Maya<version>\\Python\\Lib\\site-packages"* ( windows ), into *"/usr/autodesk/maya<version>/lib/python<pyversion>/site-packages"* ( Linux ) or into *"/Applications/Autodesk/maya<version>/Maya.app/Contents/Frameworks/Python.framework/Versions/<pyversion>/lib/python<pyversion>/site-packages"* ( OSX ).

.. _repo-clone-label: 

2. Get A or Your Repository Clone
---------------------------------
Clone the MRV mainline repository from gitorious or github. Either fork your own on www.gitorious.org/mrv or www.github.com/Byron/mrv and clone from your fork, or clone from the mainline repository as shown here.

Execute the following::

 $ git clone git://gitorious.org/mrv/mainline.git mrv
 $ git submodule update --init
 
On linux and OSX, you would have done this in a shell of your choice. On windows, you would have retrieved a shell using the "Git Bash Here" menu entry in your RMB explorer menu when clicking on a parent-folder of your choice.

Windows
^^^^^^^
On Windows, make sure that the MRV repository has at least one folder between itself and the drive letter. Otherwise you are not able to run tests properly due to some issue with nose on windows (apparently). 

* This is wrong:

 * c:\\mrv\\[.git]
 
* This would work:

 * c:\\projects\\mrv\\[.git]


3. Run the tests
----------------
By running the tests, you verify that the installation actually succeeded as you are able to run MRV in a standalone interpreter.

In your shell, you should now be able to execute the ``tmrv`` command as follows::
	
	$ cd mrv
	$ # start the tests for the given maya version, 2011 in this case
	$ test/bin/tmrv 2011

All tests are expected to succeed. Please note that ``tmrv`` just executes ``mrv/bin/mrv`` and launches nosetest afterwards, hence all parameters supported ``nosetests`` in your particular installation will work here as well.

On OSX, the default python installation will not work if you intend to run Maya2010 or later. Please see the ``Troubleshooting`` guide for a solution which is essentially using mayapy. This can be achieved using the following command::
	
	$ test/bin/tmrv 2011  --mrv-mayapy

On *windows*, in a command prompt, execute::
	
	$ cd mrv
	$ python test\bin\tmrv 2011 <full/path/to/test/directory>

.. note:: On windows, you can use the same commands presented here if you use a git-bash instead of cmd.exe.
	
Troubleshooting
---------------
This paragraph informs about possible issues which have a solution already.

OSX and 32bit/64bit Mismatch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Starting with Maya2011, maya is delivered as 64 bit binary. The default interpreter in your path should be 64 bits as well, but if it is not, you have to make some adjustments. Conversely, Maya2010 uses Pyhthon2.6 which is 64 bit on Snow Leopard, whereas Maya was just compiled in 32 bits.

To solve the issue, either install a python interpreter which matches the architecture of your respective maya version, or use mayapy.

Still troubled ? Use mayapy
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If the standalone interpreter just doesn't want to work on your platform or with your particular configuration, you may always use ``mayapy``, which can be found in the *<maya_install_directory>/bin* folder. It will setup a standalone interpreter which automatically pulls in the packages required for Maya to work.

As a side-effect, ``nose`` needs to be installed in mayapy's *site-packages* directory, as indicated in the :ref:`installation section<install-label>`.

To force using mayapy, use the ``--mrv-mayapy`` flag::
	
	$ # start the mayapy python interpreter in interactive mode
	$ bin/mrv 2011 --mrv-mayapy
	
	$ # run all tests in mayapy
	$ /test/bin/tmrv 2009 --mrv-mayapy


