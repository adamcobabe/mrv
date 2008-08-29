"""B{byronimo.nodes.base}

Contains some basic  classes that are required to run the nodes system

All classes defined here can replace classes in the node type hierarachy if the name
matches. This allows to create hand-implemented types.

Implementing an undoable method
-------------------------------
   - decorate with @undoable
   - minimize probability that your operation will fail before creating an operation ( for efficiency )
   - only use operation's doIt() method to apply your changes
   - if the operation's target is already met ( a node you should create already exists ), you have to
   create an empty operation anyway ( otherwise cmds.undo would not undo your command as expected, but 
   the previous one )
   - if you raise, you should not have created an undo operation

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


from byronimo.util import uncapitalize, capitalize, IntKeyGenerator, getPythonIndex, iDagItem, Call
from byronimo.maya.util import StandinClass
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.maya.nodes.types import nodeTypeToMfnClsMap, nodeTypeTree
import maya.OpenMaya as api
import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx
import byronimo.maya.namespace as namespace
undo = __import__( "byronimo.maya.undo", globals(), locals(),[ 'undo' ] )
import sys


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


def makeAbsolutePath( nodename ):
	if not nodename.startswith( '|' ):
		return '|' + nodename
	return nodename
	
def isAbsolutePath( nodename ):
	return nodename.startswith( '|' )

def toDagPath( apiobj ):
	"""Find ONE valid dag path to the given dag api object"""
	dagpath = DagPath( )
	api.MFnDagNode( childNode._apiobj ).getPath( dagpath )
	return dagpath
	

def toApiobj( nodename ):
	""" Convert the given nodename to the respective MObject
	@note: uses unique names only, and will fail if a non-unique path is given
	@note: even dag objects will end up as MObject
	@note: code repeats partly in toApiobjOrDagPath as its supposed to be as fast 
	as possible - this method gets called quite a few times in benchmarks"""
	global _nameToApiSelList
	_nameToApiSelList.clear()
	
	nodename = makeAbsolutePath( nodename )
		
	objnamelist = [ nodename ]
	if nodename.count( '|' ) == 1:	# check dep node too !
		objnamelist.append( nodename[1:] )
	
	for name in objnamelist:
		try:	# DEPEND NODE ?
			_nameToApiSelList.add( name )
		except:
			continue
		else:
			obj = api.MObject()
			_nameToApiSelList.getDependNode( 0, obj )
			
			# if we requested a dg node, but got a dag node, fail 
			if name.count( '|' ) == 0 and obj.hasFn( api.MFn.kDagNode ):
				continue
			
			return obj
		# END if no exception on selectionList.add
	# END for each test-object
	return None



def toApiobjOrDagPath( nodename, dagPlugs=True ):
	"""Convert the given nodename to the respective MObject or DagPath
	@note: we treat "nodename" and "|nodename" as the same objects as they occupy the 
	same namespace - one time a dep node is meant, the other time a dag node. 
	If querying a dag node, the dep node with the same name is not found, although it is in 
	the same freaking namespace ! IMHO this is a big bug !"""
	global _nameToApiSelList
	_nameToApiSelList.clear()
	
	nodename = makeAbsolutePath( nodename )
		
	objnamelist = [ nodename ]
	if nodename.count( '|' ) == 1:	# check dep node too !	 ( "|nodename", but "nodename" could exist too, occupying the "|nodename" name !
		objnamelist.append( nodename[1:] )
	
	for name in objnamelist:
		try:	# DEPEND NODE ?
			_nameToApiSelList.add( name )
		except:
			continue
		else:
			try:
				dag = api.MDagPath()
				_nameToApiSelList.getDagPath( 0 , dag )
				return DagPath( dag )
			except RuntimeError:
				obj = api.MObject()
				_nameToApiSelList.getDependNode( 0, obj )
				
				# if we requested a dg node, but got a dag node, fail 
				if name.count( '|' ) == 0 and obj.hasFn( api.MFn.kDagNode ):
					continue
				
				return obj
		# END if no exception on selectionList.add
	# END for each object name
	return None
	
#} END node mapping 



#{ Base 

def objExists( objectname ):
	"""@return: True if given object exists, false otherwise
	@param objectname: we always use absolute paths to have a unique name
	@note: perfer this method over mel as the API is used directly as we have some special 
	handling to assure we get the right nodes"""
	return toApiobj( objectname ) is not None


def delete( *args ):
	"""Delete the given Node instances
	@note: all deletions will be stored on one undo operation"""
	mod = undo.DGModifier()
	for node in args:
		mod.deleteNode( node._apiobj )
	mod.doIt()

@undoable
def createNode( nodename, nodetype, autocreateNamespace=True, renameOnClash = True ):
	"""Create a new node of nodetype with given nodename
	@param nodename: like "mynode" or "namespace:mynode" or "|parent|mynode" or 
	"|ns1:parent|ns1:ns2:parent|ns3:mynode". The name may contain any amount of parents
	and/or namespaces.
	@note: For reasons of safety, dag nodes must use absolute paths like "|parent|child" - 
	otherwise names might be ambiguous ! This method will assume absolute paths !
	@param nodetype: a nodetype known to maya to be created accordingly
	@param autocreateNamespace: if True, namespaces given in the nodename will be created
	if required
	@param renameOnClash: if True, nameclashes will automatcially be resolved by creating a unique 
	name - this only happens if a dependency node has the same name as a dag node
	@raise RuntimeError: If nodename contains namespaces or parents that may not be created
	@raise NameError: If name of desired node clashes as existing node has different type
	@note: As this method is checking a lot and tries to be smart, its relatively slow ( creates ~400 nodes / s )
	@return: the newly create Node"""
	global _mfndep
	
	if nodename in ( '|', '' ):
		raise RuntimeError( "Cannot create '|' or ''" )
	
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
			
			parentnode = createdNode = newapiobj				# update parent 
		else:
			# create dg node - really have to check for clashes afterwards 
			mod = undo.DGModifier( )
			newapiobj = mod.createNode( actualtype )								# create
			mod.renameNode( newapiobj, dagtoken )									# rename 
			mod.doIt()
			createdNode = newapiobj
		# END (partial) node creation
		
		# CLASHING CHECK ( and name update ) !
		# PROBLEM: if a dep node with name of dagtoken already exists, it will 
		# rename the newly created (sub) node although it is not the same !
		_mfndep.setObject( newapiobj )
		actualname = _mfndep.name()
		if actualname != dagtoken:
			# Is it a renamed node because because a dep node of the same name existed ?
			# Could be that a child of the same name existed too 
			if not renameOnClash:
				msg = "named %s did already exist - cannot create a dag node with same name due to maya limitation" % nodepartialname
				raise NameError( msg )
			else:
				# update the tokens and use the new path
				subpaths[ i ] =  actualname
				nodepartialname = '|'.join( subpaths[ 0 : i+1 ] )
		# END dag token renamed
		
	# END for each partial path
	
	if createdNode is None:
		raise RuntimeError( "Failed to create %s ( %s )" % ( nodename, nodetype ) )
	
	return Node( createdNode )





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
		clsinstance._apidagpath = DagPath( dagpath )	# add some convenience to it 
		
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
			
		
		if not apiobj_or_dagpath or ( isinstance( apiobj_or_dagpath, api.MDagPath ) and not apiobj_or_dagpath.isValid() ) or ( isinstance( apiobj_or_dagpath, api.MObject ) and apiobj_or_dagpath.isNull() ):
			raise ValueError( "object does not exist: %s" % objorname )
		
		# CREATE INSTANCE 
		return _checkedInstanceCreationDagPathSupport( apiobj_or_dagpath, cls, Node ) 


	#{ Overridden Methods 
	def __eq__( self, other ):
		"""compare the nodes according to their api object"""
		otherapiobj = None
		if isinstance( other, basestring ):
			otherapiobj = toApiobj( other )
		else: # assume Node 
			otherapiobj = other._apiobj
			
		return self._apiobj == otherapiobj		# does not appear to work as expected ... 
		
	def __ne__( self, other ):
		return not Node.__eq__( self, other )
	
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
	
	
	
	#{ Edit
	@undoable
	def rename( self, newname, autocreateNamespace=True, renameOnClash = True ):
		"""Rename this node to newname
		@param newname: new name of the node 
		@param autocreateNamespace: if true, namespaces given in newpath will be created automatically, otherwise 
		a RuntimeException will be thrown if a required namespace does not exist
		@param renameOnClash: if true, clashing names will automatically be resolved by adjusting the name 
		@return: renamed node which is the node itself
		@note: for safety reasons, this node is dagnode aware and uses a dag modifier for them !"""
		if '|' in newname:
			raise NameError( "new node names may not contain '|' as in %s" % newname )
		
		# ALREADY EXISTS ? 
		if not renameOnClash:
			exists = False
			
			if isinstance( self, DagNode ):	# dagnode: check existing children under parent 
				testforobject = self.getParent().getFullChildName( newname )	# append our name to the path
				if objExists( testforobject ):
					raise RuntimeError( "Object %s did already exist" % testforobject )                            
			else:
				exists = objExists( newname )	# depnode: check if object exists
				
			if exists:
				raise RuntimeError( "Node named %s did already exist, failed to rename %s" % ( newname, self ) )
		# END not renameOnClash handling  
		
		# NAMESPACE 
		ns = ":".join( newname.split( ":" )[:-1] )
		if not namespace.exists( ns ) and not autocreateNamespace:
			raise RuntimeError( "Cannot rename %s to %s as namespace %s does not exist" % ( self, newname, ns ) )
		ns = namespace.create( ns )		# assure its there 
		
		
		# NOTE: this stupid method will also rename shapes !!!
		# you cannot prevent it, so we have to store the names and rename it lateron !!
		shapenames = shapes = None			# HACK: this is dagnodes only ( only put here for convenience, should be in DagNode ) 
		
		# rename the node
		mod = None
		if isinstance( self, DagNode ):
			mod = undo.DagModifier( )
			shapes = self.getShapes( )
			shapenames = [ s.getBasename( ) for s in shapes  ]
		else:
			mod = undo.DGModifier( )
		mod.renameNode( self._apiobj, newname )
		
		
		# RENAME SHAPES BACK !
		#######################
		# Yeah, of course the rename method renames shapes although this has never been 
		# requested ... its so stupid ... 
		if shapes:
			for shape,shapeorigname in zip( shapes, shapenames ): 	 # could use izip, but this is not about memory here  
				mod.renameNode( shape._apiobj, shapeorigname )
		
		# rename children back
		mod.doIt()
		
		return self
		
	@undoable
	def delete( self ):
		"""Delete this node
		@note: if the undo queue is enabled, the object becomes invalid, but stays alive until it 
		drops off the queue
		@note: if you want to delete many nodes, its more efficient to delete them 
		using the global L{delete} method"""
		mod = undo.DGModifier( )
		mod.deleteNode( self._apiobj )
		mod.doIt()
		
		
	#} END edit
		
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
		attrs = cmds.affects( attribute.getName() , str(self), by=by )
		
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


class DagNode( Entity, iDagItem ):
	""" Implements access to DAG nodes """
	__metaclass__ = nodes.MetaClassCreatorNodes
	_sep = "|"
	kNextPos = api.MFnDagNode.kNextPos
	
	
	#{ Overridden from Object 
	def __eq__( self, other ):
		"""Compare MObjects directly"""
		if not isinstance( other, Node ):
			other = Node( other )
		if isinstance( other, DagNode ):
			return self._apidagpath == other._apidagpath
		return self._apiobj == other._apiobj
		
	def __ne__( self, other ):
		return not DagNode.__eq__( self, other )
		
	def __getitem__( self, index ):
		"""@return: if index >= 0: Node( child )  at index                                   
		if index < 0: Node parent at  -(index+1)( if walking up the hierarchy )
		@note: returned child can be transform or shape, use L{getShapes} or 
		L{getChildTransforms} if you need a quickfilter """
		if index > -1:
			return self.getChild( index )
		else:
			for i,parent in enumerate( self.iterParents( ) ):
				if i == -(index+1):
					return parent
			# END for each parent 
			raise IndexError( "Parent with index %i did not exist for %r" % ( index, self ) )
		
	#}
	
	#{ Hierarchy Modification
	@undoable
	def reparent( self, parentnode, renameOnClash=True, raiseOnInstance=True ):
		""" Change the parent of all nodes ( also instances ) to be located below parentnode
		@param parentnode: Node instance of transform under which this node should be parented to
		if None, node will be reparented under the root ( which only works for transforms )
		@param renameOnClash: resolve nameclashes by automatically renaming the node to make it unique
		@param instanceCheck: if True, this method will raise if you try to reparent an instanced object.
		If false, instanced objects will be merged into the newly created path under parentnode, effectively 
		eliminating all other paths , keeping the newly created one 
		@return : copy of self pointing to the new dag path self                    
		@note: will remove all instance of this object and leave this object at only one path - 
		if this is not what you want, use the addChild method instead as it can properly handle this case  
		@note: this method handles namespaces properly """
		
		if raiseOnInstance and self.getInstanceCount( False ) > 1:
			raise RuntimeError( "%r is instanced - reparent operation would destroy direct instances" % self )
		
		if not renameOnClash and parentnode and self != parentnode:
			# check existing children of parent and raise if same name exists 
			# I think this check must be string based though as we are talking about
			# a possbly different api object with the same name - probably api will be faster
			testforobject = parentnode.getFullChildName( self.getBasename( ) )	# append our name to the path
			if objExists( testforobject ):
				raise RuntimeError( "Object %s did already exist" % testforobject )
		# END rename on clash handling 
			
		thispathobj = self._apidagpath.getApiObj()
		# HAVE TO USE MEL !!
		# As stupid dagmodifier cannot handle instances right ( as it works on MObjects
		mod = None		# create it once we are sure the operation takes place 
		if parentnode:
			if parentnode == self:
				raise RuntimeError( "Cannot parent object %s under itself" % self )
			
			mod = undo.DagModifier( )
			parentpathobj = parentnode._apidagpath.getApiObj()
			mod.reparentNode( thispathobj, parentpathobj )
		else:
			# sanity check
			if isinstance( self, nodes.Shape ):
				raise RuntimeError( "Shape %s cannot be parented under root '|' but needs a transform" % self )
			mod = undo.DagModifier( )
			mod.reparentNode( thispathobj )
		
		mod.doIt()
		
		# UPDATE DAG PATH
		# find it in parentnodes children
		if parentnode:
			for child in parentnode.getChildren():
				if DependNode.__eq__( self, child ):
					return child
		else: # return updated version of ourselves 
			return Node( self._apiobj )
					
		
		raise AssertionError( "Could not find self in children after reparenting" )
		
	@undoable
	def addInstancedChild( self, childNode, position=api.MFnDagNode.kNextPos ):
		"""Add childnode as instanced child to this node
		@note: for more information, see L{addChild}
		@note: its a shortcut to addChild allowing to clearly indicate what is happening"""
		return self.addChild( childNode, position = position, keepExistingParent=True )
	
	@undoable
	def removeChild( self, childNode ):
		"""@remove the given childNode ( being a child of this node ) from our child list, effectively 
		parenting it under world !
		@param childNode: Node to unparent - if it is not one of our children, no change takes place 
		@return: copy of childnode pointing to one valid dag path  
		@note: the child will dangle in unknown space and might have no parents at all !"""
		# print "( %i, %i ) REMOVE CHILD: %r from %r" % ( api.MGlobal.isUndoing(),api.MGlobal.isRedoing(),childNode , self )
		op = undo.GenericOperation( )
		dagfn = api.MFnDagNode( self._apidagpath )
		
		# The method will not fail if the child cannot be found in child list
		# just go ahead
		
		op.addDoit( dagfn.removeChild, childNode._apiobj )
		op.addUndoit( self.addChild, childNode, keepExistingParent=True )	# TODO: add child to position it had 
		op.doIt()
		 
		return Node( childNode._apiobj )	# will attach A new dag path respectively - it will just pick the first one it gets 
		
		
	@undoable
	def addChild( self, childNode, position=api.MFnDagNode.kNextPos, keepExistingParent=False,
				 renameOnClash=True):
		"""Add the given childNode as child to this Node. Allows instancing !
		@param childNode: Node you wish to add
		@param position: the index to which to add the new child, kNextPos will add it as last child.
		It supports python style negative indices 
		@param keepExistingParent: if True, the childNode will be instanced as it will 
		have its previous parent and this one, if False, the previous parent will be removed 
		from the child's parent list
		@param renameOnClash: resolve nameclashes by automatically renaming the node to make it unique
		@return: childNode whose path is pointing to the new child location 
		@note: the keepExistingParent flag is custom implemented as it would remove all existng parentS, 
		not just the one of the path behind the object ( it does not use a path, so it must remove all existing 
		parents unfortunatly ! )"""
		# print "( %i/%i ) ADD CHILD (keep=%i): %r to %r"  % ( api.MGlobal.isUndoing(),api.MGlobal.isRedoing(), keepExistingParent, DependNode( childNode._apiobj ) , self )
		
		# CHILD ALREADY THERE ?
		#########################
		# We do not raise if the user already has what he wants 
		# check if child is already part of our children
		children = None
		# lets speed things up - getting children is expensive
		if isinstance( childNode, nodes.Transform ):
			children = self.getChildTransforms( )
		else:
			children = self.getShapes( )
		
		# compare MObjects
		for exChild in children:
			if DependNode.__eq__( childNode, exChild ):
				return exChild								# exchild has proper dagpath
		del( children )			# release memory 
		
		if not renameOnClash:
			# check existing children of parent and raise if same name exists 
			# I think this check must be string based though as we are talking about
			# a possbly different api object with the same name - probably api will be faster
			testforobject = self.getFullChildName( childNode.getBasename( ) )	# append our name to the path
			if objExists( testforobject ):
				raise RuntimeError( "Object %s did already exist below %r" % ( testforobject , self ) )
		# END rename on clash handling 
			
		
		# ADD CHILD 
		###############
		op = undo.GenericOperationStack( )
		
		pos = position
		if pos != self.kNextPos:
			pos = getPythonIndex( pos, self.getChildCount() )
			
		dagfn = api.MFnDagNode( self._apidagpath )
		docmd = Call( dagfn.addChild, childNode._apiobj, pos, True )
		undocmd = Call( self.removeChild, childNode )
		
		op.addCmd( docmd, undocmd )
		
		
		# EXISTING PARENT HANDLING 
		############################
		# if we do not keep parents, we also have to re-add it to the original parent
		# therefore wer create a dummy do with a real undo
		undocmdCall = None
		parentTransform = None
		if not keepExistingParent:
			# remove from childNode from its current parent ( could be world ! )
			parentTransform = childNode.getParent( )
			validParent = parentTransform
			if not validParent: 
				# get the world, but initialize the function set with an mobject !
				# works for do only in the world case !
				worldobj = api.MFnDagNode( childNode._apidagpath ).parent( 0 )
				validParent = DagNode( worldobj )
			# END if no valid parent 
				
			docmd = Call( validParent.removeChild, childNode )
			# TODO: find current position of item at parent restore it exactly
			undocmdCall = Call( validParent.addChild, childNode, keepExistingParent= True )	# call ourselves
			
			# special case to add items back to world 
			# MGlobal. AddToMOdel does not work, and addChild on the world dag node 
			# does not work either when re-adding the child ( but when removing it !! )
			# clear undocmd as it will not work and bake a mel cmd !
			op.addCmd( docmd, undocmdCall )
		# END if not keep existing parent
		
		op.doIt()
				
		# UPDATE THE DAG PATH OF CHILDNODE
		################################
		# find dag path at the used index
		dagIndex = pos
		if pos == self.kNextPos:
			dagIndex = self.getChildCount() - 1	# last entry as child got added  
		newChildNode = Node( self._apidagpath.getChildPath( dagIndex ) )
		
		# update undo cmd to use the newly created child with the respective dag path 
		undocmd.args = [ newChildNode ]
		
		# ALTER CMD FOR WORLD SPECIAL CASE ?
		######################################
		# alter undo to readd childNode to world using MEL ? - need final name for 
		# this, which is why we delay so much 
		if not keepExistingParent and not parentTransform and undocmdCall is not None:			# have call and child is under world  
			undocmdCall.func = cmds.parent
			undocmdCall.args = [ str( newChildNode ) ]
			undocmdCall.kwargs = { "add":1, "world":1 }

		return newChildNode
		
	@undoable
	def addParent( self, parentnode, position=api.MFnDagNode.kNextPos ):
		"""Adds ourselves as instance to the given parentnode at position 
		@return: self with updated dag path"""
		return parentnode.addChild( self, position = position, keepExistingParent = True )
		
	@undoable
	def setParent( self, parentnode, position=api.MFnDagNode.kNextPos ):
		"""Change the parent of self to parentnode being placed at position 
		@return: self with updated dag path"""
		return parentnode.addChild( self, position = position, keepExistingParent = False )
		
	@undoable
	def removeParent( self, parentnode  ):
		"""Remove ourselves from given parentnode
		@return: None"""
		return parentnode.removeChild( self )
	

	#} END hierarchy modification
		
	#{ Edit
	@undoable
	def delete( self ):
		"""Delete this node - this special version must be 
		@note: if the undo queue is enabled, the object becomes invalid, but stays alive until it 
		drops off the queue
		@note: if you want to delete many nodes, its more efficient to delete them 
		using the global L{delete} method"""
		mod = undo.DagModifier( )
		mod.deleteNode( self._apiobj )
		mod.doIt()
		
	@undoable
	def duplicate( self, newpath, autocreateNamespace=True, renameOnClash=True ):
		"""Duplciate the given node to newpath
		@param newpath: result depends on its format
		   - 'newname' - relative path, the node will be duplicated not chaning its current parent, isInstance must be false
		   - '|parent|newname' - absolut path, the node will be duplicated and reparented under the given path
		@param autocreateNamespace: if true, namespaces given in newpath will be created automatically, otherwise 
		a RuntimeException will be thrown if a required namespace does not exist 
		@param renameOnClash: if true, clashing names will automatically be resolved by adjusting the name
		@return: newly create Node 
		@note: duplicate performance could be improved by checking more before doing work that does not 
		really change the scene, but adds an undo options
		@note: inbetween parents are always required as needed
		@todo: add example for each version of newpath 
		@note: instancing can be realized using the L{addChild} function"""
		# print "-"*5+"DUPLICATE: %r to %s" % (self,newpath)+"-"*5
		thisNodeIsShape = isinstance( self, nodes.Shape )
		
		# Instance Parent Check
		dagtokens = newpath.split( '|' )
		
	
		# need at least transform and shapename if path is absolute
		numtokens = 3				# like "|parent|shape" -> ['','parent', 'shape']
		shouldbe = '|transformname|shapename'
		if not thisNodeIsShape:
			numtokens = 2			# like "|parent" -> ['','parent']
			shouldbe = '|transformname'
			
		if '|' in newpath and ( newpath == '|' or len( dagtokens ) < numtokens ):
			raise NameError( "Duplicate paths should be at least %s, was %s" % ( shouldbe, newpath ) ) 
		# END not instance path checking 
		
		
		# TARGET EXISTS ?
		#####################
		if objExists( newpath ):
			exnode = Node( newpath )
			if not isinstance( exnode, self.__class__ ):
				raise RuntimeError( "Existing object at path %s was of type %s, should be %s" 
									% ( newpath, exnode.__class__.__name__, self.__class__.__name__ ) )
			return 	exnode# return already existing one as it has a compatible type
		# END target exists check
		

		
		# DUPLICATE IT WITH UNDO 
		############################
		# it will always duplicate the transform and return it
		# in case of instances, its the only way we have to get it below an own parent 
		op = undo.GenericOperationStack( )
		doitcmd = Call( api.MFnDagNode( self._apidagpath ).duplicate, False, False )
		undoitcmd = Call( None )												# placeholder, have to change it soon
		duplicate_node_parent = Node( op.addCmdAndCall( doitcmd, undoitcmd ) )		# get the duplicate 
		
		# bake the object to a string for deletion - adjust undocmd
		undoitcmd.func = cmds.delete
		undoitcmd.args = [ str( duplicate_node_parent ) ]
		
		
		# RENAME DUPLICATE CHILDREN
		###########################
		#
		childsourceparent = self.getTransform()			# good if we are transform
		self_shape_duplicated = None		# store Node of duplicates that corresponds to us ( only if self is shape ) 
	
		srcchildren = childsourceparent.getChildrenDeep( )
		destchildren = duplicate_node_parent.getChildrenDeep( )
		
		if len( srcchildren ) != len( destchildren ):
			raise AssertionError( "childcount of source and duplicate must match" )
	
		# this is the only part where we have a one-one relationship between the original children
		# and their copies - store the id the current basename once we encounter it
		selfbasename = self.getBasename()
		for i,targetchild in enumerate( destchildren ):
			#print "RENAME %r to %s" % ( targetchild, srcchildren[ i ].getBasename( ) )
			srcchildbasename = srcchildren[ i ].getBasename( )
			targetchild.rename( srcchildbasename )
			# HACK: we should only check the intermediate children, but actually conisder them deep
			# trying to reduce risk of problem by only setting duplicate_shape_index once
			if not self_shape_duplicated and selfbasename == srcchildbasename:
				self_shape_duplicated = targetchild
					
		# END CHILD RENAME 
		
		dupparent_for_deletion = None			 # might later be filled to delete intermediate transform
			
		# REPARENT 
		###############
		# create requested parents up to transform
		parenttokens = dagtokens[:-1]
		leafobjectname = dagtokens[-1:][0]		# the basename of the dagpath
		
		if len( parenttokens ):			# could be [''] too if newpath = '|newpath'
			parentnodepath = '|'.join( parenttokens )
			parentnode = childsourceparent			# in case we have a relative name 		
			
			# happens on input like "|name"
			if parentnodepath != '': 
				parentnode = createNode( parentnodepath, "transform", 
										renameOnClash=renameOnClash,
										autocreateNamespace=autocreateNamespace )
			# END create parent handling
			
			# get all children
			nodes_for_parenting = duplicate_node_parent.getChildren()
			dupparent_for_deletion = duplicate_node_parent				# remove the parent - its not required anymore
			
			 
			# DO THE REPARENT - parent can be none to indicate parenting below root, okay for transforms
			for reparent_node in nodes_for_parenting:
				reparent_node.reparent( parentnode, renameOnClash=renameOnClash )
			
		# END parent handling 
		
		# FIND RETURN NODE
		######################
		
		final_node = rename_target = duplicate_node_parent		# item that is to be renamed to the final name later
		
		# rename target must be the child matching our name
		if thisNodeIsShape:	# want shape, have transform
			final_node = rename_target = self_shape_duplicated				
		
		
		# DELETE INTERMEDIATE PARENTS 
		################################
		# assure we do not delete ourselves if the target path is a shape below our 
		# own transform 
		selfparent = self.getParent()
		if dupparent_for_deletion and selfparent and dupparent_for_deletion != selfparent:
			#print "DUP FOR DELETION %r" % dupparent_for_deletion
			dupparent_for_deletion.delete()
		
		
		# RENAME TARGET
		# rename the target to match the leaf of the path
		#print "RENAME TARGET BEFORE: %r"  % rename_target
		rename_target.rename( leafobjectname, autocreateNamespace = autocreateNamespace, 
							  renameOnClash=renameOnClash )
		#print "RENAME TARGET AFTER: %r"  % rename_target	
		#print "FinalName: %r ( %r )" % ( final_node, self )
		
		return final_node
		
	#} END edit
	
	#{ Overridden from DependNode
	
	def isValid( self ):
		"""@return: True if the object exists in the scene
		@note: Handles DAG objects correctly that can be instanced, in which case 
		the MObject may be valid , but the respective dag path is not.
		Additionally, if the object is not parented below any object, everything appears 
		to be valid, but the path name is empty """
		return self._apidagpath.isValid() and self._apidagpath.fullPathName() != '' and DependNode.isValid( self )
		
	def getName( self ):
		"""@return: fully qualified ( long ) name of this dag node"""
		return self.getFullPathName( )

	
	#{ Hierarchy Query
	
	def getParentAtIndex( self, index ):
		"""@return: Node of the parent at the given index - non-instanced nodes only have one parent 
		@note: if a node is instanced, it can have L{getParentCount} parents
		@todo: Update dagpath afterwards ! Use dagpaths instead !"""
		sutil = api.MScriptUtil()
		uint = sutil.asUint()
		sutil.setUint( uint , index )
		
		return nodes.Node( api.MFnDagNode( self._apidagpath ).parent( uint ) )
	
	def getTransform( self ):
		"""@return: Node to lowest transform in the path attached to our node
		@note: for shapes this is the parent, for transforms the transform itself"""
		# this should be faster than asking maya for the path and converting 
		# back to a Node
		if isinstance( self, nodes.Transform ):	
			return self	
		return Node( self._apidagpath.getTransform( ) )
	
	def getParent( self ):
		"""@return: Maya node of the parent of this instance or None if this is the root"""
		p = self._apidagpath.getParent( )
		if not p:
			return None
		return nodes.Node( p )
	
	def getChildren( self, predicate = lambda x: True ):
		"""@return: all child nodes below this dag node if predicate returns True for passed Node"""
		childNodes = [ Node( p ) for p in self._apidagpath.getChildren() ]
		return [ p for p in childNodes if predicate( p ) ]

	def getChildrenByType( self, nodeType, predicate = lambda x: True ):
		"""@return: all childnodes below this one matching the given nodeType and the predicate
		@param nodetype: class of the nodeTyoe, like nodes.Transform"""
		childNodes = [ Node( p ) for p in self._apidagpath.getChildren() ]
		return [ p for p in childNodes if isinstance( p, nodeType ) and predicate( p ) ]
		
	def getShapes( self, predicate = lambda x: True ):
		"""@return: all our Shape nodes
		@note: you could use getChildren with a predicate, but this method is more 
		efficient as it uses dagpath functions to filter shapes"""
		shapeNodes = [ Node( s ) for s in self._apidagpath.getShapes() ]	# could use getChildrenByType, but this is faster 
		return [ s for s in shapeNodes if predicate( s ) ]
		
	def getChildTransforms( self, predicate = lambda x: True ):
		"""@return: list of all transform nodes below this one """
		transformNodes = [ Node( s ) for s in self._apidagpath.getTransforms() ] # could use getChildrenByType, but this is faster
		return [ t for t in transformNodes if predicate( t ) ]
		
	def getInstanceNumber( self ):
		"""@return: our instance number
		@note: 0 does not indicate that this object is not instanced - use getInstanceCount instead"""
		return self._apidagpath.getInstanceNumber()
	
	def getInstance( self, instanceNumber ):
		"""@return: Node to the instance identified by instanceNumber
		@param instanceNumber: range( 0, self.getInstanceCount()-1 )"""
		# secure it - could crash if its not an instanced node 
		if self.getInstanceCount( False ) == 1:
			if instanceNumber:
				raise AssertionError( "instanceNumber for non-instanced nodes must be 0, was %i" % instanceNumber )
			return self
			
		allpaths = api.MDagPathArray()
		self.getAllPaths( allpaths )
		return Node( allpaths[ instanceNumber ] )
		
	#} END hierarchy query
	
	
	#{ Iterators 
	def iterInstances( self, excludeSelf = False ):
		"""Get iterator over all ( direct and indirect )instances of this node
		@param excludeSelf: if True, self will not be returned, if False, it will be in 
		the list of items
		@note: Iterating instances is more efficient than querying all instances individually using 
		L{getInstance}
		@todo: add flag to allow iteration of indirect instances as well """
		# prevents crashes if this method is called within a dag instance added callback
		if self.getInstanceCount( True ) == 1:	
			if not excludeSelf:
				yield self
			raise StopIteration
		
		ownNumber = -1
		if excludeSelf:
			ownNumber = self.getInstanceNumber( )
		
		allpaths = api.MDagPathArray()
		self.getAllPaths( allpaths )
		
		# paths are ordered by instance number 
		for i in range( allpaths.length() ):
			# index is NOT instance number ! If transforms are instanced, children increase instance number
			dagpath = allpaths[ i ]
			if dagpath.instanceNumber() != ownNumber:
				yield Node( dagpath )
		# END for each instance 
	
	
	#}
	
	
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
		 
	
class PluginData: 
	"""Wraps plugin data as received by a plug. If plugin's registered their data
	types and tracking dictionaries with this class, the original self pointer 
	can easily be retrieved using this classes interface"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	
		
	def getData( self ):
		"""@return: python data wrapped by this plugin data object
		@note: the python data should be made such that it can be changed using 
		the reference we return - otherwise it will be read-only as it is just a copy !
		@note: the data retrieved by this method cannot be used in plug.setMObject( data ) as it
		is ordinary python data, not an mobject 
		@raise RuntimeError: if the data object's id is unknown to this class"""
		mfn = self._mfncls( self._apiobj )
		datatype = mfn.typeId( )
		try:
			trackingdict = sys._dataTypeIdToTrackingDictMap[ datatype.id() ]
		except KeyError:
			raise RuntimeError( "Datatype %r is not registered to python as plugin data" % datatype )
		else:
			# retrieve the data pointer
			dataptrkey = OpenMayaMPx.asHashable( mfn.data() )
			try:
				return trackingdict[ dataptrkey ]
			except KeyError:
				raise RuntimeError( "Could not find data associated with plugin data pointer at %r" % dataptrkey )
			
			
	
	
