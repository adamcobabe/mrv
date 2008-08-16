"""B{byronimo.maya.nodes}

All classes required to wrap maya nodes in an object oriented manner into python objects
and allow easy handling of them.

These python classes wrap the API representations of their respective nodes - most general 
commands will be natively working on them.

These classes follow the node hierarchy as supplied by the maya api.

Optionally: Attribute access is as easy as using properties like 
  node.translateX
  
@note: it is important not to cache these as the underlying obejcts my change over time.
For long-term storage, use handles instead.

Default maya commands will require them to be used as string variables instead.

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


_thismodule = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.path import Path
env =  __import__( "byronimo.maya.env", globals(), locals(), ['env'] ) 
from types import *


#{ Common
def getMfnDBPath( mfnclsname ):
	"""Generate a path to a database file containing mfn wrapping information"""
	appversion = str( env.getAppVersion( )[0] )
	return Path( __file__ ).p_parent.p_parent / ( "cache/mfndb/"+appversion+"/"+mfnclsname )


def addCustomType( newcls, metaClass=types.MetaClassCreatorNodes, parentClsName=None ):
	""" Add a custom class to this module - it will be handled like a native type  
	@param newcls: new class object if metaclass is None, otherwise string name of the 
	type name to be created by your metaclass
	@param metaClass: custom metaclass to create newcls type string
	@param parentClsName: if metaclass is set, the parentclass name ( of a class existing 
	in the nodeTypeTree ( see /maya/cache/nodeHierarchy_version.html )
	Otherwise, if unset, the parentclassname will be extracted from the newcls object
	@raise KeyError: if the parentClsName does not exist""" 
	newclsname = newcls
	newclsobj = None
	parentname = parentClsName
	if not isinstance( newcls, basestring ):
		newclsname = newcls.__name__
		newclsobj = newcls
		if not parentClsName:
			parentname = newcls.__bases__[0].__name__
	
	# add to hierarchy tree 
	import types
	types._addCustomType( _thismodule, parentname, newclsname, metaclass=metaClass )
	
	# add the class to our module if required
	if newclsobj:
		setattr( _thismodule, newclsname, newclsobj )
	

#}


if 'init_done' not in locals():
	init_done = False
	
if not init_done:
	types.MetaClassCreatorNodes.targetModule = _thismodule			# init metaclass with our module
	import apipatch
	
	types.init_nodehierarchy( )
	types.init_nodeTypeToMfnClsMap( )
	apipatch.init_applyPatches( )
	types.init_wrappers( _thismodule )

	# overwrite dummy node bases with hand-implemented ones
	from base import *
	
	
	
init_done = True
