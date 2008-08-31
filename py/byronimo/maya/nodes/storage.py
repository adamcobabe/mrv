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
	
	# register plugin data in the respective class 
	nodes.registerPluginDataTrackingDict( PyPickleData.kPluginDataId, sys._maya_pyPickleData_trackingDict )
	
	
#} END initialization


import maya.OpenMaya as api
import maya.OpenMayaMPx as mpx

import sys 
import cPickle
import cStringIO
import base64
import struct


#{ Storage Plugin

####################
## Tracking Dict
# assure we only have it once 
if not hasattr( sys, "_maya_pyPickleData_trackingDict" ):
	sys._maya_pyPickleData_trackingDict = {}


############################
## Storage Node
######################
	
def addStorageAttributes( cls, dataType ):
	""" Call this method with your MPxNode derived class to add attributes 
	which can be used by the StorageClass
	@note: this allows your own plugin node to receive storage compatability
	@param dataType: the type of the typed attribute - either MTypeID or MFnData enumeration
	An MTypeID must point to a valid and already registered plugin data.
	@return: attribute api object of its master compound attribute ( it corresponds
	to the class's aData attribute )"""
	tAttr = api.MFnTypedAttribute()
	mAttr = api.MFnMessageAttribute()
	cAttr = api.MFnCompoundAttribute()
	nAttr = api.MFnNumericAttribute()
	
	cls.aData = cAttr.create( "ba_data", "dta" )					# connect to instance transforms
	if True:
		dataID = tAttr.create( "ba_data_id", "id", api.MFnData.kString )
		
		typeInfo = nAttr.create( "ba_data_type", "type", api.MFnNumericData.kInt )	# can be used for additional type info
		
		typedData = tAttr.create( "ba_value", "dval", dataType )
		
		messageData = mAttr.create( "ba_message", "dmsg" )
		mAttr.setArray( True )
		
		
		cAttr.addChild( dataID )
		cAttr.addChild( typeInfo )
		cAttr.addChild( typedData )
		cAttr.addChild( messageData )
		
	# END COMPOUND ATTRIBUTE
	cAttr.setArray( True )
	
	# add attr
	cls.addAttribute( cls.aData )
	return cls.aData
	
	
class StorageMayaNode( mpx.MPxNode ):
	""" Base Class defining common functions for all EntityNodes """
	
	kPluginNodeTypeName = "StorageNode"
	kPluginNodeId = api.MTypeId( 0x0010D134 )
	
	aData = api.MObject()
	
	def __init__( self ):
		return mpx.MPxNode.__init__( self )
		
	@staticmethod
	def creator( ):
		return mpx.asMPxPtr( StorageMayaNode() )
		

def initStorageMayaNodeAttrs( ):
	"""Called to initialize the attributes of the storage node"""
	addStorageAttributes( StorageMayaNode, PyPickleData.kPluginDataId )
	
	

