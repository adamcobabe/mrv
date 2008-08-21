"""B{byronimo.nodes.undo}

Contains the undo engine allowing to adjust the scene with api commands while 
providing full undo and redo support.

Features
--------
   - modify dag or dg using the undo - enabled DG and DAG modifiers
   - modify values using Nodes and their plugs ( as the plugs are overridden
   to store undo information )
   - fully usable including MEL command ( using L{GenericOperation}

Limitations
-----------
	- You need a rather long undo queue as undo will count the individual byronimo cmds
	although most of them are actually not undoable 

@todo: more documentation about how to use the system and how it actually works 

@newfield revision: Revision
@newfield id: SVN Id """

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import maya.cmds as cmds
import maya.mel as mel

#{ Initialization 

def __initialize():
	""" Assure our plugin is loaded - called during module intialization"""
	import os
	
	pluginpath = os.path.splitext( __file__ )[0] + ".py"
	if not cmds.pluginInfo( pluginpath, q=1, loaded=1 ):
		cmds.loadPlugin( pluginpath )
	
	# assure our decorator is available !
	import __builtin__
	setattr( __builtin__, 'undoable', undoable )
	
#} END initialization


#{ Undo Plugin
import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx


# Use sys as general placeholder that will only exist once !
# Global vars do not really maintain their values as modules get reinitialized 
# quite often it seems 
import sys
if not hasattr( sys, "_maya_stack_depth" ):
	sys._maya_stack_depth = 0
	sys._maya_stack = []
	

# command
class UndoCmd( mpx.MPxCommand ):
	kCmdName = "byronimoUndo"
	fPush = "-psh"
	fPop = "-pop"
	
	def __init__(self):
		mpx.MPxCommand.__init__(self)
		self._operations = None
	
	#{ Command Methods 
	def doIt(self,argList):
		"""Called on first instantiation of the command
		Store all information we need
		During doit, this command will never execute any operation on the buffer, 
		thus you need to exectute it yourself the first time"""
		parser = om.MArgParser( self.syntax(), argList )
		
		
		# if we push, we increment the stack indicating the current call level
		# If it reaches zero again, we get take the undo operatiosn
		if parser.isFlagSet( self.fPush ):
			sys._maya_stack_depth += 1
			return 
		elif parser.isFlagSet( self.fPop ):
			sys._maya_stack_depth -= 1
			
			# if we reach the starting level, we can actually store the undo buffer
			# and allow us to be placed on the undo queue
			if sys._maya_stack_depth == 0:
				self._operations = sys._maya_stack
				sys._maya_stack = []					# clear the operations list 
			# END if stack 0
			return 
		# END stack handling 
		
		# still here ?
		msg = "call with -push or -pop only"
		self.displayError( msg )
		raise RuntimeError( msg )
			
	def redoIt( self ):
		"""Called on once a redo is requested"""
		if not self._operations:
			return
		
		for op in self._operations:
			op.doIt( )
		
	def undoIt( self ):
		"""Called once undo is requested"""
		if not self._operations:
			return
			
		# run in reversed order !
		for index in xrange( len( self._operations )-1, -1, -1 ):
			self._operations[ index ].undoIt()
		
	def isUndoable( self ):
		"""@return: True if we are undoable - it depends on the state of our 
		undo stack """
		return self._operations is not None
		
	# END command methods 
	
	@staticmethod
	def creator():
		return mpx.asMPxPtr( UndoCmd() )
		
	
	# Syntax creator
	@staticmethod
	def createSyntax( ):
		syntax = om.MSyntax()
		
		# stack commands - thats all we need
		syntax.addFlag( UndoCmd.fPush, "-pushStack" )
		syntax.addFlag( UndoCmd.fPop, "-popStack" )
		
		syntax.enableEdit( )
		
		return syntax


