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

env = __import__( "byronimo.maya.env", globals(), locals(), ['env'] )
nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
from byronimo.maya.util import MetaClassCreator
import byronimo.maya as bmaya
from byronimo.path import Path
from byronimo.util import uncapitalize
import maya.OpenMaya as api
import re
import inspect
import new
import UserDict

####################
### CACHES ########
##################
nodeTypeTree = None
nodeTypeToMfnTypeMap = {}			# allows to see the most specialized compatible mfn type for a given node type 



#####################
#### META 		####
##################

class MetaClassCreatorNodes( MetaClassCreator ):
	"""Builds the base hierarchy for the given classname based on our typetree
	@todo: build classes with slots only as members are pretermined"""
	
	nameToTreeMap = set( [ 'FurAttractors', 'FurCurveAttractors', 'FurGlobals', 'FurDescription','FurFeedback' ] ) # special name handling 
	targetModule = None				# must be set in intialization to tell this class where to put newly created classes
	
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
		""" Create a function that makes a MayaNode natively use its associated Maya 
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
			def wrapMfnFunc( self, *args, **kwargs ):
				mfninst = mfncls( self._apiobj )
				return rvalfunc( getattr( mfninst, mfnfuncname )( *args, **kwargs ) )
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
		getattrorig = None
		if hasattr( newcls, '__getattr__' ):
			getattrorig =  newcls.__dict__.get( '__getattr__', None )
		getattrorig.__name__ = "__getattr_orig" 
		
		# CREATE GET ATTR CUSTOM FUNC
		# called if the given attribute is not available in class 
		def meta_getattr_lazy( self, attr ):
			mfncls = getattr( newcls, '_mfncls' )			# garantueed to be available
			mfndb = None
			if mfncls :
				if not hasattr( newcls, '_mfndb' ):
					mfndb = thiscls._readMfnDB( mfncls.__name__ )
					setattr( newcls, '_mfndb', mfndb )
				else:
					mfndb = getattr( newcls,'_mfndb' )
			# END if mfncls available
			
			try:
				# get function as well as its possibly changed name 
				newclsfunc = thiscls._wrapMfnFunc( mfncls, attr, funcMutatorDB=newcls._mfndb )
				if not newclsfunc:
					raise KeyError( "Function %s has been deleted" + attr )
					
				newinstfunc = new.instancemethod( newclsfunc, self, newcls )	# create the respective instance method !
			except KeyError, ke:
				if not getattrorig:
					raise AttributeError
				# does not exist, pass on the call to whatever we had - thus we take precedence
				# passing the call allows subclasses to use function set methods of superclasses
				# accordingly
				return getattrorig( self, attr )
			else: 
				# store the new function on instance level !
				setattr( self, attr, newinstfunc )
				
				# ... and on class level
				setattr( newcls, attr, newclsfunc )
				return newinstfunc
				
		# END getattr_lazy func definition 		
		
		meta_getattr_lazy.__name__ = "__getattr__"
		setattr( newcls, "__getattr__", meta_getattr_lazy )
	
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global nodeTypeTree
		
		# will be used later 
		def func_nameToTree( name ):
			if name in metacls.nameToTreeMap:
				return name
			return uncapitalize( name )
		
		
		# TODO: ask our NodeType to MfnSet database and attach it to the cls dict
		# ( if not yet there ). By convention, there is only one mfn per class
		
		# SETUP slots - add common members
		# NOTE: does not appear to have any effect :(
		
		newcls = super( MetaClassCreatorNodes, metacls ).__new__( nodeTypeTree, metacls.targetModule, 
																metacls, name, bases, clsdict, 
																nameToTreeFunc = func_nameToTree )
				
				
		# lazy mfn wrapping 
		# Functions from mfn should be wrapped on demand to the respective classes as they 
		# should be generated only when used
		# Wrap the existing __getattr__ method in an own one linking mfn methods if possibly
		mfncls = newcls.__dict__.get( "_mfncls", None )
		if mfncls:
			metacls._wrapLazyGetAttr( newcls )
		# END if mfncls defined 
		
	
		return newcls
		
	# END __new__	
		
		

###################################
#### Initialization Methods   ####
#################################

def init_nodehierarchy( ):
	""" Parse the nodes hiearchy from the maya doc and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent
	mfile = mfile / ( "cache/nodeHierarchy_%s.html" % env.getAppVersion()[0] )
	lines = mfile.lines( retain=False )			# just read them in one burst
	
	hierarchylist = []
	regex = re.compile( "<tt>([ >]*)</tt><.*?>(\w+)" )	# matches level and name
	rootOffset = 1
	
	hierarchylist.append( (0,"mayaNode" ) )
	
	for line in lines:
		m = regex.match( line )
		if not m: continue
		
		levelstr, name = m.groups()
		level = levelstr.count( '>' ) + rootOffset
		
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
			if not hasattr( MfnMemberMap, funcname ):
				raise ValueError("'%s' is unknown to MfnMemberMap - it must be implemented here" % funcname )
			
			return getattr( MfnMemberMap, funcname )

		def rvalFuncToStr( self ):
			if self.rvalfunc is None: return 'None'
			return self.rvalfunc.__name__
	
	
	def initFromFile( self, filepath ):
		""" Initialize the database with values from the given file
		@note: the file must have been written using the L{writeToFile} method"""
		self.clear()
		fobj = open( filepath, 'r' )
		
		fileversion = int( fobj.readline( ).strip( ) )		# get version 
		if fileversion != self.version:
			raise ValueError( "File version %i does not match class version %i" % (fileversion,self.version ) )
			
		# get the entries
		for line in fobj:
			tokens = [ item.strip() for item in line.split( '|' ) ]
			key = tokens[ 1 ]
			self[ key ] = self.Entry( flag=tokens[0], rvalfunc=tokens[2], newname=tokens[3] )
			
		
	
	def writeToFile( self, filepath ):
		"""Write our database contents to the given file"""
		klist = self.keys()
		klist.sort()
		
		fobj = open( filepath, 'w' )
		fobj.write( "%i\n" % self.version )		# write version
		
		methodswritten = set()
		for key in klist:							# write entries
			e = self[ key ]
			fobj.write( "%-4s|%-40s|%-20s|%-40s\n" % ( e.flag, key,e.rvalFuncToStr(), e.newname ) )
			methodswritten
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
		if self.has_key( funcname ): return self[ funcname ]
		for mfnfuncname,entry in self.iteritems():
			if entry.newname == funcname:
				return mfnfuncname
		# END for each key, value
		raise KeyError( "Function named '%s' did not exist in db" % key )
	

def writeMfnDBCacheFiles( ):
	"""Create a simple Memberlist of available mfn classes and their members 
	to allow a simple human-editable way of adjusting which methods will be added
	to the MayaNodes"""
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
		