############################
## Custom Data
##################
# Used as custom storage
class PyPickleData( mpx.MPxData ):
	"""Allows to access a pickled data object natively within a maya file. 
	In ascii mode, the pickle will be encoded into string data, in binary mode 
	the cPickle will be taken in its original value.
	
	To get the respective dict-references back, we use a tracking dict as proposed
	by the API Docs
	
	@note: This datatype is copies the data by reference which is why maya always calls 
	the copy constructor, even if you retrieve a const data reference, where this would not be 
	required actually. This is fine for most uses
	@note: as the datatype is reference based, undo is currently not supported ( or does not 
	work as it is expected to do"""
	
	kPluginDataId = api.MTypeId( 0x0010D135 )
	kDataName = "PickleData"
	
	def __init__(self):
		mpx.MPxData.__init__( self )
		self.__data = dict()
		sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] = self.__data

	def __del__( self ):
		"""Remove ourselves from the dictionary to prevent flooding"""
		del( sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] )

	def _writeToStream( self, ostream, asBinary ):
		"""Write our data binary or ascii respectively"""
		sout = cStringIO.StringIO()
		cPickle.dump( self.__data, sout, protocol=2 )
		
		if not asBinary:
			api.MStreamUtils.writeChar( ostream, '"', asBinary )
			
		# assure number of bytes is a multiple of 4
		if asBinary:
			for c in range( sout.tell() % 4 ):
				sout.write( chr( 0 ) )		# 0 bytes 
		
		# NOTE: even binaries will be encoded as this circumvents the 0 byte which terminates the 
		# char byte stream ... can't help it but writing individual bytes 
		# TODO: improve this if it turns out to be too slow 
		api.MStreamUtils.writeCharBuffer( ostream, base64.b64encode( sout.getvalue() ), asBinary )
		
		if not asBinary:
			api.MStreamUtils.writeChar( ostream, '"', asBinary )
	
	def writeBinary(self, out):
		"""cPickle to cStringIO, write in 4 byte packs using ScriptUtil"""
		self._writeToStream( out, True )
	
	def readBinary(self, inStream, numBytesToRead ):
		"""Read in 4 byte packs to cStringIO, unpickle from there
		@note: this method is more complicated than it needs be since asCharPtr does not work !
		It returns a string of a single char ... which is not the same :) !
		@note: YES, this is a CUMBERSOME way to deal with bytes ... terrible, thanks maya :), thanks python"""
		sio = cStringIO.StringIO( )
		scriptutil = api.MScriptUtil( )
		scriptutil.createFromInt( 0 )
		intptr = scriptutil.asIntPtr()
		
		# require multiple of 4 !
		if numBytesToRead % 4 != 0:
			raise AssertionError( "Require multiple of for for number of bytes to be read, but is %i" % numBytesToRead )
		
		bitmask = 255								# mask the lower 8 bit
		shiftlist = [ 0, 8, 16, 24 ]				# used to shift bits by respective values 
		for i in xrange( numBytesToRead  / 4 ):
			api.MStreamUtils.readInt( inStream, intptr, True )
			intval = scriptutil.getInt( intptr )
			
			# convert to chars - endianess should be taken care of by python
			#for shift in [ 24, 16, 8, 0 ]:
			for shift in shiftlist:
				sio.write( chr( ( intval >> shift ) & bitmask ) )
			# END for each byte
		# END for all 4 bytes to read 
		
		self.__data = cPickle.loads( base64.b64decode( sio.getvalue() ) )
		sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] = self.__data

	def writeASCII(self, out):
		"""cPickle to cStringIO, encode with base64 encoding"""
		self._writeToStream( out, False )
		
	
	def readASCII(self, args, lastParsedElement ):
		"""Read base64 element and decode to cStringIO, then unpickle"""
		parsedIndex = api.MScriptUtil.getUint( lastParsedElement )
		base64encodedstring = args.asString( parsedIndex )
		self.__data = cPickle.loads( base64.b64decode( base64encodedstring ) )
		
		parsedIndex += 1
		api.MScriptUtil.setUint(lastParsedElement,parsedIndex)	# proceed the index
		
		# update tracking dict 
		sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] = self.__data
	

			
	def copy( self, other ):
		"""Copy other into self - allows copy pointers as maya copies the data each 
		time you retrieve it"""
		otherdata = sys._maya_pyPickleData_trackingDict[ mpx.asHashable( other ) ]
		self.__data = otherdata
		sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] = self.__data
		
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
	mplugin.deregisterNode( StorageMayaNode.kPluginNodeId )

#} END plugin


#{ Storage Access

