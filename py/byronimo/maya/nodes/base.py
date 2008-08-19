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


from byronimo.util import uncapitalize, capitalize, IntKeyGenerator, getPythonIndex, iDagItem
from byronimo.maya.util import StandinClass
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.maya.nodes.types import nodeTypeToMfnClsMap, nodeTypeTree
import maya.OpenMaya as api
import maya.cmds as cmds
import byronimo.maya.namespace as namespace
undo = __import__( "byronimo.maya.undo", globals(), locals(),[ 'undo' ] )


############################
#### Cache 			  	####
##########################
# to prevent always creating instances of the same class per call
_nameToApiSelList = api.MSelectionList() 
_mfndep = api.MFnDependencyNode()

############################
#### Methods 		  	####
##########################

#{ Node Mapping 

def nodeTypeToNodeTypeCls( nodeTypeName ):
	""" Convert the given  node type (str) to the respective python node type class
	@param nodeTypeName: the type name you which to have the actual class for  """
	try: 
		nodeTypeCls = getattr( nodes, capitalize( nodeTypeName ) )
	except AttributeError:
		raise TypeError( "NodeType %s unknown - it cannot be wrapped" % nodeTypeName )
			
	# CHECK FOR STANDIN CLASS 
	###########################
	# The class type could still be a standin - call it  
	if isinstance( nodeTypeCls, StandinClass ):
		nodeTypeCls = nodeTypeCls.createCls( )
	
	return nodeTypeCls



def toApiobj( nodeName ):
	""" Convert the given nodename to the respective MObject
	@note: even dag objects will end up as MObject """
	global _nameToApiSelList
	_nameToApiSelList.clear()
	
	try:	# DEPEND NODE ?
		_nameToApiSelList.add( nodeName )
	except:
		return None 
	else:
		obj = api.MObject()
		_nameToApiSelList.getDependNode( 0, obj )
		return obj
		
	# END if no exception on selectionList.add  
	return None



def toApiobjOrDagPath( nodeName, dagPlugs=True ):
	""" Convert the given nodename to the respective MObject or DagPath"""
	global _nameToApiSelList
	_nameToApiSelList.clear()
	
	try:	# DEPEND NODE ?
		_nameToApiSelList.add( nodeName )
	except:
		return None 
	else:
		try:
			dag = api.MDagPath()
			_nameToApiSelList.getDagPath( 0 , dag )
			return DagPath( dag )
		except RuntimeError:
			obj = api.MObject()
			_nameToApiSelList.getDependNode( 0, obj )
			return obj
		
	# END if no exception on selectionList.add  
	return None
	
#} END node mapping 



#{ Base 

def objExists( objectname ):
	"""@return: True if given object exists, false otherwise
	@note: perfer this method over mel as the API is used directly"""
	try:
		Node( objectname )
	except ValueError:
		return False
	else:
		return True


