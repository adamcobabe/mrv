"""B{byronimo.nodes.base}

Contains some basic  classes that are required to run the nodes system

All classes defined here can replace classes in the node type hierarachy if the name
matches. This allows to create hand-implemented types.

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


from byronimo.util import capitalize, IntKeyGenerator
from byronimo.maya.util import StandinClass
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.maya.nodes.types import nodeTypeToMfnClsMap
import maya.OpenMaya as api


############################
#### Methods 		  	####
##########################

def apiTypeToNodeTypeCls( apiobj ):
	""" Convert the given api object ( MObject ) or type name to the respective python node type class
	@param apiobj: MObject or nodetype name """
	nodeTypeName = apiobj			# assume string
	if not isinstance( apiobj, basestring ):
		fnDepend = api.MFnDependencyNode( apiobj )      
		nodeTypeName = capitalize( fnDepend.typeName( ) )
		 
	try: 
		nodeTypeCls = getattr( nodes, nodeTypeName )
	except AttributeError:
		raise TypeError( "NodeType %s unknown - it cannot be wrapped" % nodeTypeName )
			
	# CHECK FOR STANDIN CLASS 
	###########################
	# The class type could still be a standin - call it  
	if isinstance( nodeTypeCls, StandinClass ):
		nodeTypeCls = nodeTypeCls.createCls( )
	
	return nodeTypeCls
	

def toApiObject( nodeName, dagPlugs=True ):
	""" Get the API MPlug, MObject or (MObject, MComponent) tuple given the name 
	of an existing node, attribute, components selection
	@param dagPlugs: if True, plug result will be a tuple of type (MDagPath, MPlug)
	@note: based on pymel          
	""" 
	sel = api.MSelectionList()
	try:	# DEPEND NODE ?
		sel.add( nodeName )
	except:
		if "." in nodeName :
			# COMPOUND ATTRIBUTES
			#  sometimes the index might be left off somewhere in a compound attribute 
			# (ex 'Nexus.auxiliary.input' instead of 'Nexus.auxiliary[0].input' )
			#  but we can still get a representative plug. this will return the equivalent of 'Nexus.auxiliary[-1].input'
			try:
				buf = nodeName.split('.')
				obj = toApiObject( buf[0] )
				plug = api.MFnDependencyNode(obj).findPlug( buf[-1], False )
				if dagPlugs and isValidMDagPath(obj): 
					return (obj, plug)
				return plug
			except RuntimeError:
				return
	else:
		if "." in nodeName :
			try:
				# Plugs
				plug = api.MPlug()
				sel.getPlug( 0, plug )
				if dagPlugs:
					try:
						# Plugs with DagPaths
						sel.add( nodeName.split('.')[0] )
						dag = api.MDagPath()
						sel.getDagPath( 1, dag )
						#if isValidMDagPath(dag) :
						return (dag, plug)
					except RuntimeError: pass
				return plug
			
			except RuntimeError:
				# Components
				dag = api.MDagPath()
				comp = api.MObject()
				sel.getDagPath( 0, dag, comp )
				#if not isValidMDagPath(dag) :	 return
				return (dag, comp)
		else:
			try:
				# DagPaths
				dag = api.MDagPath()
				sel.getDagPath( 0, dag )
				#if not isValidMDagPath(dag) : return
				return dag
		                                                                                    
			except RuntimeError:
				# Objects
				obj = api.MObject()
				sel.getDependNode( 0, obj )			 
				#if not isValidMObject(obj) : return	 
				return obj
	# END if no exception on selectionList.add  
	return None
	

############################
#### Classes		  	####
##########################

def _checkedClsCreation( apiobj, clsToBeCreated, baseClsObj ):
	"""Utiliy method creating a new class instance according to additional type information
	Its used by __new__ constructors to finalize class creation
	@param apiobj: the MObject or the type name the caller figured out so far
	@param clsToBeCreated: the cls object as passed in to __new__
	@param baseClsObj: the class of the caller containing the __new__ method
	@return: create clsinstance if the proper type ( according to nodeTypeTree"""
	# get the node type class for the api type object
	nodeTypeCls = apiTypeToNodeTypeCls( apiobj )
	
	# NON-MAYA NODE Type 
	# if an explicit type was requested, assure we are at least compatible with 
	# the given cls type - our node type is supposed to be the most specialized one
	# cls is either of the same type as ours, or is a superclass 
	if clsToBeCreated is not baseClsObj and clsToBeCreated is not nodeTypeCls:
		if not issubclass( nodeTypeCls, clsToBeCreated ):
			raise TypeError( "Explicit class %r must be %r or a superclass of it" % ( clsToBeCreated, nodeTypeCls ) )
		else:
			nodeTypeCls = cls						# respect the wish of the client
	# END if explicit class given 
	
	# FININSH INSTANCE 
	clsinstance = super( baseClsObj, cls ).__new__( nodeTypeCls )
	clsinstance._apiobj = apiobj			# set the api object - if this is a string, the called has to take care about it
	return clsinstance

class MayaNode( object ):
	"""Common base for all maya nodes, providing access to the maya internal object 
	representation
	Use this class to directly create a maya node of the required type"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	def __new__ ( cls, *args, **kwargs ):
		"""return the proper class for the given object
		@param args: arg[0] is the node to be wrapped
			- string: wrap the API object with the respective name 
			- MObject
			- MObjectHandle
			- MDagPath
		@todo: assure support for instances of MayaNodes ( as kind of copy constructure ) 
		@note: this area must be optimized for speed"""
		
		if not args:
			raise ValueError( "First argument must specify the node to be wrapped" )
			
		objorname = args[0]
		apiobj = None
		
		# GET AN API OBJECT
		if isinstance( objorname, ( api.MObject, api.MDagPath ) ):
			apiobj = objorname
		elif isinstance( objorname, api.MObjectHandle ):
			apiobj = objorname.object()
		elif isinstance( objorname, basestring ):
			if objorname.find( '.' ) != -1:
				raise ValueError( "%s cannot be handled" % objorname ) 
			apiobj = toApiObject( objorname )
			
			# currently we only handle objects - subclasses will get the type they need
			if isinstance( apiobj, api.MDagPath ):
				apiobj = apiobj.node()
			
		else:
			raise ValueError( "objects of type %s cannot be handled" % type( objorname ) )
			
			
		
		if not apiobj or apiobj.isNull( ):
			raise ValueError( "object could not be handled: %s" % objorname )
		
		
		# get the node type class for the api type object
		nodeTypeCls = apiTypeToNodeTypeCls( apiobj )
		
		
		# NON-MAYA NODE Type 
		# if an explicit type was requested, assure we are at least compatible with 
		# the given cls type - our node type is supposed to be the most specialized one
		# cls is either of the same type as ours, or is a superclass 
		if cls is not MayaNode and cls is not nodeTypeCls:
			if not issubclass( nodeTypeCls, cls ):
				raise TypeError( "Explicit class %r must be %r or a superclass of it" % ( cls, nodeTypeCls ) )
			else:
				nodeTypeCls = cls						# respect the wish of the client
		# END if explicit class given 
		
		
		
		
		# FININSH INSTANCE 
		self = super( MayaNode, cls ).__new__( nodeTypeCls )
		self._apiobj = apiobj
		
		return self
	
	

class DependNode( MayaNode ):
	""" Implements access to dependency nodes 
	
	Depdency Nodes are manipulated using an MObjectHandle which is safest to go with, 
	but consumes more memory too !"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	_mfncls = api.MFnDependencyNode
	
	#{ Overridden Methods 
	def __getattr__( self, attr ):
		"""Interpret attributes not in our dict as attributes on the wrapped node, 
		create a plug for it and add it to our class dict, effectively caching the attribute"""
		depfn = DependNode._mfncls( self._apiobj )
		try:
			plug = self.findPlug( str(attr) )
		except RuntimeError:		# perhaps a base class can handle it
			try: 
				return super( DependNode, self ).__getattr__( self, attr )
			except AttributeError:
				raise AttributeError( "Attribute '%s' does not exist on '%s', neither as function not as attribute" % ( attr, self.name() ) )
		
		self.__dict__[ attr ] = plug
		return plug
	#}
	
	#{ Connections and Attributes 
	def getConnections( self ):
		"""@return: list of L{Plug}s that are connected"""
		cons = api.MPlugArray()
		mfn = DependNode._mfncls( self._apiobj ).getConnections( cons )
		return PlugArray( cons )
		
	#} 
	
	
	#{ Edit Methods 
	
	
	#}
	
class Entity( DependNode ):
	"""Common base for dagnodes and paritions"""
	__metaclass__ = nodes.MetaClassCreatorNodes


class DagNode( Entity ):
	""" Implements access to DAG nodes """
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	
class Plug( api.MPlug ):
	""" Wrap a maya plug to assure we always get MayaNodes ( instead of MObjects )
	By overridding many object methods, the access to plugs becomes very pythonic"""
	# __slots__ = []  	 apparently it will always have a dict 
	
	def fancy( self ):
		return 1
	
	
class Attribute( api.MObject ):
	"""Represents an attribute in general - this is the base class
	Use this general class to create attribute wraps - it will return 
	a class of the respective type """
	def __new__ ( cls, *args, **kwargs ):
		"""return an attribute class of the respective type for given MObject
		@param args: arg[0] is attribute's MObject to be wrapped
		@note: this area must be optimized for speed"""
		
		if not args:
			raise ValueError( "First argument must specify the node to be wrapped" )
			
		attr = args[0]
		apiobj = None
		
		# try which node type fits
		global nodeTypeToMfnClsMap
		attrtypekeys = [ "unitAttribute","typedAttribute","numericAttribute","messageAttribute"
						"matrixAttribute","lightDataAttribute","genericAttribute","enumAttribute",
						"compoundAttribute" ]
						
		for attrtype in attrtypekeys:
			attrmfn = nodeTypeToMfnClsMap[ attrtype ]
			
						
						
		
	
	
class PlugArray( api.MPlugArray ):
	""" Wrap MPlugArray to make it compatible to pythonic contructs
	Also it will always contain Plug objects isntead of MPlugs
	
	This wrapper will handle like python classes and always return Plug objects."""
	
	__len__ = api.MPlugArray.length
	
	def __setitem__ ( self, index, plug ):
		return self.set( plug, index )
	
	def __getitem__ ( self, index ):
		return Plug( api.MPlugArray.__getitem__( self,  index ) )
		
	def __iter__( self ):
		"""@return: iterator object"""
		return IntKeyGenerator( self )
		
		

