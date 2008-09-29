"""B{byronimo.automation.processes.base}
Contains base class and common methods for all processes  

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

__all__ = list()

from byronimo.dgengine import NodeBase
from byronimo.dgfacadeengine import GraphNodeBase
from byronimo.dgengine import plug
from byronimo.dgengine import Attribute

import byronimo.automation.base as wflbase
from byronimo.path import Path
from byronimo.util import Or

#####################
## EXCEPTIONS ######
###################
#{ Exceptions 

class DirtyException( ValueError ):
	"""Exception thrown when system is in dirty query mode and the process detects
	that it is dirty.
	
	The exception can also contain a report that will be returned using the 
	getReport function.
	"""
	def __init__( self, report = '' ):
		self.report = report
		
	#{ Interface
		
	def getReport( ):
		"""@return: printable report, usually a string or some object that 
		responds to str() appropriately"""
		return self.report
	
	#} END interface
	
#} END exceptions 


#####################
## Methods    ######
###################
def track_output_call( func ):
	"""Wraps the proecss.evaluateStateBase function allowing to gather plenty of information 
	about the call, as well as error statistics"""
	
	def track_func( self, plug, mode ):
		pdata = self.getWorkflow()._trackOutputQueryStart( self, plug, mode )
		
		try:
			result = func( self, plug, mode )
		except Exception,e:
			pdata.exception = e
			self.getWorkflow()._trackOutputQueryEnd( None )
			raise 
			
		self.getWorkflow()._trackOutputQueryEnd( result )
		return result 
		
	# END track func 
		
	
	return track_func


#####################
## Classes    ######
###################

class ProcessBase( NodeBase ):
	"""The base class for all processes, defining a common interface
	
	Inputs and Outputs of this node are statically described using plugs
	"""
	kNo, kGood, kPerfect = 0, 127, 255				# specify how good a certain target can be produced
	is_state, target_state, dirty_check = ( 1,2,4 )
	
	noun = "Noun ProcessBase,redefine in subclass"	# used in reports 
	verb = "Verb ProcessBase,redefine in subclass" # used in reports 
	
	__all__.append( "ProcessBase" )
	
	
	def __init__( self, id, *args, **kwargs ):
		"""Initialize process with most common information
		@param noun: noun describing the process, ( i.e. "Process" )
		@param verb: verb describing the process, ( i.e. "processing" )
		@param workflow: workflow this instance of part of """
		NodeBase.__init__( self, id = id )		# init last - need our info first !
		
	
	#{ iDuplicatable Interface 
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it"""
		return self.__class__( self.id )
		
	def copyFrom( self, other, *args, **kwargs ):
		""" Does nothing """
		# noun and verb is coming from the class anyway, it has been created
		# during instance creation 
		
	#} END iDuplicatable
	

	#{ Query
	
	def getTargetRating( self, target ):
		"""@return: tuple( int, PlugShell )
		int between 0 and 255 - 255 means target matches perfectly, 0 
		means complete incompatability. Any inbetweens indicate the target can be 
		achieved, but maybe just in a basic way
		If rate is 0, the object will be None, otherwise its a plugShell to the 
		input attribute that can take target as input. In process terms this means 
		that at least one output plug exists that produces the target.
		@param target: instance or class of target to check for compatability
		@raise TypeError: if the result is ambiguous"""
		# query our ouput plugs for a compatible attr
		inplugs = self.getInputPlugs( )
		plugrating = self.filterCompatiblePlugs( inplugs, target, raise_on_ambiguity = 1 )
		
		if not plugrating:		#	 no plug ?
			return ( 0 , None )
			
		# remove all non-writable plugs - they can never be targets 
		writableRatedPlugs = []
		for rate,plug in plugrating:				# rate,plug tuple 
			if not  plug.attr.flags & Attribute.writable:
				continue			# need to set the attribute
				
			# connected plugs are an option, but prefer the ones being open
			if self.toShell( plug ).getInput():
				rate /= 2.0
				
			writableRatedPlugs.append( (rate,plug) )
		# END writable only filters
		
		if not writableRatedPlugs:
			return ( 0, None )
			
		writableRatedPlugs.sort()		# high comes last
		
		rate, plug = writableRatedPlugs[-1] 
		return ( int(rate), self.toShell( plug ) )
		
		
	def getSupportedTargetTypes( self ):
		"""@return: list target types that can be output
		@note: targetTypes are classes, not instances"""
		return [ p.attr.typecls for p in self.getInputPlugs() ]
	
	#} END query 

	#{ Interface
	
	def evaluateState( self, plug, mode ):
		"""@return: an instance suitable to be stored in the given plug
		@param plug: plug that triggered the computation - use it to compare against
		your classes plugs to see which output is required and return a result suitable
		to be stored in plug
		@param mode: bit flags as follows:
		is_state: your return value represents the current state of the process - your output will 
				represent what actually is present. You may not alter the state of your environment, 
				thus this operation is strictly read-only.
				According to your output, when called you need to setup a certain state 
				and return the results according to that state. This flag means you are requrested
				to return everything that is right according to the state you shall create.
				If this state is disabled, you should not return the current state, but behave 
				according to the other ones.
		target_state: your return value must represent the 'should' state - thus you must assure 
				that the environment is left in a state that matches your plug state - the result 
				of that operation will be returned.
				Usually, but not necessarily, the is_state is also requested so that the output
				represents the complete new is_state ( the new state after you changed the environment
				to match the plug_state )
		dirty_check: Always comes in conjunction with is_state. You are required to return the is_state
				but raise a DirtyException if your inputs would require you to adjust the environment 
				to deliver the plug state. If the is_state if the environment is the plug_state
				as there is nothing to do for you, do not raise and simply return your output.
		The call takes place as there is no cache for plugType.
		@note: needs to be implemented by subclasses, but subclasses can just call their 
		superclass for all unhandled plugs resulting in consistent error messages"""
		raise PlugUnhandled( "Plug %s.%s cannot be handled - check your implementation" % ( self, str( plug ) ) )
		

	# } END interface
	
	#{ Overridden from NodeBase
	
	def compute( self, plug, mode = None ):
		"""Just wire the call to our output base as it will be tracked and hooked into our 
		system"""
		return self.evaluateStateBase( plug, mode )
		
	#}# END overridden from NodeBase
	
	
	#{ Base 
	# methods that drive the actual call
	@track_output_call
	def evaluateStateBase( self, plug, mode ):
		"""Base implementation of the output, called by L{getInput} Method. 
		Its used to have a general hook for the flow tracing
		@param plug: plug to evaluate
		@param mode: the mode of the valuation
		@return: result of the computation"""
		wfl = self.getWorkflow()
		finalmode = wfl._mode			# use global mode 
		
		# if we are root, we take the mode given by the caller though 
		if wfl._callgraph.getCallRoot().process == self:
			finalmode = mode 
	
		# exceptions are handled by dgengine	
		# call actually implemented method
		return self.evaluateState( plug, finalmode )
		
	def prepareProcess( self ):
		"""Will be called on all processes of the workflow once before a target is 
		actually being queried by someone
		It should be used to do whatever you think is required to work as process.
		This uauslly is a special case for most preocesses"""
		pass 
		
	def getWorkflow( self ):
		"""@return: the workflow instance we are connected with. Its used to query global data"""
		return self.graph
	
	#} END base 
	
	
