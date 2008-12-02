# -*- coding: utf-8 -*-
"""B{byronimotest.byronimo.maya.benchmark.calculations}

Some more math related tests 

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


class TestCalculations( unittest.TestCase ):
	
	def test_0randomizeScene( self ):
		"""byronimo.maya.nodes.benchmark: simply randomize the transformations of dag nodes on a scene"""
		numnodes = 2500
		benchfile = common.get_maya_file( "large_scene_%i.mb" % 2500 )
		bmaya.Scene.open( benchfile, force = 1 )
		
		starttime = time.clock()
		nodecount = 0
		for node in iters.iterDagNodes( api.MFn.kTransform, asNode = True ):
			translation = api.MVector( float( random.randint( -20, 20 ) ), float( random.randint( -20, 20 ) ), float( random.randint( -20, 20 ) ) )
			node.setTranslation( translation, api.MSpace.kWorld )
			nodecount += 1
		# END for each object
		elapsed = time.clock() - starttime
		print "Randomized %i node translations in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )
		
		# save tmp
		common._saveTempFile( "randomscene.mb" )
		

	def test_1computeCenter( self ):
		"""byronimo.maya.nodes.benchmark: compute the center point of all  dagnodes in scene"""
		
		starttime = time.clock()
		
		# GET AVERAGE POSITION 
		pos = api.MVector()
		nodecache = list()			# for the previous wrapped nodes
		
		for node in iters.iterDagNodes( api.MFn.kTransform, asNode = True ):
			pos += node.getTranslation( api.MSpace.kWorld )
			nodecache.append( node )
		# END for each node 
		
		nodecount = len( nodecache )
		pos /= float( nodecount )
		elapsed = time.clock() - starttime
		
		print "Average position of %i nodes is: <%f,%f,%f> in %f s" % ( nodecount, pos.x,pos.y,pos.z, elapsed )
		
		
		# NOW SET ALL NODES TO THE GIVEN VALUE
		starttime = time.clock()
		
		for node in nodecache:
			node.setTranslation( pos, api.MSpace.kWorld )
		# END for each node 
		
		elapsed = time.clock() - starttime
		print "Set %i nodes to average position in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )
		
		common._saveTempFile( "averaged.mb" )
