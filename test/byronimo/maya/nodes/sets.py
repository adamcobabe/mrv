# -*- coding: utf-8 -*-
"""B{mayarvtest.byronimo.maya.nodes.sets}

Test sets and partitions

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


import unittest
import byronimo.maya.nodes as nodes
import byronimo.maya.nodes.iterators as iterators
import maya.cmds as cmds
import maya.OpenMaya as api
import byronimotest.byronimo.maya as common
import byronimo.maya as bmaya
import byronimo.maya.nodes.sets as sets
import byronimotest.byronimo.maya.nodes as ownpackage

class TestSets( unittest.TestCase ):
	""" Test set and partition handling """

	def test_createAddRemove( self ):
		"""byronimo.maya.nodes.sets: create,add and remove"""
		if not ownpackage.mayRun( "sets" ): return
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
		if not ownpackage.mayRun( "sets" ): return
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

		# MULTI-MEMBER UNDO/REDO
		##########################
		s.removeMembers( memberlist )
		self.failUnless( s.getMembers().length() == 0 )
		cmds.undo()
		self.failUnless( s.getMembers().length() == len( memberlist ) )
		cmds.redo()
		self.failUnless( s.getMembers().length() == 0 )

		# add members again
		s.addMembers( memberlist )
		self.failUnless( s.getMembers().length() == len( memberlist ) )
		cmds.undo()
		self.failUnless( s.getMembers().length() == 0 )
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

		cmds.undo()
		self.failUnless( s.getMembers().length() == sellist.length() )

		cmds.redo()
		self.failUnless( s.getMembers().length() == 0 )


		# TEST CLEAR
		#############
		s.addMembers( sellist )
		self.failUnless( s.getMembers().length() == sellist.length() )

		s.clear()
		self.failUnless( s.getMembers().length() == 0 )

		cmds.undo()
		self.failUnless( s.getMembers().length() == sellist.length() )


		# USING SETMEMBERS
		########################
		members = self._getMemberList()
		# replace
		s.setMembers( members[0:2], 0 )
		self.failUnless( s.getMembers().length() == 2 )
		
		# add
		s.setMembers( members[-2:-1], 1 )
		self.failUnless( s.getMembers().length() == 3 )
		
		# remove
		s.setMembers( members[0:2], 2 )
		self.failUnless( s.getMembers().length() == 1 )
		
		cmds.undo()
		self.failUnless( s.getMembers().length() == 3 )

	def test_setOperations( self ):
		"""byroniom.maya.nodes.sets: unions, intersections, difference, overloaded ops"""
		if not ownpackage.mayRun( "sets" ): return
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

		# add 0 members
		s2.addMembers( [] )

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
		if not ownpackage.mayRun( "setsforce" ): return

		# one transform, two sets, one partition
		s1 = nodes.createNode( "ms1", "objectSet" )
		s2 = nodes.createNode( "ms2", "objectSet" )
		p = nodes.createNode( "p1", "partition" )

		s3 = nodes.createNode( "ms3", "objectSet" )
		s4 = nodes.createNode( "ms4", "objectSet" )
		t = nodes.createNode( "my_trans", "transform" )
		t2 = nodes.createNode( "my_trans2", "transform" )

		p.addSets( [ s1, s2 ] )

		# Also adding sets
		################
		# Internally the check for added objects can use intersection operations
		# to see whether objects are actually in there - if there would not be
		# some notion of 'sets_are_members', it would take the members of sets as items for
		# intersection
		for o1, o2 in [ (t,t2), (s3,s4) ]:
			# SINGLE OBJECT
			###############
			multiobj = [ o1, o2 ]
			s1.addMember( o1 )
			self.failUnlessRaises( sets.ConstraintError, s2.addMember, o1 )	# failure, as errors are not ignored
			s2.addMember( o1, ignore_failure = 1 )		# ignore failure

			# FORCE
			s2.addMember( o1, force = 1 )
			self.failUnless( s2.isMember( o1 ) )

			# MULTIPLE OBJECTS
			###################
			self.failUnlessRaises( sets.ConstraintError, s1.addMembers, multiobj )			# fails as t is in s2
			s1.addMembers( [ o2 ] )			# works as t2 is not in any set yet
			self.failUnless( s1.isMember( o2 ) )

			# FORCE all objects into s1
			s1.addMembers( multiobj, force = 1 )
			self.failUnless( s1.getIntersection( multiobj, sets_are_members = 1 ).length() == 2 )


			# and once more
			s1.clear()
			s2.clear()

			for s in s1,s2:
				assert s.getMembers().length() == 0


			s1.addMembers( multiobj )
			self.failUnlessRaises( sets.ConstraintError, s2.addMembers, multiobj, force = False, ignore_failure = False )
			assert s2.getMembers().length() == 0

			s2.addMembers( multiobj, force = False, ignore_failure = 1 )
			assert s2.getMembers().length() == 0

			# now force it
			s2.addMembers( multiobj, force = 1 )
			assert s2.getMembers().length() == 2
		# END for each object


		# SHADER ASSIGNMENTS
		######################
		sphere = nodes.Node( cmds.polySphere( )[0] )[0]
		cube = nodes.Node( cmds.polyCube()[0] )[0]
		multi = ( sphere, cube )
		all_sets = sphere.getConnectedSets( setFilter = sphere.fSets )
		isg = all_sets[0]			# initial shading group
		rp = isg.getPartitions()[0]# render partition

		assert str( isg ).startswith( "initial" )

		snode = nodes.createNode( "mysg", "shadingEngine" )
		snode.setPartition( rp, 1 )

		self.failUnlessRaises( sets.ConstraintError, snode.addMember, sphere )
		self.failUnlessRaises( sets.ConstraintError, snode.addMembers, multi )

		# now force it in
		snode.addMembers( multi, force = 1, ignore_failure = 0 )
		assert snode.getMembers().length() == 2
		assert snode.getIntersection( multi ).length() == 2

	def test_renderPartition( self ):
		"""byronimo.maya.nodes.sets: assure renderpartition works for us"""
		if not ownpackage.mayRun( "setsrenderpartition" ): return

		rp = nodes.Node( "renderPartition" )
		assert len( rp.getSets( ) )		# at least the initial shading group


	def test_z_memberHandlingComps( self ):
		"""byronimo.maya.nodes.sets: member handling with components - needs to run last"""
		if not ownpackage.mayRun( "sets" ): return
		bmaya.Scene.open( common.get_maya_file( "perComponentAssignments.ma" ), force = 1 )
		p1 = nodes.Node( "|p1trans|p1" )
		s1 = nodes.Node( "s1" )					# sphere with face shader assignments
		s2 = nodes.Node( "s2" )					# sphere with one object assignment

		# shading engines
		sg1 = nodes.Node( "sg1" )
		sg2 = nodes.Node( "sg2" )


		# REMOVE AND SET FACE ASSIGNMENTS
		####################################
		# get all sets assignments
		setcomps = p1.getComponentAssignments( setFilter = nodes.Shape.fSetsRenderable )

		for setnode, comp in setcomps:
			# NOTE: must be member in the beginning, but the isMember method does not
			# work properly with components
			if comp.isNull():
				continue

			self.failUnless( setnode.isMember( p1, component = comp ) )
			# remove the components
			p1.removeFrom( setnode, component = comp )

			self.failUnless( not setnode.isMember( p1, component = comp ) )

			# add member again
			setnode.addMember( p1, component = comp, ignore_failure = False )

			self.failUnless( setnode.isMember( p1, component = comp ) )
		# END for each set component assignment

		# create a component with 3 faces
		f3 = nodes.createComponent( nodes.SingleIndexedComponent, api.MFn.kMeshPolygonComponent )
		for i in range( 3 ): f3.addElement( i )
		f6 = nodes.createComponent( nodes.SingleIndexedComponent, api.MFn.kMeshPolygonComponent )
		for i in range( 3,6 ): f6.addElement( i )

		# FORCE OVERWRITING EXISITNG FACE ASSIGNMNETS
		###############################################
		for sg,comp in zip( ( sg1, sg2 ), ( f3,f6 ) ):
			self.failUnlessRaises( nodes.ConstraintError, sg.addMember, s1, component = f3 )

			# force it
			s1.addTo( sg, component = comp, force = 1 )
			self.failUnless( s1.isMemberOf( sg, component = comp ) )
		# END for each shading engine

		# FORCE WITH OBJECT ASSIGNMENTS
		###############################
		# TODO



