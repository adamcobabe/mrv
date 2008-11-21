"""B{byronimo.util}
All kinds of utility methods and classes that are used in more than one modules

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: configuration.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import networkx.tree as nxtree
from collections import deque as Deque
import weakref
import inspect 

############################
#### Methods 		  	####
##########################

def decodeString( valuestr ):
	""" @return: int,float or str from string valuestr - a string that encodes a 
	numeric value or a string
	@raise TypeError: if the type could not be determined"""
	# put this check here intentionally - want to allow
	if not isinstance( valuestr, basestring ):
		raise TypeError( "Invalid value type: only int, long, float and str are allowed", valuestr )
		
	types = ( long, float )
	for numtype in types:
		try:
			val = numtype( valuestr )
			
			# truncated value ?
			if val != float( valuestr ):
				continue
				
			return val
		except ( ValueError,TypeError ):
			continue
	# END for each numeric type 
	
	# its just a string and not a numeric type  
	return valuestr
	
def decodeStringOrList( valuestrOrList ):
	"""@return: as L{decodeString}, but returns a list of appropriate values if 
	the input argument is a list or tuple type"""
	if isinstance( valuestrOrList , ( list, tuple ) ):
		return [ decodeString( valuestr ) for valuestr in valuestrOrList ]
	
	return decodeString( valuestrOrList )

def capitalize(s):
	"""@return: s with first letter capitalized"""
	return s[0].upper() + s[1:]

def uncapitalize(s, preserveAcronymns=False):
	"""@return: s with first letter lower case
	@param preserveAcronymns: enabled ensures that 'NTSC' does not become 'nTSC'
	@note: from pymel
	"""
	try:
		if preserveAcronymns and s[0:2].isupper():
			return s
	except IndexError: pass
	
	return s[0].lower() + s[1:]

def getPythonIndex( index, length ):
	"""Compute the actual index based on the given index and array length, thus
	-1 will result in the last array element's index"""
	if index > -1: return index
	return length + index			# yes, length be better 1 or more ;)


def copyClsMembers( sourcecls, destcls, overwritePrefix = None, forbiddenMembers = [] ):
	"""Copy the members or sourcecls to destcls while ignoring member names in forbiddenMembers
	It will only copy mebers of this class, not its base classes
	@param sourcecls: class whose members should be copied
	@param destcls: class to receive members from sourcecls
	@param overwritePrefix: if None, existing members on destcls will not be overwritten, if string, 
	the original method will be stored in a name like prefix+originalname ( allowing you to access the 
	original method lateron )
	@note: this can be useful if you cannot inherit from a class directly because you would get 
	method resolution order problems
	@note: see also the L{MetaCopyClsMembers} meta class"""
	for name,member in sourcecls.__dict__.iteritems():
		if name in forbiddenMembers:
			continue
		try:
			# store original - overwritten members must still be able to access it
			if hasattr( destcls, name ):
				if not overwritePrefix:
					continue
				morig = getattr( destcls, name )
				type.__setattr__( destcls, overwritePrefix+name, morig )
			#print ( "%s - adjusted with %s.%s" % ( destcls.__name__,sourcecls.__name__, name ) )
			type.__setattr__( destcls, name, member )
		except TypeError:
			pass 
	# END for each memebr in sourcecls

def getPackageClasses( importBase, packageFile, predicate = lambda x: True ):
	"""@return: all classes of modules of the given package file that additionally 
	match given predicate
	@param importBase: longest import base path whose submodules contain the classes to import  
	@param packageFile: the filepath to the package, as given in your __file__ variables 
	@param predicate: receives the class and returns True if it is a class you are looking for"""
	from glob import glob
	import os
	import inspect

	packageDir = os.path.dirname( packageFile )
	
	# get all submodules
	basenameNoExt = lambda n: os.path.splitext( os.path.split( n )[1] )[0]
	pymodules = glob( os.path.join( packageDir, "*.py" ) )
	pymodules = [ basenameNoExt( m ) for m in pymodules 
							if not os.path.basename( m ).startswith( '_' ) ]
			
	outclasses = []
	classAndCustom = lambda x: inspect.isclass( x ) and predicate( x )
	for modulename in pymodules: 
		modobj = __import__( "%s.%s" % ( importBase, modulename ), globals(), locals(), [''] )
		for name,obj in inspect.getmembers( modobj, predicate = classAndCustom ):
			outclasses.append( obj )
	# import the modules 
	return outclasses
	
