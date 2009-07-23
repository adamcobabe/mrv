# -*- coding: utf-8 -*-
"""B{mayarvtest.byronimo.maya.benchmark.calculations}

Some more math related tests

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
import byronimo.maya as bmaya
import byronimo.maya.nodes as nodes
import byronimotest.byronimo.maya as common
import sys
import maya.cmds as cmds
import byronimo.maya.undo as undo
import maya.OpenMaya as api
import string
import random
import time
import byronimo.maya.nodes.iterators as iters
import byronimotest.byronimo.maya.benchmark as bcommon


class TestCalculations( unittest.TestCase ):

	def test_0randomizeScene( self ):
		"""byronimo.maya.nodes.benchmark: assign unique transformations to dag nodes in a scene"""
		if not bcommon.mayRun( "randomize" ): return
		numnodes = 2500
		benchfile = common.get_maya_file( "large_scene_%i.mb" % 2500 )
		bmaya.Scene.open( benchfile, force = 1 )

		starttime = time.time()
		nodecount = 0
		vec = api.MVector()
		for i, node in enumerate( iters.iterDagNodes( api.MFn.kTransform, asNode = True ) ):
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
		"""byronimo.maya.nodes.benchmark: compute the center point of all  dagnodes in scene"""
		if not bcommon.mayRun( "center" ): return
		starttime = time.time()

		# GET AVERAGE POSITION
		pos = api.MVector()
		nodecache = list()			# for the previous wrapped nodes

		for node in iters.iterDagNodes( api.MFn.kTransform, asNode = True ):
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
