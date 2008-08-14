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
from byronimo.maya.util import MetaClassCreator
import byronimo.maya as bmaya
from byronimo.path import Path
from byronimo.util import uncapitalize
import re
import maya.OpenMaya as api


####################
### CACHES ########
##################
nodeTypeTree = None




#####################
#### META 		####
##################

class MetaClassCreatorNodes( MetaClassCreator ):
	"""Builds the base hierarchy for the given classname based on our typetree
	@todo: build classes with slots only as members are pretermined"""
	
	nameToTreeMap = set( [ 'FurAttractors', 'FurCurveAttractors', 'FurGlobals', 'FurDescription','FurFeedback' ] ) # special name handling 
	targetModule = None				# must be set in intialization to tell this class where to put newly created classes
	
	
	@staticmethod
	def _wrapMfnFunc( mfncls, funcname, instancePtr = None, funcMutatorDB = dict() ):
		""" Create a function that makes a MayaNode natively use its associated Maya 
		function set on calls.
		
		The created function will use the api object of the cls instance to initialize
		a function set of mfncls and execute the function in question
		
		The method mutation database allows to adjust the way a method is being wrapped
		@param mfncls: Maya function set class from which to take the functions
		@param funcname: name of the function set function to be wrapped
		@param instancePtr: if not None, the wrapped method will be bound to the instance, 
		otherwise it will assume self to be passed in automatically
		@param funcMutatorDB: datastructure:
		{ "mfnfuncname": ( rvalMutatorFunction, newname ) [ , ... ] }
			- mfnfuncname: name of the function in the mfn class
			- rvalMutatorFunction: if not None, will be given the return value of the wrpaped 
			function and should return an altered and possibly wrapped value
			- newname: if not None, a new name for the function mfnfuncname
		
		@raise KeyError: if the given function does not exist in mfncls"""
		# check the dict for method name - we do not want to see methods of 
		# base classes - will raise accordingly 
		mfnfunc = mfncls.__dict__[ funcname ]			# will just raise on error 
		mfndb = funcMutatorDB
		
		# get mfndb data and create appropriate function
		newfunc = None
		if instancePtr:
			def wrapMfnFunc( *args, **kwargs ):
				mfninst = mfncls( instancePtr._apiobj )					# use the given mfn only - we do not assume proper mfn inheritance yet
				return getattr( mfninst, funcname )( *args, **kwargs )
			newfunc = wrapMfnFunc
		else:
			# bound to class, self will be attached on class instantiation
			def wrapMfnFunc( self, *args, **kwargs ):
				mfninst = mfncls( self._apiobj )
				return getattr( mfninst, funcname )( *args, **kwargs )
			newfunc = wrapMfnFunc
			
		newfunc.__name__ = funcname			# rename the method 
		return newfunc

	
	@staticmethod
	def _readMfnDB( mfnclsname ):
		"""@return: mfn database describing how to handle the functions in the 
		function set described by mfnclsname
		If no explicit information exists, an empty dictionary will be returned as 
		NullDatabase"""
		return dict()
		
	@classmethod
	def _wrapLazyGetAttr( thiscls, newcls ):
		""" Attach the lazy getattr wrapper to newcls """
		getattrorig = None
		if hasattr( newcls, '__getattr__' ):
			getattrorig =  getattr( newcls, '__getattr__' )
			
		# CREATE GET ATTR CUSTOM FUNC
		# called if the given attribute is not available in class 
		def meta_getattr_lazy( self, attr ):
			if not hasattr( newcls, '_mfndb' ):
				setattr( newcls, '_mfndb', thiscls._readMfnDB( newcls.__name__ ) )
			
			mfncls = getattr( newcls, '_mfncls' )
			try:
				# Here it comes: We need two functions:
				# 1: function for the current instance - has the method is created
				#	 lazily, the self pointer could not be attached to the class (yet)
				# 	and thus needs to be given as free variable
				# 2: function for class - this will allow new instances of this class
				# 	to be 'born' with properly working, self-bound methods right from the start
				# 	thus this intitial overhead is just one once !
				kwargs = { 'funcMutatorDB' : newcls._mfndb, 'instancePtr' : self }
				newinstfunc = thiscls._wrapMfnFunc( mfncls, attr, **kwargs  )
				kwargs.pop( 'instancePtr' )
				newclsfunc = thiscls._wrapMfnFunc( mfncls, attr, **kwargs )
			except KeyError:
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
	
	

	



