# -*- coding: utf-8 -*-
"""B{mayarv.maya.env}

Allows to query the maya environment, like variables, version numbers and system
paths.

@todo: more documentation
@todo: logger !


@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


from maya import cmds


def getAppVersion( ):
	"""
	@return: tuple( float( version ), int( bits ), string( versionString ) ), the
	version will be truncated to *not* include sub-versions
	@note: maya.cmds.about() will crash if called with an external interpreter
	"""
	bits = 32
	if cmds.about( is64=1 ):
		bits = 64

	versionString = cmds.about( v=1 )
	version = versionString.split( ' ' )[0]
	if version.find( '.' ) != -1:
		version = version[0:3]

	# truncate to float
	version = float( version )
	return ( version, bits, versionString )
