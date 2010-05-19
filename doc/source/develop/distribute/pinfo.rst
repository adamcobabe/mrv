
##########################
Project Information Module
##########################

When preparing a project for distribution, project information such at the project's name and the project's version need to be accessible by various parties, like the documentation compiler or the :ref:`setup script <setup-label>`.

Its of utmost importance to keep this information consistent at all times, hence it is stored at exactly one location, the project information module, called ``info.py``.

The ``info`` module is located in the project's root package.

***************
Module Contents
***************

The ``info`` module contains global variables to which the respective values are assigned directly, such as:

* The name of the project
* The name of the root package, which might be ``yp`` for a project named ``Your Project``
* the **version** of the project in python ``sys.version_info`` compatible format. 
* Author & License Information

For more information, please see the file itself for in-source documentation.

===========
Executables
===========
Worthy of special mention are the executable paths which are important to the :doc:`documentation generator <docs>` as well as the :doc:`distribution system <setup>`.

As MRV aims to be used by derived projects, it will try not make direct calls to its own script executables, but instead reads their location from the module info to give such projects a chance to put in their specialized, but commandline-compatible versions of default :doc:`MRV scripts <../../tools>` as ``makedoc``, ``tmrv`` and ``tmrvr``.

============
Setup KWargs
============
The setup kwargs are passed to the setup routine in the ``makedoc`` script such as in ``setup(**info.setup_kwargs)``, where they eventually wind in the ``Distribution`` instance that drives the distribution process itself.

The MRV version of the setup_kwargs looks quite massive and cluttered, but in-place comments should help to make it decipherable, so it is worth a look if you intend to distribute your project and want to understand more.

The version of the dictionary of the :ref:`Template Project <template-project-label>` is much less frightening though and might be a good first introduction as well.
