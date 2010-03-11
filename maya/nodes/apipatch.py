# -*- coding: utf-8 -*-
"""
Contains patch classes that are altering their respective api classes

The classes here are rather verbose and used as patch-template which can be
handled correctly by epydoc, and whose method will be used to patch the respective
api classes.

As they are usually derived from the class they patch , they could also be used directly

@note: NEVER IMPORT CLASSES DIRECTLY IN HERE, keep at least one module , thus:
NOT: thisImportedClass BUT: module.thisImportedClass !
"""
import base
import mayarv.maya.undo as undo

import mayarv.util as util
from mayarv.util import getPythonIndex
import maya.OpenMaya as api
import maya.cmds as cmds
import inspect
import itertools
import it




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
	module = __import__( "mayarv.maya.nodes.apipatch", globals(), locals(), ['apipatch'] )
	classes = [ v for v in globals().values() if inspect.isclass(v) ]
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
	
	# in Maya 2010, these classes have an as_units method allowing 
	# it to be used in python without the use of getattr
	if hasattr(api.MTime, 'asUnits'):
		def __float__( self ): return self.asUnits(self.uiUnit())
	else:
		def __float__( self ): return getattr(self, 'as')(self.uiUnit())
	# END conditional implementation
	def __repr__(self): return '%s(%s)' % ( self.__class__.__name__, float(self) )


class MTime( api.MTime, TimeDistanceAngleBase ) :
	pass

class MDistance( api.MDistance, TimeDistanceAngleBase ) :
	pass

class MAngle( api.MAngle, TimeDistanceAngleBase ) :
	pass


# patch some Maya api classes that miss __iter__ to make them iterable / convertible to list
class PatchIterablePrimitives( Abstract ):
	"""@note: Classes derived from this base should not be used directly"""
	@classmethod
	def _applyPatch( cls ):
		"""Read per-class values from self and create appropriate methods and
		set them as well
		@note: idea from pymel"""
		def __len__(self):
			""" Number of components in Maya api iterable """
			return self._length
		# END __len__
		type.__setattr__( cls.__bases__[0], '__len__', __len__ )

		def __iter__(self):
			""" Iterates on all components of a Maya base iterable """
			for i in range( self._length ) :
				yield self.__getitem__( i )
		# END __iter__
		type.__setattr__( cls.__bases__[0], '__iter__', __iter__)

		def __str__( self ):
			return "[ %s ]" % " ".join( str( f ) for f in self )
		# END __str__

		type.__setattr__( cls.__bases__[0], '__str__', __str__)

		# allow the class members to be used ( required as we are using them )
		return True

class PatchMatrix( Abstract, PatchIterablePrimitives ):
	"""Only for matrices"""
	@classmethod
	def _applyPatch( cls ):
		"""Special version for matrices"""
		PatchIterablePrimitives._applyPatch.im_func( cls )
		def __iter__(self):
			""" Iterates on all 4 rows of a Maya api MMatrix """
			for r in range( self._length ) :
				row = self.__getitem__( r )
				yield [ self.scriptutil( row, c ) for c in range( self._length ) ]
		# END __iter__
		type.__setattr__( cls.__bases__[0], '__iter__', __iter__ )


		def __str__( self ):
			return "\n".join( str( v ) for v in self )
		# END __str__

		type.__setattr__( cls.__bases__[0], '__str__', __str__)

		return True



class MVector( api.MVector, PatchIterablePrimitives ):
	_length =3

class MFloatVector( api.MFloatVector, PatchIterablePrimitives ):
	_length =3

class MPoint( api.MPoint, PatchIterablePrimitives ):
	_length =4

class MFloatPoint( api.MFloatPoint, PatchIterablePrimitives ):
	_length =4

class MColor( api.MColor, PatchIterablePrimitives ):
	_length =4

class MQuaternion( api.MQuaternion, PatchIterablePrimitives ):
	_length =4

class MEulerRotation( api.MEulerRotation, PatchIterablePrimitives ):
	_length =4

class MMatrix( api.MMatrix, PatchMatrix ):
	_length =4
	scriptutil = api.MScriptUtil.getDoubleArrayItem

