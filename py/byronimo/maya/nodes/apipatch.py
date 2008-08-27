"""B{byronimo.maya.nodes.apipatch}

Contains patch classes that are altering their respective api classes  

The classes here are rather verbose and used as patch-template which can be 
handled correctly by epydoc, and whose method will be used to patch the respective
api classes.

As they are usually derived from the class they patch , they could also be used directly

@note: NEVER IMPORT CLASSES DIRECTLY IN HERE, keep at least one module , thus:
NOT: thisImportedClass BUT: module.thisImportedClass !

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


nodes = __import__( "byronimo.maya.nodes", globals(), locals(), [ 'nodes' ] )
undo = __import__( "byronimo.maya.undo", globals(), locals(), ['undo'] )

import byronimo.util as util
from byronimo.util import getPythonIndex 
import maya.OpenMaya as api
import maya.cmds as cmds 
import inspect 



def init_applyPatches( ):
	"""Called by package __init__ method to finally apply the patch according to 
	the template classes 
	Template classes must derive from the to-be-patched api class first, and can derive
	from helper classes providing basic patch methods.
	Helper classes must derive from Abstract to indicate their purpose
	
	If a class has an _applyPatch method, it will be called and not additional. If 
	it returns True, the class members will be applied as usual, if False the method will stop
	
	@note: overwritten api methods will be renamed to _api_methodname
	@note: currently this method works not recursively"""
	module = __import__( "byronimo.maya.nodes.apipatch", globals(), locals(), ['apipatch'] )
	classes = [ r[1] for r in inspect.getmembers( module, predicate = inspect.isclass ) ]
	forbiddenMembers = [ '__module__','_applyPatch','__dict__','__weakref__','__doc__' ]
	
	for cls in classes:
		# use the main class as well as all following base
		# the first base is always the main maya type that is patched - we skip it
		templateclasses = [ cls ]
		templateclasses.extend( cls.__bases__[ 1: ] )
		
		# assure that the actual class rules over methods from lower base classes
		# by applying them last 
		templateclasses.reverse()

		# skip abstract classes ?
		if cls is Abstract or cls.__bases__[0] is Abstract:
			continue
			
		apicls = cls.__bases__[0]
		
		# SPECIAL CALL INTERFACE ?
		# If so, call and let the class do the rest
		if hasattr( cls, "_applyPatch" ):
			if not cls._applyPatch(  ):
				continue
		
		for tplcls in templateclasses:
			util.copyClsMembers( tplcls, apicls, overwritePrefix="_api_",
										forbiddenMembers = forbiddenMembers )
		# END for each template class
	# END for each cls of this module 
	pass 


class Abstract:
	"""Class flagging that subclasses should be abstract and are only to be used 
	as superclass """
	pass 

############################
#### Primitive Types   ####
##########################

#{ Primitive Types
class TimeDistanceAngleBase( Abstract ):
	"""Base patch class for all indicated classes
	@note: idea for patches from pymel"""
	def __str__( self ): return str(float(self))
	def __int__( self ): return int(float(self))
	def __float__( self ): return self.as(self.uiUnit())
	def __repr__(self): return '%s(%s)' % ( self.__class__.__name__, float(self) )
	

class MTime( api.MTime, TimeDistanceAngleBase ) :
	pass 
	                          
class MDistance( api.MDistance, TimeDistanceAngleBase ) :
	pass 
	
class MAngle( api.MAngle, TimeDistanceAngleBase ) :
	pass 
	
	
# patch some Maya api classes that miss __iter__ to make them iterable / convertible to list
class PatchIteratblePrimitives( Abstract ):
	"""@note: Classes derived from this base should not be used directly"""
	@classmethod
	def _applyPatch( cls ):
		"""Read per-class values from self and create appropriate methods and 
		set them as well
		@note: idea from pymel"""		
		def __len__(self):
			""" Number of components in Maya api iterable """
			return self.length
		# END __len__
		type.__setattr__( cls.__bases__[0], '__len__', __len__)
		
		def __iter__(self):
			""" Iterates on all components of a Maya base iterable """
			for i in xrange( self.length ) :
				yield self.__getitem__( i )
		# END __iter__
		type.__setattr__( cls.__bases__[0], '__iter__', __iter__)
		
		# allow the class members to be used ( required as we are using them )
		return True

class PatchMatrix( Abstract, PatchIteratblePrimitives ):
	"""Only for matrices"""
	@classmethod
	def _applyPatch( cls ):
		"""Special version for matrices"""
		PatchIteratblePrimitives._applyPatch.im_func( cls )
		def __iter__(self):
			""" Iterates on all 4 rows of a Maya api MMatrix """
			for r in xrange( self.length ) :
				yield [ self.scriptutil(self.__getitem__( r ), c) for c in xrange(self.length) ]
		# END __iter__
		type.__setattr__( cls.__bases__[0], '__iter__', __iter__ )
		return True
		



class MVector( api.MVector, PatchIteratblePrimitives ):
	length = 3

class MFloatVector( api.MFloatVector, PatchIteratblePrimitives ):
	length = 3

class MPoint( api.MPoint, PatchIteratblePrimitives ):
	length = 4

class MFloatPoint( api.MFloatPoint, PatchIteratblePrimitives ):
	length = 4

class MColor( api.MColor, PatchIteratblePrimitives ):
	length = 4

class MQuaternion( api.MQuaternion, PatchIteratblePrimitives ):
	length = 4
	
class MEulerRotation( api.MEulerRotation, PatchIteratblePrimitives ):
	length = 4

class MMatrix( api.MMatrix, PatchMatrix ):
	length = 4
	scriptutil = api.MScriptUtil.getDoubleArrayItem
	
class MFloatMatrix( api.MFloatMatrix, PatchMatrix ):
	length = 4
	scriptutil = api.MScriptUtil.getFloatArrayItem
# 
class MTransformationMatrix( api.MTransformationMatrix, PatchMatrix ):
	length = 4
	
	@classmethod
	def _applyPatch( cls ):
		"""Special version for matrices"""
		PatchMatrix._applyPatch.im_func( cls )
		def __iter__(self):
			""" Iterates on all 4 rows of a Maya api MMatrix """
			return self.asMatrix().__iter__()
		# END __iter__
		type.__setattr__( cls.__bases__[0], '__iter__', __iter__ )
		return True
#} 

#############################
#### BASIC 		Types   ####
##########################

#{ Basic Types
class MPlug( api.MPlug, util.iDagItem ):
	""" Wrap a maya plug to assure we always get Nodes ( instead of MObjects )
	By overridding many object methods, the access to plugs becomes very pythonic"""
	# __slots__ = []  	 apparently it will always have a dict 
	
	#{ Overridden Methods
	def __getitem__( self, index ):
		"""@return: Plug at physical index """
		return self.getByIndex( index )
		
	def __len__( self ):
		"""@return: Plug at physical index """
		if not self.isArray( ): return 0
		return self.getNumElements( )
		
	def __iter__( self ):
		"""@return: iterator object"""
		return util.IntKeyGenerator( self )
		
	def __str__( self ):
		"""@return: name of plug"""
		#print repr( self )
		#if self.isNull(): return ""
		return api.MPlug.name( self ) 
		
	def __repr__( self ):
		"""@return: our class representation"""
		return "%s(%s_asAPIObj)" % ( self.__class__.__name__, self.getName() )

	def __getattr__( self, attr ):
		"""@return: a child plug with the given name or fail
		@note: if a name is not known to this class, we check for children having 
		attr as short or long name
		@note: once an attribute has been found, it will be cached in dict for fast
		repetitive query"""
		if attr == 'thisown' or attr == 'this':			# special pointer type usually requested
			return api.MPlug.__getattr__( self, attr ) 
		
		plug = None
		for child in self.getChildren( ):
			# short and long name test 
			if child.partialName( ).split('.')[-1] == attr or child.partialName( 0, 0, 0, 0, 0, 1 ).split('.')[-1] == attr: 
				plug = child
				break
		# END for each child
		
		# found something ?
		if plug is not None:
			setattr( self, attr, plug )
			return plug
			
		# let default handler do the job 
		#return super( MPlug, self ).__getattr__( self, attr )
		raise AttributeError( "'%s' child plug not found in %s" % ( attr, self ) )
	
	
	def __eq__( self, other ):
		"""Compare plugs,handle elements correctly"""
		if not api.MPlug._api___eq__( self, other ):
			return False 
			
		# see whether elements are right - both must be elements if one is 
		if self.isElement():
			return self.getLogicalIndex( ) == other.getLogicalIndex()
			
		return True
	
	#} Overridden Methods
	
	#{ Plug Hierarchy Query 
	def getParent( self ):
		"""@return: parent of this plug or None
		@note: for array plugs, this is the array, for child plugs the actual parent """
		p = None
		if self.isChild( ):
			p = api.MPlug.parent( self )
		elif self.isElement( ):
			p = self.getArray( )
		
		if p.isNull( ):	# sanity check - not all
			return None
		
		return p
	
	def getChildren( self , predicate = lambda x: True):
		"""@return: list of intermediate child plugs, [ plug1 , plug2 ]
		@param predicate: return True to include x in result"""
		outchildren = []
		if self.isCompound( ):
			nc = self.getNumChildren( )
			for c in xrange( nc ):
				child = self.getChild( c )
				if predicate( child ):
					outchildren.append( child )
			# END FOR EACH CHILD
		# END if is compound 
		
		return outchildren
		
	def getSubPlugs( self , predicate = lambda x: True):
		"""@return: list of intermediate sub-plugs that are either child plugs or elemnt plugs
		@param predicate: return True to include x in result
		@note: use this function recursively for easy deep traversal of all 
		combinations of array and compound plugs"""
		if self.isCompound( ):
			outchildren = []
			nc = self.getNumChildren( )
			for c in xrange( nc ):
				child = self.getChild( c )
				if predicate( child ):
					outchildren.append( child )
			# END FOR EACH CHILD 
			return outchildren
		elif self.isArray( ):
			return [ elm for elm in self ]
		
		# we have no sub plugs 
		return []
	
	#} END hierarcy query 
	
	
	#{ Connections ( Edit )
	
	@undoable
	def connectTo( self, destplug, force=True ):
		"""Connect this plug to the right hand side plug
		@param destplug: the plug to which to connect this plug to
		@param force: if True, the connection will be created even if another connection 
		has to be broken to achieve that. 
		If False, the connection will fail if destplug is already connected to another plug
		@return: destplug allowing chained connections a >> b >> c
		@note: equals lhsplug >> rhsplug ( force = True ) or lhsplug > rhsplug ( force = False )
		@raise RuntimeError: If destination is already connected and force = False """
		
		# handle possibly connected plugs 
		if self.isConnectedTo( destplug ):		# already connected ?
			return 
		
		mod = None		# create mod only once we really need it
		
		# is destination already input-connected ? - disconnect it if required 
		destinputplug = destplug.p_input
		if not destinputplug.isNull():
			if not force:
				raise RuntimeError( "%s > %s failed as destination is connected to %s" % ( self, destplug, destinputplug ) )
			else:
				# disconnect
				mod = undo.DGModifier( )
				mod.disconnect( destinputplug, destplug )
			# END disconnect existing 
		# END destination is connected 
						
		# otherwise we can do the connection
		if not mod:
			mod = undo.DGModifier( )
			
		mod.connect( self, destplug )	# finally do the connection
		mod.doIt( )
		return destplug 
	
	def disconnect( self ):
		"""Completely disconnect all inputs and outputs of this plug
		@return: self, allowing chained commands"""
		self.disconnectInput
		self.disconnectOutputs
		return self 
	
	@undoable	
	def disconnectInput( self ):
		"""Disconnect the input connection if one exists
		@return: self, allowing chained commands"""
		inputplug = self.p_input
		if inputplug.isNull():
			return self
		
		mod = undo.DGModifier( )
		mod.disconnect( inputplug, self )
		mod.doIt()
		return self
		
	@undoable
	def disconnectOutputs( self ):
		"""Disconnect all outgoing connections if they exist
		@return: self, allowing chained commands"""
		outputplugs = self.getOutputs()
		if not len( outputplugs ):
			return self
			
		mod = undo.DGModifier()
		for destplug in outputplugs:
			mod.disconnect( self, destplug )
		mod.doIt()
		return self
		
	@undoable
	def disconnectFrom( self, other ):
		"""Disconnect this plug from other plug if they are connected
		@note: equals a | b 
		@return: other plug allowing to chain disconnections"""
		if not self.isConnectedTo( other ):
			return 
		
		mod = undo.DGModifier( )
		mod.disconnect( self, other )
		mod.doIt()
		
		return other
		
	#} END connections edit 
		
		
	#{ Connections ( Query )
	@staticmethod
	def haveConnection( lhsplug, rhsplug ):
		"""@return: True if lhsplug and rhs plug are connected - the direction does not matter
		@note: equals lhsplug & rhsplug"""
		return lhsplug.isConnectedTo( rhsplug ) or rhsplug.isConnectedTo( lhsplug )
		
	def isConnectedTo( self, destplug ):
		"""@return: True if this plug is connected to destination plug ( in that order )
		@note: return true for self > destplug but false for destplug > self
		@note: use the haveConnection method whether both plugs have a connection no matter which direction
		@note: equals self >= destplug
		@note: use L{isConnected} to find out whether this plug is connected at all"""
		return destplug in self.getOutputs()
		
	def getOutputs( self ):
		"""@return: MPlugArray with all plugs having this plug as source
		@todo: should the method be smarter and deal nicer with complex array or compound plugs ?""" 
		outputs = api.MPlugArray()
		self.connectedTo( outputs, False, True )
		return outputs
		
	def getInput( self ):
		"""@return: plug being the source of a connection to this plug or a null plug 
		if no such plug exists"""
		inputs = api.MPlugArray()
		self.connectedTo( inputs, True, False )
		
		noInputs = len( inputs )
		if noInputs == 0:
			# TODO: find a better way to get a MPlugPtr type that can properly be tested for isNull
			pa = api.MPlugArray( )
			pa.setLength( 1 )
			return pa[0]
		
		if noInputs == 1:
			return inputs[0]
			
		# must have more than one input - can this ever be ?
		raise ValueError( "Plug %s has more than one input plug - check how that can be" % self )
		
	def getConnections( self ):
		"""@return: tuple with input and outputs ( inputPlug, outputPlugs )"""
		return ( self.getInput( ), self, getOutputs( ) )
		
		
	#} END connections query 
	
	#{ Affects Query 
	def getDependencyInfo( self, by=False ):
		"""@return: list of plugs on this node that this plug affects or is being affected by
		@param by: if false, affected attributplugs will be returned, otherwise the attributeplugs affecting this one
		@note: you can also use the L{getDependencyInfo} method on the node itself if plugs are not 
		required - this will also be faster
		@note: have to use MEL :("""
		ownnode = self.getNode()
		attrs = cmds.affects( self.getAttribute().getName() , ownnode, by=by )
		
		outplugs = []
		depfn = api.MFnDependencyNode( ownnode._apiobj )
		
		for attr in attrs:
			outplugs.append( depfn.findPlug( attr ) )
		return outplugs
		
	def affects( self ):
		"""@return: list of plugs affected by this one"""
		return self.getDependencyInfo( by = False )
		
	def affected( self ):
		"""@return: list of plugs affecting this one"""
		return self.getDependencyInfo( by = True )
			
	#}
	
	#{ General Query
	def getNextLogicalIndex( self ):
		"""@return: index of logical indexed plug that does not yet exist
		@note: as this method does a thorough search, it is relatively slow
		compared to a simple numPlugs + 1 algorithm 
		@note: only makes sense for array plugs"""
		indices = api.MIntArray()
		self.getExistingArrayAttributeIndices( indices )
		
		logicalIndex = 0
		numIndices = indices.length()
		
		# do a proper serach
		if numIndices == 1:
			logicalIndex =  indices[0] + 1	# just increment the first one
		else:
			# assume indices are SORTED, smallest first
			for i in xrange( numIndices - 1 ):
				if indices[i+1] - indices[i] > 1:
					logicalIndex = indices[i] + 1 	# at least one free slot here
					break
				else:
					logicalIndex = indices[i+1] + 1	# be always one larger than the last one
			# END for each logical index
		# END if more than one indices exist
		return logicalIndex
		
	def getNextLogicalPlug( self ):
		"""@return: plug at newly created logical index
		@note: only valid for array plugs"""
		return self.getByLogicalIndex( self.getNextLogicalIndex() )
	
	def getAttribute( self ):
		"""@return: Attribute instance of our underlying attribute"""
		return nodes.Attribute( api.MPlug._api_attribute( self ) )
		
	def getNode( self ):
		"""@return: Node instance of our underlying node"""
		return nodes.Node( api.MPlug._api_node( self ) )
	
	def asMObject( *args, **kwargs ):
		"""@return: our Mobjects wrapped in L{Data}"""
		return nodes.Data( api.MPlug._api_asMObject( *args, **kwargs ) )
		
	#} END query
	
	
	#{ Properties
	p_outputs = property( getOutputs )
	p_input = property( getInput )
	p_connections = property( getConnections )
	
	#}
	
	#{ Name Remapping 
	__rshift__ = lambda self,other: self.connectTo( other, force=True )
	__gt__ = lambda self,other: self.connectTo( other, force=False )
	__ge__ = isConnectedTo
	__and__ = lambda lhs,rhs: MPlug.haveConnection( lhs, rhs )
	__or__ = disconnectFrom
	node = getNode
	attribute = getAttribute
	getChild = api.MPlug.child
	getArray = api.MPlug.array
	getByIndex = api.MPlug.elementByPhysicalIndex
	getByLogicalIndex = api.MPlug.elementByLogicalIndex
	getConnectionByPhysicalIndex = api.MPlug.connectionByPhysicalIndex
	getNumElements = api.MPlug.numElements
	getName = api.MPlug.name
	getPartialName = api.MPlug.partialName
	getLogicalIndex = api.MPlug.logicalIndex
	getNumChildren = api.MPlug.numChildren
	#} END name remapping 
	
#}



#############################
#### ARRAYS			    ####
##########################

#{ Arrays 

class ArrayBase( Abstract ):
	""" Base class for all maya arrays to easily fix them
	@note: set _apicls class variable to your api base class """
	
	def __len__( self ):
		return self._apicls.length( self )
	
	def __setitem__ ( self, index, item ):
		"""@note: does not work as it expects a pointer type - probably a bug"""
		return self.set( item, getPythonIndex( index, len( self ) ) )
	
	def __getitem__ ( self, index ):
		return self._apicls._api___getitem__( self,  getPythonIndex( index, len( self ) ) )
		
	def __iter__( self ):
		"""@return: iterator object"""
		return util.IntKeyGenerator( self ) 


class MPlugArray( api.MPlugArray, ArrayBase ):
	""" Wrap MPlugArray to make it compatible to pythonic contructs"""
	_apicls = api.MPlugArray
	
class MObjectArray( api.MObjectArray, ArrayBase ):
	""" Wrap MObject to make it compatible to pythonic contructs"""
	_apicls = api.MObjectArray
		
#}
	
