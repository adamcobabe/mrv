# -*- coding: utf-8 -*-
"""generic python style storage
This module contains a storage interface able to easily handle python-style
data within maya scenes.


@todo: more documentation, how to use the system


 """

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import mayarv.maya.undo as undo
from mayarv.util import iDuplicatable
import maya.cmds as cmds
nodes = __import__( "mayarv.maya.nodes", globals(), locals(), [ 'nodes' ] )


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
import binascii
import struct
import copy

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
	""" Base Class defining the storage node data interfaces  """

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
		"""Remove ourselves from the dictionary to prevent flooding
		@note: we can be called even if maya is already unloaded or shutting down"""
		if mpx.asHashable is not None:
			del( sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] )
		# call super just to be on the safe side in future, currently it appears
		# not to be required
		try:
			super( PyPickleData, self ).__del__( )
		except AttributeError:
			# Maya 2008 and following do not require this anymore as they
			# do not have a del method implemented apparently
			pass

	def _writeToStream( self, ostream, asBinary ):
		"""Write our data binary or ascii respectively"""
		sout = cStringIO.StringIO()
		try:
			cPickle.dump( self.__data, sout, protocol=2 )
		except cPickle.PicklingError, e:
			sys.__stdout__.write( str( e ) )
			return
		# END pickle error handling

		if not asBinary:
			api.MStreamUtils.writeChar( ostream, '"', asBinary )

		# assure number of bytes is a multiple of 4
		if asBinary:
			for c in range( sout.tell() % 4 ):
				sout.write( chr( 0 ) )		# 0 bytes

		# NOTE: even binaries will be encoded as this circumvents the 0 byte which terminates the
		# char byte stream ... can't help it but writing individual bytes
		# TODO: improve this if it turns out to be too slow
		api.MStreamUtils.writeCharBuffer( ostream, binascii.b2a_base64( sout.getvalue() ).strip(), asBinary )

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

		self.__data = cPickle.loads( binascii.a2b_base64( sio.getvalue() ) )
		sys._maya_pyPickleData_trackingDict[ mpx.asHashable( self ) ] = self.__data

	def writeASCII(self, out):
		"""cPickle to cStringIO, encode with base64 encoding"""
		self._writeToStream( out, False )


	def readASCII(self, args, lastParsedElement ):
		"""Read base64 element and decode to cStringIO, then unpickle"""
		parsedIndex = api.MScriptUtil.getUint( lastParsedElement )
		base64encodedstring = args.asString( parsedIndex )
		self.__data = cPickle.loads( binascii.a2b_base64( base64encodedstring ) )

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

