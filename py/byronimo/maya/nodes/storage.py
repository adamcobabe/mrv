"""B{byronimo.maya.nodes.storage} generic python style storage 
This module contains a storage interface able to easily handle python-style 
data within maya scenes.


@todo: more documentation, how to use the system 

@newfield revision: Revision
@newfield id: SVN Id """

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import maya.cmds as cmds
import sys 
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), [ 'nodes' ] )

#{ Initialization 

def __initialize():
	""" Assure our plugin is loaded - called during module intialization"""
	import os
	
	pluginpath = os.path.splitext( __file__ )[0] + ".py"
	if not cmds.pluginInfo( pluginpath, q=1, loaded=1 ):
		cmds.loadPlugin( pluginpath )
	
	# We simply inherit from the DependNode, and thus do not need to be added
	# to the custom type system 
	
#} END initialization


#{ Storage Plugin

import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx
import copy


####################
## Tracking Dict
# assure we only have it once 
if not hasattr( sys, "_mayba_pyPickleDatba_trackingDict" ):
	sys._mayba_pyPickleDatba_trackingDict = {}


############################
## Storage Node
######################
	
def addStorageAttributes( cls ):
	""" Call this method with your MPxNode derived class to add attributes 
	which can be used by the StorageClass
	@note: this allows your own plugin node to receive storage compatability
	@return: attribute api object of its master compound attribute ( it corresponds
	to the class's aData attribute )"""
	gAttr = om.MFnGenericAttribute()
	tAttr = om.MFnTypedAttribute()
	mAttr = om.MFnMessageAttribute()
	cAttr = om.MFnCompoundAttribute()
	nAttr = om.MFnNumericAttribute()
	
	cls.aData = cAttr.create( "ba_data", "dta" )					# connect to instance transforms
	if True:
		dataID = tAttr.create( "ba_data_id", "id", om.MFnData.kString )
		
		typeInfo = nAttr.create( "ba_data_type", "type", om.MFnNumericData.kInt )	# can be used for additional type info
		
		genericData = gAttr.create( "ba_value", "dgen" )
		gAttr.setArray( True )
		
		messageData = mAttr.create( "ba_message", "dmsg" )
		mAttr.setArray( True )
		
		
		cAttr.addChild( dataID )
		cAttr.addChild( typeInfo )
		cAttr.addChild( genericData )
		cAttr.addChild( messageData )
		
	# END COMPOUND ATTRIBUTE
	cAttr.setArray( True )
	
	# add attr
	cls.addAttribute( cls.aData )
	return cls.aData
	
	
class StorageMayaNode( mpx.MPxNode ):
	""" Base Class defining common functions for all EntityNodes """
	
	kPluginNodeTypeName = "StorageNode"
	kPluginNodeId = om.MTypeId( 0x0010D134 )
	
	aData = om.MObject()
	
	def __init__( self ):
		return mpx.MPxNode.__init__( self )
		
	@staticmethod
	def creator( ):
		return mpx.asMPxPtr( StorageMayaNode() )
		

def initStorageMayaNodeAttrs( ):
	"""Called to initialize the attributes of the storage node"""
	addStorageAttributes( StorageMayaNode )
	
	

