# -*- coding: utf-8 -*-
"""B{byronimo.maya.utils}
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


import maya.mel as mm
import maya.OpenMaya as om
import maya.cmds as cmds
import byronimo.util as util
from byronimo.util import capitalize,uncapitalize
import networkx.exception as networkxexc
import os

#{ Return Value Conversion
def noneToList( res ):
	"""@return: list instead of None"""
	if res is None:
		return []
	return res
#}
	
	
	
	
#{ MEL Function Wrappers
 
def makeEditOrQueryMethod( inCmd, flag, isEdit=False, methodName=None ):
	"""Create a function calling inFunc with an edit or query flag set.
	@note: THIS CODE HAS BEEN DUPLICATED TO MAYA.UI.UTIL !
	@param inCmd: maya command to call 
	@param flag: name of the query or edit flag
	@param isEdit: If not False, the method returned will be an edit function
	@param methoName: the name of the method returned, defaults to inCmd name  """
	
	func = None
	if isEdit:
		def editFunc(self, val, **kwargs): 
			kwargs[ 'edit' ] = True
			kwargs[ flag ] = val
			return inCmd( self, **kwargs )
			
		func = editFunc
	# END if edit 
	else:
		def queryFunc(self, **kwargs): 
			kwargs[ 'query' ] = True
			kwargs[ flag ] = True
			return inCmd( self, **kwargs )
			
		func = queryFunc
	# END if query 
	
	if not methodName:
		methodName = flag 
	func.__name__ = methodName
			 
	return func


def queryMethod( inCmd, flag, methodName = None ):
	""" Shorthand query version of makeEditOrQueryMethod """
	return makeEditOrQueryMethod( inCmd, flag, isEdit=False, methodName=methodName )

def editMethod( inCmd, flag, methodName = None ):
	""" Shorthand edit version of makeEditOrQueryMethod """
	return makeEditOrQueryMethod( inCmd, flag, isEdit=True, methodName=methodName )

def propertyQE( inCmd, flag, methodName = None ):
	""" Shorthand for simple query and edit properties """
	editFunc = editMethod( inCmd, flag, methodName = methodName )
	queryFunc = queryMethod( inCmd, flag, methodName = methodName )
	return property( queryFunc, editFunc )
	
#} 
	
def isIterable( obj ):
	return hasattr(obj,'__iter__') and not isinstance(obj,basestring)

def pythonToMel(arg):
	if isinstance(arg,basestring):
		return u'"%s"' % cmds.encodeString(arg)
	elif isIterable(arg):
		return u'{%s}' % ','.join( map( pythonToMel, arg) ) 
	return unicode(arg)


############################
#### Classes		  	####
##########################
	
#{ Utitliy Classes

class Mel(util.Singleton):
	"""This class is a necessity for calling mel scripts from python. It allows scripts to be called
	in a cleaner fashion, by automatically formatting python arguments into a string 
	which is executed via maya.mel.eval().	An instance of this class is already created for you 
	when importing pymel and is called mel.	 
	
	@note: originated from pymel, added customizations  """
			
	def __getattr__(self, command):
		"""Only for instances of this class - call methods directly as if they where 
		attributes """
		if command.startswith('__') and command.endswith('__'):
			return self.__dict__[command]
		def _call(*args):
		
			strArgs = map( pythonToMel, args)
							
			cmd = '%s(%s)' % ( command, ','.join( strArgs ) )
			#print cmd
			try:
				return mm.eval(cmd)
			except RuntimeError, msg:
				info = self.whatIs( command )
				if info.startswith( 'Presumed Mel procedure'):
					raise NameError, 'Unknown Mel procedure'
				raise RuntimeError, msg
			
		return _call
	
	@staticmethod
	def call( command, *args ):
		""" Call a mel script , very simpilar to Mel.myscript( args )
		@todo: more docs """
		strArgs = map( pythonToMel, args)
						
		cmd = '%s(%s)' % ( command, ','.join( strArgs ) )

		try:
			return mm.eval(cmd)
		except RuntimeError, msg:
			info = Mel.call( "whatIs", command )
			if info.startswith( 'Presumed Mel procedure'):
				raise NameError, ( 'Unknown Mel procedure: ' + cmd )
			raise RuntimeError, msg
	
	@staticmethod
	def mprint(*args):
		"""mel print command in case the python print command doesn't cut it. i have noticed that python print does not appear
		in certain output, such as the rush render-queue manager."""
		#print r"""print (%s\\n);""" % pythonToMel( ' '.join( map( str, args))) 
		mm.eval( r"""print (%s);""" % pythonToMel( ' '.join( map( str, args))) + '\n' )
				
	@staticmethod
	def eval( command ):
		""" same as maya.mel eval """
		return mm.eval( command )	 
	
	@staticmethod
	def _melprint( cmd, msg ):
		mm.eval( """%s %s""" % ( cmd, pythonToMel( msg ) ) )	
	
	error = staticmethod( lambda *args: Mel._melprint( "error", *args ) )
	trace = staticmethod( lambda *args: Mel._melprint( "trace", *args ) )
	info = staticmethod( lambda *args: Mel._melprint( "print", *args ) )
	
	
 
class OptionVarDict( util.Singleton ):
	"""	 A singleton dictionary-like class for accessing and modifying optionVars.
	@note: Idea and base Implementation from PyMel, modified by byronimo to fix some issues 
	"""
	class OptionVarList(tuple):
		def __new__( cls, key, val ):
			"""modify constructor to work with tuple"""
			newinstpreinit = tuple.__new__( cls, val )
			newinstpreinit.key = key
			return newinstpreinit
			
		def appendVar( self, val ):
			""" values appended to the OptionVarList with this method will be added to the Maya optionVar at the key denoted by self.key.
			"""
			val = OptionVarDict._checkType( val )
			if isinstance( val, basestring):
				return cmds.optionVar( stringValueAppend=[self.key,unicode(val)] )
			if isinstance( val, (bool,int) ):
				return cmds.optionVar( intValueAppend=[self.key,int(val)] )
			if isinstance( val, float):
				return cmds.optionVar( floatValueAppend=[self.key,val] )
			
	
	def __contains__(self, key):
		return cmds.optionVar( exists=key )
			
	def __getitem__(self,key):
		val = cmds.optionVar( q=key )
		if isinstance(val, list):
			val = self.OptionVarList( key, val )
		return val
		
	def __setitem__(self,key,val):
		if isinstance( val, basestring):
			return cmds.optionVar( stringValue=[key,unicode(val)] )
		if isinstance( val, (int,bool)):
			return cmds.optionVar( intValue=[key,int(val)] )
		if isinstance( val, float):
			return cmds.optionVar( floatValue=[key,val] )
			
		if isinstance( val, (list,tuple) ):
			if len(val) == 0:
				return cmds.optionVar( clearArray=key )
				
			if isinstance( val[0], basestring):
				cmds.optionVar( stringValue=[key,unicode(val[0])] ) # force to this datatype
				for elem in val[1:]:
					cmds.optionVar( stringValueAppend=[key,unicode(elem)] )
				return
				
			if isinstance( val[0], (int,bool)):
				cmds.optionVar(	 intValue=[key,int(val[0])] ) # force to this datatype
				for elem in val[1:]:
					cmds.optionVar( intValueAppend=[key,int(elem)] )
				return
				
			if isinstance( val[0], float):
				cmds.optionVar( floatValue=[key,val[0]] ) # force to this datatype
				for elem in val[1:]:
					cmds.optionVar( floatValueAppend=[key,float(elem)] )
				return

		raise TypeError, 'unsupported datatype: strings, ints, float, lists, and their subclasses are supported'			

	def __delitem__( self, key ):
		"""Delete the optionvar identified by key"""
		cmds.optionVar( rm = str( key ) )
		
	def keys(self):
		return cmds.optionVar( list=True )
		
	def iterkeys( self ):
		"""@return: iterator to option var names"""
		return iter( self.keys() )
		
	def itervalues( self ):
		"""@return: iterator to optionvar values"""
		for key in self.iterkeys():
			yield self[ key ]

	def iteritems( self ):
		"""@return: iterators to tuple of key,value pairs"""
		for key in self.iterkeys():
			yield ( key, self[ key ] )
			
	def get(self, key, default=None):
		if self.has_key(key):
			return self[key]
		else:
			return default
		
	def has_key(self, key):
		return cmds.optionVar( exists=key )

	def pop(self, key):
		val = self[ key ]
		del( self[ key ] )
		return val
		

# use it as singleton
optionvars = OptionVarDict()

class CallbackBase( object ):
	""" Base type taking over the management part when wrapping maya messages into an 
	appropriate python class. 
	
	It has the advantage of easier usage as you can pass in any function with the 
	appropriate signature"""
	
	def __init__( self ):
		"""initialize our base variables"""
		self._middict = {}						# callbackGroup -> maya callback id
		self._callbacks = {}				# callbackGroup -> ( callbackStringID -> Callacble )
	
	def _addMasterCallback( self, callbackID, *args, **kwargs ):
		"""Called once the base has to add actual maya callback.
		It will be added once the first client adds himself, or removed otherwise once the last
		client removed himself.
		Make sure your method registers this _call method with *args and **kwargs to allow
		it to acftually deliver the call to all registered clients
		@param existingID: if -1, the callback is to be added - in that case you have to 
		return the created unique message id
		@param callbackID: if not None, specifies the callback type that was requested"""
		raise NotImplementedError()
		
	def _getCallbackGroup( self, callbackID ):
		""" Returns a group where this callbackID passed to the addListener method belongs to.
		By default, one callbackID describes one callback group
		@note: override if you have different callback groups, thus different kinds of callbacks
		that you have to register with different methods"""
		return callbackID
		
	def _call( self, *args, **kwargs ):
		""" Iterate over listeners and call them. The method expects the last 
		argument to be the callback group that _addMasterCallback method supplied to the 
		callback creation method
		@note: will throw only in debug mode 
		@todo: implement debug mode !"""
		cbgroup = args[-1]
		if cbgroup not in self._callbacks:
			raise KeyError( "Callback group: " + cbgroup + " did not exist" )
		
		cbdict = self._callbacks[ cbgroup ]
		for callback in cbdict.itervalues():
			try:
				callback( *args, **kwargs )
			except:
				print( "ERROR: Callback failed" )
				raise
				
		# END callback loop
		
	def addListener( self, listenerID, callback, callbackID = None, *args, **kwargs ):
		""" Call to register to receive events triggered by this class
		@param listenerID: hashable item identifying you 
		@param callback: callable method, being called with the arguments of the respective
		callback - read the derived classes documentation about the signature
		@param callbackID: will be passed to the callback creator allowing it to create the desired callback
		@raise ValueError: if the callback could not be registered 
		@note: Override this method if you need to add specific signature arguments, and call 
		base method afterwardss"""
		
		cbgroup = self._getCallbackGroup( callbackID )
		cbdict = self._callbacks.get( cbgroup, dict() )
		if len( cbdict ) == 0: self._callbacks[ cbgroup ] = cbdict		# assure the dict is actually in there !
		
		# are we there already ?
		if listenerID in cbdict: 
			return
		
		# assure we get a callback
		if len( cbdict ) == 0:
			try:
				self._middict[ cbgroup ] = self._addMasterCallback( cbgroup, callbackID, *args, **kwargs )
			except RuntimeError:
				raise ValueError( "Maya Message ID is supposed to be set to an approproriate value, got " + str( self._middict[ cbgroup ] ) )
				
		# store the callable for later use
		cbdict[ listenerID ] = callback
		
	
	def removeListener( self, listenerID, callbackID = None ):
		"""Remove the listener with the given listenerID so it will not be notified anymore if 
		events occour. Never raises
		@param callbackID: must be the callbackID you added the listener with"""
		cbgroup = self._getCallbackGroup( callbackID )
		if cbgroup not in self._callbacks:
			return 
		
		cbdict = self._callbacks[ cbgroup ]
		try: 
			del( cbdict[ listenerID ] )
		except KeyError:
			pass
		
		# if there are no listeners, remove the callback 
		if len( cbdict ) == 0:
			mid = self._middict[ cbgroup ]
			om.MSceneMessage.removeCallback( mid )
		

class MuteUndo( object ):
	"""Instantiate this class to disable the maya undo queue - on deletion, the 
	previous state will be restored
	@note: useful if you want to save the undo overhead involved in an operation, 
	but assure that the previous state is always being reset"""
	def __init__( self ):
		self.prevstate = cmds.undoInfo( q=1, st=1 )
		cmds.undoInfo( swf = 0 )

	def __del__( self ):
		cmds.undoInfo( swf = self.prevstate )

#} END utility classes
				 


class StandinClass( object ):
	""" Simple Function Object allowing to embed the name of the type as well as
	the metaclass object supposed to create the actual class. It mus be able to completely 
	create the given class.
	@note: Use it at placeholder for classes that are to be created on first call, without 
	vasting large amounts of memory if one wants to precreate them."""
	def __init__( self, classname, classcreator=type ):
		self.clsname = classname
		self.classcreator = classcreator
		self._createdClass = None
		
	def createCls( self ):
		""" Create the class of type self.clsname using our classcreator - can only be called once !
		@return : the newly created class"""
		if self._createdClass is None:
			self._createdClass = self.classcreator( self.clsname, tuple(), {} )
			
		return self._createdClass
		
	def __call__( self, *args, **kwargs ):
		newcls = self.createCls( )
		return newcls( *args, **kwargs )


	


class MetaClassCreator( type ):
	""" Builds the base hierarchy for the given classname based on our
	typetree """
	
	def __new__( 	dagtree, module, metacls, name, bases, clsdict, 
					nameToTreeFunc=uncapitalize, treeToNameFunc=capitalize ):
		"""Create a new class from hierarchy information found in dagtree and 
		put it into the module if it not yet exists
		@param dagtree: L{byronimo.util.DAGTree} instance with hierarchy information
		@param module: the module instance to which to add the new classes to
		@param nameToTreeFunc: convert the class name to a name suitable for dagTree look-up
		@param treeToNameFunc: convert a value from the dag tree into a valid class name ( used for parent lookup )"""
		# recreate the hierarchy of classes leading to the current type
		nameForTree = nameToTreeFunc( name )
		parentname = None
		try:
			parentname = dagtree.parent( nameForTree )
		except networkxexc.NetworkXError:
			# we can handle and thus ignore key errors, mostly created by subclass
			# of our wrapped classes 
			pass 
		# END parent name handling 
		
		parentcls = None
		
		# ASSURE PARENTS
		#####################
		# Parent classes must be available in advance
		if parentname != None:
			parentclsname = treeToNameFunc( parentname )
			parentcls = module.__dict__[ parentclsname ]
			if isinstance( parentcls, StandinClass ):
				parentcls = parentcls.createCls( )
		# END if parent cls name defined
		
		# could be a user-defined class coming with some parents already - thus assure 
		# that the auto-parent is not already in there
		# NOTE: bases is sometimes filled with types, sometimes with classes 
		if parentcls and not ( parentcls in bases or isinstance( parentcls, bases ) ):
			bases += ( parentcls, )
			
		# create the class 
		newcls = super( MetaClassCreator, metacls ).__new__( metacls, str( name ), bases, clsdict )
		
		# change the module - otherwise it will get our module 
		newcls.__module__ = module.__name__
		
		# replace the dummy class in the module 
		module.__dict__[ name ] = newcls
		
		 
			
		return newcls
