# -*- coding: utf-8 -*-
"""B{byronimo.automation.qa}
Specialization of workflow to provide quality assurance capabilities.

General Idiom of a quality assurance facility is to provide read-only checks for 
possibly quaility issues and possibly a fix for them.

The interface is determined by plugs that define the capabilities of the node implementing 
the checks.

The quality assurance framework is defined by:
	L{QAWorkflow}
	L{QAProcess}
	L{QACheckResult}
	L{QACheckAttribute}
	
They specialize the respective parts of the workflow

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


from workflow import Workflow
from process import ProcessBase
from byronimo.util import CallbackBase
from byronimo.dgengine import Attribute, plug, ComputeFailed
from byronimo.enum import create as enum 

event = CallbackBase.Event


class CheckIncompatibleError( ComputeFailed ):
	"""Raised if a check cannot accomdate the requested mode and thus cannot run"""
	pass 
	
	
class QAProcess( ProcessBase ):
	"""Quality Assurance Process including a specialized QA interface"""
	
	# query: find issues and report them using L{QACheckResult}, but do not attempt to fix
	# fix: find issues and fix them, report fixed ( and possibly failed ) items by
	eMode = enum( "query", "fix" )	# computation mode for QAProcesses
	
	#( Configuration
	# QA Processes do not require this feature due to their quite simplistic call structure
	# If required, subclasses can override this though
	track_compute_calls = False 
	#) END configuration 
	
	
	#{ Interface 
	def assureQuality( self, check, mode ):
		"""Called when the test identified by plug should be handled
		@param check: QACheck to be checked for issues
		@param mode: mode of the computation, see L{QAProcess.eMode} 
		@return: QACheckResult instance keeping information about the outcome of the test"""
		raise NotImplementedError( "To be implemented by subclass" )
	
	#} END interface 
	
	#{ Overridden from Process Base 
	def evaluateState( self, plug, mode ):
		"""Prepares the call to the actual quality check implemenetation and assuring 
		test identified by plug can actually be run in the given mode"""
		if mode is self.eMode.fix and not plug.attr.implements_fix:
			raise CheckIncompatibleError( "Plug %s does not implement issue fixing" % plug )
			
		return self.assureQuality( plug, mode )
		
		
	#} END overridden from process base 
	

	
class QACheckAttribute( Attribute ):
	"""The Test Attribute represents an interface to a specific test as implemented 
	by the parent L{QAProcess}.
	The QA Attribute returns specialized quality assurance results and provides
	additional information about the respective test
	@note: as this class holds meta information about the respective test ( see L{QACheck} ) 
	user interfaces may use it to adjust it's display"""
	
	def __init__( 	self, annotation, has_fix = False,  
				 	flags = Attribute.computable ):
		"""Initialize attribute with meta information
		@param annoation: information string describing the purpose of the test
		@param has_fix: if True, the check must implement a fix for the issues it checks for, 
		if False, it can only report issues
		@param flags: configuration flags for the plug - default to trigger computation even without 
		input"""
		super( QACheckAttribute, self ).__init__( QACheckResult, flags ) 
		self.annotation = annotation
		self.implements_fix = has_fix
		
		
		
class QACheck( plug ):
	"""Defines a test suitable to be run and computed by a L{QAProcess}
	It's nothing more than a convenience class as the actual information is held by the 
	respective L{QACheckAttribute}.
	All non-plug calls are passed on to the underlying attribute, allowing it to 
	be treated like one"""
	def __init__( self, *args, **kwargs ):
		super( QACheck, self ).__init__( QACheckAttribute( *args, **kwargs ) )
		
	def __getattr__( self, attrname ):
		return getattr( self.attr, attrname )
	
	

