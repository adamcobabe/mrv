# -*- coding: utf-8 -*-
"""
Provides classes and functions operating on the MayaAPI class database

:note: This module must not be auto-initialized as it assumes its parent package to 
be present already
:note: The implementation is considered internal and may change any time unless stated
otherwise.
"""
__docformat__ = "restructuredtext"

from mrv.path import Path
from mrv.util import PipeSeparatedFile
import mrv.maya.env as env
import mrv.maya as mrvmaya

import maya.cmds as cmds

import UserDict
import inspect
from cStringIO import StringIO

import logging
log = logging.getLogger("mrv.maya.mdb")

__all__ = ("createDagNodeHierarchy", "createTypeNameToMfnClsMap", "getApiModules", 
           "getApiModules", "mfnDBPath", "cacheFilePath", "writeMfnDBCacheFiles", 
           "PythonMFnCodeGenerator", "MFnMemberMap", "MFnMethodDescriptor" )

#{ Initialization 

def createDagNodeHierarchy( ):
	""" Parse the nodes hierarchy file and return a `DAGTree` with its data
	:return: `DAGTree`"""
	mfile = cacheFilePath( "nodeHierarchy", "hf", use_version = 1 )
	return mrvmaya.dag_tree_from_tuple_list( mrvmaya.tuple_list_from_file( mfile ) )

def createTypeNameToMfnClsMap( ):
	"""Parse a file associating node type names with the best compatible MFn function 
	set and return a dictionary with the data
	
	:return: dict(((nodeTypeNameStr : api.MFnCls), ...)) dictionary with nodetypeName
	MFn class mapping"""
	typenameToClsMap = dict()
	
	cfile = cacheFilePath( "nodeTypeToMfnCls", "map" )
	fobj = open( cfile, 'r' )
	pf = PipeSeparatedFile( fobj )

	version = pf.beginReading( )	 # don't care about version
	for nodeTypeName, mfnTypeName in pf.readColumnLine( ):
		found = False
		for apimod in getApiModules():
			try:
				typenameToClsMap[ nodeTypeName ] = getattr( apimod, mfnTypeName )
				found = True
				break				# it worked, there is only one matching class
			except AttributeError:
				pass
		# END for each api module
		if not found:
			log.debug("Couldn't find mfn class named %s" % mfnTypeName)
	# END for each type/mfnclass pair
	fobj.close()
	
	return typenameToClsMap
	
#} END initialization


#{ Utilities 

def getApiModules():
	""":return: tuple of api modules containing MayaAPI classes
	:note: This takes a moment to load as it will import many api modules. Delay 
	the call as much as possible"""
	import maya.OpenMaya as api
	import maya.OpenMayaAnim as apianim
	import maya.OpenMayaUI	as apiui
	import maya.OpenMayaRender	as apirender
	import maya.OpenMayaFX as apifx
	
	return (api, apianim, apiui, apirender, apifx)

def mfnDBPath( mfnclsname ):
	"""Generate a path to a database file containing mfn wrapping information"""
	return Path(cacheFilePath("mfndb/"+ mfnclsname, '', use_version=False)[:-1])	# cut the '.'

def cacheFilePath( filename, ext, use_version = False ):
	"""Return path to cache file from which you would initialize data structures
	
	:param use_version: if true, the maya version will be appended to the filename  """
	mfile = Path( __file__ ).parent()
	version = ""
	if use_version:
		version = cmds.about( version=1 ).split( " " )[0]
	# END use version
	return mfile / ( "cache/%s%s.%s" % ( filename, version, ext ) )

def writeMfnDBCacheFiles(  ):
	"""Create a simple Memberlist of available mfn classes and their members
	to allow a simple human-editable way of adjusting which methods will be added
	to the Nodes.
	
	:note: currently writes information about all known api modules"""
	for apimod in getApiModules():
		mfnclsnames = [ clsname for clsname in dir( apimod ) if clsname.startswith( "MFn" ) ]
		for mfnname in mfnclsnames:
			mfnfile = mfnDBPath( mfnname )
			mfncls = getattr( apimod, mfnname )

			try:
				mfnfuncs =  [ f  for f  in mfncls.__dict__.itervalues( )
								if callable( f  ) and not f .__name__.startswith( '_' )
								and not f .__name__.startswith( '<' )
								and not f .__name__.endswith( mfnname )	# i.e. delete_MFnName
								and not inspect.isclass( f  ) ]
			except AttributeError:
				continue		# it was a function, not a class

			if not len( mfnfuncs ):
				continue

			db = MFnMemberMap()
			if mfnfile.exists():
				db = MFnMemberMap( mfnfile )

			# assure folder exists
			folder = mfnfile.dirname()
			if not folder.isdir(): folder.makedirs()


			# write data - simple set the keys, use default flags
			for func in mfnfuncs:
				# it could be prefixed with the function set name - remove the prefix
				# This happens in maya2008 + and may introduce plenty of new methods
				fname = func.__name__
				if fname.startswith(mfnname):
					fname = fname[len(mfnname)+1:]	# cut MFnName_(function)
				# END handle prefix
				
				db.createEntry(fname)
			# END for each function to add

			# finally write the change db
			db.writeToFile( mfnfile )
		# END for each api class
	# END for each api module