@undoable
def createNode( nodename, nodetype, autocreateNamespace=True, autoRename = True ):
	"""Create a new node of nodetype with given nodename
	@param nodename: like "mynode" or "namespace:mynode" or "|parent|mynode" or 
	"|ns1:parent|ns1:ns2:parent|ns3:mynode". The name may contain any amount of parents
	and/or namespaces.
	@note: For reasons of safety, dag nodes must use absolute paths like "|parent|child" - 
	otherwise names might be ambiguous ! This method will assume absolute paths !
	@param nodetype: a nodetype known to maya to be created accordingly
	@param autocreateNamespace: if True, namespaces given in the nodename will be created
	if required
	@param autoRename: if True, nameclashes will automatcially be resolved by creating a unique 
	name - this only happens if a dependency node has the same name as a dag node
	@raise RuntimeError: If nodename contains namespaces or parents that may not be created
	@raise NameError: If name of desired node clashes as existing node has different type
	@note: As this method is checking a lot and tries to be smart, its relatively slow ( creates ~400 nodes / s )
	@return: the newly create Node"""
	global _mfndep
	if nodename.startswith( '|' ):
		nodename = nodename[1:]
		
	subpaths = nodename.split( '|' )
	
	parentnode = None
	createdNode = None
	lenSubpaths = len( subpaths )
	start_index = 1
	
	# SANITY CHECK ! Must use absolute dag paths 
	if  nodename[0] != '|':
		nodename = "|" + nodename				# update with pipe
		subpaths.insert( 0, '' )
		lenSubpaths += 1
	
	for i in xrange( start_index, lenSubpaths ):						# first token always pipe, need absolute paths
		nodepartialname = '|'.join( subpaths[ 0 : i+1 ] )
		
		# DG NODE exists although DAG node is desired ?
		################################
		# in the first iteration, we also have to check whether a dep node with the 
		# same name exists. If we check for "|nodename" it will not find a dep node with 
		# "nodename" although you can create that dep node by giving "|nodename"
		if i == start_index and lenSubpaths > 2 and objExists( nodepartialname[1:] ):
			# check whether the object is really not a dag node 
			if not isinstance( Node( nodepartialname[1:] ), DagNode ):
				raise NameError( "dag node is requested, but root node name was taken by dependency node: %s" % nodepartialname[1:] ) 
			
		# DAG ITEM EXISTS ?
		######################
		if objExists( nodepartialname ):
			parentnode = createdNode = toApiobj( nodepartialname )	
			
			# could be that the node already existed, but with an incorrect type
			if i == lenSubpaths - 1:				# in the last iteration
				tmp_node = Node( createdNode )
				existing_node_type = uncapitalize( tmp_node.__class__.__name__ )
				if nodetype != existing_node_type:
					# allow more specialized types, but not less specialized ones 
					if nodetype not in nodeTypeTree.parent_iter( existing_node_type ):
						msg = "node %s did already exist, its type %s is incompatible with the requested type %s" % ( nodepartialname, existing_node_type, nodetype )
						raise NameError( msg )
				# END nodetypes different
			# END end of iteration handling 
			
			continue
		# END node item exists 
		
			
		# it does not exist, check the namespace
		dagtoken = '|'.join( subpaths[ i : i+1 ] )
		
		if autocreateNamespace:
			namespace.create( ":".join( dagtoken.split( ":" )[0:-1] ) )	# will resolve to root namespace at least
		
		# see whether we have to create a transform or the actual nodetype 
		actualtype = "transform"
		if i + 1 == lenSubpaths:
			actualtype = nodetype
			
		# create the node - either with or without parent
		# NOTE: usually one could just use a dagModifier for everything, but I do not 
		# trust wrapped inherited methods with default attributes
		#print "DAGTOKEN = %s - PARTIAL NAME = %s - TYPE = %s" % ( dagtoken, nodepartialname, actualtype )
		if parentnode or actualtype == "transform":
			# create dag node
			mod = undo.DagModifier( )
			newapiobj = None
			if parentnode:		# use parent
				newapiobj = mod.createNode( actualtype, parentnode )		# create with parent  
			else:
				newapiobj = mod.createNode( actualtype )							# create 
			
			mod.renameNode( newapiobj, dagtoken )									# rename
			mod.doIt()																# apply op
			
			# PROBLEM: if a dep node with name of dagtoken already exists, it will 
			# rename the newly created (sub) node although it is not the same !
			_mfndep.setObject( newapiobj )
			actualname = _mfndep.name()
			if actualname != dagtoken:
				if not autoRename:
					msg = "DependencyNode named %s did already exist - cannot create a dag node with same name due to maya limitation" % nodepartialname
					raise NameError( msg )
				else:
					# update the tokens and use the new path
					subpaths[ i ] =  actualname
					nodepartialname = '|'.join( subpaths[ 0 : i+1 ] )
				
			parentnode = createdNode = newapiobj				# update parent 
		else:
			# create dg node
			mod = undo.DGModifier( )
			newapiobj = mod.createNode( actualtype )								# create
			mod.renameNode( newapiobj, dagtoken )									# rename 
			mod.doIt()
			createdNode = newapiobj
		# END (partial) node creation
	# END for each partial path
	
	if createdNode is None:
		raise RuntimeError( "Failed to create %s ( %s )" % ( nodename, nodetype ) )
	
	return Node( createdNode )


@undoable
def moveNode( node, newpath, instanced = False , autocreateNamespace=True, autocreateParents=True ):
	"""Move or rename the given node to match newpath
	@param newpath: changes result depending on the name:
	- relative path name ( i.e. 'newname' ) will rename the node in place, keeping the parent
	- absolute path name ( i.e. '|newname' ) will rename to newname and change parents to fit the given path
	@param instanced: if True, the node at newpath will  be an instance of node, otherwise a copy  
	@note: this method handles namespaces properly 
	@note: be aware that children will be copied by default"""
	pass 

#}


