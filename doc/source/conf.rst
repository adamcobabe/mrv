==================
Configuring MRV
==================
The framework can be configured using environment variables which have sensible defaults. A full listing can be found here, but specialized articles will reference them as well where they see it fit.

The notation used is: NAME_OF_VARIABLE (=default value).

 * *MRV_UNDO_ENABLED* (=1)
  * If enabled, the undo plugin will be loaded automatically. The undo related decorators will produce a wrapper method dealing with the undo stack automatically. The MPlug.msetX methods will put their changes onto the undo queue as well.
  * If disabled, the plugin will not be loaded automatically. The most undo related decorators will just return the original method, hence no undo-related overhead occurs at runtime. Calling MPlug.msetX will be exactly the same as calling MPlug.setX.
 
 * *MRV_PERSISTENCE_ENABLED* (=0)
  * If enabled, the persitance module will initialize itself and load the respective plugin.
  * If disabled, the plugin will not be loaded automatically. Also the plugin specific code will not be generated. In case your plugin or tool relies on the availability of persitence, call ``mrv.maya.nt.enforcePersistance``.
  
 * *MRV_APIPATCH_APPLY_GLOBALLY* (=0)
  * If enabled, the patched methods of global api classes such as the ones of MPlug, which resided in the 'm' namespace, will additionally copied into the global namespace. This makes them available as i.e. MPlug.asetFloat as well as MPlug.setFloat, possibly overriding the existing ones. Use this setting if you would like to use MRV's enhancements more naturally when typing, but only if you can control the environment in which your program is running (  within a studio for example ).
  * If disabled, all additions to API types provided by MRV will reside in the 'm' namespace unless they only make the type more pythonic in a general and optimized way. This is the default to assure MRV does not interfere with existing setups. All software meant for use in uncontrolled environments must use the 'm' namespace methods, otherwise proper behavior is not garantueed.
  
 * *MRV_DEBUG_MPLUG_SETX* (=0)
  * If enabled, all calls to MPlug.setX will raise an AssertionError. This helps to assure that you do not accidentally put in bugs related to incorrect undo by using the non-mrv, non-undoable MPlug.setX methods directly ( instead of using the msetX methods instead ). Its adivsed to only turn on this mode for individual runs or if a bug of that kind is suspected, as the performance loss will be tremendous !
  
.. note:: Environment variables are only effective if they are set before the respective mrv modules are imported, hence it is not possible to alter the behaviour after the import.

=======
Logging
=======
TODO: Primer about how to configure the logging of mrv - it is the default logging module. Change the test system to use a file config instead of the basicConfig method
