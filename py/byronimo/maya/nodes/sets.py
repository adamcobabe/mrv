"""B{byronimo.nodes.sets}

Contains improved clases for set and partition editing 

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


import base as nodes
import types
import maya.OpenMaya as api
import maya.cmds as cmds
import byronimo.maya.namespace as namespace
undo = __import__( "byronimo.maya.undo", globals(), locals(),[ 'undo' ] )
import iterators

class ObjectSet:
	""" Extended and more convenient object set interface dealing with Nodes ( and 
	provides the original MFnSet interface as well
	"""                                                               
	__metaclass__ = types.MetaClassCreatorNodes
	kReplace, kAdd, kRemove = range( 3 )
	
	#{ Partition Handling 
	
	def getPartitions( self ):
		"""@return: list of Nodes of partitions the entity is set is part of"""
		return [ p.getNode() for p in self.partition.p_outputs ]
		 
	
	@undoable 	
	def setPartition( self, partition, mode ):
		"""Add, add exclusive or remove the given partition from our partition list
		@param partition: Node, representing the partition, or a list of such
		@param mode: 	0 = replace
						1 = add 
						2 = remove 
		@return: self for chained operations
		@note: use the supplied enumeration to specify the mode"""
		# convert to list
		prts = partition
		if isinstance( partition, Partition ):
			prts = [ partition ]
			
		if mode == self.kReplace:
			self.setPartition( self.getPartitions( ), self.kRemove )
			mode = self.kAdd		# now the partitions have to be added
			# go ahead with the add
		# END replace mode 
			
		if mode == self.kRemove:
			for part in prts:
				self.partition.disconnectNode( part )
			return self
		# END remove mode 
				
		if mode == self.kAdd:
			# only allow to be connected once 
			for part in prts:
				self.partition.connectToArray( part.sets, exclusive_connection = True )
			# END for each partition to be added
			return self
		# END add mode 
			
		raise AssertionError( "Invalid mode given: %i" % mode )
				
	#} END partition handling
	
	#{ Member Editing
	
	def _toMemberObj( self, member ):
		"""Convert member to a valid member object ( MObject, DagPath or Plug )"""
		memberobj = member
		
		if isinstance( member, nodes.DagNode ):
			memberobj = member._apidagpath
		elif isinstance( member, nodes.DependNode ):
			memberobj = member._apiobj
			
		return memberobj
		
	
	def _addRemoveMember( self, member, mode ):
		"""Add or remove the member with undo support
		@param mode: kRemove or kAdd"""
		memberobj = self._toMemberObj( member )
			
		op = undo.GenericOperation()
		mfninst = self._mfncls( self._apiobj )
		doitfunc = mfninst.addMember
		undoitfunc = mfninst.removeMember
		
		# for dag paths, append empty component mobjects
		args = [ memberobj ]
		if isinstance( memberobj, api.MDagPath ):	# add component ( default None )
			args.append( api.MObject() )
		
		# swap functions if we remove the node
		if mode == ObjectSet.kRemove:
			tmp = undoitfunc
			undoitfunc = doitfunc
			doitfunc = tmp
		# END variable switching
			
		op.addDoit( doitfunc, *args )
		op.addUndoit( undoitfunc, *args )
		op.doIt( )
		return self
		
	def _addRemoveMembers( self, members, mode ):
		"""Add or remove the members to the set
		@param mode: kRemove or kAdd"""
		op = undo.GenericOperation()
		sellist = members
		if not isinstance( sellist, api.MSelectionList ):
			sellist = nodes.toSelectionList( sellist )
		
		# prepare operation
		mfninst = self._mfncls( self._apiobj )
		doitfunc = mfninst.addMembers
		undoitfunc = mfninst.removeMembers
		
		# swap functions if we remove the node
		if mode == ObjectSet.kRemove:
			tmp = undoitfunc
			undoitfunc = doitfunc
			doitfunc = tmp
			
			
		op.addDoit( doitfunc, sellist )
		op.addUndoit( undoitfunc, sellist )
		op.doIt()
		return self
	
	@undoable
	def addMember( self, member ):
		"""Add the item to the set
		@param member: Node, MObject, MDagPath or plug
		@todo: handle components - currently its only possible when using selection lists
		@return: self """
		return self._addRemoveMember( member, ObjectSet.kAdd )
		
	@undoable
	def removeMember( self, member ):
		"""Remove the member from the set
		@param member: member of the list, for types see L{addMember}"""
		return self._addRemoveMember( member, ObjectSet.kRemove )
	
	@undoable
	def addMembers( self, nodes ):
		"""Add items from iterable or selection list as members to this set
		@param nodes: MSelectionList or list of Nodes and Plugs
		@return: self """
		return self._addRemoveMembers( nodes, ObjectSet.kAdd )
	
	@undoable
	def removeMembers( self, nodes ):
		"""Remove items from iterable or selection list from this set
		@param nodes: see L{addMembers}
		@return: self """
		return self._addRemoveMembers( nodes, ObjectSet.kRemove )
			
	#} END member editing
	
	
	#{ Member Query 
	
	def getMembers( self, flatten = False ):
		"""@return: MSelectionList with members of this set
		@param flatten: if True, members that are objectSets themselves will be resolved to their 
		respective members
		@note: the members are ordinary api objects that still need to be wrapped
		@note: use iterMembers to iterate the members as wrapped Nodes"""
		sellist = api.MSelectionList()
		self._mfncls( self._apiobj ).getMembers( sellist, flatten )
		return sellist
		
	def iterMembers( self, **kwargs ):
		"""Iterate members of this set
		@note: All keywords of iterMembers are supported
		@note: if 'handlePlugs' is False, the iteration using a filter type will be faster"""
		return iterators.iterSelectionList( self.getMembers( ), **kwargs ) 
	
	def isMember( self, obj ):
		"""@return: True if obj is a member of this set
		@note: all keywords of L{iterators.iterSelectionList} are supported"""
		return self._mfncls( self._apiobj ).isMember( self._toMemberObj( obj ) )
	
	#} END member query 
	
	
	#{ Set Operations
	
	class _TmpSet( object ):
		"""Temporary set that will delete itself once its python destructor is called"""
		__slots__ = "setobj"
		def __init__( self, sellist ):
			dgmod = api.MDGModifier( )
			self.setobj = dgmod.createNode( "objectSet" )
			dgmod.doIt( )
			# add members
			mfnset = api.MFnSet( self.setobj )
			mfnset.addMembers( sellist )
			
		def __del__( self ):
			"""Delete our own set upon deletion"""
			dgmod = api.MDGModifier()
			dgmod.deleteNode( self.setobj )
			dgmod.doIt()
		
		
	def _toValidSetOpInput( self, objects ):
		"""Method creating valid input for the union/intersection or difference methods
		@note: it may return a temporary set that will delete itself once the wrapper object
		is being destroyed
		@note: set """
		if isinstance( objects, (tuple, list) ):
			# MOBJECTARRAY OF SETS
			if isinstance( objects[ 0 ], ObjectSet ):
				objarray = api.MObjectArray( )
				for setNode in objects: 
					objarray.append( setNode._apiobj )
				return objarray
			else:
				# create selection list from nodes and use a tmpSet 
				sellist = nodes.toSelectionList( objects )
				return self._TmpSet( sellist )
		# END list handling
		
		# still here, handle a single object
		singleobj = objects
		if isinstance( singleobj, api.MSelectionList ):
			return self._TmpSet( singleobj )
			
		if isinstance( singleobj, ObjectSet ):
			return singleobj._apiobj
			
		if isinstance( singleobj, api.MObject ) and singleobj.hasFn( api.MFn.kSet ):
			return singleobj
			
		# assume best for MObject arrays - usually we pass it in ourselves 
		if isinstance( singleobj, api.MObjectArray ):
			return singleobj
			
		raise TypeError( "Type InputObjects for set operation ( %r ) was not recognized" % objects )
		
	
	def _applySetOp( self, objects, opid ):
		"""Apply the set operation with the given id"""
		# have to do it in steps to assure our temporary set will be deleted after 
		# the operation has finished
		obj = fobj = self._toValidSetOpInput( objects )
		outlist = api.MSelectionList()
		if isinstance( obj, self._TmpSet ):
			fobj = obj.setobj	# need to keep reference to _TmpSet until it was used
		
		mfnset = self._mfncls( self._apiobj )
		if opid == "union":
			mfnset.getUnion( fobj, outlist )
		elif opid == "intersection":
			mfnset.getIntersection( fobj, outlist )
			
		return outlist

	def getUnion( self, objects ):
		"""Create a union of the given items with the members of this set
		@param objects: an ObjectSet, an MObject of an object set, a list of ObjectSets 
		or a list of wrapped Objects or an MSelectionList. 
		If you have objects in a list as well as sets
		themselves, objects must come first as the operation will fail otherwise.
		@return: MSelectionList of all objects of self and objects """
		return self._applySetOp( objects, "union" )
		
	def getIntersection( self, objects ):
		"""As L{getUnion}, but returns the intersection ( items in common ) of this 
		set with objects
		@return: MSelectionList of objects being in self and in objects"""
		return self._applySetOp( objects, "intersection" )
		
	def getDifference( self, objects ):
		"""@return: the result of self - objects, thus objects will be substracted from our obejcts 
		@param objecfts: see L{getUnion}
		@return: MSelectionList containing objects of self not being in objects list"""
		# have to do the intersections individually and keep them 
		intersections = []
		obj = fobj = self._toValidSetOpInput( objects )
		outlist = api.MSelectionList()
		if isinstance( obj, self._TmpSet ):
			fobj = obj.setobj	# need to keep reference to _TmpSet until it was used
		
		# either we have a single _tmpSet, or a list of sets 
		#if not isinstance( fobj , ( tuple, list ) ):
		if not hasattr( fobj, '__iter__' ):
			fobj = [ fobj ]
		
		for item in fobj:
			intersections.append( self.getIntersection( item ) )
		
		# remove intersecting members temporarily 
		for its in intersections:
			self.removeMembers( its )
			
		difference = self.getMembers()
		
		# add members again 
		for its in intersections:
			self.addMembers( its )
			
		return difference
		
	def iterUnion( self, setOrSetsOrObjects, **kwargs ):
		"""As getUnion, but returns an iterator
		@param **kwargs: passed to iterators.iterSelectionList"""
		return iterators.iterSelectionList( self.getUnion( setOrSetsOrObjects ), **kwargs )
		
	def iterIntersection( self, setOrSetsOrObjects, **kwargs ):
		"""As getIntersection, but returns an iterator
		@param **kwargs: passed to iterators.iterSelectionList"""
		return iterators.iterSelectionList( self.getIntersection( setOrSetsOrObjects ), **kwargs )
		
	def iterDifference( self, setOrSetsOrObjects, **kwargs ):
		"""As getDifference, but returns an iterator
		@param **kwargs: passed to iterators.iterSelectionList"""
		return iterators.iterSelectionList( self.getDifference( setOrSetsOrObjects ), **kwargs )
		
	#} END set operations
	
	#{ Operators
	__add__ = getUnion
	__sub__ = getDifference
	__and__ = getIntersection
	#} END operators
	
class Partition:
	"""Deal with common set <-> partition interactions"""
	__metaclass__ = types.MetaClassCreatorNodes
	
	#{ Set Membership 
	
	@undoable
	def _addRemoveMember( self, objectset, mode ):
		sets = objectset
		if isinstance( objectset, ObjectSet ):
			sets = [ objectset ]
			
		for oset in sets:
			oset.setPartition( self, mode )
		# END for each set to add/remove
		
		return self
	
	
	def addMember( self, objectset ):
		"""Add the given objectset or list of sets to the partition
		@param objectset: one or multiple object sets 
		@return: self allowing chained calls"""
		return self._addRemoveMember( objectset, ObjectSet.kAdd )
		
	def removeMember( self, objectset ):
		"""Remove the given objectset from the partition
		@param objectset: one or multiple object sets 
		@return: self allowing chained calls"""
		return self._addRemoveMember( objectset, ObjectSet.kRemove )
		
	def replaceMember( self, objectset ):
		"""Replace existing objectsets with the given one(s
		@param objectset: one or multiple object sets 
		@return: self allowing chained calls)"""
		return self._addRemoveMember( objectset, ObjectSet.kReplace )
		
	@undoable
	def clear( self ):
		"""remove all members from this partition"""
		for m in self.getMembers():
			self.removeMember( m )
			
	def getMembers( self ):
		"""@return: sets being member of this partition"""
		return [ p.getNode() for p in self.sets.getInputs() ]
		
	#}END set membership
	
	#{ Name Remapping
	addSets = addMember
	removeSets = removeMember
	replaceSets = replaceMember
	getSets = getMembers
	#} END name remapping 