class StorageBase( iDuplicatable ):
	"""A storage node contains a set of attributes allowing it to store
	python data and objects being stored in a pickled format upon file save.
	Additionally you can store connections.
	Nodes used with this interface must be compatible to the following attribute scheme.
	To create that scheme, use L{addStorageAttributes}



	Attribute Setup
	
	-- shortname ( description ) [ data type ] --
	dta ( data )[ multi compound ]
	 	id ( data id )[ string ]
		type ( data type ) [ int ]	# for your own use, store bitflags to specify attribute
		dval ( data value ) [ python pickle ]
		dmsg ( data message )[ multi message ]

	Configuration
	
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
	_partitionIdAttr = "bda_storagePartition"
	__slots__ = ( '_attrprefix', '_node' )

	class PyPickleValue( object ):
		"""Wrapper object prividing native access to the wrapped python pickle object
		and to the corresponding value plug, providing utlity methods for easier handling"""
		__slots__ = ( '_plug', '_pydata', '_isReferenced', '_updateCalled' )

		def __init__( self, valueplug, pythondata ):
			"""value plug contains the plugin data in pythondata"""
			object.__setattr__( self, '_plug', valueplug )
			object.__setattr__( self, '_pydata', pythondata )
			object.__setattr__( self, '_isReferenced', valueplug.getNode( ).isReferenced( ) )
			object.__setattr__( self, '_updateCalled', False )

		def __len__( self ):
			return len( self._pydata )

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
	# END class pypickle value



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

	#} END overridden methods

	#( iDuplicatable
	def createInstance( self, *args, **kwargs ):
		"""Create a new instance with our type"""
		return self.__class__( self._attrprefix, self._node )

	def copyFrom( self, other, *args, **kwargs ):
		"""Copy all values from other to ourselves
		@param shallow: kwargument, if True, default False, only a shallow copy will
		be made. If False, a deep copy will be made
		@note: only does so if the attribute prefixes actually match ( which should be
		the case if we get here, checking for it anyway
		@note: as pickle data always copies by reference to be efficient, we have to explicitly
		create new data to assure we really copy it
		@todo: copy connections to our messages as well, make it an option at least"""
		if self.getAttributePrefix() != other.getAttributePrefix():
			raise AssertionError( "Attribute prefixes between self and other did not match" )

		shallow = kwargs.pop( "shallow", False )
		for dataid in other.getDataIDs():
			othervalplug = other.getStoragePlug( dataid, plugType = self.kValue, autoCreate = False )
			ownvalplug = self.getStoragePlug( dataid, plugType = self.kValue, autoCreate = True )

			self._clearData( ownvalplug )

			if shallow:
				ownvalplug.setMObject( othervalplug.asMObject() )
			else:
				owndict = self.getPythonDataFromPlug( ownvalplug )
				otherdict = other.getPythonDataFromPlug( othervalplug )

				# copy each value
				for key in otherdict:
					val = otherdict[ key ]
					if isinstance( val, iDuplicatable ):
						owndict[ key ] = val.duplicate( )
					else:
						# try deep copy, use shallow copy on error
						try:
							owndict[ key ] = copy.deepcopy( val )
						except copy.Error:
							owndict[ key ] = val
					# END copy operation
				# END for each key to deep copy
			# END shallow/deep copy
		# END for each dataid

	#) END iDuplicatable

	#{ Edit
	def __makePlug( self, dataID ):
		"""Find an empty logical plug index and return the newly created
		logical plug with given dataID"""
		elementPlug = self._node.dta.getNextLogicalPlug( )
		elementPlug['id'].setString( dataID )
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

	def _clearData( self, valueplug ):
		"""Safely clear the data in valueplug - its undoable"""
		# NOTE: took special handling out - it shuld be done in the api-patch
		# for an MPlug
		plugindataobj = api.MFnPluginData( ).create( PyPickleData.kPluginDataId )
		valueplug.setMObject( plugindataobj )



	@undoable
	def clearAllData( self ):
		"""empty the whole storage, creating new python storage data to assure
		nothing is still referenced
		@note: use this method if you want to make sure your node
		is empty after it has been duplicated ( would usually be done in the
		postContructor"""
		for compoundplug in self._node.dta:
			self._clearData( compoundplug['dval'] )
		# END for each element in data compound

	@undoable
	def clearData( self, dataID ):
		"""Clear all data stored in the given dataID"""
		try:
			valueplug = self.getStoragePlug( dataID, plugType=self.kValue, autoCreate = False )
		except AttributeError:
			return
		else:
			self._clearData( valueplug )
		# ELSE attr exists and clearage is required

	#} END edit


	#{ Query Plugs
	def findStoragePlug( self, dataID ):
		"""@return: compond plug with given dataID or None"""
		actualID = self._attrprefix + dataID
		for compoundplug in self._node.dta:
			if compoundplug['id'].asString( ) == actualID:
				return compoundplug
		# END for each elemnt ( in search for mathching dataID )
		return None

	def getDataIDs( self ):
		"""@return: list of all dataids available in the storage node
		@note: respects attribute prefix, and will only see ids with matching prefix.
		The prefix itself is transparent and will not bre returned"""
		outids = list()
		for compoundplug in self._node.dta:
			did = compoundplug['id'].asString( )
			if did and did.startswith( self._attrprefix ):
				outids.append( did[ len( self._attrprefix ) : ] )
			# END if is valid id
		# END for each compound plug element
		return outids

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
		@raise AttributeError: if a plug with dataID does not exist and default value is None
		@raise TypeError: if  plugtype unknown """
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
			return ( matchedplug['dval'], matchedplug['dmsg'] )
		elif plugType == StorageBase.kStorage:
			return matchedplug
		elif plugType == StorageBase.kValue:
			return matchedplug['dval']
		elif plugType == StorageBase.kMessage:
			return matchedplug['dmsg']
		else:
			raise TypeError( "Invalid plugType value: %s" % plugType )

	#} END query plugs


	#{ Query Data
	def getPythonData( self, dataID, **kwargs ):
		"""@return: PyPickleVal object at the given index ( it can be modified natively )
		@param dataID: id of of the data to retrieve
		@param index: element number of the plug to retrieve, or -1 to get a new plug.
		Plugs will always be created, the given index specifies a logical plug index
		@param **kwargs: all arguments supported by L{getStoragePlug}"""
		storagePlug = self.getStoragePlug( dataID, plugType = StorageBase.kStorage, **kwargs )
		valplug = storagePlug['dval']
		return self.getPythonDataFromPlug( valplug )


	@classmethod
	def getPythonDataFromPlug( cls, valplug ):
		"""Exract the python data using the given plug directly
		@param valplug: data value plug containing the plugin data
		@return: PyPickleData object allowing data access"""

		# initialize data if required
		# if the data is null, we do not get a kNullObject, but an exception - fair enough ...
		try:
			plugindata = valplug.asData()
		except RuntimeError:
			# set value
			plugindataobj = api.MFnPluginData( ).create( PyPickleData.kPluginDataId )

			# data gets copied here - re-retrieve data
			valplug._api_setMObject( plugindataobj ) # use original version only - no undo support
			plugindata = nodes.Data( plugindataobj )

		# exstract the data
		#return plugindata.getData()
		return StorageBase.PyPickleValue( valplug, plugindata.getData( ) )

	#} END query Data

	#{ Set Handling
	def getObjectSet( self, dataID, setIndex, autoCreate = True ):
		"""Get an object set identified with setIndex at the given dataId
		@param dataID: id identifying the storage plug on this node
		@param setIndex: logical index at which the set will be connected to our message plug array
		@param autoCreate: if True, a set will be created if it does not yet exist
		@raises ValueError: if a set does not exist at setIndex and autoCreate is False
		@raises: AttributeError: if the plug did not exist ( and autocreate is False )
		@note: method is implicitly undoable if autoCreate is True, this also means that you cannot
		explicitly undo this operation as you do not know if undo has been queued or not
		@note: newly created sets will automatically use partitions if one of the sets does"""
		mp = self.getStoragePlug( dataID, self.kMessage, autoCreate = autoCreate )
		# array plug having our sets
		setplug = mp.getByLogicalIndex( setIndex )
		inputplug = setplug.p_input
		if inputplug.isNull():
			if not autoCreate:
				raise AttributeError( "Set at %s[%i] did not exist on %r" % ( self._attrprefix + dataID, setIndex, self ) )
			su = undo.StartUndo()			# make the following operations atomic
			objset = nodes.createNode( dataID + "Set", "objectSet", forceNewLeaf = True )
			inputplug = objset.message
			inputplug >> setplug

			# hook it up to the partition
			if self.getPartition( dataID ):
				self.setPartition( dataID, True )
		# END create set as needed


		# return actual object set
		return inputplug.getNode()

	@undoable
	def deleteObjectSet( self, dataID, setIndex ):
		"""Delete the object set identified by setIndex
		@note: the method is implicitly undoable
		@note: use this method to delete your sets instead of manual deletion as it will automatically
		remove the managed partition in case the last set is being deleted
		@note: operation is implicitly undoable"""
		try:
			objset = self.getObjectSet( dataID, setIndex, autoCreate = False )
		except ( ValueError, AttributeError ):
			# did not exist, its fine
			return
		else:
			# if this is the last set, remove the partition as well
			#su = undo.StartUndo()			# make the following operations atomic
			if len( self.getSets( dataID ) ) == 1:
				self.setPartition( dataID, False )

			nodes.delete( objset )
		# END obj set handling

	def getSets( self, dataID ):
		"""@return: all object sets stored under the given dataID"""
		mp = self.getStoragePlug( dataID, self.kMessage, autoCreate = False )
		allnodes = [ p.getNode() for p in mp.getInputs() ]
		return [ n for n in allnodes if isinstance( n, nodes.ObjectSet ) ]


	@undoable
	def setPartition( self, dataID, state ):
		"""Make all sets in dataID use a partition or not
		@param dataID: id identifying the storage plug
		@param state: if True, a partition will be used, if False, it will be disabled
		@note: this method makes sure that all sets are hooked up to the partition
		@raises: AttributeError: if the plug did not exist ( and autocreate is False )
		@return: if state is True, the name of the possibly created ( or existing ) partition"""
		sets = self.getSets( dataID )
		partition = self.getPartition( dataID )

		if state:
			if partition is None:
				# create partition
				partition = nodes.createNode( "storagePartition", "partition", forceNewLeaf=True )

				tattr = api.MFnTypedAttribute( )
				attr = tattr.create( self._partitionIdAttr, "pid", api.MFnData.kString )
				partition.addAttribute( attr )
			# END create partition

			# make sure all sets are members of our partition
			partition.addSets( sets )
			return partition
		else:
			if partition:
				# delete partition
				# have to clear partition as, for some reason, or own node will be killed as well !
				partition.clear()
				nodes.delete( partition )
		# END state check


	def getPartition( self, dataID ):
		"""@return: partition Node attached to the sets at dataID or None if state
		is disabled"""
		sets = self.getSets( dataID )

		# get the dominant partition
		partitions = []
		for s in sets:
			partitions.extend( s.getPartitions() )

		for p in partitions:
			if hasattr( p, self._partitionIdAttr ):
				return p
		# END for each partition

		# nothing found, there is no partition yet
		return None




	#} END set handling

	# Query General

	def getStorageNode( self ):
		"""@return: Node actually being used as storage"""
		return self._node

	def setStorageNode( self, node ):
		"""Set ourselves to use the given storage compatible node
		@note: use this if the path of our instance has changed - otherwise
		trying to access functions will fail as the path of our node might be invalid"""
		self._node = node

	def getAttributePrefix( self ):
		"""@return: our attribute prefix
		@note: it is read-only to assure we will never 'forget' about our data"""
		return self._attrprefix

	# END query general


class StorageNode( nodes.DependNode, StorageBase ):
	"""This node can be used as pythonic and easy-to-access value container - it could
	be connected to your node, and queried for values actually being queried on your node.
	As value container, it can easily be replaced by another one, or keep different sets of information
	@note: the storage node can only use generic attributes and recover them properly during scene reload
	if the configuration of the generic attributes have been setup properly - they are unique only per
	node type, not per instance of the node type.
	Thus it is recommened to use the storage node attribute base on your own custom type that setsup the
	generic attributes as it requires during plugin load"""

	#{ Overrriden Methods
	def __init__( self, *args ):
		"""initialize bases properly"""
		nodes.DependNode.__init__( self, *args )
		StorageBase.__init__( self )


	#} END overridden methods


#}


