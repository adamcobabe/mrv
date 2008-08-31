"""B{byronimo.nodes.types}

Deals with types of objects and mappings between them 

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

nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.maya.util import MetaClassCreator
import byronimo.maya as bmaya
from byronimo.path import Path
from byronimo.util import uncapitalize, PipeSeparatedFile
import maya.OpenMaya as api
import re
import inspect
import new
import UserDict

####################
### CACHES ########
##################
nodeTypeTree = None
nodeTypeToMfnClsMap = {}			# allows to see the most specialized compatible mfn cls for a given node type 



#####################
#### META 		####
##################

class MetaClassCreatorNodes( MetaClassCreator ):
	"""Builds the base hierarchy for the given classname based on our typetree
	@todo: build classes with slots only as members are pretermined"""
	
	nameToTreeMap = set( [ 'FurAttractors', 'FurCurveAttractors', 'FurGlobals', 'FurDescription','FurFeedback' ] ) # special name handling 
	targetModule = None				# must be set in intialization to tell this class where to put newly created classes
	mfnclsattr = '_mfncls'
	mfndbattr = '_mfndb'
	apiobjattr = '_apiobj'
	apipathattr = '_apidagpath'
	getattrorigname = '__getattr_orig'
	
	@staticmethod
	def _readMfnDB( mfnclsname ):
		"""@return: mfn database describing how to handle the functions in the 
		function set described by mfnclsname
		If no explicit information exists, the db will be empty"""
		db = MfnMemberMap( )
		try:
			db.initFromFile( nodes.getMfnDBPath( mfnclsname ) )
		except IOError:
			pass 
		return db
		

	@staticmethod
	def _wrapMfnFunc( mfncls, funcname, funcMutatorDB = None ):
		""" Create a function that makes a Node natively use its associated Maya 
		function set on calls.
		
		The created function will use the api object of the cls instance to initialize
		a function set of mfncls and execute the function in question
		
		The method mutation database allows to adjust the way a method is being wrapped
		@param mfncls: Maya function set class from which to take the functions
		@param funcname: name of the function set function to be wrapped
		@param funcMutatorDB: datastructure:
		{ "mfnfuncname": ( rvalMutatorFunction, newname ) [ , ... ] }
			- mfnfuncname: name of the function in the mfn class
			- rvalMutatorFunction: if not None, will be given the return value of the wrpaped 
			function and should return an altered and possibly wrapped value
			- newname: if not None, a new name for the function mfnfuncname
		
		@raise KeyError: if the given function does not exist in mfncls
		@return:  wrapped function"""
		# check the dict for method name - we do not want to see methods of 
		# base classes - will raise accordingly
		mfndb = funcMutatorDB
		mfnfuncname = funcname		# method could be remapped - if so we need to lookup the real name
		
			
		rvalfunc = None
		# adjust function according to DB
		if funcMutatorDB: 
			entry = funcMutatorDB.get( funcname, None )
			if entry:
				# delete function ?
				if entry.flag == MfnMemberMap.kDelete:
					return None
					
				rvalfunc = entry.rvalfunc
				if entry.newname and entry.newname != '':		# item has been renamed, get original mfn function
					mfnfuncname = mfndb.getMfnFunc( funcname )
				# END name remap handling 
			# END if entry available 
		# END if db available 
		mfnfunc = mfncls.__dict__[ mfnfuncname ]			# will just raise on error 
		newfunc = None
		
		# bound to class, self will be attached on class instantiation
		if rvalfunc:	# wrap rval function around
			# INITIALIZED DAG NODES WITH DAG PATH !
			if mfncls is api.MFnDagNode:			# yes, we duplicate code here to keep it fast !!
				def wrapMfnFunc( self, *args, **kwargs ):
					mfninst = mfncls( self._apidagpath )
					return rvalfunc( getattr( mfninst, mfnfuncname )( *args, **kwargs ) )
				newfunc = wrapMfnFunc
			else:
				def wrapMfnFunc( self, *args, **kwargs ):
					mfninst = mfncls( self._apiobj )
					return rvalfunc( getattr( mfninst, mfnfuncname )( *args, **kwargs ) )
				newfunc = wrapMfnFunc
		else:
			if mfncls is api.MFnDagNode:			# yes, we duplicate code here to keep it fast !!
				def wrapMfnFunc( self, *args, **kwargs ):
					mfninst = mfncls( self._apidagpath )
					return getattr( mfninst, mfnfuncname )( *args, **kwargs )
				newfunc = wrapMfnFunc
			else:
				def wrapMfnFunc( self, *args, **kwargs ):
					mfninst = mfncls( self._apiobj )
					return getattr( mfninst, mfnfuncname )( *args, **kwargs )
				newfunc = wrapMfnFunc
			
		newfunc.__name__ = funcname			# rename the method 
		return newfunc

	
	@classmethod
	def _wrapLazyGetAttr( thiscls, newcls ):
		""" Attach the lazy getattr wrapper to newcls """
		# keep the original getattr 
		if hasattr( newcls, '__getattr__' ):
			getattrorig =  newcls.__dict__.get( '__getattr__', None )
			if getattrorig:
				getattrorig.__name__ = thiscls.getattrorigname
				setattr( newcls, thiscls.getattrorigname, getattrorig )
		
		# CREATE GET ATTR CUSTOM FUNC
		# called if the given attribute is not available in class 
		def meta_getattr_lazy( self, attr ):
			actualcls = None										# the class finally used to store located functions 
			
			# MFN ATTRTIBUTE HANDLING
			############################
			# check all bases for and their mfncls for a suitable function
			newclsfunc = newinstfunc = None							# try to fill these
			for basecls in newcls.mro():
				if not hasattr( basecls, thiscls.mfnclsattr ):			# could be object too or user defined cls
					continue
				
				mfncls = getattr( basecls, thiscls.mfnclsattr )
				if not mfncls:
					continue 
					
				mfndb = None
				
				# GET MFNDB allowing automated method mutations
				if not hasattr( basecls, thiscls.mfndbattr ):
					if mfncls :
						mfndb = thiscls._readMfnDB( mfncls.__name__ )
					setattr( basecls, thiscls.mfndbattr, mfndb )
				else:
					mfndb = getattr( basecls,thiscls.mfndbattr )
				# END mfndb handling 
				
				# get function as well as its possibly changed name 
				try:
					newclsfunc = thiscls._wrapMfnFunc( mfncls, attr, funcMutatorDB=mfndb )
					if not newclsfunc: # Function %s has been deleted - ignore
						continue 
				except KeyError:  		# function not available in this mfn - ignore
					continue 
				newinstfunc = new.instancemethod( newclsfunc, self, basecls )	# create the respective instance method !
				actualcls = basecls
				break					# stop here - we found it 
			# END for each basecls ( searching for mfn func )
			
			# STORE MFN FUNC ( if available )
			# store the new function on instance level !
			# ... and on class level
			if newclsfunc:
				# assure we do not call overwridden functions 
				object.__setattr__( self, attr, newinstfunc )
				type.__setattr__( actualcls, attr, newclsfunc )		# setattr would do too, but its more dramatic this way :)
				return newinstfunc
			
			
			# ORIGINAL ATTRIBUTE HANDLING
			###############################
			# still no funcion ? Continue with non-mfn search routine )
			# try to find orignal getattrs in our base classes - if we have overwritten 
			# them we find them under a backup attribute, otherwise we check the name of the 
			# original method for our lazy tag ( we never want to call our own counterpart on a 
			# base class  
			getattrorigfunc = None
			for basecls in newcls.mro():
				if hasattr( basecls, thiscls.getattrorigname ):
					getattrorigfunc = getattr( basecls, thiscls.getattrorigname )
					break
				# END orig getattr method check
					
				# check if the getattr function itself is us or not 
				if hasattr( basecls, '__getattr__' ):
					getattrfunc = getattr( basecls, '__getattr__' )
					if getattrfunc.func_name != "meta_getattr_lazy":
						getattrorigfunc = getattrfunc
						break
				# END default getattr method check
			# END for each base ( searching for getattr_orig or nonoverwritten getattr )
			
			if not getattrorigfunc:
				raise AttributeError( "Could not find mfn function for attribute '%s'" % attr )
				
			# pass on the call - if this method produces an output, its responsible for caching 
			# it in the isntance dict 
			return getattrorigfunc( self, attr )
			# EMD orig getattr handling 
			
			
				
		# END getattr_lazy func definition 		
		
		# STORE LAZY GETATTR 
		#meta_getattr_lazy.__name__ = "__getattr__"	# lets keep the original method, we us it for 
		# identification !
		setattr( newcls, "__getattr__", meta_getattr_lazy )
	
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global nodeTypeTree
		global nodeTypeToMfnClsMap
		
		# will be used later 
		def func_nameToTree( name ):
			if name in metacls.nameToTreeMap:
				return name
			return uncapitalize( name )
		
		# ATTACH MFNCLS
		#################
		# ask our NodeType to MfnSet database and attach it to the cls dict
		# ( if not yet there ). By convention, there is only one mfn per class
		mfncls = None
		if not clsdict.has_key( metacls.mfnclsattr ):
			treeNodeTypeName = func_nameToTree( name )
			if nodeTypeToMfnClsMap.has_key( treeNodeTypeName ):
				mfncls = nodeTypeToMfnClsMap[ treeNodeTypeName ]
				clsdict[ metacls.mfnclsattr ] = mfncls
		else:
			mfncls = clsdict[ metacls.mfnclsattr ]
			
		clsdict[ metacls.mfnclsattr ] = mfncls			# we have at least a None mfn
		clsdict[ metacls.apiobjattr ] = None			# always have an api obj
		
		
		# SETUP slots - add common members
		# NOTE: does not appear to have any effect :(
		
		# CREATE CLS
		#################
		newcls = super( MetaClassCreatorNodes, metacls ).__new__( nodeTypeTree, metacls.targetModule, 
																metacls, name, bases, clsdict, 
																nameToTreeFunc = func_nameToTree )
				
				
		# LAZY MFN WRAPPING
		#####################
		# Functions from mfn should be wrapped on demand to the respective classes as they 
		# should be generated only when used
		# Wrap the existing __getattr__ method in an own one linking mfn methods if possibly
		mfncls = newcls.__dict__.get( metacls.mfnclsattr, None )
		if mfncls:
			metacls._wrapLazyGetAttr( newcls )
		# END if mfncls defined 
		
	
		return newcls
		
	# END __new__	
		
		

###################################
#### Initialization Methods   ####
#################################

def getCacheFilePath( filename, ext ):
	"""Return path to cache file from which you would initialize data structures"""
	mfile = Path( __file__ ).p_parent.p_parent
	return mfile / ( "cache/%s.%s" % ( filename, ext ) )
	

def init_nodehierarchy( ):
	""" Parse the nodes hiearchy from the maya doc and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = getCacheFilePath( "nodeHierarchy", "html" )
	lines = mfile.lines( retain=False )			# just read them in one burst
	
	hierarchylist = []
	regex = re.compile( "<tt>([ >]*)</tt><.*?>(\w+)" )	# matches level and name
	
	
	for line in lines:
		m = regex.match( line )
		if not m: continue
		
		levelstr, name = m.groups()
		level = levelstr.count( '>' ) 
		
		hierarchylist.append( ( level, name ) )
	# END for each line 
	global nodeTypeTree
	nodeTypeTree = bmaya._dagTreeFromTupleList( hierarchylist )
	
