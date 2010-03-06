# -*- coding: utf-8 -*-
"""
Allows convenient access and handling of namespaces in an object oriented manner
@todo: more documentation
"""
from mayarv.maya import undo
from mayarv.maya.util import noneToList, MuteUndo
from mayarv.util import iDagItem, CallOnDeletion
import maya.cmds as cmds
import maya.OpenMaya as api
import re



#{ Static Access
def create( *args ):
	"""see L{Namespace.create}"""
	return Namespace.create( *args )

def getCurrent( ):
	"""see L{Namespace.getCurrent}"""
	return Namespace.getCurrent()

def getUnique( *args, **kwargs ):
	"""see L{Namespace.getUnique}"""
	return Namespace.getUnique( *args, **kwargs )

def exists( namespace ):
	"""@return : True if given namespace ( name ) exists"""
	return Namespace( namespace ).exists()

#} END Static Access



class Namespace( unicode, iDagItem ):
	""" Represents a Maya namespace
	Namespaces follow the given nameing conventions:
	   - Paths starting with a column are absolute
	      - :absolute:path
	   - Path separator is ':'"""
	re_find_duplicate_sep = re.compile( ":{2,}" )
	_sep = ':'
	rootNamespace = ':'
	_defaultns = [ 'UI','shared' ]			# default namespaces that we want to ignore in our listings
	defaultIncrFunc = lambda b,i: "%s%02i" % ( b,i )
	
	# to keep instance small
	__slots__ = tuple()

	#{ Overridden Methods

	def __new__( cls, namespacepath, absolute = True ):
		""" Initialize the namespace with the given namespace path
		@param namespacepath: the namespace to wrap - it should be absolut to assure
		relative namespaces will not be interpreted in an unforseen manner ( as they
		are relative to the currently set namespace
		Set it ":" ( or "" ) to describe the root namespace
		@param absolute: if True, incoming namespace names will be made absolute if not yet the case
		@note: the namespace does not need to exist, but many methods will not work if so.
		NamespaceObjects returned by methods of this class are garantueed to exist"""

		if namespacepath != cls.rootNamespace:
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
		@return: the create Namespace object"""
		newns = cls( namespaceName )

		if newns.exists():		 # skip work
			return newns

		cleanup = CallOnDeletion( None )
		if newns.isAbsolute():	# assure root is current if we are having an absolute name
			previousns = Namespace.getCurrent()
			cls( Namespace.rootNamespace ).setCurrent( )
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

	def moveObjects( self, targetNamespace, force = True, autocreate=True ):
		"""Move objects from this to the targetNamespace
		@param force: if True, namespace clashes will be resolved by renaming, if false
		possible clashes would result in an error
		@param autocreate: if True, targetNamespace will be created if it does not exist yet
		@todo: Implement undo !"""
		targetNamespace = self.__class__( targetNamespace )
		if autocreate and not targetNamespace.exists( ):
			targetNamespace = Namespace.create( targetNamespace )

		cmds.namespace( mv=( self, targetNamespace ), force = force )

	def delete( self, move_to_namespace = rootNamespace, autocreate=True ):
		"""Delete this namespace and move it's obejcts to the given move_to_namespace
		@param move_to_namespace: if None, the namespace to be deleted must be empty
		If Namespace, objects in this namespace will be moved there prior to namespace deletion
		move_to_namespace must exist
		@param autocreate: if True, move_to_namespace will be created if it does not exist yet
		@note: can handle sub-namespace properly
		@raise RuntimeError:
		@todo: Implement undo !"""
		if self == self.rootNamespace:
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
			self.moveObjects( move_to_namespace, autocreate=autocreate )

		# finally delete the namespace
		cmds.namespace( rm=self )

	# need to fully qualify it as undo is initialized after us ...
	@undo.undoable
	def setCurrent( self ):
		"""Set this namespace to be the current one - new objects will be put in it
		by default"""
		# THIS IS FASTER !
		melop = undo.GenericOperation( )
		melop.addDoit( cmds.namespace, set = self )
		melop.addUndoit( cmds.namespace, set = Namespace.getCurrent() )
		melop.doIt()

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
	def getUnique( cls, basename, incrementFunc = defaultIncrFunc ):
		"""Create a unique namespace
		@param basename: the base name of the namespace, like ":mynamespace"
		@param incrementFunc: func( basename, index ), returns a unique name generated
		from the basename and the index representing the current iteration
		@return: unique namespace that is garantueed not to exist below the current
		namespace"""
		i = 0
		while True:
			testns = cls( incrementFunc( basename, i ) )
			i += 1

			if not testns.exists():
				return testns
		# END while loop
		raise ValueError( "Should never come here" )

	def exists( self ):
		"""@return: True if this namespace exists"""
		return cmds.namespace( ex=self )

	def isAbsolute( self ):
		"""@return: True if this namespace is an absolut one, defining a namespace
		from the root namespace like ":foo:bar"""
		return self.startswith( self._sep )

	def getParent( self ):
		"""@return: parent namespace of this instance"""
		if self == self.rootNamespace:
			return None

		parent = iDagItem.getParent( self )	# considers children like ":bar" being a root
		if parent == None:	# we are just child of the root namespcae
			parent = self.rootNamespace
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
		#if self == self.rootNamespace:
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
			raise ValueError( "All involved namespaces need to be absoslute: " + self + " , " + basenamespace )

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
			return ( Namespace.rootNamespace, objectname )

		return ( cls( objectname[:rpos] ), objectname[rpos+1:] )


	def _removeDuplicateSep( self, name ):
		"""@return: name with duplicated : removed"""
		return self.re_find_duplicate_sep.sub( self._sep, name )

	def substitute( self, find_in, replacement ):
		"""@return: string with our namespace properly substituted with replacement such
		that the result is a properly formatted object name ( with or without namespace
		depenging of the value of replacement
		As this method is based on string replacement, self might as well match sub-namespaces
		if it is relative
		@note: if replacement is an empty string, it will effectively cut the matched namespace
		off the object name
		@note: handles replacement of subnamespaces correctly as well
		@note: as it operates on strings, the actual namespaces do not need to exist"""
		# special case : we are root
		if self == Namespace.rootNamespace:
			return self._removeDuplicateSep( self.__class__( replacement, absolute=False ) + find_in )

		# do the replacement
		return self._removeDuplicateSep( find_in.replace( self, replacement ) )

	@classmethod
	def substituteNamespace( cls, thisns, find_in, replacement ):
		"""Same as L{substitute}, but signature might feel more natural"""
		return thisns.substitute( find_in, replacement )

	#} END query methods


	#{ Iterators

	@classmethod
	def _getNamespaceObjects( cls, namespace, sellist, curdepth, maxdepth, asStrings ):
		"""if as strings is given, the sellist returned will be a list of strings"""
		if maxdepth and not ( curdepth < maxdepth ):
			return

		namespace.setCurrent()
		objs = cmds.namespaceInfo( lod=1 )
		if objs:
			# REMOVE INVALID OBJECTS
			############################
			# its very annoying that maya wholeheartedly retuns special objects that noone can work with
			if namespace == Namespace.rootNamespace:
				
				forbiddenlist = [ "groundPlane", "groundPlane_transform", "world", "CubeCompass", "Manipulator1", "UniversalManip", "defaultCreaseDataSet" ]
				for item in forbiddenlist:
					try:
						objs.remove( item )
					except ValueError:
						# this list contains objects that might not exist in all scenes or all maya versions 
						pass 
					# END exception handling
				# END for each item to remove
			# END forbidden object removal


			# OBJECT OUTPUT HANDLING
			#########################
			if asStrings:
				sellist.extend( objs )
			else:
				for obj in objs:
					try:
						sellist.add( obj )
					except RuntimeError:
						# sometimes there are invalid or special objects that cannot be put onto
						# the list apparently ... nothing will always work here :/
						print "Failed to put object '%s' onto selection list" % obj
					# END add exception handling
				# END for each obj in string object list
			# END if selection list is required
		# END if there are objects

		for child in namespace.getChildren():	# children are abolute
			Namespace._getNamespaceObjects( child, sellist, curdepth + 1, maxdepth, asStrings )
	# END lod recursive method


	def getSelectionList( self, depth=1, as_strings = False, child_predicate = lambda x: True  ):
		"""@return: selection list containing all objects in the namespace ( or list of strings if
		as_strings is True )
		@param depth: if 1, only objects in this namespace will be returned
		if 0, all subnamespaces will be included as well,
		if 0<depth<x include all objects up to the x subnamespace
		@param child_predicate: return True for all childnamespaces to include in your query
		@param as_strings: if true, the selection list returned will be a list of strings instead
		of a selection list object.
		Use L{listObjectStrings} to have a more specific name for the method
		@note: if the namespace does not exist, an empty selection list will be returned
		@note: use iterSelectionList to operate on it"""
		sellist = None
		if as_strings:
			sellist = []
		else:
			sellist = api.MSelectionList()

		if not self.exists():
			return sellist

		# FILL SELLIST
		#################
		# assure we do not record this and alter the undoqueue
		disableUndo = MuteUndo()
		curns = self.getCurrent()		# store for later
		self._getNamespaceObjects( self, sellist, 0, depth, as_strings )
		curns.setCurrent()				# reset current

		return sellist

	def listObjectStrings( self, **kwargs ):
		"""As above, but returns a list of strings instead of as selection list
		@note: this convenience method supports all arguments as L{getSelectionList}"""
		kwargs[ "as_strings" ] = 1
		return self.getSelectionList( **kwargs )


	def iterObjects( self, depth=1, child_predicate = lambda x: True, **kwargs ):
		"""As above, but returns iterator on all objects in the namespace
		@param **kwargs: given to the selection list iterator
		@note: this is a convenience method
		@note: the method is inherently inefficient as a full list of object names
		in the naemspace will be retrieved anyway"""
		from nodes.it import iterSelectionList
		sellist = self.getSelectionList( depth = depth, child_predicate = child_predicate, as_strings = False )

		return iterSelectionList( sellist, **kwargs )


	#} END objects
