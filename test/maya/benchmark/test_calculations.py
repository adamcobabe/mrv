# -*- coding: utf-8 -*-
"""
Some more math related tests



"""



import unittest
import mayarv.maya as bmaya
import mayarv.maya.nodes as nodes
import mayarv.test.maya as common
import sys
import maya.cmds as cmds
import mayarv.maya.undo as undo
import maya.OpenMaya as api
import string
import random
import time
import mayarv.maya.nodes.it as it
import mayarv.test.maya.benchmark as bcommon


class TestCalculations( unittest.TestCase ):

	def test_0randomizeScene( self ):
		"""mayarv.maya.nodes.benchmark: assign unique transformations to dag nodes in a scene"""
		if not bcommon.mayRun( "randomize" ): return
		numnodes = 2500
		benchfile = common.get_maya_file( "large_scene_%i.mb" % 2500 )
		bmaya.Scene.open( benchfile, force = 1 )

		starttime = time.time()
		nodecount = 0
		vec = api.MVector()
		for i, node in enumerate( it.iterDagNodes( api.MFn.kTransform, asNode = True ) ):
			vec.x = i*3
			vec.y = i*3+1
			vec.z = i*3+2
			node.setTranslation( vec, api.MSpace.kWorld )
			nodecount += 1
		# END for each object
		elapsed = time.time() - starttime
		print "Randomized %i node translations in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

		# save tmp
		common._saveTempFile( "randomscene.mb" )


	def test_1computeCenter( self ):
		"""mayarv.maya.nodes.benchmark: compute the center point of all  dagnodes in scene"""
		if not bcommon.mayRun( "center" ): return
		starttime = time.time()

		# GET AVERAGE POSITION
		pos = api.MVector()
		nodecache = list()			# for the previous wrapped nodes

		for node in it.iterDagNodes( api.MFn.kTransform, asNode = True ):
			pos += node.getTranslation( api.MSpace.kWorld )
			nodecache.append( node )
		# END for each node

		nodecount = len( nodecache )
		pos /= float( nodecount )
		elapsed = time.time() - starttime

		print "Average position of %i nodes is: <%f,%f,%f> in %f s" % ( nodecount, pos.x,pos.y,pos.z, elapsed )


		# NOW SET ALL NODES TO THE GIVEN VALUE
		starttime = time.time()

		for node in nodecache:
			node.setTranslation( pos, api.MSpace.kWorld )
		# END for each node

		elapsed = time.time() - starttime
		print "Set %i nodes to average position in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

		common._saveTempFile( "averaged.mb" )