def init_wrappers( targetmodule ):
	""" Create Standin Classes that will delay the creation of the actual class till 
	the first instance is requested
	@param targetmodule: the module to which to put the wrappers"""	 
	global nodeTypeTree
	bmaya._initWrappers( targetmodule, nodeTypeTree.nodes_iter(), MetaClassCreatorNodes )
	

def init_nodeTypeToMfnClsMap( ):
	"""Fill the cache map supplying additional information about the MFNClass to use
	when creating the classes"""
	cfile = getCacheFilePath( "nodeTypeToMfnCls", "map" )
	fobj = open( cfile, 'r' )
	pf = PipeSeparatedFile( fobj )
	global nodeTypeToMfnClsMap
	
	version = pf.beginReading( )	 # don't care about version
	for nodeTypeName, mfnTypeName in pf.readColumnLine( ):
		nodeTypeToMfnClsMap[ nodeTypeName ] = getattr( api, mfnTypeName )
		
	fobj.close()
		

def _addCustomType( targetmodule, parentclsname, newclsname, metaclass=MetaClassCreatorNodes ):
	""" Add a custom type to the system such that a node with the given type will 
	automatically be wrapped with the corresponding class name
	@param targetmodule: the module to which standin classes are supposed to be added 
	@param parentclsname: the name of the parent node type - if your new class 
	has several parents, you have to add the new types beginning at the first exsiting parent
	as written in the maya/cache/nodeHierarchy.html file
	@param newclsname: the new name of your class - it must exist targetmodule
	@param metaclass: meta class object to be called to modify your type upon creation
	It will not be called if the class already exist in targetModule. Its recommended to derive it 
	from the metaclass given as default value.
	@raise KeyError: if the parentclsname does not exist """
	global nodeTypeTree	
	
	# add new type into the type hierarchy #
	parentclsname = uncapitalize( parentclsname )
	newclsname = uncapitalize( newclsname )
	nodeTypeTree.add_edge( ( parentclsname, newclsname ) )
	
	# create wrapper ( in case newclsname does not yet exist in target module )
	bmaya._initWrappers( targetmodule, [ newclsname ], metaclass )
	
	