#} END base ( classes )

		
#{ Basic Types 

class DagPath( api.MDagPath, iDagItem ):
	"""Wraps a dag path adding some additional convenience functions
	@note: We do NOT patch the actual api type as this would make it unusable to be passed in 
	as reference/pointer type unless its being created by maya itself. Thus we manually convert
	all dagpaths the system returns to our type having some more convenience in it"""
	
	_sep = '|'		#	used by iDagItem
	
	#{ Overridden Methods 
	def __len__( self ):
		"""@return: number of dag nodes in this path"""
		return self.length( )
		
	def __str__( self ):
		"""@return: full path name"""
		return self.getFullPathName()
		
	#}
	
	#{ Query
	
	def getApiObj( self ):
		"""@return: the unwrapped api object this path is referring to"""
		return  api.MDagPath.node( self )
	
	def getNode( self ):
		"""@return: Node of the node we are attached to"""
		return nodes.Node( self.getApiObj( ) )
		
	def getTransform( self ):
		"""@return: path of the lowest transform in the path
		@note: if this is a shape, you would get its parent transform"""
		return api.MDagPath.transform( self )
		
	def getParent( self ):
		"""@return: DagPath to the parent path of the node this path points to"""
		copy = DagPath( self )
		copy.pop( 1 )
		if len( copy ) == 0:		# ignore world !
			return None
		return copy
		 
	def getNumShapes( self ):
		"""@return: return the number of shapes below this dag path"""
		sutil = api.MScriptUtil()
		uintptr = sutil.asUintPtr()
		sutil.setUint( uintptr , 0 )
		
		api.MDagPath.numberOfShapesDirectlyBelow( self, uintptr )
		
		return sutil.getUint( uintptr )
	
	def getChildPath( self, index ):
		"""@return: a dag path pointing to this path's shape with num"""
		copy = DagPath( self )
		copy.push( api.MDagPath.child(self, index ) )
		return copy
		
		
	def getChildren( self , predicate = lambda x: True ):
		"""@return: list of child DagPaths of this path
		@note: this method is part of the iDagItem interface"""
		outPaths = []
		for i in xrange( self.getChildCount() ):
			childpath = self.getChildPath( i )
			if predicate( childpath ):
				outPaths.append( childpath )
		return outPaths
		
		
	#}                                       
	
	#{ Edit Inplace
	def pop( self, num ):
		"""Pop the given number of items off the end of the path
		@return: self
		@note: will change the current path in place"""
		api.MDagPath.pop( self, num )
		return self
	
	def extendToChild( self, num ):
		"""Extend this path to the given child number - can be shape or transform
		@return: self """
		api.MDagPath.extendToShapeDirectlyBelow( self, num )
		return self	
		
	def getChildrenByFn( self, fn, predicate = lambda x: True ):
		"""Get all children below this path supporting the given MFn.type
		@return: paths to all matched paths below this path
		@param fn: member of MFn"""
		isMatch = lambda p: p.getApiObj().hasFn( fn )
		return [ p for p in self.getChildren( predicate = isMatch ) if predicate( p ) ]
		
	def getShapes( self, predicate = lambda x: True ):
		"""Get all shapes below this path
		@return: paths to all shapes below this path
		@param predicate: returns True to include path in result"""
		return self.getChildrenByFn( api.MFn.kShape, predicate=predicate )
	
	def getTransforms( self, predicate = lambda x: True ):
		"""Get all transforms below this path
		@return: paths to all transforms below this path
		@param predicate: returns True to include path in result"""
		return self.getChildrenByFn( api.MFn.kTransform, predicate=predicate )
	#} END edit in place  
	
	
	
	#{ Name Remapping 
	
	getApiType = api.MDagPath.apiType
	node = getNode
	child = getChildPath
	getChildCount = api.MDagPath.childCount 
	transform = getTransform
	getApiType = api.MDagPath.apiType
	getLength = api.MDagPath.length
	numberOfShapesDirectlyBelow = getNumShapes
	getInstanceNumber = api.MDagPath.instanceNumber
	getPathCount = api.MDagPath.pathCount
	getFullPathName = api.MDagPath.fullPathName
	getPartialName = api.MDagPath.partialPathName 
	isNull = lambda self: not api.MDagPath.isValid( self )
	
	
	getInclusiveMatrix = api.MDagPath.inclusiveMatrix
	getInclusiveMatrixInverse = api.MDagPath.inclusiveMatrixInverse
	getExclusiveMatrixInverse = api.MDagPath.exclusiveMatrixInverse
	
	#}


#} END basic types

#{ Foreward created types

class Transform:
	"""Precreated class to allow isinstance checking against their types 
	@note: bases determined by metaclass """
	__metaclass__ = nodes.MetaClassCreatorNodes 

class Shape:
	"""Precreated class to allow isinstance checking against their types
	@note: bases determined by metaclass"""
	__metaclass__ = nodes.MetaClassCreatorNodes


#} END foreward created types

	
