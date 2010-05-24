
############
Installation
############
MRV can be installed in multiple flavors and in multiple ways. At first the mere amount of combinations might be staggering, but this guide will help you to narrow the options down according to your specific needs and permission level.

Another good news is, that this guide in fact explains how to install new python software in general, and can be applied not only to mrv, but to most other pure python package out there. If you know one, you know 'em all.

First of all, if you want to develop using MRV, its recommended to jump right to the :ref:`developer installation <install-label>`. This guide continues with installation instructions for those who seek a quick look or those who want to install MRV based software.

Basically, installing the Package [1]_ is as simple as putting it into your python interpreter's ``PYTHONPATH``, this guide only makes the effort trying to show you the most common ways to do it.

.. note:: If you want to skip all the reading at first, you may also watch the `MRV Installation Guide on Youtube <http://www.youtube.com/user/ByronBates99#p/c/D0F37129CE775529>`_ - you may choose your platform there.

**************************
Preliminary Considerations
**************************
All you need to use the Package [1]_ is a python interpreter compatible to your maya version. There you may choose between using the system's python interpreter, or the one shipped with maya, called *mayapy*.

==================
CPython vs. Mayapy
==================
MRV's recommended development interpreter is the **system's python interpreter**, ``cpython``, because:

* it starts slightly faster (as tested on linux) than mayapy
* its easier to install auxiliary packages using `easy_install`_ or your platforms package manager (linux and OSX). This implies that :ref:`imrv <imrv-label>` will work much more easily.
* you can flexibly choose the maya version to run if you have multiple installed

Disadvantages on non-linux platforms are that:

* it must be compiled for the same architecture as your maya version. Maya 64 will need a 64 bit version of the interpreter for instance. 

If the latter statement is an issue for you, you will just want to go with ``mayapy`` instead, which is a bit more restricted and less flexible, but fully functional as well.

Compatibility
-------------
Besides the fact that ``cpython`` must be compiled for the same architecture as your maya installation, i.e. 32bit or 64bit, it must also be compatible with maya's python binding.

* Python **2.4** will work with **Maya 8.5**
* Python **2.5** will work with **Maya 2008 and 2009**
* Python **2.6** will work with **Maya 2010 and 2011**

.. note:: On windows, the system interpreter appears to only work if python 2.6 is used, but it might crash on 2.5 or earlier. MRV can always use ``mayapy`` as a fallback though.

Python Executable Names
-----------------------
The :ref:`mrv script <mrv-label>` can be seen as something like a launchpad as it will configure mrv and derived projects, as well as the process' environment, to allow maya standalone to be started properly. In that sense, it is much like a more general ``mayapy`` which serves the same purpose.

Coming with its duties of adjusting the python process' environment, it needs python to be restarted, possibly in a different version. To accomplish this, it will use the python executables in your PATH. 

On linux, this is automatically being handled for you, and mrv will find the expected executables named ``python<version>``, ``<version>`` being 2.4, 2.5 or 2.6, if these are installed.

On windows, usually only the last installed python executable is in the PATH. To help mrv, you need to copy ``python.exe`` of the python installation of your choice and rename the copy to ``python<version>.exe`` where ``<version>`` is ``24`` , ``25`` , or ``26``. If ``mrv`` cannot find the executable, it will try to use ``mayapy`` instead. 

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
 
  * :ref:`Manual Installation (PYTHONPATH) <manual-pythonpath-label>`
 
* Install it for several people at once

 * :ref:`Manual Installation (PYTHONPATH) <manual-pythonpath-label>`
 * *Of course one could repeat single-person installation routines for several people, but this sort of uncontrolled redundancy is not advisable in most cases.*
 
****************************
Easy Install with Setuptools
****************************
This installation type works for use with the system's python interpreter, and usually root or administrator privileges are required. At the end of the procedure, MRV will be installed on your system.

If you have `easy_install`_ on your *linux* or *osx* system, it is as easy as typing into a shell [3]_::
    
    $ easy_install[-<py-version>] mrv
    
Where the optional *<py-version>* is 2.4, 2.5 or 2.6. If it worked, you should be able to run ``mrv`` and ``imrv`` right away::
    
    $ mrv<py-version> -c "import mrv.maya.all"
    $ imrv<py-version>

