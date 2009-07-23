# -*- coding: utf-8 -*-
"""B{mayarv.nodes.geometry}

Contains implementations ( or improvements ) to mayas geometric shapes

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

import base
import types
import maya.OpenMaya as api
import iterators
from byronimo.enum import create as enum

class Shape( base.DagNode ):	 # base for epydoc !
	"""Interface providing common methods to all geometry shapes as they can be shaded.
	They usually support per object and per component shader assignments

	@note: as shadingEngines are derived from objectSet, this class deliberatly uses
	them interchangably when it comes to set handling.
	@note: for convenience, this class implements the shader related methods
	whereever possible
	@note: bases determined by metaclass"""

	__metaclass__ = base.nodes.MetaClassCreatorNodes




	#{ preset type filters
	fSetsRenderable = base.SetFilter( api.MFn.kShadingEngine, False, 0 )	# shading engines only
	fSetsDeformer = base.SetFilter( api.MFn.kSet, True , 1)				# deformer sets only
	#} END type filters

	#{ Sets Interface

	def _parseSetConnections( self, allow_compoents ):
		"""Manually parses the set connections from self
		@return: tuple( MObjectArray( setapiobj ), MObjectArray( compapiobj ) ) if allow_compoents, otherwise
		just a list( setapiobj )"""
		sets = api.MObjectArray()
		iogplug = self._getSetPlug()			# from DagNode , usually iog plug

		# this will never fail - logcical index creates the plug as needed
		# and drops it if it is no longer required
		if allow_compoents:
			components = api.MObjectArray()

			# take full assignments as well - make it work as the getConnectedSets api method
			for dplug in iogplug.getOutputs():
				sets.append( dplug.getNodeApiObj() )
				components.append( api.MObject() )
			# END full objecft assignments

			for compplug in iogplug['objectGroups']:
				for setplug in compplug.getOutputs():
					sets.append( setplug.getNodeApiObj() )		# connected set

					# get the component from the data
					compdata = compplug['objectGrpCompList'].asData()
					if compdata.getLength() == 1:			# this is what we can handle
						components.append( compdata[0] ) 	# the component itself
					else:
						raise AssertionError( "more than one compoents in list" )

				# END for each set connected to component
			# END for each component group

			return ( sets, components )
		else:
			for dplug in iogplug.getOutputs():
				sets.append( dplug.getNodeApiObj() )
			return sets
		# END for each object grouop connection in iog


	def getComponentAssignments( self, setFilter = fSetsRenderable, use_api = True ):
		"""@return: list of tuples( objectSetNode, Component ) defininmg shader
		assignments on per component basis.
		If a shader is assigned to the whole object, the component would be a null object, otherwise
		it is an instance of a wrapped IndexedComponent class
		@param setFilter: see L{getConnectedSets}
		@param use_api: if True, api methods will be used if possible which is usually faster.
		If False, a custom non-api implementation will be used instead.
		This can be required if the apiImplementation is not reliable which happens in
		few cases of 'weird' component assignments
		@note: the sets order will be the order of connections of the respective component list
		attributes at instObjGroups.objectGroups
		@note: currently only meshes and subdees support per component assignment, whereas only
		meshes can have per component shader assignments
		@note: SubDivision Components cannot be supported as the component type kSubdivCVComponent
		cannot be wrapped into any component function set - reevaluate that with new maya versions !
		@note: deformer set component assignments are only returned for instance 0 ! They apply to all
		output meshes though"""

		# SUBDEE SPECIAL CASE
		#########################
		# cannot handle components for subdees - return them empty
		if self._apiobj.apiType() == api.MFn.kSubdiv:
			print "WARNING: components are not supported for Subdivision surfaces due to m8.5 api limitation"
			sets = self.getConnectedSets( setFilter = setFilter )
			return [ ( setnode, api.MObject() ) for setnode in sets ]
		# END subdee handling

		sets = components = None

		# MESHES AND NURBS
		##################
		# QUERY SETS AND COMPONENTS
		# for non-meshes, we have to parse the components manually
		if not use_api or not self._apiobj.hasFn( api.MFn.kMesh ) or not self.isValidMesh():
			# check full membership
			sets,components = self._parseSetConnections( True )
		# END non-mesh handling
		else:
			# MESH - use the function set
			# take all fSets by default, we do the filtering
			sets = api.MObjectArray()
			components = api.MObjectArray()
			self.getConnectedSetsAndMembers( self.getInstanceNumber(), sets, components, False )
		# END sets/components query


		# wrap the sets and components
		outlist = list()
		for setobj,compobj in zip( sets, components ):
			if not setFilter( setobj ):
				continue

			setobj = base.Node( api.MObject( setobj ) )								# copy obj to get memory to python
			compobj = api.MObject( compobj )											# make it ours
			if not compobj.isNull():
				compobj = base.Component( compobj )

			outlist.append( ( setobj, compobj ) )
		# END for each set/component pair
		return outlist

	#} END set interface


class GeometryShape( Shape ):	# base for epydoc !
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
	__metaclass__ = base.nodes.MetaClassCreatorNodes
	# component types that make up a mesh
	eComponentType = enum( "vertex", "edge", "face", "uv" )

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
		setFilter = kwargs.pop( "setFilter", Shape.fSetsRenderable )
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