def iterNetworkxGraph( graph, startItem, direction = 0, prune = lambda i,g: False, 
					   stop = lambda i,g: False, depth = -1, branch_first=True, 
					   visit_once = True, ignore_startitem=1 ):
	"""@return: list of items that are related to the given startItem
	@param direction: specifies search direction, either :
	0 = items being successors of startItem
	1 = items being predecessors of startItem
	@param prune: return True if item i in graph g should be pruned from result
	@param stop: return True if item i in graph g should be returned, but should also 
	stop the search in that direction
	@param depth: define at which level the iteration should not go deeper
	if -1, there is no limit
	i.e. if 1, you would only get the first level of predessessors/successors 
	@param branch_first: if True, items will be returned branch first, otherwise depth first
	@param visit_once: if True, items will only be returned once, although they might be encountered
	several times
	@param ignore_startitem: if True, the startItem will be ignored and automatically pruned from 
	the result 
	@note: this is an adjusted version of L{dgengine.iterShells}"""
	visited = set()
	stack = Deque()
	stack.append( ( 0 , startItem ) )		# startitem is always depth level 0
	
	def addToStack( stack, lst, branch_first, dpth ):
		if branch_first:
			reviter = ( ( dpth , lst[i] ) for i in range( len( lst )-1,-1,-1) )
			stack.extendleft( reviter )
		else:
			stack.extend( ( dpth,item ) for item in lst )
	# END addToStack local method
	
	# adjust function to define direction
	directionfunc = graph.successors
	if direction == 1:
		directionfunc = graph.predecessors
	
	while stack:
		d, item = stack.pop()			# depth of item, item
		
		if item in visited:
			continue
		
		if visit_once:
			visited.add( item )
		
		if stop( item, graph ):
			continue
			
		skipStartItem = ignore_startitem and ( item == startItem )
		if not skipStartItem and not prune( item, graph ):
			yield item
		
		# only continue to next level if this is appropriate !
		nd = d + 1
		if depth > -1 and nd > depth:
			continue
		
		addToStack( stack, directionfunc( item ), branch_first, nd )
	# END for each item on work stack


############################
#### Classes 		  	####
##########################



#{ Interfaces 

class iDagItem( object ):
	""" Describes interface for a DAG item.
	Its used to unify interfaces allowing to access objects in a dag like graph
	Of the underlying object has a string representation, the defatult implementation 
	will work natively.
	
	Otherwise the getParent and getChildren methods should be overwritten
	@note: a few methods of this class are abstract and need to be overwritten
	@note: this class expects the attribute '_sep' to exist containing the 
	separator at which your object should be split ( for default implementations ).
	This works as the passed in pointer will belong to derived classes that can 
	define that attribute on instance or on class level"""
	
	kOrder_DepthFirst, kOrder_BreadthFirst = range(2)
	
	#{ Configuration
	# separator as appropriate for your class if it can be treated as string
	# if string treatment is not possibly, override the respective method
	_sep = None
	#} END configuration 
	
	#{ Query Methods 
	
	def isRoot( self ):
		"""@return: True if this path is the root of the DAG """
		return self ==  self.getRoot()
		
	def getRoot( self ):
		"""@return: the root of the DAG - it has no further parents"""
		parents = self.getParentDeep( )
		if not parents:
			return self
		return parents[-1]
	
	def getBasename( self ):
		"""@return: basename of this path, '/hello/world' -> 'world'"""
		return str(self).split( self._sep )[-1]
		
	def getParent( self ):
		"""@return: parent of this path, '/hello/world' -> '/hello' or None if this path 
		is the dag's root"""
		tokens =  str(self).split( self._sep )
		if len( tokens ) <= 2:		# its already root 
			return None
			
		return self.__class__( self._sep.join( tokens[0:-1] ) )
		
	def getParentDeep( self ):
		"""@return: all parents of this path, '/hello/my/world' -> [ '/hello/my','/hello' ]"""
		return list( self.iterParents( ) )
		
		return out 
		
	def getChildren( self , predicate = lambda x: True):
		"""@return: list of intermediate children of path, [ child1 , child2 ]
		@param predicate: return True to include x in result
		@note: the child objects returned are supposed to be valid paths, not just relative paths"""
		raise NotImplementedError( )
		
	def getChildrenDeep( self , order = kOrder_BreadthFirst, predicate=lambda x: True ):
		"""@return: list of all children of path, [ child1 , child2 ]
		@param order: order enumeration 
		@param predicate: returns true if x may be returned
		@note: the child objects returned are supposed to be valid paths, not just relative paths"""
		out = []
		
		if order == self.kOrder_DepthFirst:
			def depthSearch( child ):
				if not predicate( c ):
					return 
				children = child.getChildren( predicate = predicate )
				for c in children:
					depthSearch( c )
				out.append( child )
			# END recursive search method
			
			depthSearch( self )
		# END if depth first 
		elif order == self.kOrder_BreadthFirst:
			childstack = Deque( [ self ] )		
			while childstack:
				item = childstack.pop( )
				if not predicate( item ):
					continue 
				children = item.getChildren( predicate = predicate )
				
				childstack.extendleft( children )
				out.extend( children )
			# END while childstack
		# END if breadth first 
		return out
		
	def isPartOf( self, other ):
		"""@return: True if self is a part of other, and thus can be found in other
		@note: operates on strings only"""
		return str( other ).find( str( self ) ) != -1
		
	def isRootOf( self, other ):
		"""@return: True other starts with self
		@note: operates on strings
		@note: we assume other has the same type as self, thus the same separator"""
		selfstr =  self.addSep( str( self ), self._sep )
		other = self.addSep( str( other ), self._sep )
		return other.startswith( selfstr )
		
	#} END Query Methods
	
	#{ Iterators 
	def iterParents( self , predicate = lambda x : True ):
		"""@return: generator retrieving all parents up to the root
		@param predicate: returns True for all x that you want to be returned"""
		curpath = self
		while True:
			parent = curpath.getParent( )
			if not parent:
				raise StopIteration
			
			if predicate( parent ):	
				yield parent
				
			curpath = parent
		# END while true
		
		
	#} END Iterators 

	#{ Name Generation
	@staticmethod
	def addSep( item, sep ):
		"""@return: item with separator added to it ( just once )
		@note: operates best on strings
		@param item: item to add separator to
		@param sep: the separator"""
		if not item.endswith( sep ):
			item += sep
		return item
		
	def getFullChildName( self, childname ):
		"""Add the given name to the string version of our instance
		@return: string with childname added like name _sep childname"""
		sname = self.addSep( str( self ), self._sep )
		
		if childname.startswith( self._sep ):
			childname = childname[1:]
			
		return sname + childname		
	
	#} END name generation