#} END functions 

class MFnCodeGeneratorBase(object):
	"""Define the interface and common utility methods to generate a string defining 
	code for a given MFnMethod according to the meta data provided by an `MFnMethodDescriptor`.
	
	Once instantiated, it can create any number of methods"""
	__slots__ = 'module_dict'
	def __init__(self, module_dict):
		"""Intialize this instance"""
		self.module_dict = module_dict
	
	#{ Utilities
	def _toRvalFunc( self, funcname ):
		""":return: None or a function which receives the return value of our actual mfn function"""
		if not isinstance( funcname, basestring ):
			return funcname
		if funcname == 'None': return None
		
		try:
			return self.module_dict[funcname]
		except KeyError:
			raise ValueError("'%s' is unknown to nodes module - it must be implemented there" % funcname )
	#} END utilities
	
	
	#{ Interface 
	def generateMFnClsMethodWrapper(self, source_method_name, target_method_name, mfn_fun_name, method_descriptor, flags=0):
		"""
		:return: string containing the code for the wrapper method as configured by the 
			method descriptor
		:param source_method_name: Original name of the method - this is the name under which 
			it was requested.
		:param target_method_name: Name of the method in the returned code string
		:param mfn_fun_name: original name of the MFn function
		:param method_descriptor: instance of `MFnMethodDescriptor`
		:param flags: bit flags providing additional information, depending on the actual 
		implementation. Unsupported flags are ignored."""
		raise NotImplementedError("To be implemented in SubClass")
	#} END interfacec
	

