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
		
		# ADD PARTITION
		####################
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
		
		
		# PARTITIONS 
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
		