def _checkedInstanceCreationDagPathSupport( apiobj_or_dagpath, clsToBeCreated, basecls ):
	"""Same purpose and attribtues as L{_checkedInstanceCreation}, but supports 
	dagPaths as input as well"""
	global _mfndep
	
	apiobj = apiobj_or_dagpath
	dagpath = None
	if isinstance( apiobj, api.MDagPath ):
		apiobj = api.MDagPath.node( apiobj_or_dagpath )
		dagpath = apiobj_or_dagpath
		
	_mfndep.setObject( apiobj )
	nodeTypeName = _mfndep.typeName( )
	clsinstance = _checkedInstanceCreation( apiobj, nodeTypeName, clsToBeCreated, basecls )	
	
	# ASSURE WE HAVE A DAG PATH
	# Dag Objects should always have a dag path even if none was passed in 
	if not dagpath and isinstance( clsinstance, DagNode ):
		dagpath = api.MDagPath( )
		api.MFnDagNode( apiobj ).getPath( dagpath )
	
	if dagpath:
		clsinstance._apidagpath = dagpath
		
	return clsinstance


def _checkedInstanceCreation( apiobj, typeName, clsToBeCreated, basecls ):
	"""Utiliy method creating a new class instance according to additional type information
	Its used by __new__ constructors to finalize class creation
	@param apiobj: the MObject of object to wrap
	@param typeName: the name of the node type to be created
	@param clsToBeCreated: the cls object as passed in to __new__
	@param basecls: the class of the caller containing the __new__ method
	@param addDagPath: if True, the apiobj will is a dag path and will additionally 
	be attached to the instance, if False it is an api object. The reason why this is 
	not kwarg is that its supposed to be as fast as possible - many clients are calling 
	this method, mostly with apiobjs
	@return: create clsinstance if the proper type ( according to nodeTypeTree"""
	# get the node type class for the api type object
	
	nodeTypeCls = nodeTypeToNodeTypeCls( typeName )
	
	# NON-MAYA NODE Type 
	# if an explicit type was requested, assure we are at least compatible with 
	# the given cls type - our node type is supposed to be the most specialized one
	# cls is either of the same type as ours, or is a superclass 
	if clsToBeCreated is not basecls and clsToBeCreated is not nodeTypeCls:
		if not issubclass( nodeTypeCls, clsToBeCreated ):
			raise TypeError( "Explicit class %r must be %r or a superclass of it" % ( clsToBeCreated, nodeTypeCls ) )
		else:
			nodeTypeCls = clsToBeCreated						# respect the wish of the client
	# END if explicit class given 
	
	# FININSH INSTANCE
	clsinstance = super( basecls, clsToBeCreated ).__new__( nodeTypeCls )
	
	clsinstance._apiobj = apiobj				# set the api object - if this is a string, the called has to take care about it
	return clsinstance


def _createInstByPredicate( apiobj, cls, basecls, predicate ):
	"""Allows to wrap objects around MObjects where the actual compatabilty 
	cannot be determined by some nodetypename, but by the function set itself.
	Thus it uses the nodeTypeToMfnClsMap to get mfn cls for testing
	@param cls: the class to be created
	@param basecls: the class where __new__ has actually been called
	@param predicate: returns true if the given nodetypename is valid, and its mfn 
	should be taken for tests
	@return: new class instance, or None if no mfn matched the apiobject"""
	# try which node type fits
	# All attribute instances end with attribute
	# NOTE: the capital case 'A' assure we do not get this base class as option - this would
	# be bad as it is compatible with all classes
	global nodeTypeToMfnClsMap
	attrtypekeys = [ a for a in nodeTypeToMfnClsMap.keys() if predicate( a ) ]
	
	for attrtype in attrtypekeys:
		attrmfncls = nodeTypeToMfnClsMap[ attrtype ]
		try: 
			mfn = attrmfncls( apiobj )
		except RuntimeError: 
			continue
		else:
			newinst = _checkedInstanceCreation( apiobj, attrtype, cls, basecls )		# lookup in node tree 
			return newinst
	# END for each known attr type
	return None
	

############################
#### Classes		  	####
##########################



