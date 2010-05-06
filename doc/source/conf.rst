#############
Configuration
#############
The framework can be configured using environment variables which have sensible defaults. A full listing can be found here, but specialized articles will reference them as well where they see it fit.

*********************
Environment Variables
*********************

The notation used is: NAME_OF_VARIABLE (=default value). Variables with *_STANDALONE_* in their name indicate that the configuration flag will only apply if MRV is run in a standalone python interpreter, like cpython or mayapy, but has no effect if run in maya interactive mode.

* *MRV_UNDO_ENABLED* (=1)
 
 * If enabled, the undo plugin will be loaded automatically. The undo related decorators will produce a wrapper method dealing with the undo stack which adds slight overhead. The ``MPlug.msetX`` methods will put their changes onto the undo queue as well, which requires them to query the value before its being set.
 * If disabled, the plugin will not be loaded automatically. The most undo related decorators will just return the original method, hence no undo-related overhead occurs at runtime. Calling ``MPlug.msetX`` will be exactly the same as calling ``MPlug.setX``.
 
* *MRV_PERSISTENCE_ENABLED* (=0)
 
 * If enabled, the persistence module will initialize itself and load the respective plugin, which enables the ``StorageNode`` to be used.
 * If disabled, the plugin will not be loaded automatically. In case your plugin or tool relies on the availability of persistence, call ``mrv.maya.nt.enforcePersistence``.
  
* *MRV_LOGGING_INI* (=<not set>)
 
 * If set to a path, may include environment variables, the logging module will be initialized according to the information provided in the given configuration file. The file matches the logging configuration file format described in the `python documentation <http://docs.python.org/library/logging.html#configuration>`_.
  
  * An example configuration file can be :download:`downloaded here <download/logging.cfg>`. 
  
* *MRV_APIPATCH_APPLY_GLOBALLY* (=0)
 
 * If enabled, the patched methods of global api classes such as the ones of ``MPlug``, which reside in the 'm' namespace, will additionally be copied into the global namespace. This makes them available as ``MPlug.msetFloat`` as well as ``MPlug.setFloat``, possibly overriding the existing ones. Use this setting if you would like to use MRV's enhancements more naturally when typing, but only if you can control the environment in which your program is running, within a studio for example.
 * If disabled, all patched additions to MayaAPI types provided by MRV will reside in the 'm' namespace unless they only make the type more pythonic in a general and optimized way. This is the default to assure MRV does not interfere with existing setups. All software meant for use in uncontrolled environments must use the 'm' namespace methods, otherwise proper behavior is not guaranteed.
  
* *MRV_DEBUG_MPLUG_SETX* (=0)
 
 * If enabled, all calls to ``MPlug.setX`` will raise an AssertionError. This helps to assure that you do not accidentally put in bugs related to incorrect undo by using the non-mrv, non-undoable ``MPlug.setX`` methods directly, instead of using the ``MPlug.msetX`` methods. Its adivsed to only turn this mode on for individual runs or if a bug of that kind is suspected, as the performance loss will be noticeable !
  
* *MRV_STANDALONE_INIT_OPTIONVARS* (=0)
 
 * If enabled, MRV will assure the  optionVar database is initialized and filled with previously saved values. These are part of the user preferences.
  
* *MRV_STANDALONE_AUTOLOAD_PLUGINS* (=0)
 
 * If enabled, plugins setup for automatic loading at startup will be loaded by MRV.
 * Unless you can assure the computer you run on will auto-load the plugins you require, its good practice not to rely on any plugin to be auto-loaded.
  
* *MRV_STANDALONE_RUN_USER_SETUP* (=0)
 
 * If enabled, MRV runs the userSetup.(mel|py) at the very end of its initialization routine.
  
.. note:: Environment variables are only effective if they are set before the respective mrv modules are imported, hence it is not possible to alter the behavior after the import in most cases.

*******
Logging
*******
MRV's logging facility is based on the `built-in logging module <http://docs.python.org/library/logging.html#>`_ provided by the python runtime.

By default, python's logging is not initialized which is why no messages will be output at all during normal operation.

If you like to change this easily, you may initialize the logging module prior to importing mrv using::
	
	import logging
	# INFO level shows only the most important information, as well as errors and warnings
	logging.basicConfig(level=logging.INFO)
	
MRV's unittest framework automatically initializes the logging module on DEBUG level. 

If you like to have more precise control over the logging, namely which parts of MRV should log, and at which verbosity level and format, please see the *MRV_LOGGING_INI* environment variable above.
