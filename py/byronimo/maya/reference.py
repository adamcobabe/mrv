# -*- coding: utf-8 -*-
"""B{byronimo.maya.reference}

Allows convenient access and handling of references in an object oriented manner
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

from byronimo.path import Path
from byronimo.util import And
from byronimo.exceptions import *
from byronimo.maya.namespace import Namespace
from byronimo.maya.util import noneToList
import maya.cmds as cmds
from byronimo.util import iDagItem
from itertools import ifilter


################
## FILTERS ###
###########
#{ Exceptions
class FileReferenceError( ByronimoError ):
	pass 

#}

################
## FILTERS ###
###########
#{ Filters 



#}




################
## Classes ###
###########
class FileReference( Path, iDagItem ):
	"""Represents a Maya file reference
	@note: do not cache these instances but get a fresh one when you have to work with it
	@note: as FileReference is also a iDagItem, all the respective methods, especially for 
	parent/child iteration and query can be used as well"""
	
	
	editTypes = [	'setAttr','addAttr','deleteAttr','connectAttr','disconnectAttr','parent' ]
	
	@classmethod
	def _splitCopyNumber( cls, path ):
		"""@return: ( path, copynumber ), copynumber is at least 0 """
		buf = path.split( '{' )
		cpn = 0
		if len( buf ) > 1:
			cpn = int( buf[1][:-1] )
			path = buf[0]
		return path,cpn
	
	#{ Object Overrides
	
	def __new__( cls, filepath = None, refnode = None, **kwargs ):
		def handleCreation( refnode , **kwargs ):
			""" Initialize the instance by a reference node - lets not trust paths """
			unresolved = kwargs.pop( "unresolved", False )
			path = cmds.referenceQuery( refnode, filename=1, un=unresolved )
			path,cpn = cls._splitCopyNumber( path )
			self = Path.__new__( cls, path )
			self._refnode = refnode					# keep it for now 
			return self
		# END creation handler 
		
		if refnode:
			return handleCreation( refnode, **kwargs )
		if filepath:
			return handleCreation( cmds.referenceQuery( filepath, rfn=1 ), **kwargs )
		raise ValueError( "Specify either filepath or refnode" )
	
	def __init__( self, *args, **kwargs ):
		""" Initialize our iDagItem base """
		return iDagItem.__init__( self, separator = '/' )
	
	def __eq__( self, other ):
		"""Special treatment for other filereferences"""
		# need equal copy numbers as well as equal paths 
		if isinstance( other, FileReference ):
			return self.getCopyNumber() == other.getCopyNumber() and Path.__eq__( self, other )
			
		return Path.__eq__( self, other )
	
	def __ne__( self, other ):
		return not self.__eq__( other )
		
	#} END object overrides 
	
	#{ Static Methods 
	@classmethod
	def create( cls, filepath, namespace=None, load = True ):
		"""Create a reference with the given namespace
		@param filename: path describing the reference file location 
		@param namespace: if None, a unique namespace will be generated for you
		else the given namespace will hold all referenced objects. 
		@param load: 
		@raise ValueError: if the namespace does already exist 
		@raise RuntimeError: if the reference could not be created"""
		filepath = Path( cls._splitCopyNumber( filepath )[0] )
		
		def nsfunc( base, i ):
			if not i: return base
			return "%s%i" % ( base,i )
		
		ns = namespace 	
		if not ns:										# assure unique namespace 
			nsbasename = filepath.stripext().basename()
			ns = Namespace.getUnique( nsbasename, incrementFunc = nsfunc )
		else:
			ns = Namespace( ns )		# assure we have a namespace object 
		
		ns = ns.getRelativeTo( Namespace( Namespace.rootNamespace ) )
		if ns.exists():
			raise ValueError( "Namespace %s for %s does already exist" % (ns,filepath) )
			
		# assure we keep the current namespace
		prevns = Namespace.getCurrent()
		createdRefpath = cmds.file( filepath, ns=str(ns),r=1,dr=not load ) 
		prevns.setCurrent( )
		
		return FileReference( createdRefpath )
		
	@classmethod
	def find( cls, paths, **kwargs ):
		"""Find the reference for each path in paths
		@param **kwargs: all supported by L{ls}
		@param ignore_extension: if True, default False, the extension will be ignored, 
		thus an MA file will be meatched with an MB file. The references found will still have 
		their extension
		@return: list( FileReference|None, ... ) 
		if a filereference was found for given occurrence of Path, it will be returned 
		at index of the current path in the input paths, otherwise it is None.
		@note: zip( paths, result ) to get a corresponding tuple list associating each input path
		with the located reference"""
		if not isinstance( paths, (list,tuple) ) or hasattr( paths, 'next' ):
			raise TypeError( "paths must be tuple, was %s" % type( paths ) )
			
		ignore_ext = kwargs.pop( "ignore_extension", False )
		refs = cls.ls( **kwargs )
		
		# build dict for fast lookup 
		lut = dict()
		
		pathscp = paths[:]								# copy them before change !
		
		if ignore_ext:
			# actually, keep the instance number - just count it up
			countlut = dict()
			# as keys we do not allow environment variables, as there could be 
			# versions with and without vars,although all pointing to the same path, 
			# pure string comparison will not find them 
			def getCountTuple( filepath ):
				pathnoext = Path( filepath ).expandvars().splitext()[0]		
				count = countlut.get( pathnoext, 0 )
				countlut[ pathnoext ] = count + 1
				return ( pathnoext , count )
				
			for ref in refs:
				lut[ getCountTuple( ref ) ] = ref			# keys have no ext
			
			countlut = dict()
			for i,path in enumerate( pathscp ):
				pathscp[i] = getCountTuple( path )
		else:
			lut.update( ( ref, ref ) for ref in refs )		# ref will take care about the comparison
		# END split extensions on request 
		
		
		# remove the keys once we hit them !
		outlist = list()
		for path in pathscp:
			ref = lut.get( path, None )
			outlist.append( ref )
			
			# no need to delete the keys as they have to be unique anyway 
		# END for each path to find 
		return outlist
		
	@classmethod
	def ls( cls, referenceFile = "", predicate = lambda x: True, unresolved = False ):
		""" list all references in the scene or in referenceFile
		@param referenceFile: if not empty, the references below the given reference file will be returned
		@param predicate: method returning true for each valid file reference object
		@param unresolved: if True, paths will not be resolved, thus you will see environment variables , 
		but positive effects of the dirmap will not be visible as well
		@return: list of L{FileReference}s objects"""
		out = []
		for reffile in cmds.file( str( referenceFile ), q=1, r=1, un=unresolved ):
			refobj = FileReference( filepath = reffile, unresolved = unresolved )
			if predicate( refobj ):
				out.append( refobj )
		# END for each reference file
		return out
		
	@classmethod
	def lsDeep( cls, predicate = lambda x: True, **kwargs ):
		""" Return all references recursively 
		@param **kwargs: support for arguments as in lsReferences"""
		refs = cls.ls( **kwargs )
		out = refs
		for ref in refs:
			out.extend( ref.getChildrenDeep( order = iDagItem.kOrder_BreadthFirst, predicate=predicate ) )
		return out
		
	
	def remove( self, **kwargs ):
		""" Remove the given reference 
		@note: assures that no namespaces of that reference are left, remaining objects
		will be moved into the root namespace. This way the namespaces will not be wasted.
		This fails if there are referenced objects in the subnamespace - we currently only 
		catch that exception as the main reference removal worked anyway
		@note: **kwargs passed to namespace.delete """
		ns = self.getNamespace( )
		cmds.file( self.getFullPath( ), rr=1 )
		try:
			ns.delete( **kwargs )
		except RuntimeError:
			pass 
	
	
	def replace( self, filepath ):
		"""Replace this reference with filepath
		@param filepath: the path to the file to replace this reference with
		@return: FileReference with the updated reference
		@note: you should not use the original ref instance anymore as its unicode 
		path still uses the old path"""
		filepath = Path( self._splitCopyNumber( filepath )[0] )
		cmds.file( filepath, lr=self._refnode )
		return FileReference( refnode = self._refnode )		# return update object
		
	def importRef( self, depth=1 ):
		"""Import the reference until the given depth is reached
		@param depth: 
		   - x<1: import all references and subreferences
		   - x: import until level x is reached, 1 imports just self such that
		   all its children are on the same level as self was before import
		@return: list of FileReference objects that are now in the root namespace - this list could 
		be empty if all subreferences are fully imported"""
		def importRecursive( reference, curdepth, maxdepth ):
			# load ref
			reference.setLoaded( True )
			children = reference.getChildren()
			cmds.file( reference.getFullPath(), importReference=1 )
			
			if curdepth == maxdepth - 1:
				return children
				
			outsubrefs = []
			for childref in children:
				outsubrefs.extend( importRecursive( childref, curdepth+1, maxdepth ) )
				
			return outsubrefs
		# END importRecursive
		
		return importRecursive( self, 0, depth )
		
	#}
	
	
	#{ Nodes Query 
	def iterNodes( self, asNode = True, dag=True, dg=True,
				  assemblies=False, assembliesInReference=False,
				  predicate = None):
		"""Creates iterator over nodes in this reference
		@param asNode: if True, return wrapped Nodes, if False string names will 
		be returned 
		@param dag: if True, return dag nodes
		@param dg: if True, return dg nodes
		@param assemblies: if True, return only dagNodes with no parent 
		@param assembliesInReference: if True, return only dag nodes that have no 
		parent in their own reference. They may have a parent not coming from their 
		reference though. This flag causes a big negative performance impact. Only works
		if asNode = 1
		@param predicate: if function returns True for Mode|string n, n will be yielded
		@raise ValueError: if incompatible arguments have been given """
		allnodes = noneToList( cmds.referenceQuery( self.getFullPath(), n=1, dp=1 ) )
		
		# additional ls filtering 
		filterargs = dict()
		if not dag:
			filterargs[ 'dep' ] = 1
			
		if not dg:
			filterargs[ 'type' ] = "dagNode"
			
		if assemblies:
			filterargs[ 'assemblies' ] = 1
			
		
		# APPLY ADDITIONAL FILTER
		if filterargs:
			allnodes = noneToList( cmds.ls( allnodes, **filterargs ) )
			
	
		myfilter = And( ) 
		# ASSEMBILES IN REFERENCE ?
		if assembliesInReference:
			if not asNode:
				raise ValueError( "assembliesInReference requires asNode to be 1" )
				
			rns = self.getNamespace()
			
			def isRootInReference( n ):
				parent = n.getParent()
				if parent is None:
					return True
					
				return not rns.isRootOf( parent.getNamespace() )
			# END filter method 	
			
			myfilter.functions.append( isRootInReference )
		# END assembliesInReference	
		
		if predicate:
			myfilter.functions.append( predicate )
		
		nodesIter = None
		if asNode:
			import byronimo.maya.nodes as nodes
			nodesIter = ( nodes.Node( name ) for name in allnodes )
		else:
			nodesIter = iter( allnodes )
			
		return ifilter( myfilter, nodesIter )
	#}
	
	#{Edit Methods	
	def cleanup( self, unresolvedEdits = True, 
				 editTypes = editTypes ):
		"""remove unresolved edits or all edits on this reference
		@param unresolvedEdits: if True, only dangling connections will be removed, 
		if False, all reference edits will be removed - the reference will be unloaded for this.
		The loading state of the reference will stay unchanged after the operation.
		@param editTypes: list of edit types to remove during cleanup"""
		wasloaded = self.p_loaded
		if not unresolvedEdits:
			self.p_loaded = False
			
		for etype in editTypes:
			cmds.file( cr=self._refnode, editCommand=etype )
			
		if not unresolvedEdits:
			self.p_loaded = wasloaded
		
		
	def setLocked( self, state ):
		"""Set the reference to be locked or unlocked
		@param state: if True, the reference is locked , if False its unlocked and 
		can be altered"""
		if self.isLocked( ) == state:
			return 
			
		# unload ref 
		wasloaded = self.p_loaded
		self.p_loaded = False 
		
		# set locked
		cmds.setAttr( self._refnode+".locked", state )
		
		# reset the loading state
		self.p_loaded = wasloaded
		
		
	def setLoaded( self, state ):
		"""set the reference loaded or unloaded
		@param state: True = unload reference, True = load reference """
		
		if state == self.isLoaded( ):			# already desired state
			return
		
		if state:
			cmds.file( loadReference=self._refnode )
		else:
			cmds.file( unloadReference=self._refnode )
	
	
	def setNamespace( self, namespace ):
		"""set the reference to use the given namespace
		@param namespace: Namespace instance or name of the short namespace
		@raise RuntimeError: if namespace already exists or if reference is not root"""
		shortname = namespace
		if isinstance( namespace, Namespace ):
			shortname = namespace.getBasename( )
		
		# set the namespace
		cmds.file( self.getFullPath(), e=1, ns=shortname )
		
	#}END Edit Methods
	
	
	#{Query Methods
	def exists( self ):
		"""@return: True if our file reference exists in maya"""
		try:
			self.getFullPath( )
		except RuntimeError:
			return False
		else:
			return True
		
	def isLocked( self ):
		"""@return: True if reference is locked"""
		return cmds.getAttr( self._refnode + ".locked" )
		
	def isLoaded( self ):
		"""@return: True if the reference is loaded"""
		return cmds.file( rfn=self._refnode, q=1, dr=1 ) == False
		
	def getParent( self ):
		"""@return: the parent reference of this instance or None if we are root"""
		parentrfn = cmds.referenceQuery( self._refnode, rfn=1, p=1 )
		if not parentrfn:
			return None
		return FileReference( refnode = parentrfn )
		
	def getChildren( self , predicate = lambda x: True ):
		""" @return: all intermediate child references of this instance """
		return self.ls( referenceFile = self.getFullPath(), predicate = predicate )
		
		
	def getCopyNumber( self ):
		"""@return: the references copy number - starting at 0 for the first reference
		@note: we do not cache the copy number as mayas internal numbering can change on 
		when references change - the only stable thing is the reference node name"""
		return self._splitCopyNumber( self.getFullPath() )[1]
		
	def getNamespace( self ):
		"""@return: namespace object of the namespace holding all objects in this reference"""
		fullpath = self.getFullPath()
		refspace = cmds.file( fullpath, q=1, ns=1 )
		parentspace = cmds.file( fullpath, q=1, pns=1 )[0]		# returns lists, although its always just one string
		if parentspace:
			parentspace += ":"
			
		return Namespace( ":" + parentspace + refspace )
			
	def getFullPath( self , unresolved = False ):
		"""@return: string with full path including copy number
		@param unresolved: see L{ls}
		@note: we always query it from maya as our numbers change if some other 
		reference is being removed and cannot be trusted"""
		return cmds.referenceQuery( self._refnode, f=1, un=unresolved )
		
	def getReferenceNode( self ):
		"""@return: byronimo wrapped reference node managing this reference"""
		import byronimo.maya.nodes as nodes 
		return nodes.Node( self._refnode )
		
	#}END query methods
		
	#{ Properties 
	p_locked = property( isLocked, setLocked )
	p_loaded = property( isLoaded, setLoaded )
	p_copynumber = property( getCopyNumber )
	p_namespace = property( getNamespace, setNamespace )
	#}
		
	
	