#{ Base 
class Node( object ):
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
		@todo: assure support for instances of Nodes ( as kind of copy constructure ) 
		@note: this area must be optimized for speed"""
		
		if not args:
			raise ValueError( "First argument must specify the node to be wrapped" )
			
		objorname = args[0]
		apiobj_or_dagpath = None
		
		# GET AN API OBJECT
		if isinstance( objorname, ( api.MObject, api.MDagPath ) ):
			apiobj_or_dagpath = objorname
		elif isinstance( objorname, basestring ):
			if objorname.find( '.' ) != -1:
				raise ValueError( "%s cannot be handled - create a node, then access its attribute like Node('name').attr" % objorname )
			apiobj_or_dagpath = toApiobjOrDagPath( objorname )
		elif isinstance( objorname, api.MObjectHandle ):
			apiobj_or_dagpath = objorname.object()	
		else:
			raise ValueError( "objects of type %s cannot be handled" % type( objorname ) )
			
		
		if not apiobj_or_dagpath or apiobj_or_dagpath.isNull( ):
			raise ValueError( "object does not exist: %s" % objorname )
		
		# CREATE INSTANCE 
		return _checkedInstanceCreationDagPathSupport( apiobj_or_dagpath, cls, Node ) 


	#{ Overridden Methods 
	def __eq__( self, other ):
		"""Compare MObjects directly"""
		if not isinstance( other, Node ):
			other = Node( other )
		return self._apiobj == other._apiobj
	
	#}
	

class DependNode( Node ):
	""" Implements access to dependency nodes 
	
	Depdency Nodes are manipulated using an MObjectHandle which is safest to go with, 
	but consumes more memory too !"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	
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
		
	def __str__( self ):
		"""@return: name of this object"""
		#mfn = DependNode._mfncls( self._apiobj )
		#return mfn.name()
		return self.getName()		
		
	def __repr__( self ):
		"""@return: class call syntax"""
		import traceback
		return '%s("%s")' % ( self.__class__.__name__, DependNode.__str__( self ) )
	#}
	
	#{ Connections and Attributes 
	
	def getConnections( self ):
		"""@return: MPlugArray of connected plugs"""
		cons = api.MPlugArray( )
		mfn = DependNode._mfncls( self._apiobj ).getConnections( cons )
		return cons
		
	def getDependencyInfo( self, attribute, by=True ):
		"""@return: list of attributes that given attribute affects or that the given attribute 
		is affected by 
		if the attribute turns dirty.
		@param attribute: attribute instance or attribute name  
		@param by: if false, affected attributes will be returned, otherwise the attributes affecting this one
		@note: see also L{MPlug.getAffectedByPlugs}
		@note: USING MEL: as api command and mObject array always crashed on me ... don't know :("""
		if isinstance( attribute, basestring ):
			attribute = self.getAttribute( attribute )
			
		attrs = cmds.affects( attribute.getName() , self, by=by )
		
		outattrs = []
		for attr in attrs:
			outattrs.append( self.getAttribute( attr ) )
		return outattrs
		
	def affects( self, attribute ):
		"""@return: list of attributes affected by this one"""
		return self.getDependencyInfo( attribute, by = False )
		
	def affected( self , attribute):
		"""@return: list of attributes affecting this one"""
		return self.getDependencyInfo( attribute, by = True )
			
	#} 
	
	#{ Status 
	def isValid( self ):
		"""@return: True if the object exists in the scene
		@note: objects on the undo queue are NOT valid, but alive"""
		return api.MObjectHandle( self._apiobj ).isValid()
		
	def isAlive( self ):
		"""@return: True if the object exists in memory
		@note: objects on the undo queue are alive, but NOT valid"""
		return api.MObjectHandle( self._apiobj ).isAlive()
	
	
	#} END status 
	
	#{ Edit Methods 
	
	
	#}
	
	
class Entity( DependNode ):
	"""Common base for dagnodes and paritions"""
	__metaclass__ = nodes.MetaClassCreatorNodes


class DagNode( Entity ):
	""" Implements access to DAG nodes """
	__metaclass__ = nodes.MetaClassCreatorNodes
	_dpa = api.MDagPathArray( )
	_dpac = 0
	_dpa.setLength( 2 )
	
	
	#{ Overridden from Object 
	def __eq__( self, other ):
		"""Compare MObjects directly"""
		if not isinstance( other, Node ):
			other = Node( other )
		if isinstance( other, DagNode ):
			return self._apidagpath == other._apidagpath
		return self._apiobj == other._apiobj
	#}
	
	#{ Overridden from DependNode
	def getName( self ):
		"""@return: fully qualified ( long ) name of this dag node"""
		#return self.getDagPath().getFullPathName()
		return self.getFullPathName()
	
	#{ Query 
		
		
	#} END query 
	
	
	#{ Name Remapping 
	name = getName
	#} END name remapping 
	
	
