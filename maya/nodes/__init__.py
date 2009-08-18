# -*- coding: utf-8 -*-
"""
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
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


bmaya = __import__( "mayarv.maya", globals(), locals(), ['maya'] )
_thismodule = __import__( "mayarv.maya.nodes", globals(), locals(), ['nodes'] )
from mayarv.path import Path
env =  __import__( "mayarv.maya.env", globals(), locals(), ['env'] )
bmayautil = __import__( "mayarv.maya.util", globals(), locals(), ['util'] )
from types import *
from mayarv import init_modules
import sys

if not hasattr( sys,"_dataTypeIdToTrackingDictMap" ):
		sys._dataTypeIdToTrackingDictMap = {}			 # DataTypeId : tracking dict


#{ Common
def getMfnDBPath( mfnclsname ):
	"""Generate a path to a database file containing mfn wrapping information"""
	appversion = str( env.getAppVersion( )[0] )
	return Path( __file__ ).p_parent.p_parent / ( "cache/mfndb/"+ mfnclsname )

def registerPluginDataTrackingDict( dataTypeID, trackingDict ):
	"""Using the given dataTypeID and tracking dict, nodes.MFnPluginData can return
	self pointers belonging to an MPxPluginData instance as returned by MFnPluginData.
	Call this method to register your PluginData information to the byronimo system.
	Afterwards you can extract the self pointer using plug.asMObject.getData()"""
	sys._dataTypeIdToTrackingDictMap[ dataTypeID.id() ] = trackingDict

def addCustomType( newcls, parentClsName=None, **kwargs ):
	""" Add a custom class to this module - it will be handled like a native type
	@param newcls: new class object if metaclass is None, otherwise string name of the
	type name to be created by your metaclass
	@param metaClass: custom metaclass to create newcls type string
	@param parentClsName: if metaclass is set, the parentclass name ( of a class existing
	in the nodeTypeTree ( see /maya/cache/nodeHierarchy.html )
	Otherwise, if unset, the parentclassname will be extracted from the newcls object
	@param force_creation: if True, default False, the class type will be created immediately. This
	can be useful if you wish to use the type for comparison, possibly before it is first being
	queried by the system. The latter case would bind the StandinClass instead of the actual type.
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
	types._addCustomType( _thismodule, parentname, newclsname, **kwargs )

	# add the class to our module if required
	if newclsobj:
		setattr( _thismodule, newclsname, newclsobj )


def addCustomTypeFromFile( hierarchyfile, **kwargs ):
	"""Add a custom classes as defined by the given tab separated file.
	Call addCustomClasses afterwards to register your own base classes to the system
	This will be required to assure your own base classes will be used instead of auto-generated
	stand-in classes
	@param hierarchyfile: Filepath to file modeling the class hierarchy:
	basenode
		derivednode
			subnode
		otherderivednode
	@param force_creation: see L{addCustomType}
	@note: all attributes of L{addCustomType} are supported
	@note: there must be exactly one root type
	@return: iterator providing all class names that have been added"""
	import types
	dagtree = bmaya._dagTreeFromTupleList( bmaya._tupleListFromFile( hierarchyfile ) )
	types._addCustomTypeFromDagtree( _thismodule, dagtree, **kwargs )
	return ( capitalize( nodetype ) for nodetype in dagtree.nodes_iter() )


def addCustomClasses( clsobjlist ):
	"""Add the given classes to the nodes module, making them available to the sytem
	@note: first the class hierarchy need to be updated using addCustomTypeFromFile. This
	must appen before your additional classes are parsed to assure our metaclass creator will not
	be called before it knows the class hierarchy ( and where to actually put your type
	@param clslist: list of class objects whose names are mentioned in the dagtree"""
	# add the classes
	for cls in clsobjlist:
		setattr( _thismodule, cls.__name__, cls )


def forceClassCreation( typeNameList ):
	"""Create the types from standin classes from the given typeName iterable.
	The typenames must be upper case
	@return: List of type instances ( the classes ) that have been created"""
	outclslist = []
	for typename in typeNameList:
		typeCls = getattr( _thismodule, typename )
		if isinstance( typeCls, bmayautil.StandinClass ):
			outclslist.append( typeCls.createCls() )
	# END for each typename
	return outclslist

#}

def init_package( ):
	"""Do the main initialization of this package"""
	import types
	import apipatch
	types.MetaClassCreatorNodes.targetModule = _thismodule			# init metaclass with our module

	types.init_nodehierarchy( )
	types.init_nodeTypeToMfnClsMap( )
	apipatch.init_applyPatches( )
	types.init_wrappers( _thismodule )

	# initialize modules
	init_modules( __file__, "mayarv.maya.nodes" )



if 'init_done' not in locals():
	init_done = False

if not init_done:

	init_package( )


	# overwrite dummy node bases with hand-implemented ones
	from base import *
	from sets import *
	# import additional classes required in this module
	from mayarv.maya.namespace import Namespace


init_done = True
