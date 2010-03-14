# -*- coding: utf-8 -*-
""" Tests the geometric nodes, focussing on the set handling """
from mayarv.test.maya import *
import mayarv.maya.nodes as nodes
import mayarv.maya.nodes.geometry as modmesh
import maya.OpenMaya as api
import mayarv.maya as bmaya
import mayarv.test.maya.nodes as ownpackage

class TestGeometry( unittest.TestCase ):
	""" Test general maya framework """


	def test_setHandling( self ):
		"""mayarv.maya.nodes.geometry: set handling tests for different types"""
		bmaya.Scene.open( get_maya_file( "shadertest.ma" ), force = 1 )

		# these are all shapes
		p1 = nodes.Node( "|p1trans|p1" )		# one shader
		p1i = nodes.Node( "|p1transinst|p1" )		# one shader, instanced
		p2 = nodes.Node( "|p2trans|p2" ) 	# 3 shaders, third has two faces
		p2i = nodes.Node( "|p2transinst|p2" ) 	# 3 shaders, third has two faces, instanced
		s1 = nodes.Node( "s1" )		# subdivision surface
		n1 = nodes.Node( "n1" )		# nurbs with one shader

		noncomplist = ( p1, p1i, s1, n1 )
		complist = ( p1, p1i, p2, p2i, )

		# deformed surface
		pd = nodes.Node( "|pdtrans|pd" )
		pdi = nodes.Node( "|pdtransinst|pd" )		# instance of pd
		nd = nodes.Node( "nd" ) 					# deformed nurbs
		sd = nodes.Node( "sd" )						# deformed subdee

		# dont use an instance as no deformer sets are returned
		# don't use subdees as we cannot support components there, api limitation
		deformedlist = ( pd, nd )


		# the shading groups
		sg1 = nodes.Node( "sg1" )
		sg2 = nodes.Node( "sg2" )
		sg3 = nodes.Node( "sg3" )

		# simple sets
		set1 = nodes.Node( "set1" )
		set2 = nodes.Node( "set2" )


		# TEST OBJECT ASSIGNMENTS
		#########################
		# simple assignments
		for obj in noncomplist:
			# shaders - object assignment method
			setfilter = nodes.Shape.fSetsRenderable
			sets = obj.getConnectedSets( setFilter = setfilter )
			assert len( sets ) == 1 and sets[0] == sg1 

			# TEST OBJECT SET ASSIGNMENTS
			setfilter = nodes.Shape.fSetsObject
			sets = obj.getConnectedSets( setFilter = setfilter )
			assert len( sets ) == 2 and sets[0] == set1 and sets[1] == set2 
		# END assignmnet query


		# SHOULD NOT GET COMPONENT SETS
		######################################
		# if queried with connectedSets
		for obj in noncomplist:
			sets = obj.getConnectedSets( nodes.Shape.fSets )
			for s in sets:
				assert s in ( sg1, set1, set2 ) 
		# END non-component lists check



		# TEST COMPONENT ASSIGNMENT QUERY
		#################################
		# SHADERS - components method
		for obj in complist:

			# OBJECT SET MEMBERSHIP
			# even this method can retrieve membership to default object sets
			setfilter = nodes.Shape.fSetsObject
			sets = obj.getComponentAssignments( setFilter = setfilter )
			assert len( sets ) == 2 

			# but the components must be 0, and it must have our sets
			for setnode, comp in sets:
				assert comp.isNull() 
				assert setnode in ( set1, set2 ) 

			if obj != p2:
				continue

			# COMPONENT ASSIGNMENTS
			##########################
			setfilter = nodes.Shape.fSetsRenderable
			setcomps = obj.getComponentAssignments( setFilter = setfilter )

			assert len( setcomps ) == 3 

			for setnode, component in setcomps:
				assert not component.isEmpty() 

				if setnode == sg1:
					assert component.getElement( 0 ) == 0 
				if setnode == sg2:
					assert component.getElement( 0 ) == 1 
				if setnode == sg3:
					assert component.getElement( 0 ) == 2 
					assert component.getElement( 1 ) == 3 
					assert component.getElementCount( ) == 2 
			# END for each setcomponent
		# END for each object


		# TEST DEFORMER CONNECTIONS
		#############################
		for dm in deformedlist:
			setcomps = dm.getComponentAssignments( setFilter = nodes.Shape.fSetsDeformer )

			for setobj,component in setcomps:
				if component:
					assert not component.isEmpty() 

					# add and remove
					assert dm.isMemberOf( setobj, component = component ) 

					dm.removeFrom( setobj, component = component )

					assert not setobj.isMember( dm, component = component ) 

					dm.addTo( setobj, component = component )
					#print type( component )
					#print "compinfo: numitems = %i, type = %i" % ( component.getElementCount(), component.type() )
				# END if there is a component assignment
			# END for each component

			assert len( setcomps ) == 3 
		# END for each deformed surface


		# TEST TWEAK HANDLING
		# make tweak
		ofs = ( 1.0, 1.0, 1.0 )						# offset array
		ptweak = p1.pnts.getByLogicalIndex( 0 )
		ptweak['px'].setFloat( ofs[0] )
		ptweak['py'].setFloat( ofs[1] )
		ptweak['pz'].setFloat( ofs[2] )

		p1.resetTweaks( p1.eComponentType.vertex )
		assert ptweak['px'].asFloat() == 0.0
		assert ptweak['py'].asFloat() == 0.0
		assert ptweak['pz'].asFloat() == 0.0

		puvtweak = p1.uvpt.getByLogicalIndex( 0 )
		puvtweak['ux'].setFloat( ofs[0] )
		puvtweak['uy'].setFloat( ofs[1] )

		p1.resetTweaks( p1.eComponentType.uv )
		assert puvtweak['ux'].asFloat() == 0.0
		assert puvtweak['uy'].asFloat() == 0.0



		# RESET TWEAKS , keep result
		###############################
		# TODO: compete this test, many issues are not tested, uv reset with history
		# is not verified at all
		# although tweaks have been removed, from the shape , their effect needs to stay
		for comptype in nodes.Mesh.eComponentType.vertex,nodes.Mesh.eComponentType.uv :
			bmaya.Scene.open( get_maya_file( "meshtweaks.ma" ), force = 1 )

			for mname in ( "mesh_without_history", "mesh_with_history" ):
				mesh = nodes.Node( mname )
				mesh.resetTweaks( tweak_type = comptype, keep_tweak_result = 1 )

				tweaktype = api.MFn.kPolyTweak
				if comptype == nodes.Mesh.eComponentType.uv:
					tweaktype = api.MFn.kPolyTweakUV

				history_mode = "_with_" in mname

				print " COMPTYPE = %s | HISTORY = %i " % ( comptype, history_mode )

				# HISTORY CHECK
				# assure tweak nodes have been created
				if history_mode:
					assert mesh.inMesh.p_input.getNode().getApiType() == tweaktype
				else:
					assert mesh.inMesh.p_input.isNull()
				# END history  check

				# TODO: Check that the values are truly the same ( as keep_tweak_result is 1 )
				# NOTE: currently this has only been tested with UI directly
				if comptype == nodes.Mesh.eComponentType.vertex:
					pass
				# END if vertex check
				else:
					pass
				# END uv check

				# two vertices are tweaked
			# END for each mesh name
		# END for each component type
		
	def test_mesh_components_and_iteration(self):
		m = nodes.Mesh()
		pc = nodes.PolyCube()
		pc.output > m.inMesh
		
		assert len(m.getComponentAssignments()) == 0 and m.numVertices() == 8
		
		# TEST ITERATION
		################
		self.failUnlessRaises(ValueError, m.iterComponents, "something")
		
		def get_index(it):
			if hasattr(it, 'index'):
				return it.index()
			else:
				return it.faceId()
			# END handle index
		# END check index helper
		
		converters = (lambda l: l, lambda l: iter(l), lambda l: api.MIntArray.fromList(l))
		
		
		ec = m.eComponentType
		for comp, maxindex in zip(m.eComponentType, (7, 11, 5, 5)):
			last_index = 0
			for it in m.iterComponents(comp):
				last_index = get_index(it)
			# END for each itertion pass
			assert last_index == maxindex
		# END for each component, iterator type
		
		
		
		# CONSTRAIN MIT USING COMPONENT
		self.failUnlessRaises(ValueError, m.getComponent, 1)	# invalid arg type
		vc = m.getComponent(ec.vertex).addElements(api.MIntArray.fromMultiple(1,2))
		assert isinstance(vc, nodes.SingleIndexedComponent)
		
		miv = m.iterComponents(ec.vertex, vc)
		assert miv.count() == 2
		
		
	
		
		# SHORTCUT ITERATION
		for shortname in ('vtx', 'e', 'f', 'map'):
			it_helper = getattr(m, shortname)
			assert isinstance(it_helper, modmesh._SingleIndexedComponentIterator)
			
			# plain iterator 
			assert hasattr(it_helper.iter, 'next')
			
			max_index = 0
			for it in it_helper:
				max_index = get_index(it)
			# END iterate whole mesh
			assert max_index != 0
			
			# check component iteration
			try:
				# slice
				last_index = 0
				for it in it_helper[:2]:
					last_index = get_index(it)
				# END slice iteration
				assert last_index and last_index < max_index
			except NotImplementedError:
				# double index components are not supported
				# everything else would fail as well
				continue
			# END handle exceptions
			
			# complete slice
			assert it_helper[:].count() == max_index + 1
			
			# single 
			last_index = 0
			for it in it_helper[2]:
				last_index = get_index(it)
			# END slice iteration
			assert last_index == 2
			
			# multi 
			last_index = 0
			ni = 0
			for it in it_helper[0,2]:
				last_index = get_index(it)
				ni += 1
			# END slice iteration
			assert last_index == 2 and ni == 2 
			
			# list
			for conv in converters:
				last_index = 0
				ni = 0
				for it in it_helper[conv((0,3))]:
					last_index = get_index(it)
					ni += 1
				# END slice iteration
				assert last_index == 3 and ni == 2
			# END for each argument convertion function
		# END for each iteration shortname
		
		for shortname in ('cvtx', 'ce', 'cf', 'cmap'):
			c_helper = getattr(m, shortname)
			assert isinstance(c_helper, modmesh._SingleIndexedComponentGenerator)
			
			# empty
			c = c_helper.empty()
			assert len(c.getElements()) == 0 and not c.isComplete()
			
			# slice
			c = c_helper[0:2]
			e = c.getElements()
			assert len(e) == 2 and e[0] == 0 and e[1] == 1
			
			# full slice
			c = c_helper[:]
			assert len(c.getElements()) == 0 and c.isComplete()
			
			# single
			c = c_helper[5]
			assert c.getElements()[0] == 5
			
			# multi
			c = c_helper[5,10]
			e = c.getElements()
			assert len(e) == 2 and e[0] == 5 and e[1] == 10 
			
			# list/iter/IntArray
			for conv in converters:
				c = c_helper[conv((1,5))]
				e = c.getElements()
				assert len(e) == 2 and e[0] == 1 and e[1] == 5
			# END for each type to check
		# END for each component shortcut
		
	
	@with_scene("mesh_lightlinks.ma")
	def test_lightLinkCopy( self ):
		"""mayarv.maya.nodes.geometry: test how lightlinks are copied from oen shape to another
		@note: currently we only call variants of the respective method to run it - verification
		was made in actual scenes, but is not reproducable"""
		for sourcename in ( "sphere", "torus" ):
			source = nodes.Node( sourcename )
			target = nodes.Node( "%s_target" % sourcename )
			source.copyLightLinks( target, substitute = 1 )	# substitute to target
			target.copyLightLinks( source, substitute = 1 )	# back to source
			source.copyLightLinks( target, substitute = 0 )	# copy it to target
		# END for each source mesh name


