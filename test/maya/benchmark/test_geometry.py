# -*- coding: utf-8 -*-
"""Performance Testing"""
from mayarv.test.maya import *

import mayarv.maya.nodes as nodes
import time
import sys

class TestAnimPerformance( unittest.TestCase ):
	
	@with_scene('mesh40k.mb')
	def test_mesh_iterationn(self):
		m = nodes.Node('mesh40k')
		nv = m.numVertices()
		ne = m.numEdges()
		nf = m.numPolygons()
		
		# VTX NOOP
		st = time.time()
		nc = 0
		for it in m.vtx:
			nc += 1	# to be sure it doesnt get optimized, which doesnt happen actually
		# END for each vertex
		assert nc == nv
		
		noop_elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i vertices and noop in %f s ( %f items/s )" % (nv, noop_elapsed, nv/noop_elapsed)
		
		# VTX INDEX
		st = time.time()
		for it in m.vtx:
			it.index()
		# END for each vertex
		index_elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i vertices and queried index in %f s ( %f indices/s )" % (nv, index_elapsed, nv/index_elapsed)
		
		
		# VTX INDEX
		st = time.time()
		vit = m.iterComponents(m.eComponentType.vertex)
		vitindex = vit.index
		for it in vit:
			vitindex()
		# END for each vertex
		indexc_elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i vertices and queried index (cached) in %f s ( %f indices/s )" % (nv, indexc_elapsed, nv/indexc_elapsed)
		
		
		print >>sys.stderr, "Call-overhead estimation: noop (%f) vs. index(%f)=^%f vs cached index(%f)=^%f" % ( noop_elapsed, index_elapsed, index_elapsed/noop_elapsed, indexc_elapsed, indexc_elapsed/noop_elapsed )
		
		
		# VTX POSITION
		st = time.time()
		for it in m.vtx:
			it.position()
		# END for each vertex
		elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i vertices and queried position in %f s ( %f pos/s )" % (nv, elapsed, nv/elapsed)
		
		
		
		# EDGE 2 POSITION
		st = time.time()
		for it in m.e:
			it.point(0)
			it.point(1)
		# END for each vertex
		elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i edges and queried position in %f s ( %f pos/s )" % (ne, elapsed, nv/elapsed)
		
		
		# Polygon All vtx
		st = time.time()
		ia = nodes.api.MIntArray()
		nc = 0
		for it in m.f:
			it.getVertices(ia)
			nc += 1
		# END for each vertex
		assert nc == nf
		elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i polygons and queried all poly-vertices in %f s ( %f queries/s )" % (nf, elapsed, nv/elapsed)
		
		
		# All FaceVtx
		st = time.time()
		nc = 0
		for it in m.map:
			it.position()
			nc += 1
		# END for each vertex
		elapsed = time.time() - st
		print >>sys.stderr, "Iterated %i face-vertices and queried position in %f s ( %f queries/s )" % (nc, elapsed, nc/elapsed)
		
		
		
		
		
		
		
		
		
