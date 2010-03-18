==================
Configuring MayaRV
==================
The framework can be configured using environment variables which have sensible defaults. A full listing can be found here, but specialized articles will reference them as well where they see it fit.

The notation used is: NAME_OF_VARIABLE (=default value).

 * *MAYARV_UNDO_ENABLED* (=1)
  * If enabled, the undo plugin will be loaded automatically. The undo related decorators will produce a wrapper method dealing with the undo stack automatically. The MPlug.msetX methods will put their changes onto the undo queue as well.
  * If disabled, the plugin will not be loaded automatically. The most undo related decorators will just return the original method, hence no undo-related overhead occurs at runtime. Calling MPlug.msetX will be exactly the same as calling MPlug.setX.
 
 * *MAYARV_PERSISTENCE_ENABLED* (=0)
  * If enabled, the persitance module will initialize itself and load the respective plugin.
  * If disabled, the plugin will not be loaded automatically. Also the plugin specific code will not be generated. In case your plugin or tool relies on the availability of persitence, call ``mayarv.maya.nt.enforcePersistance``.
  
 * *MAYARV_DEBUG_MPLUG_SETX* (=0)
  * If enabled, all calls to MPlug.setX will raise an AssertionError. This helps to assure that you do not accidentally put in bugs related to incorrect undo by using the non-mrv, non-undoable MPlug.setX methods directly ( instead of using the msetX methods instead ). Its adivsed to only turn on this mode for individual runs or if a bug of that kind is suspected, as the performance loss will be tremendous !
  
.. note:: Environment variables are only effective if they are set before the respective mayarv modules are imported, hence it is not possible to alter the behaviour after the import.