def initializePlugin(mobject):
	mplugin = mpx.MFnPlugin(mobject)
	mplugin.registerCommand( UndoCmd.kCmdName, UndoCmd.creator, UndoCmd.createSyntax )

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = mpx.MFnPlugin(mobject)
	mplugin.deregisterCommand( UndoCmd.kCmdName )

#} END plugin


#{ Utilities
	
def undoable( func ):
	"""Decorator wrapping func so that it will start undo when it begins and end undo 
	when it ends. It assures that only toplevel undoable functions will actually produce 
	an undo event
	To mark a function undoable, decorate it:
	@@undoable
	def func( ):
		pass 
	@note: Using decorated functions appears to be only FASTER  than implementing it 
	manually, thus using these is will greatly improve code readability
	@note: if you use undoable functions, you should mark yourself undoable too - otherwise the 
	functions you call will create individual undo steps"""
	def wrapFunc( *args, **kwargs ):
		"""This is the long version of the method as it is slightly faster than
		simply using the StartUndo helper"""
		mel.eval( "byronimoUndo -psh" )
		try:
			rval = func( *args, **kwargs )
			mel.eval( "byronimoUndo -pop" )
			return rval
		except:
			mel.eval( "byronimoUndo -pop" )
			raise 
			
	# END wrapFunc
	
	wrapFunc.__name__ = func.__name__
	return wrapFunc	
	

class StartUndo:
	"""Utility class that will push the undo stack on __init__ and pop it on __del__
	@note: Prefer the undoable decorator over this one as they are easier to use and FASTER !
	@note: use this class to assure that you pop undo when your method exists"""
	def __init__( self ):
		mel.eval( "byronimoUndo -psh" )			# tuned for speed - stirng is baked

	def __del__( self ):
		mel.eval( "byronimoUndo -pop" )

def startUndo( ):
	"""Call before you start undoable operations
	@note: prefer the @undoable decorator"""
	mel.eval( "byronimoUndo -psh" )
	
def endUndo( ):
	"""Call before your function with undoable operations ends
	@note: prefer the @undoable decorator"""
	mel.eval( "byronimoUndo -pop" )
	
#} 



#{ Operations

from byronimo.util import Call

class Operation:
	"""Simple command class as base for all operations
	All undoable/redoable operation must support it
	NOTE: only operations may be placed on the undo stack !"""
	
	def __init__( self ):
		"""Operations will always be placed on the undo queue if undo is available
		This happens automatically upon creation
		@note: assure subclasses call the superclass init !"""
		if not om.MGlobal.isUndoing() and cmds.undoInfo( q=1, st=1 ):
			# sanity check !
			if sys._maya_stack_depth < 1:
				raise ValueError( "Undo-Stack was %i, but must be at least 1 before operations can be put - check your code !" % sys._maya_stack_depth )
				
			sys._maya_stack.append( self )
			
	
	def doIt( self ):
		"""Do whatever you do"""
		raise NotImplementedError
		
	def undoId( self ):
		"""Undo whatever you did"""
		raise NotImplementedError
		

