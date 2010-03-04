# -*- coding: utf-8 -*-
"""
Contains implementations ( or improvements ) to mayas geometric shapes



"""


import base
from typ import MetaClassCreatorNodes
from mayarv.enum import (create as enum, Element as elm)
import maya.OpenMaya as api

class GeometryShape( base.Shape ):	# base for epydoc !
	"""Contains common methods for all geometry types"""
	@undoable
	def copyLightLinks( self, other, **kwargs ):
		"""Copy lightlinks from one meshShape to another
		@param substitute: if True, default False, the other shape will be put
		in place of self, effectively receiving it's light-links whereas self losses
		them. This is practical in case you create a new shape below a transform that
		had a previously visible and manipulated shape whose external connections you
		wouuld like to keep"""
		def getFreeLogicalIndex( parent_plug ):
			"""@return: a free parent compound index"""
			ilogical = parent_plug.getLogicalIndex()
			array_plug = parent_plug.getArray()
			num_elments = array_plug.getNumElements()


			# one of the logical indices must be the highest one - start searching
			# at the end of the physical array
			for iphysical in xrange( num_elments - 1, -1, -1 ):
				p_plug = array_plug[ iphysical ]
				try_index = p_plug.getLogicalIndex() + 1
				try_plug = array_plug.getByLogicalIndex( try_index )

				if try_plug.getChild( 0 ).p_input.isNull():
					return try_index
			# END endless loop

			raise AssertionError( "Did not find valid free index" )
		# END helper method

		substitute = kwargs.get( "substitute", False )
		for input_plug in self.message.p_outputs:
			node = input_plug.getNode()
			if node.getApiType() != api.MFn.kLightLink:
				continue

			# we are always connected to the object portion of the compound model
			# from there we can conclude it all
			parent_compound = input_plug.getParent()
			target_compound_index = -1
			if substitute:
				target_compound_index = parent_compound.getLogicalIndex()
			else:
				target_compound_index = getFreeLogicalIndex( parent_compound )

			new_parent_compound = parent_compound.getArray().getByLogicalIndex( target_compound_index )

			# retrieve light link, connect other - light is only needed if we do not
			# substitute
			if not substitute:
				light_plug = parent_compound.getChild( 0 ).p_input
				if not light_plug.isNull():
					light_plug > new_parent_compound.getChild( 0 )
				# END if lightplug is connected
			# END if no substitute required

			# connect object
			other.message >> new_parent_compound.getChild( 1 )


		# END for each output plug


class DeformableShape( GeometryShape ):	# base for epydoc !
	pass


class ControlPoint( DeformableShape ):		# base for epydoc !
	pass


class SurfaceShape( ControlPoint ):	# base for epydoc !
	pass


