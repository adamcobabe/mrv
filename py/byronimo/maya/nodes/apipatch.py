"""B{byronimo.maya.nodes.apipatch}

Contains patch classes that are altering their respective api classes  

The classes here are rather verbose and used as patch-template which can be 
handled correctly by epydoc, and whose method will be used to patch the respective
api classes.

As they are usually derived from the class they patch , they could also be used directly

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
import byronimo.util as util
from byronimo.util import getPythonIndex 
import maya.OpenMaya as api
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
	forbiddenMembers = [ '__module__','_applyPatch' ]
	
	for cls in classes:
		# use the main class as well as all following base
		# the first base is always the main maya type that is patched
		templateclasses = [ cls ]
		templateclasses.extend( cls.__bases__[ 1: ] )
		

		# skip abstract classes ?
		if cls is Abstract or cls.__bases__[0] is Abstract:
			continue
			
		# SPECIAL CALL INTERFACE ?
		# If so, call and let the class do the rest
		if hasattr( cls, "_applyPatch" ):
			if not cls._applyPatch(  ):
				continue
		
		
		apicls = cls.__bases__[0]
		
		for tplcls in templateclasses:
			for name,member in tplcls.__dict__.iteritems():
				if name in forbiddenMembers:
					continue
				try:
					# store original - overwritten members must still be able to access it
					if hasattr( apicls, name ):
						morig = getattr( apicls, name )
						type.__setattr__( apicls, "_api_"+name, morig )
					type.__setattr__( apicls, name, member )
				except TypeError:
					pass 
				# END set patch member
			# END for each overwritten/patched member
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
	""" Wrap a maya plug to assure we always get MayaNodes ( instead of MObjects )
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
	#} Overridden Methods
	
	#{ Edit
	
	#}
	
	#{ Plug Hierarchy Query
	
	#}
	
	#{ Data Query  
	def asMObject( *args, **kwargs ):
		"""@return: our Mobjects wrapped in L{Data}"""
		return nodes.Data( api.MPlug._api_asMObject( *args, **kwargs ) )
		
	#}
	
	#{ Name Remapping 
	getChild = api.MPlug.child
	getParent = api.MPlug.parent
	getArray = api.MPlug.array
	getByIndex = api.MPlug.elementByPhysicalIndex
	getByLogicalIndex = api.MPlug.elementByLogicalIndex
	getConnectionByPhysicalIndex = api.MPlug.connectionByPhysicalIndex
	getNumElements = api.MPlug.numElements
	getName = api.MPlug.name
	getPartialName = api.MPlug.partialName
	#]
	
#}


#############################
#### ARRAYS			    ####
##########################

#{ Arrays 
class MPlugArray( api.MPlugArray ):
	""" Wrap MPlugArray to make it compatible to pythonic contructs
	Also it will always contain Plug objects isntead of MPlugs
	
	This wrapper will handle like python classes and always return Plug objects."""
	
	__len__ = api.MPlugArray.length
	
	def __setitem__ ( self, index, plug ):
		"""@note: does not work as it expects a pointer type - probably a bug"""
		return self.set( plug, getPythonIndex( index, len( self ) ) )
	
	def __getitem__ ( self, index ):
		return api.MPlugArray._api___getitem__( self,  getPythonIndex( index, len( self ) ) )
		
	def __iter__( self ):
		"""@return: iterator object"""
		return util.IntKeyGenerator( self )
		
#}
	
