# -*- coding: utf-8 -*-
"""
Test general MPlug performance
"""
from mayarv.test.lib import *
import mayarv.maya as bmaya
import mayarv.maya.undo as undo
import mayarv.maya.nodes as nodes
import maya.cmds as cmds
import maya.OpenMaya as api
from itertools import izip
import sys
import time

class TestPlugPerformance( unittest.TestCase ):
	def test_single_vs_multi_connetions(self):
		sn = nodes.createNode("network1", "network")
		tn = nodes.createNode("network2", "network")
		sn2 = nodes.createNode("network3", "network")
		tn2 = nodes.createNode("network4", "network")
		sn3 = nodes.createNode("network5", "network")
		tn3 = nodes.createNode("network6", "network")
		
		
		def pir(array, range_iter):
			for i in range_iter:
				yield array.getByLogicalIndex(i)
		# END plugs in range utility
		
		# single connection
		r = range(5000)
		st = time.time()
		for source, dest in zip(pir(sn.a, r), pir(tn.ab, r)):
			source > dest
		# END for whole range
		elapsed = time.time() - st
		print >> sys.stderr, "Single-Connected %i different multi-plugs in %f s ( %f / s )" % (len(r), elapsed, len(r) / elapsed)
		
		# multiconnect 
		st = time.time()
		api.MPlug.connectMultiToMulti(izip(pir(sn2.a, r), pir(tn2.ab, r)), force=False)
		elapsed = time.time() - st
		print >> sys.stderr, "Multi-Connected %i different multi-plugs in %f s ( %f / s )" % (len(r), elapsed, len(r) / elapsed)
		
		# multiconnect with force worstcase
		st = time.time()
		api.MPlug.connectMultiToMulti(izip(pir(sn.a, r), pir(tn2.ab, r)), force=True)
		elapsed = time.time() - st
		print >> sys.stderr, "Multi-Connected %i different multi-plugs with worstcase FORCE in %f s ( %f / s )" % (len(r), elapsed, len(r) / elapsed)
		
		# multiconnect with force bestcase
		r = range(len(r), len(r)+len(r))
		st = time.time()
		api.MPlug.connectMultiToMulti(izip(pir(sn3.a, r), pir(tn3.ab, r)), force=True)
		elapsed = time.time() - st
		print >> sys.stderr, "Multi-Connected %i different multi-plugs with bestcase FORCE in %f s ( %f / s )" % (len(r), elapsed, len(r) / elapsed)
	
	def test_general( self ):
		"""mayarv.maya.apipatch: test plug performance"""
		bmaya.Scene.new( force = True )

		s1 = nodes.createNode( "storage1", "StorageNode" )
		s2 = nodes.createNode( "storage2", "StorageNode" )
		
		s1msg = s1.getStoragePlug( "s1", plugType = 1, autoCreate = True )
		s2msg = s1.getStoragePlug( "s1", plugType = 1, autoCreate = True )

		# connect the message attributes respectively

		def measurePlugConnection( msg, func, callNumberList ):
			"""Call func of named operation msg number of times as in callNumberList"""
			for numcons in callNumberList:
				undoObj = undo.StartUndo()

				starttime = time.time()
				for i in xrange( numcons ):
					func( i )
				elapsed = time.time( ) - starttime

				print >> sys.stderr, "%i %s in %f s ( %f / s )" % ( numcons, msg, elapsed, numcons / elapsed )

				del( undoObj )

				starttime = time.time()
				cmds.undo()
				undoelapsed = time.time() - starttime

				starttime = time.time()
				cmds.redo()
				redoelapsed = time.time() - starttime

				print >> sys.stderr, "UNDO / REDO Time = %f / %f ( %f * faster than initial creation )" % ( undoelapsed, redoelapsed,  elapsed / max( redoelapsed, 0.001) )
			# END for each amount of plugs to connct
		# END measure function

		conlist = [ 250, 1000, 2000, 4000 ]

		# CONNECT MULTI PLUGS
		######################
		multifunc = lambda i: s1msg.getByLogicalIndex( i ) >> s2msg.getByLogicalIndex( i )
		measurePlugConnection( "MULTI PLUG Connected", multifunc, conlist )

		# CONNECT SINGLE PLUGS
		persp = nodes.Node( "persp" )
		front = nodes.Node( "front" )
		def singleFunc( i ):
			persp.message >> front.isHistoricallyInteresting
			persp.message | front.isHistoricallyInteresting
		measurePlugConnection( "SINGLE PLUGS Connected", singleFunc, conlist )


		# SET AND GET
		##############
		persp = nodes.Node( "persp" )
		perspshape = persp[0]
		plugs = [ persp.t['x'], perspshape.fl ]

		num_iterations = 2500
		iterations = range( num_iterations )

		undoObj = undo.StartUndo()
		starttime = time.time()
		for plug in plugs:
			for i in iterations:
				value = plug.asFloat()
				plug.setFloat( value )
			# END get set plug
		# END for each plug
		elapsed = time.time() - starttime
		del( undoObj )

		total_count = num_iterations * len( plugs )
		print >> sys.stderr, "Get/Set %i plugs %i times ( total = %i ) in %f ( %g / s )" % ( len( plugs ), num_iterations, total_count,  elapsed, total_count / elapsed )

		starttime = time.time()
		cmds.undo()
		undoelapsed = time.time() - starttime

		starttime = time.time()
		cmds.redo()
		redoelapsed = time.time() - starttime

		print >> sys.stderr, "UNDO / REDO Time = %f / %f ( %f * faster than initial set/get )" % ( undoelapsed, redoelapsed,  elapsed / max( redoelapsed, 0.001) )

