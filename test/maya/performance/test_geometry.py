# -*- coding: utf-8 -*-
"""Performance Testing"""
from mrv.test.maya import *

import mrv.maya.nt as nt
import time
import sys

class TestGeometryPerformance( unittest.TestCase ):
	
	@with_scene('mesh40k.mb')
	def test_mesh_iteration(self):
		m = nt.Node('mesh40k')
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
		ia = nt.api.MIntArray()
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
		
		
	@with_scene('mesh40k.mb')
	def test_set_vertex_colors(self):
		st = time.time()
		
		cset = 'edgeLength'
		m = nt.Node('mesh40k')
		
		m.createColorSetWithName(cset)
		m.setCurrentColorSetName(cset)
		
		lp = nt.api.MPointArray()
		m.getPoints(lp)
		
		colors = nt.api.MColorArray()
		colors.setLength(m.numVertices())
		
		vids = nt.api.MIntArray()
		vids.setLength(len(colors))
		
		el = nt.api.MFloatArray()
		el.setLength(len(colors))
		cvids = nt.api.MIntArray()
		
		# compute average edge-lengths
		max_len = 0.0
		for vid, vit in enumerate(m.vtx):
			vit.getConnectedVertices(cvids)
			cvp = lp[vid]
			accum_edge_len=0.0
			for cvid in cvids:
				accum_edge_len += (lp[cvid] - cvp).length()
			# END for each edge-id
			avg_len = accum_edge_len / len(cvids)
			max_len = max(avg_len, max_len)
			el[vid] = avg_len
			vids[vid] = vid
		# END for each vertex
		
		# normalize
		for cid in xrange(len(colors)):
			c = colors[cid]
			c.b = el[cid] / max_len
			colors[cid] = c
		# END for each color id
	
		m.setVertexColors(colors, vids, nt.api.MDGModifier())
		
		elapsed = time.time() - st
		nc = len(colors)
		print >>sys.stderr, "Computed %i vertex colors ans assigned them in %f s ( %f colors/s )" % (nc, elapsed, nc/elapsed)
		
		
		
		
		