class ArgProcessBase( ProcessBase ):
	"""Baseclass for all processes taking arguments. It will store them allowing 
	it to be properly duplicated"""
	__all__.append( "ArgProcessBase" )
	__slots__ = ( 'args','kwargs' )

	
	def __init__( self, id, *args, **kwargs ):
		"""Store args and kwargs for later duplicateion"""
		self.args = args
		self.kwargs = kwargs 
		super( ArgProcessBase, self ).__init__( id, *args, **kwargs )
		
	#{ iDuplicatable Interface
	
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it"""
		return self.__class__( self.id, *self.args, **self.kwargs )
		
	def copyFrom( self, other, *args, **kwargs ):
		"""Note: we have already given our args to the class during instance creation, 
		thus we do not copy args again"""
		pass 
		
	#} END iDuplicatable
	
	
	
class WorkflowProcessBase( GraphNodeBase, ProcessBase ):
	"""A process wrapping a workflow, allowing workflows to be nested
	Derive from this class and initialize it with the workflow you would like to have wrapped
	The process works by transmitting relevant calls to its underlying workflow, allowing 
	nodeInsideNestedWorkflow -> thisworkflow.node.plug connections 
	
	Workflows are standin nodes - they can connect anything their wrapped nodes can connect
	@note: to prevent dependency issues, the workflow instance will be bound on first use
	"""
	__all__.append( "WorkflowProcessBase" )
	
	#{ Overridden Object Methods 
	
	def __init__( self, id, workflowModulePath, workflowName, wflInstance=None, **kwargs ):
		"""@param workflowinst: instance of the Workflow you would like to wrap
		@param workflow: the workflow we are in ( the parent workflow )
		@param workflowModulePath: module import path which will contain the workflow
		@param workflowName: name of the workflow as it will exist in workflowModule 
		@param wflInstance: if given, this instance will be used instead of creating
		a new workflow. Used by copy constructor.
		@param **kwargs: all arguments required to initialize the ProcessBase"""
		
		wrappedwfl = wflInstance
		if not wrappedwfl:
			wflmod  = __import__( workflowModulePath, globals(), locals(), [''] )
			wrappedwfl = self._createWrappedWfl( wflmod, workflowName )
		
		# NOTE: baseclass stores wrapped wfl for us
		# init bases
		GraphNodeBase.__init__( self, wrappedwfl, **kwargs )
		ProcessBase.__init__( self, id, **kwargs )
		
		# adjust the ids of wrapped graph nodes with the name of their graph
		for node in self.wgraph.iterNodes():
			node.setID( "%s.%s" % ( id, node.getID() ) )
		
		# override name - per instance in our case 
		self.noun = wrappedwfl.name
		self.verb = "internally computing"
		
		
	#{ iDuplicatable Interface
	
	def createInstance( self, *args, **kwargs ):
		"""Create a copy of self and return it - required due to our very special constructor"""
		return self.__class__( self.id, None, None, wflInstance = self.wgraph  )
		
	# } END iDuplicatable
			 
			 
	def _createWrappedWfl( self, wflmod, wflname ):
		"""@return: our wrapped workflow instance
		@note: as we modify the graph with our 'virtual' connections, we copy it
		and create a new one. Workflows are global elements that should not be changed by someone
		to stop working for anotherone
		@todo: for now, we do not duplicate them  - have to implement and test proper duplication, no time now ... """
		try:
			return getattr( wflmod, wflname )
		except AttributeError:
			# try to trigger creation of workflow and add it to the module
			try:
				wfl = wflbase.loadWorkflowFromDotFile( Path( wflmod.__file__ ).p_parent / wflname + ".dot" )
				setattr( wflmod, wflname, wfl )
				return wfl
			except AttributeError:
				raise
				raise AssertionError( "Workflow module %r reuqires createWorkflow method to be implemented for nested workflows to work" % wflmod )
		# END try to copy or create workflow 
		
	#} END overridden methods 
	
	
	#{ ProcessBase Methods
	def prepareProcess( self ):
		"""As we have different callgraphs, but want proper reports, just swap in the 
		callgraph of our own workflow to allow it to be maintained correctly when the nodes 
		of the wrapped graph evaluate.
		@note: this requires that we get called after the callgraph has bene initialized"""
		if self.graph._callgraph.number_of_nodes():
			raise AssertionError( "Callgraph of parent workflow %r was not empty" % self.graph )
		
		self.wgraph._callgraph = self.graph._callgraph	# assure wrapped workflow takes our callgraph
		
		# Prepare all our wrapped nodes
		for node in self.wgraph.iterNodes( ):
			node.prepareProcess( )
			
		# ProcessBase.prepareProcess( self )
	
	#} END processbase methods
	
	#{ GraphNodeBase Methods
	
	def _iterNodes( self ):
		"""@return: generator for nodes that have no output connections or no input connections """
		noOutput = lambda node: not node.getConnections( 0, 1 )
		noInput = lambda node: not node.getConnections( 1, 0 )
		return self.wgraph.iterNodes( predicate = Or( noInput, noOutput ) ) 
	    
	def _getNodePlugs( self ):
		"""Override the base method, filtering it's output so that only unconnected plugs
		will be returned"""
		finalres = list()
		for node, plug in super( WorkflowProcessBase, self )._getNodePlugs( ):
			shell = node.toShell( plug ) 
			if not shell.getInput() and not shell.getOutputs( ):
				finalres.append( ( node , plug ) )
				#print "KEPT %s.%s" % ( node, str( plug ) )
			#else:
				#print "REMOVED %s.%s" % ( node, str( plug ) ) 
		# END for each node,plug pair
		return finalres
		
	#} end graphnodebase methods
	
	
	
		
	
	
