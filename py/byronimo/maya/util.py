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


import byronimo.maya
import maya.mel as mm
import maya.OpenMaya as om
import maya.cmds as cmds

class Singleton(object) :
	""" Singleton classes can be derived from this class,
		you can derive from other classes as long as Singleton comes first (and class doesn't override __new__ ) """
	def __new__(cls, *p, **k):
		if not '_the_instance' in cls.__dict__:
			cls._the_instance = super(Singleton, cls).__new__(cls)
		return cls._the_instance


def pythonToMel(arg):
	if isinstance(arg,basestring):
		return u'"%s"' % cmds.encodeString(arg)
	elif util.isIterable(arg):
		return u'{%s}' % ','.join( map( pythonToMel, arg) ) 
	return unicode(arg)
	
	
class Mel(Singleton):
	"""This class is a necessity for calling mel scripts from python. It allows scripts to be called
	in a cleaner fashion, by automatically formatting python arguments into a string 
	which is executed via maya.mel.eval().	An instance of this class is already created for you 
	when importing pymel and is called mel.	 
	
	@note: originated from pymel, added epydoc strings where needed  """
			
	def __getattr__(self, command):
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
	
	def call(self, command, *args ):
		""" Call a mel script , very simpilar to Mel.myscript( args )
		@todo: more docs """
		strArgs = map( pythonToMel, args)
						
		cmd = '%s(%s)' % ( command, ','.join( strArgs ) )

		try:
			return mm.eval(cmd)
		except RuntimeError, msg:
			info = self.whatIs( command )
			if info.startswith( 'Presumed Mel procedure'):
				raise NameError, 'Unknown Mel procedure'
			raise RuntimeError, msg
	
	
	def mprint(self, *args):
		"""mel print command in case the python print command doesn't cut it. i have noticed that python print does not appear
		in certain output, such as the rush render-queue manager."""
		#print r"""print (%s\\n);""" % pythonToMel( ' '.join( map( str, args))) 
		mm.eval( r"""print (%s);""" % pythonToMel( ' '.join( map( str, args))) + '\n' )
				
	def eval( self, command ):
		""" same as maya.mel eval """
		return mm.eval( command )	 
	

	def _melprint( self, cmd, msg ):
		mm.eval( """%s %s""" % ( cmd, pythonToMel( msg ) ) )	
	
	error = lambda *args: _melprint( "error", *args )
				  
	def tokenize(self, *args ):
		raise NotImplementedError, "Calling the mel command 'tokenize' from python will crash Maya. Use the string split method instead."
		

## ATTACH SINGLETON SCENE
####################
# store a mel instance in the maya module for easy access
byronimo.maya.Mel = Mel( )



class CallbackBase( object ):
	""" Base type taking over the management part when wrapping maya messages into an 
	appropriate python class. 
	
	It has the advantage of easier usage as you can pass in any function with the 
	appropriate signature"""
	
	def __init__( self ):
		"""initialize our base variables"""
		self._middict = {}						# callbackGroup -> maya callback id
		self._callbacks = {}				# callbackGroup -> ( callbackStringID -> Callacble )
	
	def _addMasterCallback( self, callbackID, *args, **kvargs ):
		"""Called once the base has to add actual maya callback.
		It will be added once the first client adds himself, or removed otherwise once the last
		client removed himself.
		Make sure your method registers this _call method with *args and **kvargs to allow
		it to acftually deliver the call to all registered clients
		@param existingID: if -1, the callback is to be added - in that case you have to 
		return the created unique message id
		@param callbackID: if not None, specifies the callback type that was requested"""
		raise NotImplementedError()
		
	def _getCallbackGroup( self, callbackID ):
		""" Returns a group where this callbackID passed to the addListener method belongs to.
		If all callbackIDs are the same, this default implementation will take care of it
		@note: override if you have different callback groups, thus different kinds of callbacks
		that you have to register with different methods"""
		return 0
		
	def _call( self, *args, **kvargs ):
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
			callback( *args, **kvargs )
		# END callback loop
		
	def addListener( self, listenerID, callback, callbackID = None, *args, **kvargs ):
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
			self._middict[ cbgroup ] = self._addMasterCallback( cbgroup, callbackID, *args, **kvargs )
			mid = self._middict[ cbgroup ]
			if mid is None or mid < 1:
				raise ValueError( "Message ID is supposed to be set to an approproriate value" )
				
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
			