On a *windows system*, its the command prompt you would use::
    
    > cd c:\Python<py-version>\Scripts
    > easy_install.exe mrv
    
To verify mrv is installed correctly, you can execute the mrv script::
    
    > ..\python.exe mrv -c "import mrv.maya.all"
    
Getting **imrv** to work with this setup on windows, please read the dedicated `IMRV`_ section.

.. have to use full url here, can't just refer to the _easy_install target for some reason 

.. note:: If you don't have an easy_install binary yet, you can install it `via the setuptools <http://pypi.python.org/pypi/setuptools>`_. The windows installation claims being for 32 bit installations only, but it works fine in 64 bit python installations as well.

**************
Retrieving MRV
**************
All the following installation methods require you to retrieve a copy of the MRV distribution. There are two ways to do that, the most common one is to download a zip archive. The less common, but more sophisticated one is to clone a git distribution repository, including the advantage to make updates to MRV very easy.

The installation topics assume you have MRV downloaded and extracted already.

.. _install-archive-label:

=======
Archive
=======
You can download a zip archive at one of the following sources:

Python Package Index:
    http://pypi.python.org/pypi/MRV
    
GitHub:
    http://github.com/Byron/mrv-distro/downloads
    
Extract the archive into a folder of your choice.

===========
(Using) Git
===========
Using a shell of your choice, checkout the git repository keeping the mrv source distribution::

    $ git clone git://github.com/Byron/mrv-distro.git mrv
    
On windows, the commandline would be the same, except that you would use the 'Git Bash Here' on a folder in the Explorer first to obtain a shell.

.. note:: The mrv source distribution repository is not meant for mrv development. If you intend to alter mrv's sources, please proceed to the `Developer Installation`_.

.. _autoinstall-label:

===========================
Auto-Install with Distutils
===========================
In all cases, you need root or administrator permissions to proceed, a shell [3]_ (*linux* and *osx*) or a command prompt, within which you change the directory to your the folder containing the downloaded MRV files::
    
    $ cd /path/to/mrv

On windows::
    
    > cd c:\path\to\mrv 

Now you execute the ``setup.py`` script with the ``install`` command given. The python interpreter used to do that determines the installation location, hence here is where you will decide whether you want to install mrv in ``cpython`` or ``mayapy`` [2]_.

**System Interpreter Linux + OSX**::
    
    $ # Installation using the system interpreter ( Linux and OSX )
    $ sudo python<py-version> setup.py install
    $ # Verify mrv works
    $ mrv<py-version> -c "import mrv.maya.all"
    
**Mayapy Linux**::

    $ # Installation using mayapy on linux
    $ sudo /usr/autodesk/maya<version>/bin/mayapy setup.py install
    $ # Verify mrv works
    $ /usr/autodesk/maya<version>/bin/mrv -c "import mrv.maya.all" 

**Mayapy OSX**::

    $ # Installation using mayapy on osx 
    $ sudo /Applications/Autodesk/maya<version>/Maya.app/Contents/bin/mayapy setup.py install
    $ # Verify mrv works ... yes, the path is real !
    $ /Applications/Autodesk/maya<version>/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/bin/mrv -c "import mrv.maya.all"
    
Replace ``<py-version>`` with ``2.4``, ``2.5`` or ``2.6``, and ``<version>`` with your maya version respectively.

On **windows**, you would instead enter something like this for the **system interpreter installation**::
    
    > # Installation using the system interpreter
    > C:\Python<py-version>\python.exe setup.py install
    > # Verify mrv works
    > c:\Python<py-version>\python.exe c:\Python<py-version\Scripts\mrv -c "import mrv.maya.all"

whereas the following is used for the **windows-mayapy** installation::
    
    > # Installation using mayapy 
    > "C:\Program Files[ (x86)]\Autodesk\Maya<version>\bin\mayapy.exe" setup.py install
    > # Verify it works - the mrv and imrv scripts are not available in mayapy for windows unless you install them manually
    > "C:\Program Files[ (x86)]\Autodesk\Maya<version>\bin\mayapy.exe" -c "mrv.maya.all"
    