class PythonMFnCodeGenerator(MFnCodeGeneratorBase):
	"""Specialization to generate python code
	
	**Flags**:
	
	 * kDirectCall:
	 	If set, the call return the actual mfn method in the best case, which is 
	 	a call as direct as it gets. A possibly negative side-effect would be that
	 	it the MFnMethod caches the function set and actual MObject/MDagPath, which 
	 	can be dangerous if held too long
	 	
	 * kMFnNeedsMObject:
	 	See `MFnMemberMap` and its InitWithMObject description
	 	
	 * kIsMObject:
	 	If set, the type we create the method for is not derived from Node, but 
	 	from MObject. This hint is required in order to generate correct calling code.
	 	
	 * kIsDagNode:
	 	If set, the type we create the method for is derived from DagNode
	 
	"""
	kDirectCall, \
	kMFnNeedsMObject, \
	kIsMObject, \
	kIsDagNode = [ 1<<i for i in range(4) ] 
	
	def generateMFnClsMethodWrapper(self, source_method_name, target_method_name, mfn_fun_name, method_descriptor, flags=0):
		"""Generates code as python string which can be used to compile a function. It assumes the following 
		globals ( or locals ) to be existing: mfncls, mfn_fun, [rvalfunc], source_method_name
		Currently supports the following meta data:
		 * method_descriptor.rvalfunc
		 
		:raise ValueError: if flags are incompatible with each other
		"""
			# if an mobject is required, we disable the isDagPath flag
		if flags & self.kIsDagNode and flags & self.kMFnNeedsMObject:
			flags ^= self.kIsDagNode
		# END handle needs MObject
		
		if flags & self.kIsMObject and flags & self.kIsDagNode:
			raise ValueError("kIsMObject and kIsDagNode are mutually exclusive")
		# END handle flags
		
		
		sio = StringIO()
		
		rvalfunname = ''
		if method_descriptor.rvalfunc != 'None':
			rvalfunname = method_descriptor.rvalfunc
		
		sio.write("def %s(self, *args, **kwargs):\n" % target_method_name)
		
	
		# mfn function call
		mfnset = "mfncls(self"
		if flags & self.kIsDagNode:
			mfnset += ".dagPath()"
		elif not flags & self.kIsMObject:
			mfnset += ".object()"
		mfnset += ")"
		
		if flags & self.kDirectCall:
			curline = "\tmfninstfunc = %s.%s\n" % (mfnset, mfn_fun_name)
			sio.write(curline)
			
			if rvalfunname:
				sio.write("\tmfninstfunc = lambda *args, **kwargs: rvalfun(mfninstfunc(*args, **kwargs))\n")
			# END handle rvalfunc name
			sio.write("\tobject.__setattr__(self, %s, mfninstfunc)\n" % source_method_name)
			sio.write("\treturn mfninstfunc(*args, **kwargs)")
		else:
			curline = "mfn_fun(%s, *args, **kwargs)" % mfnset
			if rvalfunname:
				curline = "rvalfunc(%s)" % curline
			sio.write("\treturn %s" % curline)
		# END handle direct call
		
		return sio.getvalue()
	
	#{ Interface
	
	def generateMFnClsMethodWrapperMethod(self, source_method_name, target_method_name, mfncls, mfn_fun, method_descriptor, flags=0):
		""":return: python function suitable to be installed on a class
		:param mfncls: MFnFunction set class from which the method was retrieved.
		:param mfn_fun: function as retrieved from the function set's dict. Its a bare function.
		:note: For all other args, see `MFnCodeGeneratorBase.generateMFnClsMethodWrapper`"""
		needs_MObject = flags & self.kMFnNeedsMObject
		rvalfunc = self._toRvalFunc(method_descriptor.rvalfunc)
		mfnfuncname = mfn_fun.__name__
		
		# handle MFnName_function
		if mfnfuncname.startswith(mfncls.__name__):
			mfnfuncname = mfnfuncname[len(mfncls.__name__)+1:]
			
		newfunc = None
		# bound to class, self will be attached on class instantiation
		if flags & self.kDirectCall:
			# bound to class, self will be attached on class instantiation
			if rvalfunc:	# wrap rval function around
				# INITIALIZED DAG NODES WITH DAG PATH !
				if flags & self.kIsDagNode and not needs_MObject:			# yes, we duplicate code here to keep it fast !!
					def wrapMfnFunc( self, *args, **kwargs ):
						rvallambda = lambda *args, **kwargs: rvalfunc(mfn_fun(mfncls(self.dagPath()), *args, **kwargs))
						object.__setattr__( self, source_method_name, rvallambda ) # cache it in our object
						return rvallambda( *args, **kwargs )
					newfunc = wrapMfnFunc
				else:
					if flags & self.kIsMObject:
						def wrapMfnFunc( self, *args, **kwargs ):
							rvallambda = lambda *args, **kwargs: rvalfunc(mfn_fun(mfncls(self), *args, **kwargs))
							object.__setattr__( self, source_method_name, rvallambda )
							return rvallambda( *args, **kwargs )
						newfunc = wrapMfnFunc
					else:
						def wrapMfnFunc( self, *args, **kwargs ):
							rvallambda = lambda *args, **kwargs: rvalfunc(mfn_fun(mfncls(self.object()), *args, **kwargs))
							object.__setattr__( self, source_method_name, rvallambda )
							return rvallambda( *args, **kwargs )
						newfunc = wrapMfnFunc
					# END handle MObject inheritance
			else:
				if flags & self.kIsDagNode and not needs_MObject:			# yes, we duplicate code here to keep it fast !!
					def wrapMfnFunc( self, *args, **kwargs ):
						mfnfunc = getattr(mfncls(self.dagPath()), mfnfuncname)
						object.__setattr__( self, source_method_name, mfnfunc )
						return mfnfunc( *args, **kwargs )
					newfunc = wrapMfnFunc
				else:
					if flags & self.kIsMObject:
						def wrapMfnFunc( self, *args, **kwargs ):
							mfnfunc = getattr(mfncls(self), mfnfuncname)
							object.__setattr__( self, source_method_name, mfnfunc )
							return mfnfunc( *args, **kwargs )
						newfunc = wrapMfnFunc
					else:
						def wrapMfnFunc( self, *args, **kwargs ):
							mfnfunc = getattr(mfncls(self.object()), mfnfuncname)
							object.__setattr__( self, source_method_name, mfnfunc )
							return mfnfunc( *args, **kwargs )
						newfunc = wrapMfnFunc
					# END handle MObject inheritance
			# END not rvalfunc
		else:
			if rvalfunc:	# wrap rval function around
				# INITIALIZED DAG NODES WITH DAG PATH !
				if flags & self.kIsDagNode and not needs_MObject:			# yes, we duplicate code here to keep it fast !!
					def wrapMfnFunc( self, *args, **kwargs ):
						return rvalfunc(mfn_fun(mfncls(self.dagPath()), *args, **kwargs))
					newfunc = wrapMfnFunc
				else:
					if flags & self.kIsMObject:
						def wrapMfnFunc( self, *args, **kwargs ):
							return rvalfunc(mfn_fun(mfncls(self), *args, **kwargs))
						newfunc = wrapMfnFunc
					else:
						def wrapMfnFunc( self, *args, **kwargs ):
							return rvalfunc(mfn_fun(mfncls(self.object()), *args, **kwargs))
						newfunc = wrapMfnFunc
					# END handle MObject inheritance
			else:
				if flags & self.kIsDagNode and not needs_MObject:			# yes, we duplicate code here to keep it fast !!
					def wrapMfnFunc( self, *args, **kwargs ):
						return mfn_fun(mfncls(self.dagPath()), *args, **kwargs)
					newfunc = wrapMfnFunc
				else:
					if flags & self.kIsMObject:
						def wrapMfnFunc( self, *args, **kwargs ):
							return mfn_fun(mfncls(self), *args, **kwargs)
						newfunc = wrapMfnFunc
					else:
						def wrapMfnFunc( self, *args, **kwargs ):
							return mfn_fun(mfncls(self.object()), *args, **kwargs)
						newfunc = wrapMfnFunc
					# END handle MObject inheritance
			# END not rvalfunc
		# END api accellerated method
		
		newfunc.__name__ = target_method_name
		return newfunc
	
	#} END interface 
	
	
