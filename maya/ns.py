# -*- coding: utf-8 -*-
"""
Allows convenient access and handling of namespaces in an object oriented manner
@todo: more documentation
"""
import undo
from mayarv.maya.util import noneToList
from mayarv.interface import iDagItem
from mayarv.util import CallOnDeletion
import maya.cmds as cmds
import maya.OpenMaya as api
import re

#{ internal utilties
def _isRootOf( root, other ):
	"""@return: True if other which may be a string, is rooted at 'root
	@param other: '' = root namespace'
	hello:world => :hello:world
	@param root: may be namespace or string. It must not have a ':' in front, 
	hence it must be a relative naespace, and must end with a ':'.
	@note: the arguments are very specific, but this allows the method 
	to be faster than usual"""
	return (other+':').startswith(root)
#} END internal utilities

class Namespace( unicode, iDagItem ):
	""" Represents a Maya namespace
	Namespaces follow the given nameing conventions:
	   - Paths starting with a column are absolute
	      - :absolute:path
	   - Path separator is ':'"""
	re_find_duplicate_sep = re.compile( ":{2,}" )
	_sep = ':'
	root = ':'
	_defaultns = [ 'UI','shared' ]			# default namespaces that we want to ignore in our listings
	defaultIncrFunc = lambda b,i: "%s%02i" % ( b,i )
	
	# to keep instance small
	__slots__ = tuple()

	#{ Overridden Methods

	def __new__( cls, namespacepath=root, absolute = True ):
		""" Initialize the namespace with the given namespace path
		@param namespacepath: the namespace to wrap - it should be absolut to assure
		relative namespaces will not be interpreted in an unforseen manner ( as they
		are relative to the currently set namespace
		Set it ":" ( or "" ) to describe the root namespace
		@param absolute: if True, incoming namespace names will be made absolute if not yet the case
		@note: the namespace does not need to exist, but many methods will not work if so.
		NamespaceObjects returned by methods of this class are garantueed to exist"""

		if namespacepath != cls.root:
			if absolute:
				if not namespacepath.startswith( ":" ):		# do not force absolute namespace !
					namespacepath = ":" + namespacepath
			# END if absolute
			if len( namespacepath ) > 1 and namespacepath.endswith( ":" ):
				namespacepath = namespacepath[:-1]
		# END if its not the root namespace
		return unicode.__new__( cls, namespacepath )

	def __add__( self, other ):
		"""Properly catenate namespace objects - other must be relative namespace or
		object name ( with or without namespace )
		@return: new string objec """
		inbetween = self._sep
		if self.endswith( self._sep ) or other.startswith( self._sep ):
			inbetween = ''

		return "%s%s%s" % ( self, inbetween, other )

	def __repr__( self ):
		return "Namespace(%s)" % str( self )
	#}END Overridden Methods

	#{Edit Methods
	@classmethod
	@undo.undoable
	def create( cls, namespaceName ):
		"""Create a new namespace
		@param namespaceName: the name of the namespace, absolute or relative -
		it may contain subspaces too, i.e. :foo:bar.
		fred:subfred is a relative namespace, created in the currently active namespace
		@note: if the target namespace already exists, it will be returned
		@return: the create Namespace object"""
		newns = cls( namespaceName )

		if newns.exists():		 # skip work
			return newns

		cleanup = CallOnDeletion( None )
		if newns.isAbsolute():	# assure root is current if we are having an absolute name
			previousns = Namespace.getCurrent()
			cls( Namespace.root ).setCurrent( )
			cleanup.callableobj = lambda : previousns.setCurrent()

		# create each token accordingly ( its not root here )
		tokens = newns.split( newns._sep )
		for i,token in enumerate( tokens ):		# skip the root namespac
			base = cls( ':'.join( tokens[:i+1] ) )
			if base.exists( ):
				continue

			# otherwise add the baes to its parent ( that should exist
			# put operation on the queue - as we create empty namespaces, we can delete
			# them at any time
			op = undo.GenericOperation( )
			op.addDoit( cmds.namespace, p=base.getParent() , add=base.getBasename() )
			op.addUndoit(cmds.namespace, rm=base )
			op.doIt( )
		# END for each token

		return newns

	def rename( self, newName ):
		"""Rename this namespace to newName - the original namespace will cease to exist
		@note: if the namespace already exists, the existing one will be returned with
		all objects from this one added accordingly
		@param newName: the absolute name of the new namespace
		@return: Namespace with the new name
		@todo: Implement undo !"""
		newnamespace = self.__class__( newName )


		# recursively move children
		def moveChildren( curparent, newname ):
			for child in curparent.getChildren( ):
				moveChildren( child, newname + child.getBasename( ) )
			# all children should be gone now, move the
			curparent.delete( move_to_namespace = newname, autocreate=True )
		# END internal method
		moveChildren( self, newnamespace )
		return newnamespace

	def moveNodes( self, targetNamespace, force = True, autocreate=True ):
		"""Move objects from this to the targetNamespace
		@param force: if True, namespace clashes will be resolved by renaming, if false
		possible clashes would result in an error
		@param autocreate: if True, targetNamespace will be created if it does not exist yet
		@todo: Implement undo !"""
		targetNamespace = self.__class__( targetNamespace )
		if autocreate and not targetNamespace.exists( ):
			targetNamespace = Namespace.create( targetNamespace )

		cmds.namespace( mv=( self, targetNamespace ), force = force )

	def delete( self, move_to_namespace = root, autocreate=True ):
		"""Delete this namespace and move it's obejcts to the given move_to_namespace
		@param move_to_namespace: if None, the namespace to be deleted must be empty
		If Namespace, objects in this namespace will be moved there prior to namespace deletion
		move_to_namespace must exist
		@param autocreate: if True, move_to_namespace will be created if it does not exist yet
		@note: can handle sub-namespaces properly
		@raise RuntimeError:
		@todo: Implement undo !"""
		if self == self.root:
			raise ValueError( "Cannot delete root namespace" )

		if not self.exists():					# its already gone - all fine
			return

		# assure we have a namespace type
		if move_to_namespace:
			move_to_namespace = self.__class__( move_to_namespace )

		# assure we do not loose the current namespace - the maya methods could easily fail
		previousns = Namespace.getCurrent( )
		cleanup = CallOnDeletion( None )
		if previousns != self:		# cannot reset future deleted namespace
			cleanup.callableobj = lambda : previousns.setCurrent()


		# recurse into children for deletion
		for childns in self.getChildren( ):
			childns.delete( move_to_namespace = move_to_namespace )

		# make ourselves current
		self.setCurrent( )

		if move_to_namespace:
			self.moveNodes( move_to_namespace, autocreate=autocreate )

		# finally delete the namespace
		cmds.namespace( rm=self )

	# need to fully qualify it as undo is initialized after us ...
	@undo.undoable
	def setCurrent( self ):
		"""Set this namespace to be the current one - new objects will be put in it
		by default
		@return: self"""
		# THIS IS FASTER !
		melop = undo.GenericOperation( )
		melop.addDoit( cmds.namespace, set = self )
		melop.addUndoit( cmds.namespace, set = Namespace.getCurrent() )
		melop.doIt()
		
		return self

	#} END edit methods

	#{Query Methods

	@classmethod
	def getCurrent( cls ):
		"""@return: the currently set absolute namespace """
		# will return namespace relative to the root - thus is absolute in some sense
		nsname = cmds.namespaceInfo( cur = 1 )
		if not nsname.startswith( ':' ):		# assure we return an absoslute namespace
			nsname = ":" + nsname
		return cls( nsname )

	@classmethod
	def findUnique( cls, basename, incrementFunc = defaultIncrFunc ):
		"""Find a unique namespace based on basename which does not yet exist
		in the scene and can be created.
		@param basename: basename of the namespace, like ":mynamespace" or "mynamespace:subspace"
		@param incrementFunc: func( basename, index ), returns a unique name generated
		from the basename and the index representing the current iteration
		@return: unique namespace that is guaranteed not to exist below the current
		namespace"""
		i = 0
		while True:
			testns = cls( incrementFunc( basename, i ) )
			i += 1

			if not testns.exists():
				return testns
		# END while loop
		raise AssertionError("Should never get here")

	def exists( self ):
		"""@return: True if this namespace exists"""
		return cmds.namespace( ex=self )

	def isAbsolute( self ):
		"""@return: True if this namespace is an absolut one, defining a namespace
		from the root namespace like ":foo:bar"""
		return self.startswith( self._sep )

	def getParent( self ):
		"""@return: parent namespace of this instance"""
		if self == self.root:
			return None

		parent = iDagItem.getParent( self )	# considers children like ":bar" being a root
		if parent == None:	# we are just child of the root namespcae
			parent = self.root
		return self.__class__( parent )

	def getChildren( self, predicate = lambda x: True ):
		"""@return: list of child namespaces
		@param predicate: return True to include x in result"""
		lastcurrent = self.getCurrent()
		self.setCurrent( )
		out = []
		for ns in noneToList( cmds.namespaceInfo( lon=1 ) ):		# returns root-relative names !
			if ns in self._defaultns or not predicate( ns ):
				continue
			out.append( self.__class__( ns ) )
		# END for each subspace
		lastcurrent.setCurrent( )

		return out

	def toRelative( self ):
		"""@return: a relative version of self, thus it does not start with a colon
		@note: the root namespace cannot be relative - if this is of interest for you,
		you have to check for it. This method gracefully ignores that fact to make
		it more convenient to use as one does not have to be afraid of exceptions"""
		#if self == self.root:
		#	raise ValueError( "The root namespace cannot be relative" )

		if not self.startswith( ":" ):
			return self.__class__( self )	# create a copy

		return self.__class__( self[1:], absolute=False )

	def getRelativeTo( self, basenamespace ):
		"""@return: this namespace relative to the given basenamespace
		@param basenamespace: the namespace to which the returned one should be
		relative too
		@raise ValueError: If this or basenamespace is not absolute or if no relative
		namespace exists
		@return: relative namespace"""
		if not self.isAbsolute() or not basenamespace.isAbsolute( ):
			raise ValueError( "All involved namespaces need to be absolute: " + self + " , " + basenamespace )

		suffix = self._sep
		if basenamespace.endswith( self._sep ):
			suffix = ''
		relnamespace = self.replace( str( basenamespace ) + suffix, '' )
		if relnamespace == self:
			raise ValueError( str( basenamespace ) + " is no base of " + str( self ) )

		return self.__class__( relnamespace, absolute = False )

	@classmethod
	def splitNamespace( cls, objectname ):
		"""Cut the namespace from the given  name and return a tuple( namespacename, objectname )
		@note: method assumes that the namespace starts at the beginning of the object"""
		if objectname.find( '|' ) > -1:
			raise AssertionError( "Dagpath given where object name is required" )

		rpos = objectname.rfind( Namespace._sep )
		if rpos == -1:
			return ( Namespace.root, objectname )

		return ( cls( objectname[:rpos] ), objectname[rpos+1:] )


	def _removeDuplicateSep( self, name ):
		"""@return: name with duplicated : removed"""
		return self.re_find_duplicate_sep.sub( self._sep, name )

	def substitute( self, find_in, replacement ):
		"""@return: string with our namespace properly substituted with replacement such
		that the result is a properly formatted object name ( with or without namespace
		depending of the value of replacement )
		As this method is based on string replacement, self might as well match sub-namespaces
		if it is relative
		@note: if replacement is an empty string, it will effectively cut the matched namespace
		off the object name
		@note: handles replacement of subnamespaces correctly as well
		@note: as it operates on strings, the actual namespaces do not need to exist"""
		# special case : we are root
		if self == Namespace.root:
			return self._removeDuplicateSep( self.__class__( replacement, absolute=False ) + find_in )

		# do the replacement
		return self._removeDuplicateSep( find_in.replace( self, replacement ) )

	@classmethod
	def substituteNamespace( cls, thisns, find_in, replacement ):
		"""Same as L{substitute}, but signature might feel more natural"""
		return thisns.substitute( find_in, replacement )

	#} END query methods


	#{ Object Retrieval

	def iterNodes( self, *args, **kwargs ):
		"""Return an iterator on all objects in the namespace
		@param *args: MFn.kType filter types to be used to pre-filter the nodes 
		in the namespace. This can greatly improve performance !
		@param asNode: if true, default True, Nodes will be yielded. If False, 
		you will receive MDagPaths or MObjects depending on the 'dag' kwarg
		@param dag: if True, default False, only dag nodes will be returned, otherwise you will 
		receive dag nodes and dg nodes. Instance information will be lost on the way
		though.
		@param depth: if 0, default 0, only objects in this namespace will be returned
		if -1, all subnamespaces will be included as well, the depth is unlimited
		if 0<depth<x include all objects up to the 'depth' subnamespace
		@param **kwargs: given to l{iterDagNodes} or L{iterDgNodes}, which includes the 
		option to provide a predicate function
		@note: this method is quite similar to L{FileReference.iterNodes}, but 
		has a different feature set and needs this code here for maximum performance"""
		import nodes
		dag = kwargs.pop('dag', False)
		asNode = kwargs.get('asNode', True)
		predicate = kwargs.pop('predicate', lambda n: True)
		depth = kwargs.pop('depth', 0)
		
		# we handle node conversion
		kwargs['asNode'] = False
		pred = None
		iter_type = None
		nsGetRelativeTo = type(self).getRelativeTo
		selfrela = self.toRelative()+':'
		if dag:
			mfndag = api.MFnDagNode()
			mfndagSetObject = mfndag.setObject
			mfndagParentNamespace = mfndag.parentNamespace
			
			def check_filter(n):
				mfndagSetObject(n)
				ns = mfndagParentNamespace()
				if not _isRootOf(selfrela, ns):
					return False
				
				# check depth
				if depth > -1:
					ns = Namespace(ns)
					if self == ns:		# its depth 0
						return True
					
					# one separator means two subpaths
					if nsGetRelativeTo(ns, self).count(':')+1 > depth:
						return False
				# END handle depth
				return True
			# END filter
			
			iter_type = nodes.it.iterDagNodes
			pred = check_filter
		else:
			iter_type = nodes.it.iterDgNodes
			mfndep = api.MFnDependencyNode()
			mfndepSetObject = mfndep.setObject
			mfndepParentNamespace = mfndep.parentNamespace
			
			def check_filter(n):
				mfndepSetObject(n)
				ns = mfndepParentNamespace()
				if not _isRootOf(selfrela, ns):
					return False
				# END first namespace check
				
				# duplicated to be as fast as possible
				# check depth
				if depth > -1:
					ns = Namespace(ns)
					if self == ns:		# its depth 0
						return True
					
					if nsGetRelativeTo(ns, self).count(':')+1 > depth:
						return False
				# END handle depth
				return True
			# END filter
			iter_type = nodes.it.iterDgNodes
			pred = check_filter
		# END dag handling
		

		kwargs['predicate'] = pred
		NodeFromObj = nodes.NodeFromObj
		for n in iter_type(*args, **kwargs):
			if asNode:
				n = NodeFromObj(n)
			if predicate(n):
				yield n
		# END for each object to yield
	#} END object retrieval
	
	
	# Properties 
	p_exists = property(exists)
	p_isabsolute = property(isAbsolute)
	

#{ Static Access
def createNamespace( *args ):
	"""see L{Namespace.create}"""
	return Namespace.create( *args )

def getCurrentNamespace( ):
	"""see L{Namespace.getCurrent}"""
	return Namespace.getCurrent()

def findUniqueNamespace( *args, **kwargs ):
	"""see L{Namespace.findUnique}"""
	return Namespace.findUnique( *args, **kwargs )

def existsNamespace( namespace ):
	"""@return : True if given namespace ( name ) exists"""
	return Namespace( namespace ).exists()


RootNamespace = Namespace(Namespace.root)

#} END Static Access

