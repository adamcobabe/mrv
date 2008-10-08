"""B{byronimo.nodes.geometry}

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

	
class Shape:
	"""Interface providing common methods to all geometry shapes as they can be shaded.
	They usually support per object and per component shader assignments
	
	@note: as shadingEngines are derived from objectSet, this class deliberatly uses 
	them interchangably when it comes to set handling.
	@note: for convenience, this class implements the shader related methods 
	whereever possible
	@note: bases determined by metaclass"""
	
	__metaclass__ = base.nodes.MetaClassCreatorNodes
	
	
	class SetFilter( tuple ):
		"""Utility Class  returning True or False on call, latter one if 
		the passed object does not match the filter"""
		def __new__( cls, apitype, exactTypeFlag ):
			return tuple.__new__( cls, ( apitype, exactTypeFlag ) )
			
		def __call__( self, apiobj ):
			"""@return: True if given api object matches our specifications """
			if self[ 1 ]:			# exact type 
				return apiobj.apiType() == self[ 0 ]
				
			# not exact type 
			return apiobj.hasFn( self[ 0 ] )
	# END SetFilter 
	
	#{ preset type filters
	fSetsRenderable = SetFilter( api.MFn.kShadingEngine, False )	# shading engines only 
	fSetsObject = SetFilter( api.MFn.kSet, True )				# object fSets only  	
	fSets = SetFilter( api.MFn.kSet, False )			 			# all set types 
	#} END type filters 
	
	#{ Interface
	
	def getConnectedSets( self, setFilter = fSetsObject ):
		"""@return: list of object set compatible Nodes having self as member
		@param setFilter: tuple( apiType, use_exact_type ) - the combination of the 
		desired api type and the exact type flag allow precise control whether you which 
		to get only renderable shading engines, only objectfSets ( tuple[1] = True ), 
		or all objects supporting the given object type. 
		Its preset to only return shading engines
		@note: this method ignores"""
		
		# try the possibly faster api method first , discarding components 
		try: 
			comp_assignments = self.getComponentAssignments( setFilter = setFilter )
			return [ setnode for setnode, component in comp_assignments ]
		except TypeError:
			pass 
		
		# have to parse the connections to fSets manually, finding fSets matching the required
		# type and returning them
		outlist = list()
		for dplug in self.iog[ self.getInstanceNumber() ].getOutputs():
			setobj = dplug.getNodeApiObj( )
			if not setFilter( setobj ):
				continue
			outlist.append( base.Node( setobj ) )
		# END for each connected set
		
		return outlist
		
	
	def getComponentAssignments( self, setFilter = fSetsRenderable ):
		"""@return: list of tuples( objectSetNode, Component ) defininmg shader 
		assignments on per component basis.
		If a shader is assigned to the whole object, the component would be None, otherwise
		it is an instance of a wrapped IndexedComponent class
		@param setFilter: see L{getConnectedSets}
		@note: will only return renderable sets 
		@raise TypeError: if the type wrapped by self does not support per-component assignments"""
		if not self._apiobj.hasFn( api.MFn.kMesh ):
			raise TypeError( "Only Meshes support per component assignment and retrieval" )
		
		sets = api.MObjectArray()
		components = api.MObjectArray() 
		
		# take all fSets by default, we do the filtering 
		self.getConnectedSetsAndMembers( self.getInstanceNumber(), sets, components, False )
		
		# wrap the sets and components
		outlist = list()
		for setobj,compobj in zip( sets, components ):
			if not setFilter( setobj ):
				continue
			
			setobj = base.Node( api.MObject( setobj ) )								# copy obj to get memory to python
			if compobj.isNull():
				compobj = None
			else:
				compobj = base.Component( api.MObject( compobj ) )	  
				
			outlist.append( ( setobj, compobj ) ) 
		# END for each set/component pair
		return outlist
		
	#}


class Mesh:
	"""Implemnetation of mesh related methods to make its handling more 
	convenient"""
	__metaclass__ = base.nodes.MetaClassCreatorNodes
