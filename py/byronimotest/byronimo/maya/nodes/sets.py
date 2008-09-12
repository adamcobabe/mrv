"""B{byronimotest.byronimo.maya.nodes.sets}

Test sets and partitions

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


import unittest
import byronimo.maya.nodes as nodes
import byronimo.maya.nodes.iterators as iterators 
import maya.cmds as cmds
import maya.OpenMaya as api


class TestSets( unittest.TestCase ):
	""" Test set and partition handling """
	
	def test_createAddRemove( self ):
		"""byronimo.maya.nodes.sets: create,add and remove"""
		set1 = nodes.createNode( "set1", "objectSet" )
		set2 = nodes.createNode( "set2", "objectSet" )
		set3 = nodes.createNode( "set3", "objectSet" )
		prt1 = nodes.createNode( "partition1", "partition" )
		prt2 = nodes.createNode( "partition2", "partition" )
		
		# SET PARTITION HANDLING
		#########################
		self.failUnless( len( set1.getPartitions( ) ) == 0 )
		set1.setPartition( prt1, set1.kReplace )
		self.failUnless( len( set1.getPartitions() ) == 1 )
		self.failUnless( set1.getPartitions()[0] == prt1 )
		
		# add same again
		set1.setPartition( prt1, set1.kAdd )
		self.failUnless( len( set1.getPartitions() ) == 1 )
		
		# remove
		set1.setPartition( prt1, set1.kRemove )
		self.failUnless( len( set1.getPartitions( ) ) == 0 )
		
		# remove again
		set1.setPartition( prt1, set1.kRemove )
		
		
		# PARTITION MEMBER HANDLING 
		# add multiple sets
		prt1.addSets( [ set1, set2 ] )
		self.failUnless( len( prt1.getMembers() ) == 2 )
		
		# add again
		prt1.addSets( [ set1, set2 ] )
		
		prt1.removeSets( [ set1, set2] )
		self.failUnless( len( prt1.getMembers() ) == 0 )
		
		# remove again
		prt1.removeSets( [ set1, set2] )
		
		
		prt2.addSets( [ set1, set2] )
		
		# replace multiple  
		prt2.replaceSets( [ set3 ] )
		
		
		
	def _getMemberList( self ):
		"""@return: object list with all types"""
		persp = nodes.Node( "persp" )
		front = nodes.Node( "front" )
		rg = nodes.Node( "defaultRenderGlobals" )
		ik = nodes.Node( "ikSystem" )
		s2 = nodes.Node( "defaultObjectSet" )
		return [ ik, persp, persp.translate, rg._apiobj, front._apidagpath, s2 ]
		
	def test_memberHandling( self ):
		"""byronimo.maya.nodes.sets: add/remove members from all kinds of inputs"""
		s = nodes.createNode( "memberSet", "objectSet" )
		
		# ADD/REMOVE SINGLE MEMBER 
		####################
		# add Node ( dgnode )
		memberlist = self._getMemberList( )
		
		for i,member in enumerate( memberlist ):
			s.addMember( member )
			self.failUnless( s.getMembers( ).length() == i+1 )
			self.failUnless( s.isMember( member ) )
			cmds.undo() 
			self.failUnless( s.getMembers( ).length() == i )
			cmds.redo()
		# end for each member 
		
		# clear the set by undoing it all 
		for i in range( len( memberlist ) ):
			cmds.undo()
		
		self.failUnless( s.getMembers().length() == 0 )
		
		# get it back 
		for i in range( len( memberlist ) ):
			cmds.redo()
			
		self.failUnless( s.getMembers().length() == len( memberlist ) )
		
		# remove all members
		for i,member in enumerate( memberlist ):
			s.removeMember( member )
		
		self.failUnless( s.getMembers().length() == 0 )
		
		# ADD/REMOVE MULTIPLE MEMBER 
		######################
		# add node list
		s.addMembers( memberlist )
		self.failUnless( s.getMembers().length() == len( memberlist ) )
		
		s.clear()
		self.failUnless( s.getMembers().length() == 0 )
		
		# Add selection listx
		sellist = nodes.toSelectionList( memberlist )
		s.addMembers( sellist )
		self.failUnless( s.getMembers().length() == sellist.length() )
		
		# remove members from sellist
		s.removeMembers( sellist )
		self.failUnless( s.getMembers().length() == 0 )
		
	def test_setOperations( self ):
		"""byroniom.maya.nodes.sets: unions, intersections, difference, overloaded ops"""
		memberlist = self._getMemberList( )
		s3 = nodes.createNode( "anotherObjectSet", "objectSet" )
		s = nodes.Node( "memberSet" )
		s.clear()
		s.addMembers( memberlist )
		
		side = nodes.Node( "side" )
		s2 = nodes.createNode( "memberSet2", "objectSet" )
		s2.addMember( side )
		
		# UNION
		########
		# with set
		sellist = s.getUnion( s2 )
		self.failUnless( sellist.length() == len( memberlist ) + 1 )
		
		# with sellist - will create temp set 
		sellist = s.getUnion( s2.getMembers() )
		self.failUnless( sellist.length() == len( memberlist ) + 1 )
		self.failUnless( not nodes.objExists( "set4" ) )		# tmp set may not exist
		 
		# with multiple object sets
		s.getUnion( [ s2, s3 ] )
		
		list( s.iterUnion( s2 ) )
		
		# INTERSECTION
		###############
		fewmembers = memberlist[:3]
		s2.addMembers( fewmembers )
		
		# with set
		sellist = s.getIntersection( s2 )
		self.failUnless( sellist.length() == len( fewmembers ) )
		
		# with sellist
		sellist = s.getIntersection( fewmembers ) 
		self.failUnless( sellist.length() == len( fewmembers ) )
		
		# with multi sets 
		s3.addMembers( fewmembers )
		sellist = s.getIntersection( [ s2, s3 ] ) 
		self.failUnless( sellist.length() == len( fewmembers ) )
		
		list( s.iterIntersection( s2 ) )
		
		# DIFFERENCE 
		#############
		# with set 
		s2.removeMember( side )
		sellist = s.getDifference( s2 )
		self.failUnless( s.getMembers().length() - s2.getMembers().length() == sellist.length() )
		
		# with objects  
		sellist = s.getDifference( list( s2.iterMembers() ) )
		self.failUnless( s.getMembers().length() - s2.getMembers().length() == sellist.length() )
		
		# with sellist 
		sellist = s.getDifference( s2.getMembers() )
		
		# with multiple sets
		s3.clear()
		s3.addMember( nodes.Node( "front" ) )
		sellist = s.getDifference( [ s2, s3 ] )
		
		self.failUnless( len( list( s.iterDifference( [ s2, s3 ] ) ) ) == s.getDifference( [ s2, s3 ] ).length() )
		self.failUnless( s.getMembers().length() - s2.getMembers().length() - s3.getMembers().length() == sellist.length() )
		
	def test_partitions( self ):
		"""byronimo.maya.nodes.sets: test partition constraints"""
		self.fail()
		
		