def _addCustomTypeFromDagtree( targetModule, dagtree, metaclass=MetaClassCreatorNodes ):
	"""As L{_addCustomType}, but allows to enter the type relations using a 
	L{DAGTree} instead of individual names. Thus multiple edges can be added at once
	@note: node names in dagtree must be uncapitalized"""
	global nodeTypeTree	
	
	# add edges - have to start at root 
	rootnode = dagtree.get_root()
	def recurseOutEdges( node ):		# postorder
		for child in dagtree.children_iter( node ):
			yield (node,child)
			for edge in recurseOutEdges( child ):	# step down the hierarchy 
				yield edge
				
	nodeTypeTree.add_edges_from( recurseOutEdges( rootnode ) )
	
	bmaya._initWrappers( targetModule, dagtree.nodes_iter(), metaclass )

	
################################
#### Cache Initialization ####
############################

class MfnMemberMap( UserDict.UserDict ):
	"""Simple accessor for MFnDatabase access
	Direct access like db[funcname] returns an entry object with all values"""
	kDelete = 'x'	
	version = 1
	
	class Entry:
		"""Simple entry struct keeping the actual values """				
		def __init__( self, flag='', rvalfunc = None, newname="" ):
			self.flag = flag
			self.rvalfunc = self.toRvalFunc( rvalfunc )
			self.newname = newname
			
		@staticmethod
		def toRvalFunc( funcname ):
			if not isinstance( funcname, basestring ):
				return funcname
			if funcname == 'None': return None
			if not hasattr( nodes, funcname ):
				raise ValueError("'%s' is unknown to nodes module - it must be implemented there" % funcname )
			
			return getattr( nodes, funcname )

		def rvalFuncToStr( self ):
			if self.rvalfunc is None: return 'None'
			return self.rvalfunc.__name__
	
	
	def initFromFile( self, filepath ):
		""" Initialize the database with values from the given file
		@note: the file must have been written using the L{writeToFile} method"""
		self.clear()
		fobj = open( filepath, 'r' )
		
		pf = PipeSeparatedFile( fobj )
		fileversion = pf.beginReading( )
		if fileversion != self.version:
			raise ValueError( "File version %i does not match class version %i" % (fileversion,self.version ) )
			
		# get the entries
		for tokens in pf.readColumnLine( ):
			key = tokens[ 1 ]
			self[ key ] = self.Entry( flag=tokens[0], rvalfunc=tokens[2], newname=tokens[3] )
			
		
	
	def writeToFile( self, filepath ):
		"""Write our database contents to the given file"""
		klist = self.keys()
		klist.sort()
		
		fobj = open( filepath, 'w' )
		pf = PipeSeparatedFile( fobj )
		pf.beginWriting( self.version, [ 4,40,20,40 ] )
		
		for key in klist:							# write entries
			e = self[ key ]
			pf.writeTokens( ( e.flag, key,e.rvalFuncToStr(), e.newname ) )
		# end for each key
		
		fobj.close()
	
	def __getitem__( self, key ):
		"""Try to find the method in our original method name dict, and if not 
		available search all entries for a renamed method with name == key """
		try:
			return UserDict.UserDict.__getitem__(  self, key  )
		except KeyError:
			for entry in self.itervalues():
				if entry.newname == key:
					return entry
			# END for each entry
			raise KeyError( "Function named '%s' did not exist in db" % key )
	
	def get( self, key, *args ):
		""" Overridden to assure the advanced key search is used"""
		try:
			return self[ key ]
		except KeyError:
			if args: return args[0]
	
	def createEntry( self, funcname ):
		""" Create an entry for the given function, or return the existing one 
		@return: Entry object for funcname"""
		return self.setdefault( funcname, self.Entry() )
		
	def getMfnFunc( self, funcname ):
		"""@return: functionname corresponding to the ( possibly renamed ) funcname """
		if self.has_key( funcname ): return funcname
		for mfnfuncname,entry in self.iteritems():
			if entry.newname == funcname:
				return mfnfuncname
		# END for each key, value
		raise KeyError( "Function named '%s' did not exist in db" % key )
	

def writeMfnDBCacheFiles( ):
	"""Create a simple Memberlist of available mfn classes and their members 
	to allow a simple human-editable way of adjusting which methods will be added
	to the Nodes"""
	mfnclsnames = [ clsname for clsname in dir( api ) if clsname.startswith( "MFn" ) ]
	for mfnname in mfnclsnames:
		mfnfile = nodes.getMfnDBPath( mfnname )
		mfncls = getattr( api, mfnname )
		
		try:
			mfnfuncs =  [ f  for f  in mfncls.__dict__.itervalues() 
							if callable( f  ) and not f .__name__.startswith( '_' ) 
							and not f .__name__.startswith( '<' ) and not inspect.isclass( f  ) ]
		except AttributeError:
			continue		# it was a function, not a class 
		
		if not len( mfnfuncs ):
			continue
		
		db = MfnMemberMap( )
		if mfnfile.exists():
			db.initFromFile( mfnfile )
			
		# assure folder exists
		folder = mfnfile.dirname() 
		if not folder.isdir(): folder.makedirs()
		
		
		# write data - simple set the keys, use default flags
		for func in mfnfuncs:
			db.createEntry( func.__name__)
		

		# finally write the change db
		db.writeToFile( mfnfile ) 
		