class StorageBase( object ):
	"""A storage node contains a set of attributes allowing it to store 
	python data and objects being stored in a pickled format upon file save.
	Additionally you can store connections.
	Nodes used with this interface must be compatible to the following attribute scheme.
	To create that scheme, use L{addStorageAttributes}
	
	
	
	Attribute Setup
	---------------
	-- shortname ( description ) [ data type ] -- 
	dta ( data )[ multi compound ]
	 	id ( data id )[ string ]
		type ( data type ) [ int ]	# for your own use, store bitflags to specify attribute
		dval ( data value ) [ python pickle ]
		dmsg ( data message )[ multi string ]
	
	Configuration
	-------------
	attrprefix: will prefix every attribute during attr set and get - this allows
		several clients to access the same storage base ( on the same node for example )
		It acts like a namespace
	mayaNode: the maya node holding the actual attributes
	
	@note: A byronimo node should derive from this class to allow easy attribute access of its 
	own compatible attributes - its designed for flexiblity 
	@note: attribute accepts on the generic attribute should be set by a plugin node when it 
	creates its attributes
	@todo: should self._node be stored as weakref ?"""
	kValue, kMessage, kStorage = range( 3 )
	__slots__ = ( '_attrprefix', '_node' )
	
	class PyPickleValue( object ):
		"""Wrapper object prividing native access to the wrapped python pickle object
		and to the corresponding value plug, providing utlity methods for easier handling"""
		__slots__ = frozenset( ['_plug', '_pydata', '_isReferenced', '_updateCalled'] )
		
		def __init__( self, valueplug, pythondata ):
			"""value plug contains the plugin data in pythondata"""
			object.__setattr__( self, '_plug', valueplug )
			object.__setattr__( self, '_pydata', pythondata )
			object.__setattr__( self, '_isReferenced', valueplug.getNode( ).isReferenced( ) )
			object.__setattr__( self, '_updateCalled', False )
			
		def __iter__( self ):
			return iter( self._pydata )
		
		def __getattr__( self, attr ):
			return getattr( self._pydata, attr )
			
		def __setattr__( self, attr, val ):
			try:
				object.__setattr__( self, attr, val )
			except AttributeError:
				self._pydata[ attr ] = val 
			
			
		def __getitem__( self, key ):
			return self._pydata[ key ]
			
		def __setitem__( self, key, value ):
			self._pydata[ key ] = value
			if self._isReferenced:
				self.valueChanged()		# assure we make it into the reference , but only if we change
			
		def valueChanged( self ): 
			"""Will be called automatically if the underlying value changed if 
			the node of the underlying plug is referenced
			@note: this method will only be called once during the lifetime of this object if it changes,
			as its enough to trigger reference to write the value if it changes once.
			Getting and setting data is expensive as there is a tracking dict in the background 
			being spawned with internally created copies."""
			if self._updateCalled:
				return 
			self._plug.setMObject( self._plug.asMObject() )
			self._updateCalled = True
		
	
	#{ Overridden Methods 
	def __init__( self, attrprefix = "", mayaNode = None ):
		"""Allows customization of this base to modify its behaviour
		@note: see more information on the input attributes in the class description"""
		# now one can derive from us and override __setattr__
		object.__init__( self )
		self._attrprefix = attrprefix
		self._node = mayaNode
		if not mayaNode:
			if not isinstance( self, nodes.Node ):
				raise TypeError( "StorageNode's derived class must be an instance of type %r if mayaNode is not given" % nodes.Node )
			self._node = self
		# END no maya node given handling
	
	#{ Edit
	def __makePlug( self, dataID ):
		"""Find an empty logical plug index and return the newly created 
		logical plug with given dataID"""
		elementPlug = self._node.dta.getNextLogicalPlug( )
		elementPlug.id.setString( dataID )
		return elementPlug
			
	def makePlug( self, dataID ):
		"""Create a plug that can be retrieved using the given dataID
		@param dataID: string identifier
		@return: the created master plug, containing subplugs dval and dmsg 
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
		StorageBase.kMessage: return message array plug only  
		StorageBase.kValue: return python pickle array plug only
		StorageBase.kStorage: return the storage plug itself containing message and the value plug
		None: return ( picklePlug , messagePlug )
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
			return ( matchedplug.dval, matchedplug.dmsg )
		elif plugType == StorageBase.kStorage:
			return matchedplug
		elif plugType == StorageBase.kValue:
			return matchedplug.dval
		elif plugType == StorageBase.kMessage:
			return matchedplug.dmsg
		else:
			raise TypeError( "Invalid plugType value: %s" % plugType )

	
	def getPythonData( self, dataID, **kwargs ):
		"""@return: PyPickleVal object at the given index ( it can be modified natively )
		@param dataID: id of of the data to retrieve
		@param index: element number of the plug to retrieve, or -1 to get a new plug.
		Plugs will always be created, the given index specifies a logical plug index
		@param **kwargs: all arguments supported by L{getStoragePlug}"""
		storagePlug = self.getStoragePlug( dataID, plugType = StorageBase.kStorage, **kwargs )
		valplug = storagePlug.dval
		return StorageBase.getPythonDataFromPlug( valplug )
		
		
	@staticmethod
	def getPythonDataFromPlug( valplug ):
		"""Exract the python data using the given plug directly
		@param valplug: data value plug containing the plugin data 
		@return: PyPickleData object allowing data access"""
		
		# initialize data if required
		# if the data is null, we do not get a kNullObject, but an exception - fair enough ...
		try:
			plugindata = valplug.asMObject()	 
		except RuntimeError:
			# set value
			plugindataobj = api.MFnPluginData( ).create( PyPickleData.kPluginDataId )
			
			# data gets copied here - re-retrieve data
			valplug._api_setMObject( plugindataobj ) # use original version only - no undo support
			plugindata = nodes.Data( plugindataobj )	
		
		# exstract the data
		#return plugindata.getData()
		return StorageBase.PyPickleValue( valplug, plugindata.getData( ) )
		
	
	#} END query	
	

class StorageNode( nodes.DependNode, StorageBase ):
	"""This node can be used as pythonic ans easy-to-access value container - it could 
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
	
	
	#} END overridden methods 
	

#} 