class iDuplicatable( object ):
	"""Simple interface allowing any class to be properly duplicated
	@note: to implement this interface, implement L{createInstance} and 
	L{copyFrom} in your class """
	#{ Interface 
	
	def createInstance( self, *args, **kwargs ):
		"""Create and Initialize an instance of self.__class__( ... ) based on your own data
		@return: new instance of self
		@note: using self.__class__ instead of an explicit class allows derived 
		classes that do not have anything to duplicate just to use your implementeation
		@note: you must support *args and **kwargs if one of your iDuplicate bases does"""
		raise NotImplementedError( "Implement like self.__class__( yourInitArgs )" )
		
	def copyFrom( self, other, *args, **kwargs ):
		"""Copy the data from other into self as good as possible
		Only copy the data that is unique to your specific class - the data of other 
		classes will be taken care of by them !
		@note: you must support *args and **kwargs if one of your iDuplicate bases does"""
		raise NotImplementedError( "Copy all data you know from other into self" )
		
	#} END interface
	
	def duplicate( self, *args, **kwargs ):
		"""Implements a c-style copy constructor by creating a new instance of self
		and applying the L{copyFrom} methods from base to all classes implementing the copyfrom 
		method. Thus we will call the method directly on the class
		@param *args,**kwargs : passed to copyFrom and createInstance method to give additional directions"""
		try:
			createInstFunc = getattr( self, 'createInstance' ) 
			instance = createInstFunc( *args, **kwargs )
		except TypeError,e: 		#	 could be the derived class does not support the args ( although it should
			#raise
			raise AssertionError( "The subclass method %s must support *args and or **kwargs if the superclass does, error: %s" % ( createInstFunc, e ) )
		
		
		# Sanity Check 
		if not ( instance.__class__ is self.__class__ ):
			msg = "Duplicate must have same class as self, was %s, should be %s" % ( instance.__class__, self.__class__ )
			raise AssertionError( msg )
			
		return self.copyTo( instance, *args, **kwargs )
		
	def copyTo( self, instance, *args, **kwargs ):
		"""Copy the values of ourselves onto the given instance which must be an 
		instance of our class to be compatible.
		Only the common classes will be copied to instance
		@return: altered instance
		@note: instance will be altered during theat process"""
		if not isinstance( instance, self.__class__ ):
			raise TypeError( "copyTo: Instance must be of type %s but was type %s" % ( type( self ), type( instance ) ) ) 
			
		# Get reversed mro, starting at lowest base
		mrorev = instance.__class__.mro()
		mrorev.reverse()
		
		# APPLY COPY CONSTRUCTORS !
		##############################
		for base in mrorev:
			if base is iDuplicatable:
				continue
			
			# must get the actual method directly from the base ! Getattr respects the mro ( of course )
			# and possibly looks at the base's superclass methods of the same name
			try:
				copyFromFunc = base.__dict__[ 'copyFrom' ] 
				copyFromFunc( instance, self, *args, **kwargs )
			except KeyError:
				pass 
			except TypeError,e: 		#	 could be the derived class does not support the args ( although it shold
				raise AssertionError( "The subclass method %s.%s must support *args and or **kwargs if the superclass does, error: %s" % (base, copyFromFunc,e) )
		# END for each base 
		
		# return the result !
		return instance
		
	