class MFnMethodDescriptor(object):
	"""Contains meta-information about a given method according to data read from 
	the MFnDatabase"""
	__slots__ = ("flag", "rvalfunc", "newname")
	
	def __init__( self, flag='', rvalfunc = None, newname="" ):
		self.flag = flag
		self.rvalfunc = rvalfunc
		self.newname = newname

	def rvalFuncToStr( self ):
		if self.rvalfunc is None: return 'None'
		return self.rvalfunc.__name__


class MFnMemberMap( UserDict.UserDict ):
	"""Simple accessor for MFnDatabase access
	Direct access like db[funcname] returns an entry object with all values
	
	**Globals**:
	The __globals__ entry in MFn db files allows to pass additional options.
	Currently supported ones are:
	 * 'InitWithMObject':
	 	If set, the function set's instance will be initialized with an MObject
	 	even though an MDagPath would be available.
	 	Default False"""
	__slots__ = "flags"
	kDelete = 'x'
	kInitWithMObjectFlagName = "InitWithMObject"
	

	def __init__( self, filepath = None ):
		"""intiialize self from a file if not None"""
		UserDict.UserDict.__init__( self )

		self._filepath = filepath
		if filepath:
			self._initFromFile( filepath )
			
		# initialize globals
		self.flags = 0
		ge = self.get('__global__', None)
		if ge is not None:
			# currently we only know this one
			if ge.flag == self.kInitWithMObjectFlagName:
				self.flags |= PythonMFnCodeGenerator.kMFnNeedsMObject
		# END fetch info

	def __str__( self ):
		return "MFnMemberMap(%s)" % self._filepath

	def _initFromFile( self, filepath ):
		"""Initialize the database with values from the given file
		
		:note: the file must have been written using the `writeToFile` method"""
		self.clear()
		fobj = open( filepath, 'r' )

		pf = PipeSeparatedFile( fobj )
		pf.beginReading( )
		
		# get the entries
		for tokens in pf.readColumnLine( ):
			key = tokens[ 1 ]
			self[ key ] = MFnMethodDescriptor( flag=tokens[0], rvalfunc=tokens[2], newname=tokens[3] )
		# END for each token in read column line

	def writeToFile( self, filepath ):
		"""Write our database contents to the given file"""
		klist = self.keys()
		klist.sort()

		fobj = open( filepath, 'w' )
		pf = PipeSeparatedFile( fobj )
		pf.beginWriting( ( 4,40,20,40 ) )

		for key in klist:							# write entries
			e = self[ key ]
			pf.writeTokens( ( e.flag, key,e.rvalFuncToStr(), e.newname ) )
		# end for each key

		fobj.close()

	def entry( self, funcname ):
		"""
		:return: Tuple( mfnfuncname, entry )
			original mfnclass function name paired with the
			db entry containing more information
		:raise KeyError: if no such function exists"""
		try:
			return ( funcname, self[ funcname ] )
		except KeyError:
			for mfnfuncname,entry in self.iteritems():
				if entry.newname == funcname:
					return ( mfnfuncname, entry )
			# END for each item

		raise KeyError( "Function named '%s' did not exist in db" % funcname )

	def createEntry( self, funcname ):
		""" Create an entry for the given function, or return the existing one
		
		:return: Entry object for funcname"""
		return self.setdefault( funcname, MFnMethodDescriptor() )

	def mfnFunc( self, funcname ):
		""":return: mfn functionname corresponding to the ( possibly renamed ) funcname """
		return self.entry( funcname )[0]