class Attribute( api.MObject ):
	"""Represents an attribute in general - this is the base class
	Use this general class to create attribute wraps - it will return 
	a class of the respective type """
	
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	def __new__ ( cls, *args, **kwargs ):
		"""return an attribute class of the respective type for given MObject
		@param args: arg[0] is attribute's MObject to be wrapped
		@note: this area must be optimized for speed"""
		
		if not args:
			raise ValueError( "First argument must specify the node to be wrapped" )
			
		attributeobj = args[0]
		
		
		newinst = _createInstByPredicate( attributeobj, cls, Attribute, lambda x: x.endswith( "Attribute" ) )
		
		if not newinst:
			mfnattr = api.MFnAttribute( attributeobj )
			raise ValueError( "Attribute %s typed %s was could not be wrapped into any function set" % ( mfnattr.name(), attributeobj.apiTypeStr() ) )
			
		return newinst
		# END for each known attr type
		

class Data( api.MObject ):
	"""Represents an data in general - this is the base class
	Use this general class to create data wrap objects - it will return a class of the respective type """
	
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	def __new__ ( cls, *args, **kwargs ):
		"""return an data class of the respective type for given MObject
		@param args: arg[0] is data's MObject to be wrapped
		@note: this area must be optimized for speed"""
		
		if not args:
			raise ValueError( "First argument must specify the maya node name or api object to be wrapped" )
			
		attributeobj = args[0]
		
		
		newinst = _createInstByPredicate( attributeobj, cls, Data, lambda x: x.endswith( "Data" ) )
		
		if not newinst:
			raise ValueError( "Data api object typed '%s' could not be wrapped into any function set" % attributeobj.apiTypeStr() )
			
		return newinst
		# END for each known attr type
		 
#} END base ( classes )

		
#{ Basic Types 

class DagPath( api.MDagPath, iDagItem ):
	"""Wraps a dag path adding some additional convenience functions
	@note: We do NOT patch the actual api type as this would make it unusable to be passed in 
	as reference/pointer type unless its being created by maya itself. Thus we manually convert
	all dagpaths the system returns to our type having some more convenience in it"""
	
	#{ Overridden Methods 
	def __len__( self ):
		"""@return: number of dag nodes in this path"""
		return self.length( )
		
	def __str__( self ):
		"""@return: full path name"""
		return self.getFullPathName()
		
	#}
	
	#{ Query
	def getNode( self ):
		"""@return: Node of the node we are attached to"""
		return nodes.Node( self.node( ) )
		
	def getTransform( self ):
		"""@return: Node of the lowest transform in the path
		@note: if this is a shape, you would get its parent transform"""
		return nodes.Node( self.transform( ) )
		 
	def getNumShapes( self ):
		"""@return: return the number of shapes below this dag path"""
		sutil = api.MScriptUtil()
		uintptr = sutil.asUintPtr()
		sutil.setUint( uintptr , 0 )
		
		self.numberOfShapesDirectlyBelow( uintptr )
		
		return sutil.getUint( uintptr )
	#}
	
	#{ Edit 
	def pop( self, num ):
		"""Pop the given number of items off the end of the path"""
		sutil = api.MScriptUtil()
		uint = sutil.asUint()
		sutil.setUint( uint , num )
		
		return api.MDagPath.pop( uint )
	
	def extendToShape( self, num ):
		"""Extend this path to the given shape number"""
		sutil = api.MScriptUtil()
		uint = sutil.asUint()
		sutil.setUint( uint , num )
		
		return api.MDagPath.extendToShapeDirectlyBelow( uint )
		
	
	#} END edit 
	
	
	#{ Name Remapping 
	getApiType = api.MDagPath.apiType
	node = getNode 
	transform = getTransform
	getApiType = api.MDagPath.apiType
	getLength = api.MDagPath.length
	numberOfShapesDirectlyBelow = getNumShapes
	getChildCount = api.MDagPath.childCount
	getInstanceNumber = api.MDagPath.instanceNumber
	getPathCount = api.MDagPath.pathCount
	getFullPathName = api.MDagPath.fullPathName
	getPartialName = api.MDagPath.partialPathName 
	isNull = lambda self: not api.MDagPath.isValid( self )
	
	getInclusiveMatrix = api.MDagPath.inclusiveMatrix
	getInclusiveMatrixInverse = api.MDagPath.inclusiveMatrixInverse
	getExclusiveMatrixInverse = api.MDagPath.exclusiveMatrixInverse
	
	#}


#}

	
