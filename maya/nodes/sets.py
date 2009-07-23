# -*- coding: utf-8 -*-
"""B{mayarv.nodes.sets}

Contains improved clases for set and partition editing 

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
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
undo = __import__( "byronimo.maya.undo", globals(), locals(),[ 'undo' ] )
import iterators


#{ Exceptions 
class ConstraintError( RuntimeError ):
	"""Thrown if a partition does not allow objects to be added, and the addition 
	was not forced, and failure was not ignored as well"""
#} 


class ObjectSet:
	""" Extended and more convenient object set interface dealing with Nodes ( and 
	provides the original MFnSet interface as well
	"""                                                               
	__metaclass__ = types.MetaClassCreatorNodes
	kReplace, kAdd,kAddForce, kRemove = range( 4 )
	
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
		
	
	def _forceMembership( self, member, component, is_single_member, ignore_failure ):
		"""Search all sets connected to our partitions 
		for intersecting members and remove them.
		Finally dd the members in question to us again
		@param member: can be selection list or MObject, MDagPath, MPlug
		@return: self if everything is fine"""
		for partition in self.getPartitions():
			for otherset in partition.getSets():
				if is_single_member:
					otherset.removeMember( member, component = component )
				else:
					otherset.removeMembers( otherset.getIntersection( member, sets_are_members = True ) )
				# END single member handling 
			# END for each set in partition           
		# END for each partition
		
		# finally add the member to our set once more - now it should work 
		# do not risk recursion though by setting everything to ignore errors 
		if isinstance( member, api.MSelectionList ):
			return self._addRemoveMembers( member, self.kAdd, ignore_failure )
		else:
			return self._addRemoveMember( member, component, self.kAdd, ignore_failure )
			
	
	def _checkMemberAddResult( self, member, component, mode, ignore_failure, is_single_member ):
		"""Check whether the given member has truly been added to our set
		and either force membership or raise and exception
		@param is_single_member: if True, member can safely be assumed to be a single member, 
		this speeds up operations as we do not have to use multi-member tests"""
		if mode in ( self.kAdd, self.kAddForce ):
			# do we have to check the result ?
			if mode == self.kAdd and ignore_failure:
				return self
				
			# check result - member can be MObject, MDagPath, plug, or selection list 
			numMatches = 1
			if isinstance( member, api.MSelectionList ):
				numMatches = member.length()
				
			# CHECK MEMBERS
			not_all_members_added = True
			if is_single_member:
				not_all_members_added = not self.isMember( member, component = component )
			else:
				not_all_members_added = self.getIntersection( member, sets_are_members = True ).length() != numMatches
				
			if not_all_members_added:
				if mode == self.kAddForce:
					return self._forceMembership( member, component, is_single_member, ignore_failure )
				
				# if we are here, we do not ignore failure, and raise  
				raise ConstraintError( "At least some members of %r could not be added to %r due to violation of exclusivity constraint" % (member,self) )
				
			# END if added members are not yet available
		# END if mode is add or forced add 
		return self
			
	
	def _addRemoveMember( self, member, component, mode, ignore_failure ):
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
			args.append( component )
		# END component handling 
		
		# swap functions if we remove the node
		if mode == ObjectSet.kRemove:
			tmp = undoitfunc
			undoitfunc = doitfunc
			doitfunc = tmp
		# END variable switching
			
		op.addDoit( doitfunc, *args )
		op.addUndoit( undoitfunc, *args )
		op.doIt( )
		
		return self._checkMemberAddResult( member, component, mode, ignore_failure, True )
		
	def _addRemoveMembers( self, members, mode, ignore_failure ):
		"""Add or remove the members to the set
		@param mode: kRemove or kAdd or kAddForce"""
		sellist = members
		if not isinstance( sellist, api.MSelectionList ):
			sellist = nodes.toSelectionList( sellist )
			
		lsellist = sellist.length()
		if not lsellist:
			return self
			
		# if there is only one member, use our single member function 
		# as it will be faster when checking for partition constraints
		if lsellist == 1:
			return self._addRemoveMember( iterators.iterSelectionList( sellist, asNode = 0 ).next(), api.MObject(), mode, ignore_failure )
				
		# prepare operation
		mfninst = self._mfncls( self._apiobj )
		doitfunc = mfninst.addMembers
		undoitfunc = mfninst.removeMembers
		
		# swap functions if we remove the node
		if mode == ObjectSet.kRemove:
			tmp = undoitfunc
			undoitfunc = doitfunc
			doitfunc = tmp
		# END function swapping
			
		op = undo.GenericOperation()	
		op.addDoit( doitfunc, sellist )
		op.addUndoit( undoitfunc, sellist )
		op.doIt()
		
		return self._checkMemberAddResult( sellist, None, mode, ignore_failure, False )
	
	@undoable
	def clear( self ):
		"""Clear the set so that it will be empty afterwards"""
		self.removeMembers( self.getMembers() )
	
	@undoable
	def addMember( self, member, component = api.MObject(), force = False, ignore_failure = False ):
		"""Add the item to the set
		@param member: Node, MObject, MDagPath or plug
		@param force: if True, member ship will be forced by removing the member in question 
		from the other set connected to our partitions
		@param ignore_failure: if True, a failed add due to partion constraints will result in an 
		exception, otherwise it will be silently ignored. Ignored if if force is True
		@param compoent: if member is a dagnode, you can specify a component instance 
		of type component instance ( Single|Double|TripleIndexComponent )
		@todo: handle components - currently its only possible when using selection lists
		@return: self """
		mode = self.kAdd
		if force:
			mode = self.kAddForce
		return self._addRemoveMember( member, component, mode, ignore_failure )		
		
		
	@undoable
	def removeMember( self, member, component = api.MObject()  ):
		"""Remove the member from the set
		@param member: member of the list, for types see L{addMember}"""
		return self._addRemoveMember( member, component, ObjectSet.kRemove, True )
	
	@undoable
	def addMembers( self, nodes, force = False, ignore_failure = False ):
		"""Add items from iterable or selection list as members to this set
		@param nodes: MSelectionList or list of Nodes and Plugs
		@param force: see L{addMember}
		@param ignore_failure: see L{addMember}
		@return: self """
		mode = self.kAdd
		if force:
			mode = self.kAddForce
		return self._addRemoveMembers( nodes, mode, ignore_failure )
	
	@undoable
	def removeMembers( self, nodes ):
		"""Remove items from iterable or selection list from this set
		@param nodes: see L{addMembers}
		@return: self """
		return self._addRemoveMembers( nodes, ObjectSet.kRemove, True )
			
	@undoable
	def setMembers( self, nodes, mode, **kwargs ):
		"""Adjust set membership for nodes
		@param node: items to handle, supports everything that L{addMembers} does
		@param **kwargs: arguments passed to L{addMembers} or L{removeMembers}"""
		if mode == self.kReplace:
			self.clear()
			mode = self.kAdd
		# END replace 
			
		if mode == self.kAdd:
			return self.addMembers( nodes, **kwargs )
			
		# remove 
		return self.removeMembers( nodes, **kwargs )
								   
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
		
	def iterMembers( self, *args, **kwargs ):
		"""Iterate members of this set
		@note: All keywords of iterMembers are supported
		@note: if 'handlePlugs' is False, the iteration using a filter type will be faster
		@note: handleComponents will allow component iteration - see the iterator documentation"""
		return iterators.iterSelectionList( self.getMembers( ), *args, **kwargs ) 
	
	def isMember( self, obj, component = api.MObject() ):
		"""@return: True if obj is a member of this set
		@param component is given, the component must be fully part of the set 
		for the object ( dagNode ) to be considered part of the set
		@note: all keywords of L{iterators.iterSelectionList} are supported
		@note: ismember does not appear to be working properly with component assignments.
		It returns true for components that are not actually in the givne shading group"""
		if not component.isNull():
			return self._mfncls( self._apiobj ).isMember( self._toMemberObj( obj ), component )
		return self._mfncls( self._apiobj ).isMember( self._toMemberObj( obj ) )
	
	def __contains__( self, obj ):
		"""@return: True if the given obj is member of this set"""
		return self.isMember( obj )
		
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
			# assure we release members before - otherwise they might be deleted 
			# as well if it is empty sets !
			mfnset = api.MFnSet( self.setobj )
			mfnset.clear()
			del( mfnset )
			dgmod = api.MDGModifier()
			dgmod.deleteNode( self.setobj )
			dgmod.doIt()
		
		
	@classmethod
	def _toValidSetOpInput( cls, objects, sets_are_members = False ):
		"""Method creating valid input for the union/intersection or difference methods
		@note: it may return a temporary set that will delete itself once the wrapper object
		is being destroyed
		@param sets_are_members: see L{getUnion}
		@note: set """
		if isinstance( objects, (tuple, list) ):
			# MOBJECTARRAY OF SETS
			if not objects:		# emty list, return empty mobject array
				return api.MObjectArray( )
				
			if not sets_are_members and isinstance( objects[ 0 ], ObjectSet ):
				objarray = api.MObjectArray( )
				for setNode in objects: 
					objarray.append( setNode._apiobj )
				return objarray
			else:
				# create selection list from nodes and use a tmpSet 
				sellist = nodes.toSelectionList( objects )
				return cls._TmpSet( sellist )
		# END list handling
		
		# still here, handle a single object
		singleobj = objects
		if isinstance( singleobj, api.MSelectionList ):	# Selection List ?
			return cls._TmpSet( singleobj )
			
		if not sets_are_members and isinstance( singleobj, ObjectSet ):				# Single Object Set ?
			return singleobj._apiobj
			
		if isinstance( singleobj, cls._TmpSet ):										# single set object 
			return singleobj.setobj
			
		if isinstance( singleobj, api.MObject ) and singleobj.hasFn( api.MFn.kSet ):	# MObject object set ?
			return singleobj
			
		# assume best for MObject arrays - usually we pass it in ourselves 
		if isinstance( singleobj, api.MObjectArray ):
			return singleobj
		
		# Can be Node, MDagPath or plug or MObject ( not set )
		return cls._toValidSetOpInput( ( singleobj, ), sets_are_members = sets_are_members ) # will create a tmpset then
		
		raise TypeError( "Type InputObjects for set operation ( %r ) was not recognized" % objects )
		
	
	def _applySetOp( self, objects, opid, **kwargs ):
		"""Apply the set operation with the given id"""
		# have to do it in steps to assure our temporary set will be deleted after 
		# the operation has finished
		obj = fobj = self._toValidSetOpInput( objects, **kwargs )
		outlist = api.MSelectionList()
		if isinstance( obj, self._TmpSet ):
			fobj = obj.setobj	# need to keep reference to _TmpSet until it was used
		
		mfnset = self._mfncls( self._apiobj )
		if opid == "union":
			mfnset.getUnion( fobj, outlist )
		elif opid == "intersection":
			mfnset.getIntersection( fobj, outlist )
		else:
			raise AssertionError( "Invalid Set Operation: %s" % opid )
			
		return outlist

	@classmethod
	def getTmpSet( cls, objects, sets_are_members = False ):
		"""@return: temporary set that will delete itself once it's reference count
		reaches 0. Use rval.setobj to access the actual set, as the returned object is 
		just a hanlde to it. The handle is a valid input to the set functions as well
		@param objects, sets_are_members: see L{getUnion} 
		@note: useful if you want to use the set member union, intersection or substraction 
		methods efficiently on many sets in a row - these internally operate on a set, thus 
		it is faster to use them with another set from the beginning to prevent creation of intermediate 
		sets"""
		return cls._toValidSetOpInput( objects, sets_are_members = sets_are_members )

	def getUnion( self, objects, sets_are_members = False  ):
		"""Create a union of the given items with the members of this set
		@param objects: an ObjectSet, an MObject of an object set, a list of ObjectSets 
		or a list of wrapped Objects or an MSelectionList or a single wrapped object . 
		If you have objects in a list as well as sets
		themselves, objects must come first as the operation will fail otherwise.
		@param sets_are_members: if True, objects can contain sets, but they should not be treated 
		as sets to apply the set operation with, they should simply be members of this set, and 
		thus need to be wrapped into a tmp set as well
		@return: MSelectionList of all objects of self and objects """
		return self._applySetOp( objects, "union", sets_are_members = sets_are_members )
		
	def getIntersection( self, objects, sets_are_members = False  ):
		"""As L{getUnion}, but returns the intersection ( items in common ) of this 
		set with objects
		@param objects: see L{getUnion}
		@param sets_are_members: see L{getUnion}
		@return: MSelectionList of objects being in self and in objects"""
		return self._applySetOp( objects, "intersection", sets_are_members = sets_are_members )
		
	def getDifference( self, objects, sets_are_members = False  ):
		"""@return: the result of self - objects, thus objects will be substracted from our obejcts 
		@param objects: see L{getUnion}
		@param sets_are_members: see L{getUnion}
		@return: MSelectionList containing objects of self not being in objects list"""
		# have to do the intersections individually and keep them 
		intersections = []
		obj = fobj = self._toValidSetOpInput( objects, sets_are_members = sets_are_members )
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
	
	

class ShadingEngine:
	"""Provides specialized methods able to deal better with shaders
	than the default implementation.
	@todo: Force exclusivity must be a little more elaborate - this could be overwritten
	and reimplemented to take care of the details"""
	
	__metaclass__ = types.MetaClassCreatorNodes
	
	
	
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
		"""@return: sets being member of this partition
		@note: have to filter the members as there might be non-set connections 
		in referenced environments"""
		out = list()
		for plug in self.sets.getInputs():
			node = plug.getNode()
			if not node.hasFn( api.MFn.kSet ):
				continue
			out.append( node )
		# END for each plug in set connections
		return out
		
		
	#}END set membership
	
	#{ Name Remapping
	addSets = addMember
	removeSets = removeMember
	replaceSets = replaceMember
	getSets = getMembers
	#} END name remapping 
