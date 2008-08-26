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

#{ Initialization 

def __initialize():
	""" Assure our plugin is loaded - called during module intialization"""
	import os
	
	pluginpath = os.path.splitext( __file__ )[0] + ".py"
	if not cmds.pluginInfo( pluginpath, q=1, loaded=1 ):
		cmds.loadPlugin( pluginpath )
	
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
	@note: this allows your own plugin node to receive storage compatability"""
	gAttr = om.MFnGenericAttribute()
	tAttr = om.MFnTypedAttribute()
	mAttr = om.MFnMessageAttribute()
	cAttr = om.MFnCompoundAttribute()
	
	cls.aData = cAttr.create( "ba_data", "dta" )					# connect to instance transforms
	if True:
		dataID = tAttr.create( "ba_datba_id", "id", om.MFnData.kString )
		
		genericData = gAttr.create( "ba_datba_value", "dgen" )
		gAttr.setArray( True )
		
		messageData = mAttr.create( "ba_datba_message", "dmsg" )
		mAttr.setArray( True )
		
		
		cAttr.addChild( dataID )
		cAttr.addChild( genericData )
		cAttr.addChild( messageData )
		
	# END COMPOUND ATTRIBUTE
	cAttr.setArray( True )
	
	# add attr
	cls.addAttribute( cls.aData )
	
	
class StorageNode( mpx.MPxNode ):
	""" Base Class defining common functions for all EntityNodes """
	
	kPluginNodeTypeName = "StorageNode"
	kPluginNodeId = om.MTypeId( 0x0010D134 )
	
	aData = om.MObject()
	
	def __init__( self ):
		mpx.MPxNode.__init__( self )
		
	@staticmethod
	def creator( ):
		return mpx.asMPxPtr( StorageNode() )
		

def initStorageNodeAttrs( ):
	"""Called to initialize the attributes of the storage node"""
	addStorageAttributes( StorageNode )
	
	

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
	mplugin.registerNode( 	StorageNode.kPluginNodeTypeName, StorageNode.kPluginNodeId, StorageNode.creator, initStorageNodeAttrs, mpx.MPxNode.kDependNode )

# Uninitialize script plug-in
def uninitializePlugin( mobject ):
	mplugin = mpx.MFnPlugin( mobject )
	mplugin.deregisterData( PyPickleData.kPluginDataId )
	mplugin.deregisterNode( StorageNode.kPluginNodeTypeName )

#} END plugin


#{ Storage Access



#} 

