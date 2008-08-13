"""B{byronimo.nodes.base}

Contains some basic  classes that are required to run the nodes system

@todo: more documentation

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


nodes = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
import maya.OpenMaya as api


############################
#### Methods 		  	####
##########################

def toApiObject( nodeName, dagPlugs=True ):
	""" Get the API MPlug, MObject or (MObject, MComponent) tuple given the name 
	of an existing node, attribute, components selection
	@param dagPlugs: if True, plug result will be a tuple of type (MDagPath, MPlug)
	@note: based on pymel
	""" 
	sel = api.MSelectionList()
	try:	# DEPEND NODE ?
		sel.add( nodeName )
	except:
		if "." in nodeName :
			# COMPOUND ATTRIBUTES
			#  sometimes the index might be left off somewhere in a compound attribute 
			# (ex 'Nexus.auxiliary.input' instead of 'Nexus.auxiliary[0].input' )
			#  but we can still get a representative plug. this will return the equivalent of 'Nexus.auxiliary[-1].input'
			try:
				buf = nodeName.split('.')
				obj = toApiObject( buf[0] )
				plug = api.MFnDependencyNode(obj).findPlug( buf[-1], False )
				if dagPlugs and isValidMDagPath(obj) : 
					return (obj, plug)
				return plug
			except RuntimeError:
				return
	else:
		if "." in nodeName :
			try:
				# Plugs
				plug = api.MPlug()
				sel.getPlug( 0, plug )
				if dagPlugs:
					try:
						# Plugs with DagPaths
						sel.add( nodeName.split('.')[0] )
						dag = api.MDagPath()
						sel.getDagPath( 1, dag )
						#if isValidMDagPath(dag) :
						return (dag, plug)
					except RuntimeError: pass
				return plug
			
			except RuntimeError:
				# Components
				dag = api.MDagPath()
				comp = api.MObject()
				sel.getDagPath( 0, dag, comp )
				#if not isValidMDagPath(dag) :	 return
				return (dag, comp)
		else:
			try:
				# DagPaths
				dag = api.MDagPath()
				sel.getDagPath( 0, dag )
				#if not isValidMDagPath(dag) : return
				return dag
		 
			except RuntimeError:
				# Objects
				obj = api.MObject()
				sel.getDependNode( 0, obj )			 
				#if not isValidMObject(obj) : return	 
				return obj
	# END if no exception on selectionList.add  

# def wrapNode 


############################
#### Classes		  	####
##########################

class MayaNode( unicode ):
	"""Common base for all maya nodes, providing access to the maya internal object 
	representation"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	

class DependNode( MayaNode ):
	""" Implements access to dependency nodes 
	
	Depdency Nodes are manipulated using an MObjectHandle which is safest to go with, 
	but consumes more memory too !"""
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	
class Entity( DependNode ):
	"""Common base for dagnodes and paritions"""
	__metaclass__ = nodes.MetaClassCreatorNodes


class DagNode( Entity ):
	""" Implements access to DAG nodes """
	__metaclass__ = nodes.MetaClassCreatorNodes
	
	

	
