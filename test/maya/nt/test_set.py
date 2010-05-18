# -*- coding: utf-8 -*-
""" Test sets and partitions """
from mrv.test.maya import *
import mrv.maya.nt as nt

import maya.cmds as cmds
import maya.OpenMaya as api

class TestSets( unittest.TestCase ):
	""" Test set and partition handling """

	def test_createAddRemove( self ):
		set1 = nt.createNode( "set1", "objectSet" )
		set2 = nt.createNode( "set2", "objectSet" )
		set3 = nt.createNode( "set3", "objectSet" )
		prt1 = nt.createNode( "partition1", "partition" )
		prt2 = nt.createNode( "partition2", "partition" )

		# SET PARTITION HANDLING
		#########################
		assert len( set1.partitions( ) ) == 0 
		set1.setPartition( prt1, set1.kReplace )
		assert len( set1.partitions() ) == 1 
		assert set1.partitions()[0] == prt1 

		# add same again
		set1.setPartition( prt1, set1.kAdd )
		assert len( set1.partitions() ) == 1 

		# remove
		set1.setPartition( prt1, set1.kRemove )
		assert len( set1.partitions( ) ) == 0 

		# remove again
		set1.setPartition( prt1, set1.kRemove )


		# PARTITION MEMBER HANDLING
		# add multiple sets
		prt1.addSets( [ set1, set2 ] )
		assert len( prt1.members() ) == 2 

		# add again
		prt1.addSets( [ set1, set2 ] )

		prt1.removeSets( [ set1, set2] )
		assert len( prt1.members() ) == 0 

		# remove again
		prt1.removeSets( [ set1, set2] )


		prt2.addSets( [ set1, set2] )

		# replace multiple
		prt2.replaceSets( [ set3 ] )
		
		# set like methods
		prt2.add(set1)
		assert set1 in prt2
		prt2.discard(set1)
		assert set1 not in prt2
		
		# test partition protocols 
		assert len(prt2) == len(prt2.members())
		assert [ s for s in prt2 ] == prt2.members()
		assert set3 in prt2
		
		
		assert len(prt2)
		assert isinstance(prt2.clear(), nt.Partition)
		assert len(prt2) == 0
		
		
	def _getMemberList( self ):
		""":return: object list with all types"""
		persp = nt.Node( "persp" )
		front = nt.Node( "front" )
		rg = nt.Node( "defaultRenderGlobals" )
		ik = nt.Node( "ikSystem" )
		s2 = nt.Node( "defaultObjectSet" )
		return [ ik, persp, persp.translate, rg.object(), front.dagPath(), s2 ]

	@with_undo
	def test_memberHandling( self ):
		s = nt.createNode( "memberSet", "objectSet" )

		# ADD/REMOVE SINGLE MEMBER
		####################
		# add Node ( dgnode )
		memberlist = self._getMemberList( )

		for i,member in enumerate( memberlist ):
			s.addMember( member )
			assert s.members( ).length() == i+1 
			assert s.isMember( member ) 
			cmds.undo()
			assert s.members( ).length() == i 
			cmds.redo()
		# end for each member

		# clear the set by undoing it all
		for i in range( len( memberlist ) ):
			cmds.undo()

		assert s.members().length() == 0 

		# get it back
		for i in range( len( memberlist ) ):
			cmds.redo()

		assert s.members().length() == len( memberlist ) 

		# MULTI-MEMBER UNDO/REDO
		##########################
		s.removeMembers( memberlist )
		assert s.members().length() == 0 
		cmds.undo()
		assert s.members().length() == len( memberlist ) 
		cmds.redo()
		assert s.members().length() == 0 

		# add members again
		s.addMembers( memberlist )
		assert s.members().length() == len( memberlist ) 
		cmds.undo()
		assert s.members().length() == 0 
		cmds.redo()
		assert s.members().length() == len( memberlist ) 


		# remove all members
		for i,member in enumerate( memberlist ):
			s.removeMember( member )

		assert s.members().length() == 0 

		# ADD/REMOVE MULTIPLE MEMBER
		######################
		# add node list
		s.addMembers( memberlist )
		assert s.members().length() == len( memberlist ) 

		s.clear()
		assert s.members().length() == 0 

		# Add selection listx
		sellist = nt.toSelectionList( memberlist )
		s.addMembers( sellist )
		assert s.members().length() == sellist.length() 

		# remove members from sellist
		s.removeMembers( sellist )
		assert s.members().length() == 0 

		cmds.undo()
		assert s.members().length() == sellist.length() 

		cmds.redo()
		assert s.members().length() == 0 

		
		# test smart add
		s.add(sellist)
		assert len(s) == len(sellist)
		single_item = sellist.mtoIter().next()
		s.add(single_item)
		assert len(s) == len(sellist)

		s.discard(single_item)
		assert single_item not in s
		
		s.discard(sellist.mtoList())
		assert len(s) == 0


		# TEST CLEAR
		#############
		s.addMembers( sellist )
		assert s.members().length() == sellist.length() 

		s.clear()
		assert s.members().length() == 0 

		cmds.undo()
		assert s.members().length() == sellist.length() 


		# USING SETMEMBERS
		########################
		members = self._getMemberList()
		# replace
		s.setMembers( members[0:2], 0 )
		assert s.members().length() == 2 
		
		# add
		s.setMembers( members[-2:-1], 1 )
		assert s.members().length() == 3 
		
		# remove
		s.setMembers( members[0:2], 2 )
		assert s.members().length() == 1 
		
		cmds.undo()
		assert s.members().length() == 3 
		
		
		# TEST SET PROTOCOLS
		####################
		assert len(s) == 3
		assert [ m for m in s ] == s.members().mtoList()
		assert iter(s).next() in s

	def test_setOperations( self ):
		"""byroniom.maya.nt.sets: unions, intersections, difference, overloaded ops"""
		memberlist = self._getMemberList( )
		s3 = nt.createNode( "anotherObjectSet", "objectSet" )
		s = nt.ObjectSet()
		s.clear()
		s.addMembers( memberlist )

		side = nt.Node( "side" )
		s2 = nt.createNode( "memberSet2", "objectSet" )
		s2.addMember( side )

		# UNION
		########
		# with set
		sellist = s.union( s2 )
		assert sellist.length() == len( memberlist ) + 1 

		# with sellist - will create temp set
		sellist = s.union( s2.members() )
		assert sellist.length() == len( memberlist ) + 1 
		assert not nt.objExists( "set4" ) 		# tmp set may not exist

		# with multiple object sets
		s.union( [ s2, s3 ] )

		list( s.iterUnion( s2 ) )

		# INTERSECTION
		###############
		fewmembers = memberlist[:3]
		s2.addMembers( fewmembers )

		# add 0 members
		s2.addMembers( list() )

		# with set
		sellist = s.intersection( s2 )
		assert sellist.length() == len( fewmembers ) 

		# with sellist
		sellist = s.intersection( fewmembers )
		assert sellist.length() == len( fewmembers ) 

		# with multi sets
		s3.addMembers( fewmembers )
		sellist = s.intersection( [ s2, s3 ] )
		assert sellist.length() == len( fewmembers ) 

		list( s.iterIntersection( s2 ) )

		# DIFFERENCE
		#############
		# with set
		s2.removeMember( side )
		sellist = s.difference( s2 )
		assert s.members().length() - s2.members().length() == sellist.length() 

		# with objects
		sellist = s.difference( list( s2.iterMembers() ) )
		assert s.members().length() - s2.members().length() == sellist.length() 

		# with sellist
		sellist = s.difference( s2.members() )

		# with multiple sets
		s3.clear()
		s3.addMember( nt.Node( "front" ) )
		sellist = s.difference( [ s2, s3 ] )

		assert len( list( s.iterDifference( [ s2, s3 ] ) ) ) == s.difference( [ s2, s3 ] ).length() 
		assert s.members().length() - s2.members().length() - s3.members().length() == sellist.length() 
		

	def test_partitions( self ):

		# one transform, two sets, one partition
		s1 = nt.createNode( "ms1", "objectSet" )
		s2 = nt.createNode( "ms2", "objectSet" )
		p = nt.createNode( "p1", "partition" )

		s3 = nt.createNode( "ms3", "objectSet" )
		s4 = nt.createNode( "ms4", "objectSet" )
		t = nt.createNode( "my_trans", "transform" )
		t2 = nt.createNode( "my_trans2", "transform" )

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
			self.failUnlessRaises( nt.ConstraintError, s2.addMember, o1 )	# failure, as errors are not ignored
			s2.addMember( o1, ignore_failure = 1 )		# ignore failure

			# FORCE
			s2.addMember( o1, force = 1 )
			assert s2.isMember( o1 ) 

			# MULTIPLE OBJECTS
			###################
			self.failUnlessRaises( nt.ConstraintError, s1.addMembers, multiobj )			# fails as t is in s2
			s1.addMembers( [ o2 ] )			# works as t2 is not in any set yet
			assert s1.isMember( o2 ) 

			# FORCE all objects into s1
			s1.addMembers( multiobj, force = 1 )
			assert s1.intersection( multiobj, sets_are_members = 1 ).length() == 2 


			# and once more
			assert isinstance(s1.clear(), nt.ObjectSet)
			s2.clear()

			for s in s1,s2:
				assert s.members().length() == 0


			s1.addMembers( multiobj )
			self.failUnlessRaises( nt.ConstraintError, s2.addMembers, multiobj, force = False, ignore_failure = False )
			assert s2.members().length() == 0

			s2.addMembers( multiobj, force = False, ignore_failure = 1 )
			assert s2.members().length() == 0

			# now force it
			s2.addMembers( multiobj, force = 1 )
			assert s2.members().length() == 2
		# END for each object


		# SHADER ASSIGNMENTS
		######################
		sphere = nt.Node( cmds.polySphere( )[0] )[0]
		cube = nt.Node( cmds.polyCube()[0] )[0]
		multi = ( sphere, cube )
		all_sets = sphere.connectedSets( setFilter = sphere.fSets )
		isg = all_sets[0]			# initial shading group
		rp = isg.partitions()[0]# render partition

		assert str( isg ).startswith( "initial" )

		snode = nt.createNode( "mysg", "shadingEngine" )
		snode.setPartition( rp, 1 )

		self.failUnlessRaises( nt.ConstraintError, snode.addMember, sphere )
		self.failUnlessRaises( nt.ConstraintError, snode.addMembers, multi )

		# now force it in
		snode.addMembers( multi, force = 1, ignore_failure = 0 )
		assert snode.members().length() == 2
		assert snode.intersection( multi ).length() == 2

	def test_renderPartition( self ):
		rp = nt.Node( "renderPartition" )
		assert len( rp.sets( ) )		# at least the initial shading group


	@with_scene("perComponentAssignments.ma")
	def test_z_memberHandlingComps( self ):
		p1 = nt.Node( "|p1trans|p1" )
		s1 = nt.Node( "s1" )					# sphere with face shader assignments
		s2 = nt.Node( "s2" )					# sphere with one object assignment

		# shading engines
		sg1 = nt.Node( "sg1" )
		sg2 = nt.Node( "sg2" )


		# REMOVE AND SET FACE ASSIGNMENTS
		####################################
		# get all sets assignments
		setcomps = p1.componentAssignments( setFilter = nt.Shape.fSetsRenderable )

		for setnode, comp in setcomps:
			# NOTE: must be member in the beginning, but the isMember method does not
			# work properly with components
			if comp.isNull():
				continue

			assert setnode.isMember( p1, component = comp ) 
			# remove the components
			p1.removeFrom( setnode, component = comp )

			assert not setnode.isMember( p1, component = comp ) 

			# add member again
			setnode.addMember( p1, component = comp, ignore_failure = False )

			assert setnode.isMember( p1, component = comp ) 
		# END for each set component assignment

		# create a component with 3 faces
		f3 = nt.SingleIndexedComponent.create(api.MFn.kMeshPolygonComponent)
		for i in range( 3 ): f3.addElement( i )
		f6 = nt.SingleIndexedComponent.create(api.MFn.kMeshPolygonComponent)
		for i in range( 3,6 ): f6.addElement( i )

		# FORCE OVERWRITING EXISITNG FACE ASSIGNMNETS
		###############################################
		for sg,comp in zip( ( sg1, sg2 ), ( f3,f6 ) ):
			self.failUnlessRaises( nt.ConstraintError, sg.addMember, s1, component = f3 )

			# force it
			s1.addTo( sg, component = comp, force = 1 )
			assert s1.isMemberOf( sg, component = comp ) 
		# END for each shading engine

		# FORCE WITH OBJECT ASSIGNMENTS
		###############################
		# TODO

	def test_shader_comonent_assignments(self):
		# MESH COMPONENTS
		#################
		isb = nt.Node("initialShadingGroup")
		m = nt.Mesh()
		pc = nt.PolyCube()
		pc.output.mconnectTo(m.inMesh)
		assert len(m.componentAssignments()) == 0 and m.numVertices() == 8
		
		# assign two of the 6 faces
		isb.addMember(m, m.cf[2,4])
		asm = m.componentAssignments()
		assert len(asm) == 1
		asm = asm[0]
		assert asm[0] == isb and len(asm[1].elements()) == 2
		
		# verify return types of getComponentAssignments
		asm = m.componentAssignments(asComponent=False)
		assert not isinstance(asm[0][1], nt.Component)
		
		# assign everything on component level
		isb.addMember(m, m.cf[:])
		asm = m.componentAssignments()
		assert len(asm) == 1
		asm = asm[0]
		# IMPORTANT: Setting the component complete doesnt work - it will just
		# do nothing as it doesnt check for that
		assert not asm[1].isComplete()	# it should be complete, but maya doesnt think so
		
		# assign all 6 faces 
		isb.addMember(m, m.cf[:6])
		asm = m.componentAssignments()
		assert len(asm) == 1
		asm = asm[0]
		assert len(asm[1].elements()) == 6
		
		# unassign by assigning other faces does NOT work
		isb.addMember(m, m.cf[:3])
		assert len(m.componentAssignments()[0][1].elements()) == 6
		
		# unassign all components at once does work !
		isb.removeMember(m, m.cf[:])
		asm = m.componentAssignments()
		assert len(asm) == 0
		
		# unassign just a few of many faces
		isb.addMember(m, m.cf[:6])
		assert len(m.componentAssignments()) == 1
		isb.removeMember(m, m.cf[:5])
		asm = m.componentAssignments()[0]
		e = asm[1].elements()
		assert len(e) == 1 and e[0] == 5
		
		
		# test object level assignments vs. component assignments 
		# Although they should be exclusive, they are not, hence component level
		# assignments stay, the object level ones take precedence
		isb.addMember(m)
		assert len(m.componentAssignments()) == 1
		assert m in isb
		