class MFloatMatrix( api.MFloatMatrix, PatchMatrix ):
	_length =4
	scriptutil = api.MScriptUtil.getFloatArrayItem
#
class MTransformationMatrix( api.MTransformationMatrix, PatchMatrix ):
	_length =4

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

	def getScale( self , space = api.MSpace.kTransform ):
		ms = api.MScriptUtil()
		ms.createFromDouble( 1.0, 1.0, 1.0 )
		p = ms.asDoublePtr()
		self._api_getScale( p, space );
		return MVector( *( ms.getDoubleArrayItem (p, i) for i in range(3) ) )

	def setScale( self, value, space = api.MSpace.kTransform ):
		ms = api.MScriptUtil()
		ms.createFromDouble( *value )
		p = ms.asDoublePtr()
		self._api_setScale ( p, space )

	def getRotate(self):
		return self.rotation()

	def setRotate(self, v ):
		self.setRotationQuaternion( v[0], v[1], v[2], v[3] )

	def getTranslation( self, space = api.MSpace.kTransform ):
		return self._api_getTranslation( space )

	def setTranslation( self, vector, space = api.MSpace.kTransform ):
		return self._api_setTranslation( vector, space )

#}

#############################
#### BASIC 		Types   ####
##########################

#{ Basic Types
class MPlug( api.MPlug, util.iDagItem ):
	""" Wrap a maya plug to assure we always get Nodes ( instead of MObjects )
	By overridding many object methods, the access to plugs becomes very pythonic"""
	# __slots__ = []  	 apparently it will always have a dict

	pa = api.MPlugArray( )		# the only way to get a null plug for use
	pa.setLength( 1 )

	#{ Overridden Methods
	def __getitem__( self, index ):
		"""@return:	 	Plug at physical integer index or
						Plug at logical float index or
						child plug with given name"""
		# strings are more probably I think, so lets have it first
		if isinstance( index, basestring ):
			return self.getChildByName( index )
		elif isinstance( index, float ):
			return self.getByLogicalIndex( int( index ) )
		else:
			return self.getByIndex( index )


	def __len__( self ):
		"""@return: number of physical elements in the array """
		if not self.isArray( ): return 0
		return self.getNumElements( )

	def __iter__( self ):
		"""@return: iterator object"""
		for i in xrange(len(self)):
			yield self.getByIndex(i)

	def __str__( self ):
		"""@return: name of plug"""
		#print repr( self )
		#if self.isNull(): return ""
		return api.MPlug.name( self )

	def __repr__( self ):
		"""@return: our class representation"""
		return "%s(%s_asAPIObj)" % ( self.__class__.__name__, self.getName() )

	def __eq__( self, other ):
		"""Compare plugs,handle elements correctly"""
		if not api.MPlug._api___eq__( self, other ):
			return False

		# see whether elements are right - both must be elements if one is
		if self.isElement():
			return self.getLogicalIndex( ) == other.getLogicalIndex()

		return True

	def __ne__( self, other ):
		return not( self.__eq__( other ) )

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

	def getChildByName( self, childname ):
		"""@return: childPlug with the given childname
		@raise AttributeError: if no child plug of the appropriate name could be found
		@note: reimplemented here to optimize speed"""
		outchild = None
		if self.isCompound( ):
			nc = self.getNumChildren( )
			for c in xrange( nc ):
				child = self.getChild( c )
				if (	child.partialName( ).split('.')[-1] == childname or
						child.partialName( 0, 0, 0, 0, 0, 1 ).split('.')[-1] == childname ):
					outchild = child
					break
				# END if it is the child we look for
			# END FOR EACH CHILD
		# END if is compound

		if child is None:
			raise AttributeError( "Plug %s has no child plug called %s" % ( self, childname ) )
		return child


	def getSubPlugs( self , predicate = lambda x: True):
		"""@return: list of intermediate sub-plugs that are either child plugs or element plugs
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

	#{ Attributes ( Edit )

	def _handleAttrSet( self, state, getfunc, setfunc ):
		"""Generic attribute handling"""
		op = undo.GenericOperation()
		op.addDoit( setfunc, state )
		op.addUndoit( setfunc, getfunc( ) )
		op.doIt()

	@undoable
	def setLocked( self, state ):
		"""If True, the plug's value may not be changed anymore"""
		self._handleAttrSet( state, self.isLocked, self._api_setLocked )

	@undoable
	def setKeyable( self, state ):
		"""if True, the plug may be set using animation curves"""
		self._handleAttrSet( state, self.isKeyable, self._api_setKeyable )

	@undoable
	def setCaching( self, state ):
		"""if True, the plug's value will be cached, preventing unnecessary computations"""
		self._handleAttrSet( state, self.isCachingFlagSet, self._api_setCaching )

	@undoable
	def setChannelBox( self, state ):
		"""if True, the plug will be visible in the channelbox, even though it might not
		be keyable or viceversa """
		self._handleAttrSet( state, self.isChannelBoxFlagSet, self._api_setChannelBox )

	#} END attributes edit


	#{ Connections ( Edit )

	@classmethod
	@undoable
	def connectMultiToMulti(self, iter_source_destination, force=False):
		"""Connect multiple source plugs to the same amount of detsination plugs.
		@note: This method provides the most efficient way to connect a large known 
		amount of plugs to each other
		@param iter_source_destination: Iterator yielding pairs of source and destination plugs to connect
		@param force: If True, existing input connections on the destination side will 
		be broken automatically. Otherwise the whole operation will fail if one 
		connection could not be made.
		@note: Both iterators need to yield the same total amount of plugs
		@note: In the current implementation, performance will be hurt if force 
		is specified as each destination has to be checked for a connection in advance"""
		mod = undo.DGModifier( )
		for source, dest in iter_source_destination:
			if force:
				destinputplug = dest.p_input
				if not destinputplug.isNull():
					if source == destinputplug:		
						continue
					# END skip this plug if it is already connected
					mod.disconnect(destinputplug, dest)
				# END destination is connected
			# END handle force
			mod.connect(source, dest)
		# END for each source, dest pair
		mod.doIt()
		return mod
		

	@undoable
	def connectTo( self, destplug, force=True ):
		"""Connect this plug to the right hand side plug
		@param destplug: the plug to which to connect this plug to. If it is an array plug,
		the next available element will be connected
		@param force: if True, the connection will be created even if another connection
		has to be broken to achieve that.
		If False, the connection will fail if destplug is already connected to another plug
		@return: destplug allowing chained connections a >> b >> c
		@note: equals lhsplug >> rhsplug ( force = True ) or lhsplug > rhsplug ( force = False )
		@raise RuntimeError: If destination is already connected and force = False
		@todo: currently we cannot handle nested array structures properly"""
		mod = undo.DGModifier( )

		# is destination already input-connected ? - disconnect it if required
		# Optimization: We only care if force is specified. It will fail otherwise
		if force:
			destinputplug = destplug.p_input
			if not destinputplug.isNull():
				# handle possibly connected plugs
				if self == destinputplug:		# is it us already ?
					return destplug
	
				# disconnect
				mod.disconnect( destinputplug, destplug )
				# END disconnect existing
			# END destination is connected
		# END force mode
		mod.connect( self, destplug )	# finally do the connection
		
		try:
			mod.doIt( )
		except RuntimeError:
			raise RuntimeError("Failed to connect %s to %s as destination is already connected or incompatible" % (self, destplug))
		# END connection failed handling
		return destplug

	def connectToArray( self, arrayplug, force = True, exclusive_connection = False ):
		"""Connect self an element of the given arrayplug.
		@param arrayplug: the array plug to which you want to connect to
		@param force: if True, the connection will be created even if another connection
		has to be broken to achieve that.
		@param exclusive_connection: if True and destplug is an array, the plug will only be connected
		to an array element if it is not yet connected
		@return: newly created element plug or the existing one"""
		# ARRAY PLUG HANDLING
		######################
		if arrayplug.isArray( ):
			if exclusive_connection:
				arrayplug.evaluateNumElements( )
				for delm in arrayplug:
					if self == delm.p_input:
						return delm
					# END if self == elm plug
				# END for each elemnt in destplug
			# END if exclusive array connection

			# connect the next free plug
			return self.connectTo( arrayplug.getNextLogicalPlug( ), force = force )
		# END Array handling
		raise AssertionError( "Given plug %r was not an array plug" % arrayplug )


	def disconnect( self ):
		"""Completely disconnect all inputs and outputs of this plug
		@return: self, allowing chained commands"""
		self.disconnectInput()
		self.disconnectOutputs()
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
		@param other: MPlug that will be disconnected from this plug
		@note: equals a | b
		@return: other plug allowing to chain disconnections"""
		#if not self.isConnectedTo( other ):
		#	return

		try:
			mod = undo.DGModifier( )
			mod.disconnect( self, other )
			mod.doIt()
		except RuntimeError:
			pass
		return other

	@undoable
	def disconnectNode( self, other ):
		"""Disconnect this plug from the given node if they are connected
		@param other: Node that will be completely disconnected from this plug"""
		for p in self.p_outputs:
			if p.getNode() == other:
				self | p
		# END for each plug in output

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

	def getOutput( self ):
		"""@return: out first plug that has this plug as source of a connection
		@raise IndexError: if the plug has no outputs
		@note: convenience method"""
		outputs = self.getOutputs()
		if len( outputs ) == 0:
			raise IndexError( "Plug %s was not connected to output plugs" % self )

		return outputs[0]

	def getInputs( self ):
		"""Special handler returning the input plugs of array elements
		@return: list of plugs connected to the elements of this arrayplug
		@note: if self is not an array, a list with 1 or 0 plugs will be returned"""
		out = []
		if self.isArray():
			self.evaluateNumElements()
			for elm in self:
				elminput = elm.p_input
				if elminput.isNull():
					continue
				out.append( elminput )
			# END for each elm plug in sets
		else:
			inplug = self.p_input
			if not inplug.isNull():
				out.append( inplug )
		# END array handling
		return out

	def getInput( self ):
		"""@return: plug being the source of a connection to this plug or a null plug
		if no such plug exists"""
		inputs = api.MPlugArray()
		self.connectedTo( inputs, True, False )

		noInputs = len( inputs )
		if noInputs == 0:
			# TODO: find a better way to get a MPlugPtr type that can properly be tested for isNull
			return self.pa[0]
		elif noInputs == 1:
			return inputs[0]

		# must have more than one input - can this ever be ?
		raise ValueError( "Plug %s has more than one input plug - check how that can be" % self )

	def getConnections( self ):
		"""@return: tuple with input and outputs ( inputPlug, outputPlugs )"""
		return ( self.getInput( ), self.getOutputs( ) )


	#} END connections query

	#{ Affects Query
	def getDependencyInfo( self, by=False ):
		"""@return: list of plugs on this node that this plug affects or is being affected by
		@param by: if false, affected attributplugs will be returned, otherwise the attributeplugs affecting this one
		@note: you can also use the L{getDependencyInfo} method on the node itself if plugs are not
		required - this will also be faster
		@note: have to use MEL :("""
		ownnode = self.getNode()
		attrs = cmds.affects( self.getAttribute().getName() , str( ownnode ), by=by )

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

	def getAttributeMObject( self ):
		"""@return: the original unwrapped api object - use this if you
		prefer speed over convenience"""
		return api.MPlug._api_attribute( self )

	def getAttribute( self ):
		"""@return: Attribute instance of our underlying attribute"""
		return base.Attribute( api.MPlug._api_attribute( self ) )

	def getNode( self ):
		"""@return: Node instance of our underlying node"""
		return base.NodeFromObj( api.MPlug._api_node( self ) )

	def getNodeMObject( self ):
		"""@return: unwrapped api object of the plugs node
		@note: use this if you prefer speed over convenience"""
		return api.MPlug._api_node( self )

	def asMObject( *args, **kwargs ):
		"""@return: the data api object"""
		return api.MPlug._api_asMObject( *args, **kwargs )

	def asData( *args, **kwargs ):
		"""@return: our data Mobject wrapped in L{Data}"""
		return base.Data( api.MPlug._api_asMObject( *args, **kwargs ) )
		
	def getFullyQualifiedName( self ):
		"""@return: string returning the absolute and fully qualified name of the
		plug. It might take longer to evaluate but is safe to use if you want to 
		convert the resulting string back to the actual plug"""
		return self.partialName(1, 1, 1, 0, 1, 1)
	#} END query


	#{ Set Data with Undo
	def _createUndoSetFunc( dataTypeId, getattroverride = None ):
		"""Create a function setting a value with undo support
		@param dataTypeId: string naming the datatype, like "Bool" - capitalization is
		important
		@note: if undo is globally disabled, we will resolve to implementing a faster
		function instead as we do not store the previous value.
		@note: to use the orinal method without undo, use api.MPlug.setX(your_plug, value)"""
		# this binds the original setattr and getattr, not the patched one
		getattrfunc = getattroverride
		if not getattrfunc:
			getattrfunc = getattr( api.MPlug, "as"+dataTypeId )
		setattrfunc = getattr( api.MPlug, "set"+dataTypeId )

		# YES, WE DUPLICATE CODE FOR SPEED
		####################################
		# Create actual functions
		finalWrappedSetAttr = None
		if dataTypeId == "MObject":
			def wrappedSetAttr( self, data ):
				# asMObject can fail instead of returning a null object !
				try:
					curdata = getattrfunc( self )
				except RuntimeError:
					curdata = api.MObject()
				op = undo.GenericOperation( )

				op.addDoit( setattrfunc, self, data )
				op.addUndoit( setattrfunc, self, curdata )

				op.doIt()
			# END wrapped method
			finalWrappedSetAttr = wrappedSetAttr
		else:
			def wrappedSetAttr( self, data ):
				# asMObject can fail instead of returning a null object !
				curdata = getattrfunc( self )
				op = undo.GenericOperation( )

				op.addDoit( setattrfunc, self, data )
				op.addUndoit( setattrfunc, self, curdata )

				op.doIt()
			# END wrappedSetAttr method
			finalWrappedSetAttr = wrappedSetAttr
		# END MObject special case

		# did undoable do anything ? If not, its disabled and we return the original
		wrappedUndoableSetAttr = undoable( finalWrappedSetAttr )
		if wrappedUndoableSetAttr is finalWrappedSetAttr:
			return setattrfunc
		# END return original 

		return wrappedUndoableSetAttr

	# wrap the methods
	setBool = _createUndoSetFunc( "Bool" )
	setChar = _createUndoSetFunc( "Char" )
	setShort = _createUndoSetFunc( "Short" )
	setInt = _createUndoSetFunc( "Int" )
	setFloat = _createUndoSetFunc( "Float" )
	setDouble = _createUndoSetFunc( "Double" )
	setString = _createUndoSetFunc( "String" )
	setMAngle = _createUndoSetFunc( "MAngle" )
	setMDistance = _createUndoSetFunc( "MDistance" )
	setMTime = _createUndoSetFunc( "MTime" )
	setMObject = _createUndoSetFunc( "MObject" )

	#} END set data


	#{ Properties
	p_outputs = property( getOutputs )
	p_output = property( getOutput )
	p_input = property( getInput )
	p_inputs = property( getInputs )
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



#} END basic types


#{ Function Sets
class MFnDependencyNode( api.MFnDependencyNode ):
	"""Add MFnBase methods to this function set as the base class cannot be instantiated 
	directly. Its vital for the mayarv wrapping system as the overridden method in the 
	MFnDependencyNode like type() are now on the base class"""
	
	hasObj = api.MFnBase.hasObj
	object = api.MFnBase.object
	setObject = api.MFnBase.setObject
	type = api.MFnBase.type

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
		return self.set( item, index )


_plugarray_getitem = api.MPlugArray.__getitem__
_objectarray_getitem = api.MObjectArray.__getitem__
_colorarray_getitem = api.MColorArray.__getitem__
_pointarray_getitem = api.MPointArray.__getitem__
class MPlugArray( api.MPlugArray, ArrayBase ):
	""" Wrap MPlugArray to make it compatible to pythonic contructs
	@note: for performance reasons, we do not provide negative index support"""
	_apicls = api.MPlugArray
	
	def __iter__( self ):
		"""@return: iterator object"""
		global _plugarray_getitem
		for i in xrange(len(self)):
			yield api.MPlug(_plugarray_getitem( self,  i ))
	
	def __getitem__ ( self, index ):
		"""Copy the MPlugs we return to assure their ref count gets incremented"""
		global _plugarray_getitem
		return api.MPlug(_plugarray_getitem( self,  index ))
	

class MObjectArray( api.MObjectArray, ArrayBase ):
	""" Wrap MObject to make it compatible to pythonic contructs.
	@note: This array also fixes an inherent issue that comes into play when 
	MObjects are returned using __getitem__, as the reference count does not natively
	get incremented, and the MObjects will be obsolete once the parent-array goes out 
	of scope
	@note: for performance reasons, we do not provide negative index support"""
	_apicls = api.MObjectArray
	
	def __iter__( self ):
		"""@return: iterator object"""
		global _objectarray_getitem
		for i in xrange(len(self)):
			yield api.MObject(_objectarray_getitem( self,  i ))
	
	def __getitem__ ( self, index ):
		"""Copy the MObjects we return to assure their ref count gets incremented"""
		global _objectarray_getitem
		return api.MObject(_objectarray_getitem( self,  index ))


class MColorArray( api.MColorArray, ArrayBase ):
	""" Wrap MColor to make it compatible to pythonic contructs.
	@note: for performance reasons, we do not provide negative index support"""
	_apicls = api.MColorArray
	
	def __iter__( self ):
		"""@return: iterator object"""
		global _colorarray_getitem
		for i in xrange(len(self)):
			yield _colorarray_getitem( self,  i )
	

class MPointArray( api.MPointArray, ArrayBase ):
	""" Wrap MPoint to make it compatible to pythonic contructs.
	@note: for performance reasons, we do not provide negative index support"""
	_apicls = api.MPointArray
	
	def __iter__( self ):
		"""@return: iterator object"""
		global _pointarray_getitem
		for i in xrange(len(self)):
			yield _pointarray_getitem( self,  i )
	

class MIntArray( api.MIntArray ):
	"""Attach additional creator functions"""
	
	@classmethod
	def fromRange(cls, i, j):
		"""@return: An MIntArray initialized with integers ranging from i to j
		@param i: first integer of the returned array
		@param j: last integer of returned array will have the value j-1"""
		if j < i:
			raise ValueError("j < i violated")
		if j < 0 or i < 0:
			raise ValueError("negative ranges are not supported")
		
		ia = api.MIntArray()
		l = j - i
		ia.setLength(l)
		
		# wouldn't it be great to have a real for loop now ?
		ci = 0
		for i in xrange(i, j):
			ia[ci] = i
			ci += 1
		# END for each integer
		
		# this is slightly slower
		#for ci, i in enumerate(xrange(i, j)):
		#	ia[ci] = i
		# END for each index/value pair
		
		return ia

	@classmethod
	def fromMultiple(cls, *args):
		"""@return: MIntArray created from the given indices"""
		ia = api.MIntArray()
		ia.setLength(len(args))
		
		ci = 0
		for index in args:
			ia[ci] = index
			ci += 1
		# END for each index
		
		return ia
		
	@classmethod
	def fromIter(cls, iter):
		"""@return: MIntArray created from indices yielded by iter
		@note: this one is less efficient than L{fromMultiple} as the final length 
		of the array is not predetermined"""
		ia = api.MIntArray()
		for index in iter:
			ia.append(index)
		return ia
	
	@classmethod
	def fromList(cls, list):
		"""@return: MIntArray created from the given list of indices"""
		ia = api.MIntArray()
		ia.setLength(len(list))
		
		ci = 0
		for index in list:
			ia[ci] = index
			ci += 1
		# END for each item
		
		return ia


class MSelectionList( api.MSelectionList, ArrayBase ):
	_apicls = api.MSelectionList
	
	def __iter__( self ):
		"""@return: iterator object"""
		return it.iterSelectionList(self)
	
	def __contains__( self, rhs ):
		"""@return: True if we contain rhs
		@note: As we check for Nodes as well as MayaAPI objects, we are possibly slow"""
		if isinstance(rhs, base.DagNode):
			return self.hasItem(rhs._apidagpath)
		elif isinstance(rhs, base.DependNode):
			return self.hasItem(rhs._apiobj)
		else:
			return self.hasItem(rhs)
		# END handle input type
		
	def __getitem__(self, index):
		"""Add [] operator support
		@param index: index from 0 to len(self), negative values are supported as well
		@note: this method returns Nodes or Plugs, it will not deal with components.
		If you need more control over your iteration, use L{toIter} instead"""
		if index < 0:
			index = self.length() + index
		# END handle negative index
		
		rval = None
		try: # dagpath
			rval = api.MDagPath()
			self.getDagPath(index, rval)
		except RuntimeError:
			try: # plug
				rval = MPlug.pa[0]
				self.getPlug(index, rval)
				rval.attribute()
				return rval
			except RuntimeError:
				# dg node
				rval = api.MObject()
				self.getDependNode(index, rval)
			# END its not an MObject
		# END handle dagnodes/plugs/dg nodes
		
		# its a node
		return base.NodeFromObj(rval)
	
	@staticmethod
	def fromStrings( iter_strings, **kwargs ):
		"""@return: MSelectionList initialized from the given iterable of strings
		@param **kwargs: passed to L{base.toSelectionListFromNames}"""
		return base.toSelectionListFromNames(iter_strings, **kwargs)
		
	@staticmethod
	def fromList( iter_items, **kwargs ):
		"""@return: MSelectionList as initialized from the given iterable of Nodes, 
		MObjects, MDagPaths or MPlugs
		@param **kwargs: passed to L{base.toSelectionList}"""
		return base.toSelectionList(iter_items, **kwargs)
		
	@staticmethod
	def fromComponentList( iter_components, **kwargs ):
		"""@return: MSelectionList as initialized from the given list of tuple( DagNode, Component ), 
		Component can be a filled Component object or null MObject
		@param **kwargs: passed to L{base.toComponentSelectionList}"""
		return base.toComponentSelectionList(iter_components, **kwargs)
		
	def toList( self, *args, **kwargs ):
		"""@return: list with the contents of this MSelectionList
		@param *args: passed to L{it.iterSelectionList}
		@param **kwargs: passed to L{it.iterSelectionList}"""
		return list(self.toIter(*args, **kwargs))
		
	def toIter( self, *args, **kwargs ):
		"""@return: iterator yielding of Nodes and MPlugs stored in this given selection list
		@param *args: passed to L{it.iterSelectionList}
		@param **kwargs: passed to L{it.iterSelectionList}"""
		return it.iterSelectionList( self, *args, **kwargs )
		
	def iterComponents( self, **kwargs ):
		"""@return: Iterator yielding node, component pairs, component is guaranteed 
		to carry a component, implying that this iterator applies a filter
		@param kwargs: passed on to L{it.iterSelectionList}"""
		kwargs['handleComponents'] = True
		pred = lambda pair: not pair[1].isNull()
		kwargs['predicate'] = pred
		return it.iterSelectionList( self, **kwargs )
		
	def iterPlugs( self, **kwargs ):
		"""@return: Iterator yielding all plugs on this selection list.
		@param kwargs: passed on to L{it.iterSelectionList}"""
		kwargs['handlePlugs'] = True
		pred = lambda n: isinstance(n, api.MPlug)
		kwargs['predicate'] = pred
		return it.iterSelectionList( self, **kwargs )
		
		
	
class MeshIteratorBase( Abstract ):
	"""Provides common functionality for all MItMesh classes"""
	
	def __iter__(self):
		"""@return: Iterator yielding self for each item in the iteration
		@note: the iteration will be reset before beginning it
		@note: extract the information you are interested in yourself"""
		self.reset()
		next = self.next
		if hasattr(self, 'count'):
			for i in xrange(self.count()):
				yield self
				next()
			# END for each item 
		else:
			isDone = self.isDone
			while not isDone():
				yield self
				next()
			# END while we have items
		# END handle optimized iteration, saving function calls
	
class MItMeshVertex( api.MItMeshVertex, MeshIteratorBase ):
	pass

class MItMeshEdge( api.MItMeshEdge, MeshIteratorBase ):
	pass

class MItMeshPolygon( api.MItMeshPolygon, MeshIteratorBase ):
	pass

class MItMeshFaceVertex( api.MItMeshFaceVertex, MeshIteratorBase ):
	pass
#}

