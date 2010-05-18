
##########################
Project Information Module
##########################

When preparing a project for distribution, project information such at the project's name and the project's version need to be accessible by various parties, like the documentation compiler or the :ref:`setup script <setup-label>`.

Its of utmost importance to keep this information consistent at all times, hence it is stored at exactly one location, the project information module, called ``info.py``.

The ``info`` module is located in the project's root package.

***************
Module Contents
***************

The ``info`` module contains global variables to which the respective values are assigned directly. For more information, please see the file itself for in-source documentation.


============
Setup KWargs
============
TODO: Talk about directory globs, package_data, per-command options, package_modules, and how this is used. There are some special things to bare in mind.
