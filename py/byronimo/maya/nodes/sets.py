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

class ObjectSet:
	""" Extended and more convenient object set interface dealing with Nodes ( and 
	provides the original MFnSet interface as well"""
	__metaclass__ = types.MetaClassCreatorNodes
	kReplace, kAdd, kRemove = range( 3 )
	
	#{ Partition Handling 
	
	@undoable 
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
	
	#{ Set Operations 
	
	
	
	#} END set operations 
	
	
class Partition:
	"""Deal with common set <-> partition interactions"""
	__metaclass__ = types.MetaClassCreatorNodes
	
	#{ Set Membership 
	
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