############################
## Custom Data
##################
# Used as custom storage
class PyPickleData( mpx.MPxData ):
	"""Allows to access a pickled data object natively within a maya file. 
	In ascii mode, the pickle will be encoded into string data, in binary mode 
	the cPickle will be taken in its original value.
	
	To get the respective dict-references back, we use a tracking dict as proposed
	by the API Docs"""
	
	kPluginDataId = om.MTypeId( 0x0010D135 )
	kDataName = "PickleData"
	
	def __init__(self):
		mpx.MPxData.__init__( self )
		self.__data = dict()
		sys._mayba_pyPickleDatba_trackingDict[ mpx.asHashable( self ) ] = self.__data

	def readASCII(self, args, lastParsedElement ):
		self.__data = dict()		# start fresh 
		try:
			parsedIndex = om.MScriptUtil.getUint(lastParsedElement)
			# self.__data = args.asDouble( parsedIndex )
			parsedIndex += 1
			om.MScriptUtil.setUint(lastParsedElement,parsedIndex)
			sys._mayba_pyPickleDatba_trackingDict[mpx.asHashable(self)]=self.__data
		except:
			sys.stderr.write("Failed to read ASCII value.")
			raise


	def readBinary(self, inStream, length):
		readParam = om.MScriptUtil()
		readParam.createFromDouble(0.0)
		readPtr = readParam.asDoublePtr()
		om.MStreamUtils.readDouble(inStream, readPtr, True )
		self.__data = om.MScriptUtil.getDouble( readPtr )


	def writeASCII(self, out):
		try:
			om.MStreamUtils.writeDouble(out, self.__data, False)
		except:
			sys.stderr.write("Failed to write ASCII value.")
			raise
			

	def writeBinary(self, out):
		try:
			om.MStreamUtils.writeDouble(out, self.__data, True)
		except:
			sys.stderr.write("Failed to write binary value.")
			raise
			
	def copy( self, other ):
		"""Copy other into self - if the object is not deep-copyable, use a shallow copy"""
		otherdata = sys._mayba_pyPickleDatba_trackingDict[ mpx.asHashable( other ) ]
		try:
			self.__data = copy.deepcopy( otherdata )
		except copy.Error:
			self.__data = otherdata
		
	@staticmethod
	def creator( ):
		return mpx.asMPxPtr( PyPickleData() )
	
	def typeId( self ):
		return self.kPluginDataId

	def name( self ):
		return self.kDataName



# initialize the plug-in
def initializePlugin(mobject):
	mplugin = mpx.MFnPlugin( mobject )
	mplugin.registerData( PyPickleData.kDataName, PyPickleData.kPluginDataId, PyPickleData.creator )
	mplugin.registerNode( 	StorageMayaNode.kPluginNodeTypeName, StorageMayaNode.kPluginNodeId, StorageMayaNode.creator, initStorageMayaNodeAttrs, mpx.MPxNode.kDependNode )

# Uninitialize script plug-in
def uninitializePlugin( mobject ):
	mplugin = mpx.MFnPlugin( mobject )
	mplugin.deregisterData( PyPickleData.kPluginDataId )
	mplugin.deregisterNode( StorageMayaNode.kPluginNodeTypeName )

#} END plugin


#{ Storage Access