class Mesh( SurfaceShape ):		# base for epydoc !
	"""Implemnetation of mesh related methods to make its handling more
	convenient"""
	__metaclass__ = MetaClassCreatorNodes
	# component types that make up a mesh
	eComponentType = enum( elm("vertex", api.MFn.kMeshVertComponent), 
							elm("edge", api.MFn.kMeshEdgeComponent ), 
							elm("face", api.MFn.kMeshPolygonComponent ), 
							elm("uv", api.MFn.kMeshMapComponent ) )
	
	#{ Utilities

	def copyTweaksTo( self, other ):
		"""Copy our tweaks onto another mesh
		@note: we do not check topology for maximum flexibility"""
		opnts = other.pnts
		pnts = self.pnts
		for splug in pnts:
			opnts.getByLogicalIndex( splug.logicalIndex() ).setMObject( splug.asMObject() )
		# END for each source plug in pnts

	def isValidMesh( self ):
		"""@return: True if we are nonempty and valid - emptry meshes do not work with the mfnmesh
		although it should ! Have to catch that case ourselves"""
		try:
			self.numVertices()
			return True
		except RuntimeError:
			return False

	@undoable
	def copyAssignmentsTo( self, other, **kwargs ):
		"""Copy set assignments including component assignments to other
		@param setFilter: default is fSetsRenderable
		@param **kwargs: passed to set.addMember"""
		setFilter = kwargs.pop( "setFilter", base.Shape.fSetsRenderable )
		for sg, comp in self.getComponentAssignments( setFilter = setFilter ):
			sg.addMember( other, comp, **kwargs )


	@undoable
	def resetTweaks( self, tweak_type = eComponentType.vertex, keep_tweak_result = False ):
		"""Reset the tweaks on the given mesh shape
		@param eComponentType: the component type(s) whose tweaks are to be removed,
		valid values are 'vertex' and 'uv' enum members. Pass in a scalar value or a list
		of tweak types
		@param keep_tweak_result: if True, the effect of the tweak will be kept. If False,
		it will be removed. What actually happens depends on the context:
		* [ referenced ] mesh without history:
			* copy outMesh to inMesh, resetTweaks
			* if referenced, plenty of reference edits are generated, ideally one operates
			  on non-referenced geomtry
		* [ referenced ] mesh with history
			* put tweakNode into mesh history, copy tweaks onto tweak node
		@note: currently vertex and uv tweaks will be removed if keep is enabled, thus they must
		both be specified"""
		check_types = ( isinstance( tweak_type, ( list, tuple ) ) and tweak_type ) or [ tweak_type ]
		type_map = {
							self.eComponentType.vertex : ( "pnts", api.MFnNumericData.k3Float, "polyTweak", api.MFn.kPolyTweak, "tweak" ),
							self.eComponentType.uv : ( "uvpt", api.MFnNumericData.k2Float, "polyTweakUV", api.MFn.kPolyTweakUV, "uvTweak" )
					}

		for reset_this_type in check_types:
			try:
				attrname, datatype, tweak_node_type, tweak_node_type_API, tweakattr = type_map[ reset_this_type ]
			except KeyError:
				raise ValueError( "Tweak type %s is not supported" % reset_this_type )

			# KEEP MODE
			#############
			if keep_tweak_result:
				input_plug = self.inMesh.p_input

				# history check
				if input_plug.isNull():
					# assert as we had to make the handling much more complex to allow this to work right as we copy the whole mesh here
					# containing all tweaks , not only one type
					if not ( self.eComponentType.vertex in check_types and self.eComponentType.uv in check_types ):
						print "WARNING: Currently vertex AND uv tweaks will be removed if a mesh has no history and a reset is requested"

					# take the output mesh, and stuff it into the input, then proceed
					# with the reset. This implies that all tweaks have to be removed
					out_mesh = self.outMesh.asMObject()
					self.inMesh.setMObject( out_mesh )
					self.cachedInMesh.setMObject( out_mesh )

					# finally reset all tweeaks
					return self.resetTweaks( check_types, keep_tweak_result = False )
				else:
					# create node of valid type
					tweak_node = input_plug.getNode()

					# create node if there is none as direct input
					if not tweak_node.hasFn( tweak_node_type_API ):
						tweak_node = base.createNode( "polyTweak", tweak_node_type, forceNewLeaf = 1  )

						# hook the node into the history
						input_plug >> tweak_node.inputPolymesh
						tweak_node.output >> self.inMesh

						# setup uvset tweak location to tell uvset where to get tweaks from
						if tweak_node_type_API == api.MFn.kPolyTweakUV:
							names = list()
							self.getUVSetNames( names )
							index = names.index( self.getCurrentUVSetName( ) )

							tweak_node.uvTweak.getByLogicalIndex( index ) >> self.uvSet.getByLogicalIndex( index ).uvSetTweakLocation
						# END uv special setup
					# END create tweak node

					dtweak_plug = getattr( tweak_node, tweakattr )
					stweak_plug = getattr( self, attrname )

					# copy the tweak values - iterate manually as the plug tends to
					# report incorrect values if history is present - its odd
					nt = len( stweak_plug )
					for i in xrange( nt ):
						try:
							tplug = stweak_plug[ i ]
						except RuntimeError:
							continue
						else:
							dtweak_plug.getByLogicalIndex( tplug.getLogicalIndex() ).setMObject( tplug.asMObject() )
					# END for each tweak plug



					# proceed with reset of tweaks
					pass
				# END history handling
			# END keep tweak result handling

			arrayplug = getattr( self, attrname )
			dataobj = api.MFnNumericData().create( datatype )

			# reset values, do it for all components at once using a data object
			try:
				for p in arrayplug:
					p.setMObject( dataobj )
			except RuntimeError:
				# especially uvtweak array plugs return incorrect lengths, thus we may
				# fail once we reach the end of the iteration.
				# uvpt appears to display a lenght equalling the number of uvpoints in the mesh
				# possibly only for the current uvset
				pass
		# END for tweak type to reset
		
	def getComponent(self, component_type):
		"""@return: A component object able to hold the given component type
		@param component_type: a member of the L{eComponentType} enumeration"""
		if component_type not in self.eComponentType:
			raise ValueError("Invalid component type")
		return base.SingleIndexedComponent.create(component_type.getValue())
		
	#} END utilities
		
	#{ Iterators 
	def iterComponents(self, component_type, component=api.MObject()):
		"""@return: MItIterator matching your component_type to iteartor over items
		on this mesh
		@param component_type: 
			vertex -> MItMeshVertex
			edge -> MItMeshEdge
			face -> MItMeshPolygon
		@param component: if not kNullObject, the iterator returned will be constrained
		to the given indices as described by the Component"""
		if component_type not in self.eComponentType:
			raise ValueError("Invalid component type")
			
		ec = self.eComponentType
		it_type = { 	ec.vertex : api.MItMeshVertex,
						ec.edge   : api.MItMeshEdge, 
						ec.face   : api.MItMeshPolygon }[component_type] 
		
		return it_type(self.getMDagPath(), component)
		
	def iterFaceVertex(self, component=api.MObject()):
		"""@return: FaceVertex iterator, optionally constrained to the given component
		@param component: see L{iterComponents}"""
		return api.MItMeshFaceVertex(self.getMDagPath(), component)
	#} END iterators 

	#( iDuplicatable
	def copyFrom( self, other, *args, **kwargs ):
		"""Copy tweaks and sets from other onto self
		@param setFilter: if given, default is fSets, you may specify the types of sets to copy
		if None, no set conenctions will be copied """
		other.copyTweaksTo( self )

		setfilter = kwargs.pop( "setFilter", Mesh.fSets )		# copy all sets by default
		if setfilter is not None:
			other.copyAssignmentsTo( self, setFilter = setfilter )

	#) END iDuplicatable