class GenericOperation( Operation ):
	"""Operation able to undo generic mel commands
	@usage: in your api command, create a GenericOperation operation instance, add your (mel) commands 
	that should be executed in a row as Call. To apply them, call doIt once ( and only once ! ).
	You can have only one command stored, or many if they should be executed in a row.
	The vital part is that with each do command, you supply an undo command. 
	This way your operations can be undone and redone once undo / redo is requested
	@note: this class works well with L{byronimo.util.Call}
	@note: to execute the calls added, you must call L{doIt} or L{addCmdAndCall} - otherwise 
	the undoqueue might brake if exceptions occour !
	@note: your calls may use MEL commands safely as the undo-queue will be torn off during execution
	@note: Undocommand will be applied in reversed order automatically"""
	
	def __init__( self ):
		"""intiialize our variables"""
		Operation.__init__( self )
		self._docmds = []				# list of Calls 
		self._undocmds = []				# will store reversed list !
		self._undocmds_tmp = []			# keeps undo until their do was verified !


	def doIt( self ):
		"""Call all doIt commands stored in our instance after temporarily disabling the undo queue"""
		prevstate = cmds.undoInfo( q=1, st=1 )
		cmds.undoInfo( swf=False )
		
		try:
			if self._undocmds_tmp:
				# verify each doit command before we shedule undo 
				# if it raies, we will not schedule the respective command for undo 
				for i,call in enumerate( self._docmds ):
					try:
						call()
					except:
						# forget about this and all following commands and reraise 
						del( self._docmds[i:] )
						self._undocmds_tmp = None		# next time we only execute the cmds that worked ( and will undo only them )
						raise
					else:
						self._undocmds.insert( 0, self._undocmds_tmp[i] )	# push front
				# END for each call
				self._undocmds_tmp = None			# free memory 
			else:
				for call in self._docmds:
					call()
				# END for each do calll
			# END if undo cmds have been verified
		finally:
			cmds.undoInfo( swf=prevstate )
	
	def undoIt( self ):
		"""Call all undoIt commands stored in our instance after temporarily disabling the undo queue"""
		# NOTE: the undo list is already reversed !
		prevstate = cmds.undoInfo( q=1, st=1 )
		cmds.undoInfo( swf=False )
		
		# sanity check
		try:
			if self._undocmds_tmp:	 
				raise AssertionError( "Tmp undo commands queue was not None on first undo call - this means doit has not been called before - check your code!" )
			
			for call in self._undocmds:
				call()
		finally:
			cmds.undoInfo( swf=prevstate )

		
	def addCmd( self, doCall, undoCall ):
		"""Add a command to the queue for later application
		@param doCall: instance supporting __call__ interface, called on doIt
		@param undoCall: instance supporting __call__ interface, called on undoIt"""
			
		self._docmds.append( doCall )		# push 
		self._undocmds_tmp.append( undoCall ) 

	def addCmdAndCall( self, doCall, undoCall ): 
		"""Add commands to the queue and execute it right away - either always use 
		this way to add your commands or the L{addCmd} method, never mix them !
		@return: return value of the doCall
		@note: use this method if you need the return value of the doCall right away"""
		prevstate = cmds.undoInfo( q=1, st=1 )
		cmds.undoInfo( swf=False )
		
		rval = doCall()
		self._docmds.append( doCall )
		self._undocmds.insert( 0, undoCall )
		
		cmds.undoInfo( swf=prevstate )
		return rval


from byronimo.util import MetaCopyClsMembers
import sys

class DGModifier( om.MDGModifier, Operation ):
	"""Undo-aware DG Modifier - using it will automatically put it onto the API undo queue
	@note: You MUST call doIt() before once you have instantiated an instance, even though you 
	have nothing on it. This requiredment is related to the undo queue mechanism"""
	def __init__( self ):
		"""Initialize our base classes explicitly"""
		om.MDGModifier.__init__( self )
		Operation.__init__( self )
		
	def _on_deletion_( self ):
		"""general handler to do general operation handling on deletion
		@note: NOT ( YET ) USED"""
		if not self._doitcalled:
			try:
				ownindex = sys._maya_stack.index( self )
				#print "ownindex == " + str( ownindex )
			except ValueError:
				pass
			else:
				# delete us from the queue - undo should not be called on us
				# as we have not done anything 
				del( sys._maya_stack[ ownindex ] )
		# END if doit not called before deletion - need to get us off the queue

	
class DagModifier( om.MDagModifier, Operation ):
	"""undo-aware DAG modifier, copying all extra functions from DGModifier"""
	__metaclass__ = MetaCopyClsMembers
	
	__virtual_bases__ = ( DGModifier, )
	
	def __init__( self ):
		"""Intiailize our base explicitly"""
		om.MDagModifier.__init__( self )
		Operation.__init__( self )
		
		
	
# keep aliases
#{ Aliases 

MDGModifier = DGModifier
MDagModifier = DagModifier

#}

#} END operations