class iProgressIndicator( object ):
	"""Interface allowing to submit progress information
	The default implementation just prints the respective messages
	Additionally you may query whether the computation has been cancelled by the user
	@note: this interface is a simple progress indicator itself, and can do some computations
	for you if you use the get() method yourself"""
	
	#{ Initialization 
	def __init__( self, min = 0, max = 100, is_relative = True, may_abort = False, **kwargs ):
		"""@param min: the minimum progress value
		@param max: the maximum progress value
		@param is_relative: if True, the values given will be scaled to a range of 0-100, 
		if False no adjustments will be done
		@param kwargs: additional arguments being ignored"""
		self.setRange( min, max )
		self.setRelative( is_relative )
		self.setAbortable( may_abort )
		self.__progress = min
		
		
		
	def begin( self ):
		"""intiialize the progress indicator before calling L{set} """
		self.__progress = self.__min		# refresh
	
	def end( self ):
		"""indicate that you are done with the progress indicator - this must be your last
		call to the interface""" 
		pass 
		
	#} END initialization 
	
	#{ Edit
	def refresh( self, message = None ):
		"""Refresh the progress indicator so that it represents its values on screen.
		@param message: message passed along by the user"""
		p = self.get( )
		
		if not message:
			message = self.getPrefix( p )
			
		print message
		
	def set( self, value, message = None , omit_refresh=False ):
		"""Set the progress of the progress indicator to the given value
		@param value: progress value ( min<=value<=max )
		@param message: optional message you would like to give to the user
		@param omit_refresh: by default, the progress indicator refreshes on set, 
		if False, you have to call refresh manually after you set the value"""
		self.__progress = value
		
		if not omit_refresh:
			self.refresh( message = message )
	
	def setRange( self, min, max ):
		"""set the range within we expect our progress to occour"""
		self.__min = min
		self.__max = max
	
	def setRelative( self, state ):
		"""enable or disable relative progress computations"""
		self.__relative = state
		
	def setAbortable( self, state ):
		"""If state is True, the progress may be interrupted, if false it cannot 
		be interrupted"""
		self.__may_abort = state
		
	def setup( self, range=None, relative=None, abortable=None, begin=True ):
		"""Multifunctional, all in one convenience method setting all important attributes
		at once. This allows setting up the progress indicator with one call instead of many
		@note: If a kw argument is None, it will not be set
		@param range: Tuple( min, max ) - start ane end of progress indicator range
		@param relative: equivalent to L{setRelative}
		@param abortable: equivalent to L{setAbortable}
		@param begin: if True, L{begin} will be called as well"""
		if range is not None:
			self.setRange( range[0], range[1] )
			
		if relative is not None:
			self.setRelative( relative )
		
		if abortable is not None:
			self.setAbortable( abortable )
			
		if begin:
			self.begin()
		
	#} END edit  
	
	#{ Query
	def get( self ):
		"""@return: the current progress value
		@note: if set to relative mode, values will range 
		from 0.0 to 100.0"""
		if not self.isRelative():
			mn,mx = self.getRange()
			return min( max( self.__progress, mn ), mx ) 
			
		# compute the percentage
		p = self.__progress
		mn,mx = self.getRange()
		return min( max( ( p - mn ) / float( mx - mn ), 0.0 ), 1.0 ) * 100.0
		
	def getRange( self ):
		"""@return: tuple( min, max ) value"""
		return ( self.__min, self.__max )
		
	def getPrefix( self, value ):
		"""@return: a prefix indicating the progress according to the current range
		and given value """
		prefix = ""
		if self.isRelative():
			prefix = "%i%%" % value
		else:
			mn,mx = self.getRange()
			prefix = "%i/%i" % ( value, mx )
			
		return prefix 
		
	def isAbortable( self ):
		"""@return: True if the process may be cancelled"""
		return self.__may_abort
		
	def isRelative( self ):
		"""@return: true if internal progress computations are relative, False if 
		they are treated as absolute values"""
		return self.__relative
		
	def isCancelRequested( self ):
		"""@return: true if the operation should be aborted"""
		return False
	#} END query 

#} END interfaces 