Replace ``<py-version>`` with the version of your installed interpreter, usually  ``24`` , ``25`` or ``26``. Alternatively, replace``<version>`` with the maya version you want to use.

To use ``imrv``, some additional work will be needed, please read about it in the :ref:`IMRV installation section <imrv-install-label>`.

===================
Manual Installation
===================
Doing a manual installation would be done for one of the following reasons:

* You have no root/administrator permissions and need to put mrv into a non-standard directory
* You want to setup mrv in a central location on the network to make it usable by multiple clients
* You keep all additional python modules in a central directory to keep them independent of the actual maya or python version used, which works fine for pure python modules.

**Before continuing**, make sure that your toplevel mrv folder, the one which contains the ``setup.py`` script, is named ``mrv``. This is not the case if your extracted it from an archive.

At this point, the :ref:`mrv script <mrv-label>` is already operational, which means that you can use the mrv framework if you start your own scripts through ``mrv``. 

To use MRV as a framework within your python installation, you need to make sure it is in your python path. The previous installation methods essentially put MRV into an existing PYTHONPATH location, but it is also possible to alter the PYTHONPATH by changing the environment variable.  

.. _manual-pythonpath-label:

PYTHONPATH
----------
The PYTHONPATH environment variable contains the path in which python tries to find its modules, similar to the PATH in which executables are searched by the system.

To make it available to a python installation, you can change it in three spots which differ in their area of effect:

1. **Maya.env**

 * Does not require root or administrator permissions
 * Affects only the respective Maya installation *excluding* ``mayapy``, hence you can only use MRV if maya is started in gui or batch mode.
 
 * To make the changes
 
  1. Locate the ``Maya.env`` file, ``<version>`` is the desired maya version:
 
   - ``~/maya/<version>`` (*linux*) 
   - ``~/Library/Preferences/Autodesk/maya/<version>``
   - ``C:\Documents and Settings\<your_account>\My Documents\maya\<version>`` 
  
  2. In your favorite text-editor, add or edit the line as follows:
   
   - On Linux and OSX::
       
       SEP = :
       PYTHONPATH = /path/to/directory/with/mrvroot$SEP/what/was/here/previously
       # i.e. PYTHONPATH = /home/yourname/maya_python_modules$SEP/mnt/other/maya_python_modules
       # where 'maya_python_modules' contains the folder 'mrv'
       
   - On Windows::
       
       PYTHONPATH = X:/path/to/directory/with/mrvroot;Z:/what/was/here/before
       # i.e. PYTHONPATH = C:/maya_python_modules;Z:/maya_python_modules
       # where 'maya_python_modules' contains the folder 'mrv'
   
2. **Shell Profile**

 * Does not require root or administrator permissions
 * Affects *all* python interpreters, including ``maya`` and ``mayapy``  that are launched from within the shell
 
 * To make the changes
 
  - As the shells are different on linux and OSX, it really depends on your actual platform which file you have to alter to obtain a session-independent change. This is why we focus on the **bash** as a very common shell, and change the PYTHONPATH only temporarily. The code presented here would move into your respective shell configuration file, commonly named ``~/.bashrc`` or ``~/.bash_profile``::
      
      $ export PYTHONPATH=/path/to/directory/with/mrvroot:$PYTHONPATH
      $ i.e. export PYTHONPATH=~/maya_python_modules:$PYTHONPATH
      # where 'maya_python_modules' contains the folder 'mrv'

3. **System Wide**

 * The system wide installation requires root permissions on linux. On windows system variables may be changed on per account basis without administrator permissions, but you will need these for changes that affect all accounts on the machine.
 * As these changes usually require higher level permissions, and as people having these usually know how to set environment variables, I will not go into any details here. I ... refuse :P.

Site-Packages
-------------
The ``site-packages`` folder is part of your python installation and is in the PYTHONPATH natively. If you want to put MRV in there, and if you have appropriate permissions to do so, please see the :ref:`auto-installation section <autoinstall-label>`.

.. _imrv-install-label:

