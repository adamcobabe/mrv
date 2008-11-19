"""B{byronimo.ui.controls}

Contains the most controls like buttons and sliders for more convenient use 

@todo: more documentation

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import base as uibase
import maya.cmds as cmds
import byronimo.util as util
import byronimo.maya.util as mutil
import util as uiutil

class Button( uibase.NamedUI ):
	""" Simple button interface 
	@note: you can only use either the onpress or the onrelease event, both 
	together apparently do not work"""
	_properties_ = ( "label", "align", "recomputeSize", "actionIsSubstitute" ) 
	
	e_onpress = uiutil.CallbackBaseUI.UIEvent( "command", actOnPress=True )
	e_onrelease = uiutil.CallbackBaseUI.UIEvent( "command", actOnPress=False )