class Call( object ):
	"""Call object encapsulating any code, thus providing a simple facade for it
	@note: derive from it if a more complex call is required""" 
	def __init__( self, func, *args,**kwargs ):
		"""Initialize object with function to call once this object is called"""
		self.func = func
		self.args = args
		self.kwargs = kwargs
		
	def __call__( self, *args, **kwargs ):
		"""Execute the stored function on call
		@note: having *args and **kwargs set makes it more versatile"""
		return self.func( *self.args, **self.kwargs )
		


class WeakInstFunction( object ):
	"""Create a proper weak instance to an instance function by weakly binding 
	the instance, not the bound function object.
	When called, the weakreferenced instance pointer will be retrieved, if possible, 
	to finally make the call. If it could not be retrieved, the call 
	will do nothing."""
	__slots__ = ( "_weakinst", "_clsfunc" )
	
	def __init__( self, instancefunction ):
		self._weakinst = weakref.ref( instancefunction.im_self )
		self._clsfunc = instancefunction.im_func
		
		
	def __call__( self, *args, **kwargs ):
		inst = self._weakinst()
		if not inst:	# went out of scope
			print "Instance for call has been deleted as it is weakly bound"
			return 
		
		return self._clsfunc( inst, *args, **kwargs )
	
	
class CallbackBase( iDuplicatable ):
	"""Base class for all classes that want to provide a common callback interface
	to supply event information to clients.
	Usage
	-----
	Derive from this class and define your callbacks like :
	eventname = CallbackBase.Event( "eventname" )
	Call it using 
	self.sendEvent( "eventname", [ args [ ,kwargs ] ] )
	 - depends on the assumption that eventname is also the name of the atttribute 
	   where the event class can be found 
	self.sendEvent( owncls.eventname [ args [, kwargs ] ] )
	 - will always work as no string id is being used
	If more args are given during your call, this has to be documented 
	
	Users register using 
	yourclass.eventname = callable
	
	and deregister using 
	yourclass.removeEvent( eventname, callable )
	
	@note: if use_weak_ref is True, we will weakref the eventfunction, and deal 
	properly with instance methods which would go out of scope immediatly otherwise
	
	@note: using weak-references to ensure one does not keep objects alive, 
	see L{use_weakref}"""
	
	#{ Configuration 
	# if True, the sender, thus self of an instance of this class, will be put 
	# as first arguments to functions when called for a specific event
	sender_as_argument = False
	#} END configuration 
	
	class Event( object ):
		"""Descriptor allowing to easily setup callbacks for classes derived from 
		CallbackBase"""
		#{ Configuration 
		# if true, functions will be weak-referenced - its useful if you use instance 
		# variables as callbacks 
		use_weakref = True
		#} END configuration 
		
		
		def __init__( self, eventname ):
			self._name = eventname					# original name 					
			self.eventname = eventname + "_set"	# set attr going to keep events 
			
		def _toKeyFunc( self, eventfunc ):
			"""@return: an eventfunction suitable to be used as key in our instance 
			event set"""
			if self.use_weakref:
				if inspect.ismethod( eventfunc ):
					eventfunc = WeakInstFunction( eventfunc )
				else:
					eventfunc = weakref.ref( eventfunc )
				# END instance function special handling 
			# END if use weak ref 
			return eventfunc
		
		def _keyToFunc( self, eventkey ):
			"""@return: event function from the given eventkey as stored in 
			our events set.
			@note: this is required as the event might be weakreffed or not"""
			if self.use_weakref:
				if isinstance( eventkey, WeakInstFunction ):
					return eventkey
				else:
					return eventkey()
				# END instance method handling 
			# END weak ref handling 
			return eventkey
		
		def __set__( self, inst, eventfunc ):
			"""Set a new event to our object"""
			self.__get__( inst ).add( self._toKeyFunc( eventfunc ) )
			
		def __get__( self, inst, cls = None ):
			"""Always return the set itself so that one can iterate it
			on class level, return self"""
			if cls is not None:
				return self
				
			if not hasattr( inst, self.eventname ):
				setattr( inst, self.eventname, set() )
			
			return getattr( inst, self.eventname )
			
		def remove( self, inst, eventfunc ):
			"""Remove eventfunc as listener for this event from the instance, i.e
			CallbackBaseCls.event.remove( inst, func )"""
			inst.removeEvent( self, eventfunc )
		
		def duplicate( self ):
			inst = self.__class__( "" )
			inst._name = self._name
			inst.eventname = self.eventname
			return inst
		
	# END event class 
	
	def _toEventInst( self, event ):
		"""@return: event instance for eventname or instance"""
		eventinst = event 
		if isinstance( event, basestring ):
			eventinst = getattr( self.__class__, event )
		return eventinst
		
	def removeEvent( self, event, eventfunc ):
		"""remove the given event function from the event identified by event
		@param event: either the name of the event as given upon creation or the event 
		or the event instance being a class variable of CallbackBase
		@note: will not raise if it does not exist"""
		eventinst = self._toEventInst( event )
		eventfunc = eventinst._toKeyFunc( eventfunc )
		try:
			eventinst.__get__( self ).remove( eventfunc )
		except KeyError:
			pass 
			
	def sendEvent( self, event, *args, **kwargs ):
		"""Send the given event to all registered event listeners
		@note: will catch all event exceptions trown by the methods called
		@param event: either name of event on self or the event instance itself
		@return: False if at least one event call threw an exception, true otherwise"""
		eventinst = self._toEventInst( event )
		callbackset = eventinst.__get__( self )
		success = True
		for function in callbackset:
			try:
				func = eventinst._keyToFunc( function ) 
				if func:
					if self.sender_as_argument:
						func( self, *args, **kwargs )
					else:
						func( *args, **kwargs )
					# END sendder as argument 
				# END func is valid 
				else:
					print "Listener for callback of %s was not available anymore" % self 
			except Exception:
				success = False
				#print "Error: Exception thrown by function %s during event %s" % ( func, eventname )
		# END for each registered event
		return success
		
	def listEventNames( self ):
		"""@return: list of event ids that exist on our class"""
		return [ name for name,member in inspect.getmembers( self, lambda m: isinstance( m, self.Event ) ) ]
			
		
	#{ iDuplicatable 
	def copyFrom( self, other, *args, **kwargs ):
		"""Copy callbacks from other to ourselves"""
		eventlist = inspect.getmembers( self, lambda m: isinstance( m, self.Event ) )
		for eventname,event in eventlist:
			setattr( self.__class__, eventname, event.duplicate( ) )
	
	#} END iDuplicatable
		
	