****
IMRV
****
IMRV is a tool starting an `interactive python interpreter <http://ipython.scipy.org/moin/>`_ session based on **IPython**, providing full maya python and mrv framework support. It is a great companion to quickly test objects for functionality, read docstrings, and to help building up some confidence for your new development framework as it becomes more approachable.

Please note that the following guide will do its best to explain the installation for the *system's python interpreter* only, as it allows using easy_install. As a bonus, the installation on windows will be discussed in detail as well. Describing the installation for the non-default ``mayapy`` interpreter on all platforms lies beyond the scope of this text though. 

* **Coming from easy_install on windows**

 * Easy install cannot install ipython on windows, instead you have to do it manually using installers which basically copy files into place.
 * `Installing IPython on Windows`_

* **Coming from easy_install linux and osx**

 - Actually you shouldn't be here as easy_install will have retrieved everything required to use ``ipython`` and ``imrv`` on your system.
 
* **Coming from distutils (linux and osx)**

 * Now it is time to use `easy_install`_ as it makes installing ipython as easy. 
 * `Installing IPython on Linux and OSX`_
 
* **Coming from distutils (windows)**

 * `Installing IPython on Windows`_
     
* **Coming from the manual installation (all platforms)**

 * If you have root or administrator permissions for your platform, you will have to use them now.
 * `Installing IPython on Windows`_ 
 * `Installing IPython on Linux and OSX`_
 
=============================
Installing IPython on Windows
=============================
In order to safe you from some trouble, its recommended to watch the `MRV for Windows Installation Guide on Youtube <http://www.youtube.com/user/ByronBates99#p/c/D0F37129CE775529>`_ first, the written documentation only accompanies the video.

To install ipython on windows, you need to download two installers matching your python version.

 * ipython: http://ipython.scipy.org/moin/Download ( works for 32 and 64 bit )
 * pyreadline: https://launchpad.net/pyreadline/+download ( works for 32 and 64 bit )

Install both packages into your respective python installation. To verify the installation, open a command prompt and execute::
    
    > cd x:\Python<py-version>\Scripts
    > ipython.exe
    
If you see colors, it worked, if not, you are most likely to need ``ctypes``, which can be downloaded here: http://sourceforge.net/projects/ctypes/files .

When retrying to start ipython, it should be colored now. Now you can start ipython as follows::
    
    > ..\python.exe imrv [maya-version]
    
The given ``maya-version`` must cause MRV to start the python version that you just installed ipython for, i.e. ``imrv 2010`` will cause ``python26.exe`` to be executed.

===================================
Installing IPython on Linux and OSX
===================================
Using `easy_install`_, the ipython installation couldn't be easier. You need root permissions and an internet connection for the following line to execute::

    $ sudo easy_install-<py-version> ipython
    
    $ # verify it worked
    $ ipython
    
    $ # imrv should work as well
    $ imrv<py-version>

*********
Upgrading
*********
Having a clear upgrade path is important to make updates easy. Software isn't static unless it is dead. 

The best way to do it depends on the way you previously installed MRV: 

* **easy_install**

 * Use the easy_install executable on your system to execute the following in a shell or command prompt::
     
     $ easy_install -U mrv
     > easy_install.exe -U mrv
 
* **(Using) Git**

 * Enter the git repository you cloned previously and execute the following in a shell or windows git bash::
     
     $ git fetch origin
     $ git merge origin/mrv-src
     
* **Archive**

 * Obtain the latest version in a compressed archive from one of the sources :ref:`listed here <install-archive-label>` and extract it into the same place. 
 
.. note:: It is potentially unsafe to do so without prior deletion of the original folder as files may be deleted or renamed in the new archive, causing trouble if 'merged' into an older release's folder.

**********************
Developer Installation
**********************
As a (future) developer, please have a look at the dedicated development section for detailed information on how to :ref:`get MRV (Preview) up and running <development-label>`.

-------

.. [1] The package may be MRV itself or a 'derived' package that uses MRV as framework.
.. [2] Yes, technically 'mayapy' is cpython as well, but I needed a good short name for 'System's Python Interpreter', any suggestions ?
.. [3] A shell on OSX is provided by the terminal application. Enter 'terminal' in spotlight to start it if it is your first time.
.. _easy_install: http://pypi.python.org/pypi/setuptools