class StorageBase( object ):
	"""A storage node contains a set of attributes allowing it to store 
	all kinds of generic information - it servers as a kind of dictionary for connections
	and values.
	Nodes used with this interface must be compatible to the following attribute scheme
	
	Attribute Setup
	---------------
	-- shortname ( description ) [ data type ] -- 
	dta ( data )[ multi compound ]
	 	id ( data id )[ string ]
		type ( data type ) [ int ]	# for your own use, store bitflags to specify attribute
		dgen ( data value ) [ multi generic ]
		dmsg ( data message )[ multi string ]
	
	Configuration
	-------------
	attrprefix: will prefix every attribute during attr set and get - this allows
		several clients to access the same storage base ( on the same node for example )
		It acts like a namespace
	mayaNode: the maya node holding the actual attributes
	
	@note: A byronimo node must derive from this class to allow easy attribute access of its 
	own compatible attributes
	@note: attribute accepts on the generic attribute should be set by a plugin node when it 
	creates its attributes
	@todo: should self._node be stored as weakref ?"""
	kMessage, kGeneric = range( 2 )
	
	#{ Overridden Methods 
	def __init__( self, attrprefix = "", mayaNode = None ):
		"""Allows customization of this base to modify its behaviour
		@note: see more information on the input attributes in the class description"""
		self._attrprefix = attrprefix
		self._node = mayaNode
		if not mayaNode:
			if not isinstance( self, nodes.Node ):
				raise TypeError( "StorageNode's derived class must be an instance of type %r if mayaNode is not given" % nodes.Node )
			self._node = self
		# END no maya node given handling
	
	#{ Edit
	def addAccept( self, dataID, MTypeID=None, MFnData=None, MFnNumericData=None ):
		"""Make the generic data plug behind dataID accept the given datatype 
		@param dataID: string identifying the plug your are looking for
		@param **kwargs: MTypeID, MFnNumericData or MFnData type object identifying the 
		datatye your attribute should accept. Only one of the kwargs may be set 
		@note: call this method as often as required to get the attribute you need
		@note: the plug with dataID will be created as needed
		@return: the changed generic attribute plug """
		genplug = self.getStoragePlug( dataID, autoCreate = True, plugType = self.kGeneric )
		attr = genplug.getAttribute()
		if MTypeID:
			attr.addAccept( MTypeID )
		elif MFnData:
			attr.addDataAccept( MFnData )
		else:
			attr.addNumericDataAccept( MFnNumericData )
		
		return genplug
		
		
	def removeAccept( self, dataID, MTypeID=None, MFnData=None, MFnNumericData=None):
		"""As L{addAccept}, but removes the dataType from the list of accepted types
		@note: will not raise if the plug at dataID"""
		try:
			genplug = self.getStoragePlug( dataID, autoCreate = False, plugType = self.kGeneric )
		except AttributeError:
			return 
			
		attr = genplug.getAttribute()
		if MTypeID:
			attr.removeAccept( MTypeID )
		elif MFnData:
			attr.removeDataAccept( MFnData )
		else:
			attr.removeNumericDataAccept( MFnNumericData )
			
		
		
	def __makePlug( self, dataID ):
		"""Find an empty logical plug index and return the newly created 
		logical plug with given dataID"""
		elementPlug = self._node.dta.getNextLogicalPlug( )
		elementPlug.id.setString( dataID )
		return elementPlug
			
	def makePlug( self, dataID ):
		"""Create a plug that can be retrieved using the given dataID
		@param dataID: string identifier
		@return: the created master plug, containing subplugs dgen and dmsg 
		for generic data and  message connections respectively """
		actualID = self._attrprefix + dataID
		existingPlug = self.findStoragePlug( dataID )
		if existingPlug is not None: 
			return existingPlug
		
		# otherwise create it - find a free logical index - do a proper search
		return self.__makePlug( actualID )
		
	#} END edit
	
	
	#{ Query
	def findStoragePlug( self, dataID ):
		"""@return: compond plug with given dataID or None"""
		actualID = self._attrprefix + dataID
		for compoundplug in self._node.dta:
			if compoundplug.id.asString( ) == actualID: 
				return compoundplug
		# END for each elemnt ( in search for mathching dataID )
		return None
		
	def getStoragePlug( self, dataID, plugType = None, autoCreate=False ):
		"""@return: plug of the given type, either as tuple of two plugs or the plug 
		specified by plugType
		@param dataID: the name of the plug to be returned
		@param plugType: 
		StorageBase.kMessage: return message plug only  
		StorageBase.kGeneric: return generic plug only
		None: return ( genericPlug , messagePlug )
		@param autoCreate: if True, a plug with the given dataID will be created if it does not 
		yet exist
		@raise AttributeError: if a plug with dataID does not exist and default value is None"""
		matchedplug = self.findStoragePlug( dataID )
		if matchedplug is None:
			if autoCreate:
				actualID = self._attrprefix + dataID
				matchedplug = self.__makePlug( actualID ) 
			else:
				raise AttributeError( "Plug with id %s not found on %r" % ( dataID, self._node ) )
		# END matched plug not found handling 
		
		# return the result 
		if plugType is None:
			return ( matchedplug.dgen, matchedplug.dmsg )
		elif plugType == StorageBase.kGeneric:
			return matchedplug.dgen
		elif plugType == StorageBase.kMessage:
			return matchedplug.dmsg
		else:
			raise TypeError( "Invalid plugType value: %s" % plugType )

	#} END query	
	

class StorageNode( nodes.DependNode, StorageBase ):
	"""This node can be used as generic ans easy-to-access value container - it could 
	be connected to your node, and queried for values actually being queried on your node.
	As value container, it can easily be replaced by another one, or keep different sets of information
	@note: the storage node can only use generic attributes and recover them properly during scene reload 
	if the configuration of the generic attributes have been setup properly - they are unique only per 
	node type, not per instance of the node type. 
	Thus it is recommened to use the storage node attribute base on your own custom type that setsup the 
	generic attributes as it requires during plugin load"""
	isNodeTypeTreeMember = False			# means we are not in the typetree ( not required in our case )
	
	#{ Overrriden Methods 
	def __init__( self, *args ):
		"""initialize bases properly"""
		nodes.DependNode.__init__( self, *args )
		StorageBase.__init__( self )
	
	def __getattr__( self, attr ):
		"""Try to find an attribute by data id in our array and return the plug to it
		Otherwise ask the default base node for it
		@note: the plug will be cached once found, so there is no penalty on successive access"""
		
		return super( StorageNode, self ).__getattr__( attr )
	#} END overridden methods 
	

#} 

