# -*- coding: utf-8 -*-
""" Test node iterators """
from mrv.test.maya import *
from mrv.maya.nt.it import *
import mrv.maya.nt as nt

import maya.OpenMaya as api
import maya.cmds as cmds

class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """

	def __init__( self, *args, **kwargs ):
		super( TestGeneral, self ).__init__( *args, **kwargs )


	@with_scene('empty.ma')
	def test_dagIter( self ):
		trans = nt.createNode( "trans", "transform" )
		trans2 = nt.createNode( "trans2", "transform" )
		transinst = trans.addInstancedChild( trans2 )
		mesh = nt.createNode( "parent|mesh", "mesh" )
		nurbs = nt.createNode( "parent|nurbs", "nurbsSurface" )


		assert len( list( iterDagNodes( dagpath=1 ) ) ) == 16 
		assert len( list( iterDagNodes( dagpath=0 ) ) ) == 15 

		# BREADTH FIRST
		################
		dagiter = iterDagNodes( dagpath=1,depth=0,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue
			# now the following ones are known !
			assert dagiter.next() == trans2 
			break

		# DEPTH FIRST
		##############
		dagiter = iterDagNodes( dagpath=1,depth=1,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue
			assert dagiter.next() == transinst 
			break

		# ROOT
		#########
		# MDagpath, DagNode
		for rootnode in ( trans2, trans2.dagPath() ):
			dagiter = iterDagNodes( root=rootnode,depth=1,asNode=1 )
			nextobj = dagiter.next()
			assert nextobj == trans2 
		# END for each root type
		
		# MObject only works for instances it appears
		dagiter = iterDagNodes( root=trans.object(),depth=1,asNode=1 )
		assert dagiter.next() == trans
		assert dagiter.next() == transinst
		self.failUnlessRaises(StopIteration, dagiter.next)
		
		
		# TYPES
		# single
		dagiter = iterDagNodes(api.MFn.kMesh, asNode=1 )
		assert len( list( dagiter ) ) == 1 

		# multiple
		dagiter = iterDagNodes( api.MFn.kMesh,api.MFn.kNurbsSurface, asNode=1 )
		assert len( list( dagiter ) ) == 2 


	@with_scene('perComponentAssignments.ma')
	def test_iterSelectionList( self ):
		p1 = nt.Node( "|p1trans|p1" )
		p1i = nt.Node( "|p1transinst|p1" )
		objs = [ p1, p1i ]


		# COMPONENTS
		###############
		# get components and put them onto a selection list
		sellist = None
		for handlePlugs in range(2):
			sellist = api.MSelectionList()
			for obj  in objs:
				setsandcomps = obj.componentAssignments( setFilter = nt.Shape.fSetsRenderable )
				for setnode,comp in setsandcomps:
					if comp:
						sellist.add( obj.apiObject(), comp, True )
					sellist.add( obj.apiObject(), api.MObject(), True )
				# for component assignment
			# for obj in objs
	
			seliter = iterSelectionList( sellist, asNode=1, handlePlugs=handlePlugs, handleComponents=1 )
			slist = list( seliter )
	
			numassignments = 10
			assert  len( slist ) == numassignments 
			for node,component in slist:
				assert isinstance( component, ( nt.Component, api.MObject ) ) 
	
	
			# NO COMPONENT SUPPORT
			#########################
			# it will just return the objects without components then
			seliter = iterSelectionList( sellist, asNode=1, handlePlugs=handlePlugs, handleComponents=0 )
			slist = list( seliter )
			assert  len( slist ) == numassignments 
	
			for node in slist:
				assert not isinstance( node, tuple ) 
				
			# PLUGS
			#######
			sellist.add( p1.o )
			sellist.add( p1i.i )
	
			seliter = iterSelectionList( sellist, asNode=1, handleComponents=1, handlePlugs=1 )
			slist = list( seliter )
	
			pcount = 0
			for node, component in slist:
				if cmds.about( v=1 ).startswith( "8.5" ):
					pcount += isinstance( node, (api.MPlug, api.MPlugPtr) )
				else:
					pcount += isinstance( node, api.MPlug )
				# END handle special case
			# END handle plugs
			assert pcount == 2   
		# END handle each possible plug mode )
		
		# test all code branches
		for filterType in (nt.api.MFn.kInvalid, nt.api.MFn.kUnknown):
			for predicate_rval in reversed(range(2)):
				for asNode in range(2):
					for handlePlugs in range(2):
						for handleComponents in range(2):
							predicate = lambda x: predicate_rval
							items = list(iterSelectionList(sellist, filterType, predicate=predicate, 
															asNode=asNode, handlePlugs=handlePlugs, 
															handleComponents=handleComponents))
							
							# in some cases, we do not expect any return value as 
							# it doesnt pass the filter
							if filterType == nt.api.MFn.kUnknown or predicate_rval == 0:
								assert len(items) == 0
							else:
								assert len(items) != 0
								if handleComponents:
									for item in items:
										assert isinstance(item, tuple)
										assert isinstance(item[1], nt.api.MObject)
										if not item[1].isNull() and asNode:
											assert isinstance(item[1], nt.Component)
									# END check each item
								# END handle components assertion
							# END assertion
						# END for each handleComponents
					# END for each handlePlugs value
				# END for each asNode value
			# END for each predicate
		# END for each filter type
		
		# ANIM NODE KEYS
		################
		# NOTE: Although MItSelectionList appears to know something like a kAnimSelectionItem, 
		# its unclear what exactly a 'keyset' is and how to select it. It does not 
		# relate to the graph editor keyframe selection or it doesnt work.


	@with_scene('empty.ma')
	def test_dggraph( self ):
		persp = nt.Node( "persp" )
		front = nt.Node( "front" )
		cam = nt.Node( "persp|perspShape" )

		persp.t.mconnectTo(front.t)
		front.tx.mconnectTo(cam.fl)

		# NODE LEVEL
		#############
		graphiter = iterGraph( persp, input=0, plug=0, asNode=1 )
		assert graphiter.next() == persp 
		assert graphiter.next() == front 
		self.failUnlessRaises( StopIteration, graphiter.next )

		# apparently, one cannot easily traverse plugs if just a root node was given
		mayaversion = float(cmds.about(v=1).split(' ')[0])
		graphiter = iterGraph( persp, input=1, plug=1, asNode=1 )
		
		# its fixed in 2009 and above
		if mayaversion < 2009:
			self.failUnlessRaises(StopIteration, graphiter.next)
		else:
			num_plugs = 0
			for plug in graphiter:
				num_plugs += 1
				assert isinstance(plug, api.MPlug)
			# END for each plug
			assert num_plugs
		# END version handling

		# PLUG LEVEL
		#############
		graphiter = iterGraph( persp.t, input=0, plug=1, asNode=1 )
		assert graphiter.next() == persp.t 
		assert graphiter.next() == front.t 

		# TODO: PLUGLEVEL  + filter
		# Currently I do not really have any application for this, so lets wait
		# till its needed
		
		# test all branches
		for root in (persp, persp.t, front.t):
			for inputval in range(2):
				for breadth in range(2):
					for plug in range(2):
						for prune in range(2):
							for asNode in range(2):
								for predicate_rval in range(2):
									predicate = lambda x: predicate_rval
									items = list(iterGraph(root,input=inputval, breadth=breadth,
															plug=plug, prune=prune, asNode=asNode, 
															predicate=predicate))
									if not predicate_rval:
										assert len(items) == 0
									if asNode and not plug:
										for item in items:
											assert isinstance(item, nt.Node)
										# END for each item
									# END if node asNode iteartion
									
									if plug:
										for item in items:
											assert isinstance(item, api.MPlug)
										# END for each item
									# END if plug is to be returned
								# END for each predicate rval
							# END for each asNode value
						# END for each prune value
					# END for each plug value
				# END for each traversal type
			# END for each input val
		# END for each root 


	@with_scene('empty.ma')
	def test_dgiter( self ):
		trans = nt.createNode( "trans", "transform" )
		mesh = nt.createNode( "trans|mesh", "mesh" )

		gid = nt.createNode( "gid", "groupId" )
		fac = nt.createNode( "fac", "facade" )
		fac1 = nt.createNode( "fac1", "facade" )
		oset = nt.createNode( "set", "objectSet" )

		# one type id
		assert len( list( iterDgNodes( api.MFn.kFacade ) ) ) == 2 
		assert oset in iterDgNodes( api.MFn.kSet, asNode=1 ) 

		# multiple type ids
		filteredNodes = list( iterDgNodes( api.MFn.kSet, api.MFn.kGroupId, asNode=1 ) )
		for node in [ gid, oset ]:
			assert node in filteredNodes 

		# asNode
		assert isinstance(iterDgNodes(asNode=0).next(), api.MObject)
		
		# predicate
		assert len(list(iterDgNodes(predicate=lambda n: False))) == 0