class InterfaceMaster( iDuplicatable ):
	"""Base class making the derived class an interface provider, allowing interfaces 
	to be set, queried and used including build-in use"""
	
	#{ Configuration 
	im_provide_on_instance = True			 # if true, interfaces are available directly through the class using descriptors 
	#} END configuration 
	
	#{ Helper Classes 
	class InterfaceDescriptor( object ):
		"""Descriptor handing out interfaces from our interface dict
		They allow access to interfaces directly through the InterfaceMaster without calling
		extra functions"""
		
		def __init__( self, interfacename ):
			self.iname = interfacename			# keep name of our interface 
		
		def __get__( self, inst, cls = None ):
			if inst is None:
				raise AttributeError( "Interfaces must be accessed through the instance of the class" )
			
			try:
				return inst.getInterface( self.iname )
			except KeyError:
				raise AttributeError( "Interface %s does not exist" % self.iname )
				
		def __set__( self, value ):
			raise ValueError( "Cannot set interfaces through the instance - use the setInterface method instead" ) 
	
	
	class _InterfaceHandler( object ):
		"""Utility class passing all calls to the stored InterfaceBase, updating the 
		internal caller-id"""
		def __init__( self, ibase ):
			self.__ibase = ibase
			self.__callerid = ibase._num_callers
			ibase._num_callers += 1
			
			ibase._current_caller_id = self.__callerid		# assure the callback finds the right one
			ibase.givenToCaller( )
			
		def __getattr__( self, attr ):
			self.__ibase._current_caller_id = self.__callerid 	# set our caller 
			return getattr( self.__ibase, attr )
			
		def __del__( self ):
			self.__ibase.aboutToRemoveFromCaller( )
			self.__ibase._num_callers -= 1
			self.__ibase._current_caller_id = -1
	
	
	class InterfaceBase( object ):
		"""If your interface class is derived from this base, you get access to 
		access to call to the number of your current caller.
		@note: You can register an InterfaceBase with several InterfaceMasters and 
		share the caller count respectively"""
		def __init__( self ):
			self._current_caller_id	 = -1 # id of the caller currently operating on us
			self._num_callers = 0		# the amount of possible callers, ids range from 0 to (num_callers-1)
		
		def getNumCallers( self ):
			"""@return: number possible callers"""
			return self._num_callers	
			
		def getCallerId( self ):
			"""Return the number of the caller that called your interface method
			@note: the return value of this method is undefined if called if the 
			method has been called by someone not being an official caller ( like yourself )"""
			return self._current_caller_id
			
		def givenToCaller( self ):
			"""Called once our interface has been given to a new caller.
			The caller has not made a call yet, but its id can be queried"""
			pass 
			
		def aboutToRemoveFromCaller( self ):
			"""Called once our interface is about to be removed from the current 
			caller - you will not receive a call from it anymore """
			pass 
		
	#} END helper classes 
	
	#{ Object Overrides 
	def __init__( self ):
		"""Initialize the interface base with some tracking variables"""
		self._idict = dict()			# keep interfacename->interfaceinstance relations 
	
	#} END object overrides 
	
	def copyFrom( self, other, *args, **kwargs ):
		"""Copy all interface from other to self, use they duplciate method if 
		possibly """
		for ifname, ifinst in other._idict.iteritems():
			myinst = ifinst
			if hasattr( ifinst, "duplicate" ):
				myinst = ifinst.duplicate( )
				
			self.setInterface( ifname, myinst )
		# END for each interface in other 
	
	
	#{ Interface 
	def setInterface( self, interfaceName, interfaceInstance ):
		"""Set the given interfaceInstance to be handed out once an interface 
		with interfaceName is requested from the provider base
		@param interfaceName: should start with i..., i.e. names would be iInterface
		The name can be used to refer to the interface later on
		@param interfaceInstance: instance to be handed out once an interface with the 
		given name is requested by the InterfaceMaster or None
		if None, the interface will effectively be deleted
		@raise ValueError: if given InterfaceBase has a master already """   
		if interfaceInstance is None:			# delete interface ?
			# delete from dict
			try:
				del( self._idict[ interfaceName ] )
			except KeyError:
				pass 
			
			# delete class descriptor  
			if self.im_provide_on_instance: 
				try: 
					delattr( self.__class__, interfaceName )
				except AttributeError:
					pass 
			# END del on class 
				 
		# END interface deleting
		else:
			self._idict[ interfaceName ] = interfaceInstance
			
			# set on class ?
			if self.im_provide_on_instance:
				setattr( self.__class__, interfaceName, self.InterfaceDescriptor( interfaceName ) ) 
		
		# provide class variables ?
		
		
	def getInterface( self, interfaceName ):
		"""@return: an interface registered with interfaceName
		@raise ValueError: if no such interface exists"""
		try:
			iinst = self._idict[ interfaceName ]
			
			# return wrapper if we can, otherwise just 
			if isinstance( iinst, self.InterfaceBase ):
				return self._InterfaceHandler( iinst )
			else:
				return iinst
		except KeyError:
			raise ValueError( "Interface %s does not exist" % interfaceName )
		
	def listInterfaces( self ):
		"""@return: list of names indicating interfaces available at our InterfaceMaster"""
		return self._idict.keys()
		
	#} END interface
	