class QAWorkflow( Workflow, CallbackBase ):
	"""Represents a workflow of QAProcess instances and allows to query them more 
	conveniently"""
	
	#( Configuration 
	sender_as_argument = False 
	#) END configuration 
	
	#( Filters 
	fIsQAProcess = staticmethod( lambda n: isinstance( n, QAProcess ) )
	fIsQAPlug = staticmethod( lambda p: isinstance( p, QACheck ) )
	#) END filters 
	
	#{ Events 
	# called before a check is run as func: func( check )
	preCheck = event( "preCheck" )
	
	# called if a check fails with an error: func( check, exception )
	checkError = event( "checkError" )
	
	# called after a check has been run: func( check )
	postCheck = event( "postCheck" )
	#} 
	
	def listQAProcesses( self, predicate = lambda p: True ):
		"""@return: list( Process, ... ) list of QA Processes known to this QA Workflow
		@param predicate: include process p in result if func( p ) returns True"""
		return self.iterNodes( predicate = lambda n: self.fIsQAProcess( n ) and predicate( n ) )
	
	def filterChecks( self, processes, predicate = lambda c: True ):
		"""As L{listChecks}, but allows you do define the processes to use"""
		outchecks = list()
		for node in processes:
			outchecks.extend( node.toShells( node.getPlugs( self.fIsQAPlug ) ) )
		return outchecks
	
	def listChecks( self, predicate = lambda c: True  ):
		"""List all checks as supported by L{QAProcess}es in this QA Workflow
		@param predicate: include check c in result if func( c ) returns True"""
		return self.filterChecks( self.listQAProcesses( ), predicate = predicate )
		
	def runChecks( self, checks, mode = QAProcess.eMode.query, clear_result = True ):
		"""Run the given checks in the given mode and return their results
		@param checks: list( QACheckShell, ... ) as retrieved by L{listChecks}
		@param mode: L{QAProcess.eMode} 
		@param clear_result: if True, the plug's cache will be removed forcing a computation
		if False, you might get a cached value depending on the plug's setup
		@return: list( tuple( QACheckShell ), ... ) list of pairs of 
		QACheckShells and the test result. The test result will be empty if the test 
		did not run or failed with an exception
		@events: preCheck and postCheck"""
		
		self._clearState( mode )	# assure we get a new callgraph
		
		outresult = list()
		for checkshell in checks:
			self.sendEvent( self.preCheck, checkshell )
			
			result = QACheckResult()	 	# null value 
			if clear_result:
				checkshell.clearCache( clear_affected = False )
			
			try:
				result = checkshell.get( mode ) 
			except Exception, e:
				self.sendEvent( self.checkError, checkshell, e )
				
			# record result 
			outresult.append( ( checkshell, result ) )
			self.sendEvent( self.postCheck, checkshell )
		# END for each check to run 
	
		return outresult
	
class QACheckResult( object ):
	"""Wrapper class declaring test results as a type that provides a simple interface
	to retrieve the test results
	@note: test results are only reqtrieved by QACheckAttribute plugs"""
	def __init__( self , fixed_items = None , failed_items = None, header = "" ):
		"""Initialize ourselves with default values
		@param fixed_items: if list of items, the instance is initialized with it
		@param failed_items: list of items that could not be fixed
		@param header: optional string giving additional specialized information on the 
		outcome of the test"""
		self.header = ""
		self.fixed_items = ( isinstance( fixed_items, list ) and fixed_items ) or list()
		self.failed_items = ( isinstance( failed_items, list ) and failed_items ) or list()

	def getFixedItems( self ):
		"""@return: list( Item , ... ) list of items ( the exact type may differ 
		depending on the actual test ) which have been fixed so they represent the 
		desired state"""
		return self.fixed_items
	
	def getFailedItems( self ):
		"""@return( list( Item, ... ) list of failed items being items that could not be
		fixed and are not yet in the desired state"""
		return self.failed_items
	
	def isNull( self ):
		"""@return: True if the test result is empty, and thus resembles a null value"""
		return not self.failed_items and not self.fixed_items
		
	def __str__( self ):
		msg = self.header
		msg += ", ".join( str( i ) for i in self.fixed_items )
		msg += ", ".join( str( i ) for i in self.failed_items )
		return msg 
