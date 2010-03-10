# -*- coding: utf-8 -*-
""" Test node iterators """
import unittest
import maya.OpenMaya as api
from mayarv.maya.nodes.it import *
import mayarv.test.maya as common
import mayarv.maya as bmaya
import mayarv.maya.nodes as nodes
import mayarv.test.maya.nodes as ownpackage
import maya.cmds as cmds

class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """

	def __init__( self, *args, **kwargs ):
		super( TestGeneral, self ).__init__( *args, **kwargs )
		#benchfile = common.get_maya_file( "large_scene_%i.mb" % 2500 )
		#bmaya.Scene.open( benchfile, force = 1 )


	def test_dagIter( self ):
		"""mayarv.maya.nodes.it: simple DAG iteration"""
		if not ownpackage.mayRun( "iterators" ): return
		bmaya.Scene.new( force=1 )
		trans = nodes.createNode( "trans", "transform" )
		trans2 = nodes.createNode( "trans2", "transform" )
		transinst = trans.addInstancedChild( trans2 )
		mesh = nodes.createNode( "parent|mesh", "mesh" )
		nurbs = nodes.createNode( "parent|nurbs", "nurbsSurface" )


		self.failUnless( len( list( iterDagNodes( dagpath=1 ) ) ) == 16 )
		self.failUnless( len( list( iterDagNodes( dagpath=0 ) ) ) == 15 )

		# BREADTH FIRST
		################
		dagiter = iterDagNodes( dagpath=1,depth=0,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue
			# now the following ones are known !
			self.failUnless( dagiter.next() == trans2 )
			break

		# DEPTH FIRST
		##############
		dagiter = iterDagNodes( dagpath=1,depth=1,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue
			self.failUnless( dagiter.next() == transinst )
			break

		# ROOT
		#########
		# dagpath
		dagiter = iterDagNodes( root=trans._apidagpath,depth=1,asNode=1 )
		self.failUnless( dagiter.next() == trans )		#
		self.failUnless( dagiter.next() == transinst )

		# apiobj
		dagiter = iterDagNodes( root=trans._apiobj,depth=1,asNode=1 )
		self.failUnless( dagiter.next() == trans )
		self.failUnless( dagiter.next() == transinst )

		# TYPES
		# single
		dagiter = iterDagNodes(api.MFn.kMesh, asNode=1 )
		self.failUnless( len( list( dagiter ) ) == 1 )

		# multiple
		dagiter = iterDagNodes( api.MFn.kMesh,api.MFn.kNurbsSurface, asNode=1 )
		self.failUnless( len( list( dagiter ) ) == 2 )


	def test_iterSelectionList( self ):
		"""mayarv.maya.nodes.it: Iterate selection lists"""
		if not ownpackage.mayRun( "iterators" ): return
		bmaya.Scene.open( common.get_maya_file( "perComponentAssignments.ma" ), force = 1 )

		p1 = nodes.Node( "|p1trans|p1" )
		p1i = nodes.Node( "|p1transinst|p1" )
		objs = [ p1, p1i ]


		# COMPONENTS
		###############
		# get components and put them onto a selection list
		sellist = None
		for handlePlugs in range(2):
			sellist = api.MSelectionList()
			for obj  in objs:
				setsandcomps = obj.getComponentAssignments( setFilter = nodes.Shape.fSetsRenderable )
				for setnode,comp in setsandcomps:
					if comp:
						sellist.add( obj.getApiObject(), comp, True )
					sellist.add( obj.getApiObject(), api.MObject(), True )
				# for component assignment
			# for obj in objs
	
			seliter = iterSelectionList( sellist, asNode=1, handlePlugs=handlePlugs, handleComponents=1 )
			slist = list( seliter )
	
			numassignments = 10
			self.failUnless(  len( slist ) == numassignments )
			for node,component in slist:
				self.failUnless( isinstance( component, ( nodes.Component, api.MObject ) ) )
	
	
			# NO COMPONENT SUPPORT
			#########################
			# it will just return the objects without components then
			seliter = iterSelectionList( sellist, asNode=1, handlePlugs=handlePlugs, handleComponents=0 )
			slist = list( seliter )
			self.failUnless(  len( slist ) == numassignments )
	
			for node in slist:
				self.failUnless( not isinstance( node, tuple ) )
				
			# PLUGS
			#######
			sellist.add( p1.o )
			sellist.add( p1i.i )
	
			seliter = iterSelectionList( sellist, asNode=1, handleComponents=1, handlePlugs=1 )
			slist = list( seliter )
	
			pcount = 0
			for node, component in slist:
				pcount += isinstance( node, (api.MPlug, api.MPlugPtr) )
			# END handle plugs
			self.failUnless( pcount == 2 )  
		# END handle each possible plug mode )
		
		# test all code branches
		for filterType in (nodes.api.MFn.kInvalid, nodes.api.MFn.kUnknown):
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
							if filterType == nodes.api.MFn.kUnknown or predicate_rval == 0:
								assert len(items) == 0
							else:
								assert len(items) != 0
								if handleComponents:
									for item in items:
										assert isinstance(item, tuple)
										assert isinstance(item[1], nodes.api.MObject)
										if not item[1].isNull() and asNode:
											assert isinstance(item[1], nodes.Component)
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


	def test_dggraph( self ):
		"""mayarv.maya.nodes.it: simple dg graph iteration"""
		if not ownpackage.mayRun( "iterators" ): return
		bmaya.Scene.new( force=1 )
		persp = nodes.Node( "persp" )
		front = nodes.Node( "front" )
		cam = nodes.Node( "persp|perspShape" )

		persp.t > front.t
		front.t['tx'] > cam.fl

		# NODE LEVEL
		#############
		graphiter = iterGraph( persp, input=0, plug=0, asNode=1 )
		self.failUnless( graphiter.next() == persp )
		self.failUnless( graphiter.next() == front )
		self.failUnlessRaises( StopIteration, graphiter.next )

		# apparently, one cannot easily traverse plugs if just a root node was given
		mayaversion = float(cmds.about(v=1).split(' ')[0])
		graphiter = iterGraph( persp, input=1, plug=1, asNode=1 )
		
		# its fixed in 2009 and above
		if mayaversion < 2009:
			self.failUnlessRaises( RuntimeError, graphiter.next )
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
		self.failUnless( graphiter.next() == persp.t )
		self.failUnless( graphiter.next() == front.t )

		# TODO: PLUGLEVEL  + filter
		# Currently I do not really have any application for this, so lets wait
		# till I need it


	def test_dgiter( self ):
		"""mayarv.maya.nodes.it: simple DG iteration"""
		if not ownpackage.mayRun( "iterators" ): return
		bmaya.Scene.new( force=1 )
		trans = nodes.createNode( "trans", "transform" )
		mesh = nodes.createNode( "trans|mesh", "mesh" )

		gid = nodes.createNode( "gid", "groupId" )
		fac = nodes.createNode( "fac", "facade" )
		fac1 = nodes.createNode( "fac1", "facade" )
		oset = nodes.createNode( "set", "objectSet" )

		# one type id
		self.failUnless( len( list( iterDgNodes( api.MFn.kFacade ) ) ) == 2 )
		self.failUnless( oset in iterDgNodes( api.MFn.kSet, asNode=1 ) )

		# multiple type ids
		filteredNodes = list( iterDgNodes( api.MFn.kSet, api.MFn.kGroupId, asNode=1 ) )
		for node in [ gid, oset ]:
			self.failUnless( node in filteredNodes )