class Singleton(object) :
	""" Singleton classes can be derived from this class,
		you can derive from other classes as long as Singleton comes first (and class doesn't override __new__ ) """
	def __new__(cls, *p, **k):
		if not '_the_instance' in cls.__dict__:
			cls._the_instance = super(Singleton, cls).__new__(cls)
		return cls._the_instance

class IntKeyGenerator( object ):
	"""Provides iterators for directly access list like objects supporting 
	__getitem__ method 
	@note: the list must not change size during iteration !"""
	def __init__( self, listobj ):
		"""Initialize the generator with the list to iterate"""
		self.listobj = listobj
		self.index = 0
		self.length = len( self.listobj )
	
	def __iter__( self ):
		return self

	def next( self ):
		if self.index < self.length:
			rval = self.listobj[ self.index ]
			self.index += 1
			return rval
		else:
			raise StopIteration
			

class CallOnDeletion( object ):
	"""Call the given callable object once this object is being deleted
	Its usefull if you want to assure certain code to run once the parent scope 
	of this object looses focus"""
	def __init__( self, callableobj ):
		self.callableobj = callableobj
		
	def __del__( self ):
		if self.callableobj:
			self.callableobj( )
		

class DAGTree( nxtree.DirectedTree ):
	"""Adds utility functions to DirectedTree allowing to handle a directed tree like a dag
	@note: currently this tree does not support instancing
	@todo: add instancing support"""
	
	def children( self, n ):
		""" @return: list of children of given node n """
		return list( self.children_iter( n ) ) 
	
	def children_iter( self, n ):
		""" @return: iterator with children of given node n"""
		return ( e[1] for e in self.out_edges_iter( n ) )
		
	def parent( self, n ):
		"""@return: parent of node n
		@note: currently there is only one parent, as instancing is not supported yet"""
		for parent in  self.predecessors_iter( n ):
			return parent
		return None
		
	def parent_iter( self, n ):
		"""@return: iterator returning all parents of node n"""
		while True:
			p = self.parent( n )
			if p is None:
				raise StopIteration( )
			yield p
			n = p
			
	def get_root( self, startnode = None ):
		"""@return: the root node of this dag tree
		@param startnode: if None, the first node will be used to get the root from
		( good for single rooted dags ), otherwise this node will be used to get the root from
		- thus it must exist in the dag tree"""
		if startnode is None:
			startnode = self.nodes_iter().next()
			
		root = None
		for parent in self.parent_iter( startnode ):
			root = parent
			
		return root
		

class PipeSeparatedFile( object ):
	"""Read and write simple pipe separated files containing a version number.
	
	The number of column must remain the same per line
	Format: 
	int( version )
	val11 | val2 | valn
	...	
	"""
	def __init__( self, fileobj ):
		"""Initialize the instance
		@param fileobj: fileobject where new lines will be written to or read from
		It must already be opened for reading and/or writing respectively"""
		self._fileobj = fileobj
		self._columncount = None
		
	def beginReading( self ):
		"""Start reading the file
		@return: the file version read"""
		fileversion = int( self._fileobj.readline( ).strip( ) )		# get version 
		return fileversion
		
	def readColumnLine( self ):
		"""Generator reading one line after another, returning the stripped columns
		@return: tuple of stripped column strings
		@raise ValueError: if the column count changes between the lines"""
		for line in self._fileobj:
			if not len( line.strip() ):
				continue 
				
			tokens = [ item.strip() for item in line.split( '|' ) ]
			if not self._columncount:
				self._columncount = len( tokens )
				
			if self._columncount != len( tokens ):
				raise ValueError( "Columncount changed between successive lines" )
				
			yield tuple( tokens )
		# END for each line 
		
	def beginWriting( self, version, columnSizes ):
		"""intiialize the writing process
		@param version: the file version you would like to set
		@param columnSizes: list of ints defining the size in characters for each column you plan to feed
		@note: When done writing, you have to close the file object yourself ( there is no endWriting method here )"""
		self._fileobj.write( "%i\n" % version )		# write version
		columnTokens = [ "%%-%is" % csize for csize in columnSizes ]
		self._formatstr = ( "| ".join( columnTokens ) ) + "\n" 
		
	def writeTokens( self, tokens ):
		"""Write the list of tokens to the file accordingly
		@param tokens: one token per column that you want to write
		@raise TypeError: If column count changed between successive calls""" 
		self._fileobj.write( self._formatstr % tokens )
		
		
class MetaCopyClsMembers( type ):
	"""Meta class copying members from given classes onto the type to be created
	it will read the following attributes from the class dict:
	forbiddenMembers, overwritePrefix, __virtual_bases__
	
	The virtual bases are a tuple of base classes whose members you whish to receive
	For information on these members, check the docs of L{copyClsMembers}"""
	def __new__( metacls, name, bases, clsdict ):
		forbiddenMembers = clsdict.get( 'forbiddenMembers', [] )
		overwritePrefix = clsdict.get( 'overwritePrefix', None )
		vbases = clsdict.get( '__virtual_bases__', [] )
		
		for sourcecls in vbases:
			for name,member in sourcecls.__dict__.iteritems():
				if name in forbiddenMembers:
					continue
					
				# store original - overwritten members must still be able to access it
				if name in clsdict:
					if not overwritePrefix:
						continue
					morig = clsdict[ name ]
					clsdict[ overwritePrefix+name ] = morig
				clsdict[ name ] = member
			# END for each sourcecls member
		# END for each sourcecls in bases
		
		return super( MetaCopyClsMembers, metacls ).__new__( metacls, name, bases, clsdict )
		
	
###################
## PREDICATES ###
################
#{ Predicates

class RegexHasMatch( object ):
	"""For use with python's filter method, returns True if regex matches
	Use: filter( And( f1,f2,fn ), sequence ) """
	def __init__( self, compiledRegex ):
		"""@param compiledRegex: matches incoming objects """
		self.regex = compiledRegex
		
	def __call__( self, x ):
		return self.regex.match( x ) != None

# general boolean 
class And( object ):
	"""For use with python's filter method, simulates logical AND
	Use: filter( And( f1,f2,fn ), sequence ) """
	def __init__( self, *args ):
		"""args must contain the filter methods to be AND'ed
		To append functions after creation, simply access the 'functions' attribute 
		directly as a list"""
		self.functions = list( args )
		
	def __call__( self, *args, **kwargs ):
		"""Called during filter function, return true if all functions return true"""
		val = True
		for func in self.functions:
			val = val and func( *args, **kwargs )
			if not val:
				return val
		# END for each function
		return val


class Or( object ):
	"""For use with python's filter method, simulates logical OR
	Use: filter( Or( f1,f2,fn ), sequence ) """
	def __init__( self, *args ):
		"""args must contain the filter methods to be AND'ed"""
		self.functions = args
		
	def __call__( self, *args, **kwargs ):
		"""Called during filter function, return true if all functions return true"""
		val = False
		for func in self.functions:
			val = val or func( *args, **kwargs )
			if val:
				return val
		# END for each function
		return val
		
#} END predicates 
