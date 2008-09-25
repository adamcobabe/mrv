"""B{byronimo.automation.dgfacadeengine}
Contains nodes supporting facading within a dependency graph  - this can be used 
for container tyoes or nodes containing their own subgraph even

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

from networkx import DiGraph, NetworkXError
from collections import deque
import inspect
import weakref
import itertools
import copy
from byronimo.util import iDuplicatable

from dgengine import NodeBase
from dgengine import _PlugShell
from dgengine import iPlug

#{ Shells 


class _FacadeShellOIMeta( type ):
	"""Metaclass building the method wrappers for the _FacadeShell class - not 
	all methods should be overridden, just the ones important to use"""
	
	@classmethod
	def getUnfacadeMethod( cls,funcname ):
		def unfacadeMethod( self, *args, **kwargs ):
			return getattr( self._toIShell(), funcname )( *args, **kwargs )
			
		unfacadeMethod.__name__ = funcname
		return unfacadeMethod
		
	def __new__( metacls, name, bases, clsdict ):
		unfacadelist = clsdict.get( '__unfacade__' )
		newcls = type.__new__( metacls, name, bases, clsdict )
		
		# create the wrapper functions for the methods that should wire to the 
		# original shell, thus we unfacade them
		for funcname in unfacadelist:
			setattr( newcls, funcname, metacls.getUnfacadeMethod( funcname ) )
			
		# all other attributes should be handled by the original shell class though 
		# TODO: add handlers 
		# END for each unfacade method name 
		return newcls
		
		
class _FacadeIOMeta( _FacadeShellOIMeta ):
	"""Metaclass wrapping all unfacade attributes on the plugshell trying 
	to get an input connection """

	@classmethod
	def getUnfacadeMethod( cls,funcname ):
		"""@return: wrapper method for funcname """
		def unfacadeMethod( self, *args, **kwargs ):
			"""Wrap the actual call by obtaininng a possibly special shell, and making 
			the call there """
			return getattr( self._getInputShell( ), funcname )( *args, **kwargs )
			
		unfacadeMethod.__name__ = funcname
		return unfacadeMethod
	

class _OIFacadeShell( _PlugShell ):
	"""All connections from and to the FacadeNode must actually start and end there.
	Iteration over internal plugShells is not allowed.
	Thus we override only the methods that matter and assure that the call is handed 
	to the acutal internal plugshell.
	We know everything we require as we have been fed with an IOPlugShell
	"""
	# list all methods that should not be a facade to our facade node 
	__unfacade__ = [ 'get', 'set', 'hasCache', 'setCache', 'getCache', 'clearCache' ]
	__metaclass__ = _FacadeShellOIMeta
	
	def __init__( self, *args ):
		"""Sanity checking"""
		if not isinstance( args[1], IOFacadePlug ):
			raise AssertionError( "Invalid PlugType: Need %r, got %r" % ( IOFacadePlug, args[1].__class__ ) )
			
		super( _OIFacadeShell, self ).__init__( *args )
	
	def _toIShell( self ):
		"""@return: convert ourselves to the real shell actually behind this facade plug"""
		return self.plug.inode.toShell( self.plug )
		
		
class _IOFacadeShell( _PlugShell ):
	"""This callable class, when called, will create a IOFacadePlugShell using the 
	actual facade node, not the one given as input. This allows it to have the 
	facade system handle the plugshell, or simply satisfy the original request"""
	
	__unfacade__ = _OIFacadeShell.__unfacade__
	__metaclass__ = _FacadeIOMeta
	
	def __init__( self, *args ):
		"""Initialize this instance - we can be in creator mode or in shell mode.
		ShellMode: we behave like a shell but apply customizations, true if 3 args ( node, plug, origshellcls )  
		CreatorMode: we only create shells of our type in ShellMode, true if 2 args )
		@param origshellcls[-1]: the shell class used on the manipulated node before we , must always be set as last arg
		@param facadenode[-2]: the facadenode we are connected to 
		@todo: optimize by creating the unfacade methods exactly as we need them and bind the respective instance 
		methods - currently this is solved with a simple if conditiion.
		"""
		# get the last arguments - they are supposed to be ours
		myargs = list( args )	 # cannot pop tuple
		self.origshellcls = myargs.pop( )
		self.facadenode = myargs.pop( )
		
		if myargs:				# SHELL MODE 	- init base
			# if we are supposed to be initialized with an ioPlug, keep it in a separate 
			# attribute 
			self.ioplug = None							# keep it for later comparison at least 
			if isinstance( myargs[1], IOFacadePlug ):
				self.ioplug = myargs[1]
				myargs[1] = self.ioplug.iplug		# this is the internal plug on the internal node 
			# END ioplug checking 
			
			super( _IOFacadeShell, self ).__init__( *myargs )
		# END if shell mode 
		
	def __call__( self, *args ):
		"""This equals a constructor call to the shell class on the wrapped node.
		We actually try a reverse mapping for all calls should be attempted to be handled
		by the facade node. If that works, its good, if not, we swap in the original 
		class creator and undo our modification, as this wrapped node has no 
		relation to the world of the facade node.
		This applies to everything but connection handling
		@note: the shells we create are default ones with some extra handlers 
		for exceptions"""
		myargs = list( args )				# tuple cannot be adjusted
		myargs.append( self.facadenode )
		myargs.append( self.origshellcls )
		return self.__class__( *myargs )
	
	#{ Helpers 	
	def _getInputShell( self ):
		"""Helper calling a function on the original shell if we have that information"""
		if self.ioplug is None:
			# just return the internal shell ( that will actually do the job ) 
			return self.origshellcls( self.node, self.plug )	
		
		
		# Use the facade node shell type - it will not handle connections
		facadeNodeShell = self.facadenode.toShell( self.ioplug )
		inputShell = facadeNodeShell.getInput( )
		
		# if we have an input shell, use it 
		if inputShell:
			print "BACK TRACK: '%s' <- '%s'" % ( repr( inputShell ), repr( facadeNodeShell ) )
			return inputShell
			
		# no 'outside world' inputShell found, use the internal handler instead
		# Always use the stored class - using self.node.toShell would create our shell again !
		return self.origshellcls( self.node, self.plug )
	
	# } END helpers 
	

# END shells 


#{ Nodes 
		
class FacadeNodeBase( NodeBase ):
	"""Node having no own plugs, but retrieves them by querying other other nodes
	and claiming its his own ones.
	
	Using a non-default shell it is possibly to guide all calls through to the 
	virtual PlugShell.
	
	Derived classes must override _getPlugShells which will be queried when 
	plugs or plugshells are requested. This node will cache the result and do 
	everything required to integrate itself. 
	
	It lies in the nature of this class that the plugs are dependent on a specific instance 
	of this node, thus classmethods of NodeBase have been overridden with instance versions 
	of it.
	
	The facade node keeps a plug map allowing it to map plug-shells it got from 
	you back to the original shell respectively. If the map has been missed, 
	your node will be asked for information.

	@note: facades are intrusive for the nodes they are facading - thus the nodes 
	returned by L{_getNodePlugs} will be altered. Namely the instance will get a 
	shellcls and plug override to allow us to hook into the callchain. Thus you should have 
	your own instance of the node - otherwise things might behave differently for 
	others using your nodes from another angle
	
	@note: this class could also be used for facades Container nodes that provide 
	an interface to their internal nodes"""
	shellcls = _OIFacadeShell		# overriden from NodeBase 
	
	
	#{ Object Overridden Methods
	def __init__( self, *args, **kwargs ):
		""" Initialize the instance"""
		NodeBase.__init__( self, *args, **kwargs )
		
	
	def __getattr__( self, attr ):
		"""@return: shell on attr made from our plugs - we do not have real ones, so we 
		need to call getPlugs and find it by name
		@note: to make this work, you should always name the plug names equal to their 
		class attribute"""
		for plug in self.getPlugs( ):
			if plug._name == attr:
				return self.toShell( plug )
			
		raise AttributeError( "Attribute %s does not exist on %s" % (attr,self) )
		
	#} END Object Overridden Methods 
	
	
	#{ iDuplicatable Interface 
		
	def copyFrom( self, other ):
		"""Actually, it does nothing because our plugs are linked to the internal 
		nodes in a quite complex way. The good thing is that this is just a cache that 
		will be updated once someone queries connections again.
		Basically it comes down to the graph duplicating itself using node and plug 
		methods instead of just doing his 'internal' magic"""
		pass 
	# } END iDuplicatable
	
	
	
	#{ To be Subclass-Implemented
	# not used anymore ... not for now at least !
	#def _getNodeByPlug( self, virtualplug ):
		"""Called when the facade class encounters a virtual plug that needs to be 
		converted to its real shell, thus the (node,plug) pair that originally owns the plug.
		Thus the method shall return a node owning the virtualplug. 
		It will only be called once a facade shell is supposed to be altered, see 
		L{_OIFacadeShell}
		@raise ValueError: if the virtualplug is unknown.
		@note: iterShells may actually traverse the plug-internal affects relations and 
		possibly return a shell to a client that your derived class has never seen before.
		You should take that into consideration and raise L{ValueError} if you do not know 
		the plug"""
		#  raise NotImplementedError( "_toRealShell needs to be implemented by the subclass" )
	                                  
	def _getNodePlugs( self, **kwargs ):
		"""Implement this as if it was your getPlugs method - it will be called by the 
		base - your result needs processing before it can be returned
		@return: list( tuple( node, plug ) )
		if you have an existing node that the plug or shell  you gave is from, 
		return it in the tuple, otherwise set it to a node with a shell that allows you 
		to handle it - the only time the node is required is when it is used in and with 
		the shells of the node's own shell class.
		
		The node will be altered slightly to allow input of your facade to be reached
		from the inside"""
		raise NotImplementedError( "Needs to be implemented in SubClass" )
	# END to be subclass implemented 
						
	
	#{ Nodebase Methods 
	def getPlugs( self, **kwargs ):
		"""Calls L{_getNodePlugs} method to ask you to actuallly return your 
		actual nodes and plugs or shells.
		We prepare the returne value to assure we are being called in certain occasion, 
		which actually glues outside and inside worlds together """
		yourResult = self._getNodePlugs( **kwargs )
		
		def toFacadePlug( node, plug ):
			if isinstance( plug, IOFacadePlug ):
				return plug
			return IOFacadePlug( node, plug )
		# END to facade plug helper 
		
		finalres = list()
		for orignode, item in yourResult:			# item == (plug)
			ioplug = toFacadePlug( orignode, item )
			finalres.append( ioplug )
			# END shell handling 
			
			
			# MODIFY NODE INSTANCE
			###############################
			# Allowing us to get callbacks once the node is used inside of the internal 
			# structures
			# WRAP VIRTUAL PLUG to the node 
			################################
			setattr( orignode, ioplug.getINodeAttrName( ), ioplug )
			
			
			# ADD FACADE SHELL CLASS 
			if not isinstance( orignode.shellcls, _IOFacadeShell ):
				classShellCls = orignode.shellcls
				orignode.shellcls = _IOFacadeShell( self, classShellCls )
				# END if we have to swap in our facadeIOShell
			
			
		# END for each item in result 
		
		# the final result has everything nicely put back together, but 
		# it has been altered as well
		return finalres
		
	#} end nodebase methods

class GraphNodeBase( FacadeNodeBase ):
	"""A node wrapping a graph, allowing it to be nested within the node 
	All inputs and outputs on this node are purely virtual, thus they internally connect
	to the wrapped graph.
	"""
	#{ Overridden Object Methods
	
	def __init__( self, wrappedGraph, *args, **kwargs ):
		""" Initialize the instance
		@param wrappedGraph: graph we are wrapping"""
		self.wgraph = wrappedGraph.duplicate( )
		
		FacadeNodeBase.__init__( self, *args, **kwargs )
	 
		
	#} END overridden methods
	
	#{ iDuplicatable Interface 
	def createInstance( self ):
		"""Create a copy of self and return it"""
		return self.__class__( self.wrappedGraph )	# graph will be duplicated in the constructor
		
	def copyFrom( self, other ):
		"""Create a duplicate of the wrapped graph so that we have our unique one"""
		# Graph was already dupicated and set  
		
		
	# } END iDuplicatable
	
	#{ Base Methods
	
	def _iterNodes( self ):
		"""@return: generator for nodes in our graph
		@note: derived classes could override this to just return a filtered view on 
		their nodes"""
		return self.wgraph.iterNodes( )
		
	#} END base
	
	#{ NodeBase Methods 
	
	def _getNodePlugs( self, **kwargs ):
		"""@return: all plugs on nodes we wrap ( as node,item tuple )"""
		outlist = list()

		for node in self._iterNodes():
			plugresult = node.getPlugs( **kwargs )
			outlist.extend( ( (node,item) for item in plugresult ) )
			# END update lut map
		# END for node in nodes 
		
		# the rest of the nitty gritty details, the base class will deal 
		return outlist
	
	#} end NodeBase methods
		
	def getInputPlugs( self, **kwargs ):
		"""@return: list of plugs suitable as input
		@note: convenience method"""
		return self.getPlugs( predicate = lambda p: p.providesInput(), **kwargs )
		
	def getOutputPlugs( self, **kwargs ):
		"""@return: list of plugs suitable to deliver output
		@note: convenience method"""
		return self.getPlugs( predicate = lambda p: p.providesOutput(), **kwargs )
#} END nodes


#{ Plugs
class IOFacadePlug( tuple , iPlug ):
	"""Facade Plugs are meant to be stored on instance level overriding the respective 
	class level plug descriptor.
	If used directly, it will facade the internal affects relationships and just return 
	what really is affected on the facade node
	
	Additionally they are associated to a node instance, and can thus be used to 
	find the original node once the plug is used in an OI facacde shell
	
	Its a tuple as it will be more memory efficient that way. Additionally one 
	automatically has a proper hash and comparison if the same objects come together
	
	@note: it would be more efficient memory wise to store the per node attributes 
	( like the facade node ) on node level in the overridden IO shellcls instead of 
	on per plug level, this offers the most flexibility and will provide us a perfect 
	key as well.
	"""
	
	#{ Object Overridden Methods
	                           
	def __new__( cls, *args ):
		"""Store only weakrefs, throw if we do not get 3 inputs
		@param arg[0] = internal node 
		@param arg[1] = internal plug"""
		count = 2
		if len( args ) != count:
			raise AssertionError( "Invalid Argument count, should be %i, was %i" % ( count, len( args ) ) )
		
		return tuple.__new__( cls, ( weakref.ref( arg ) for arg in args ) )
	
	
	def __getattr__( self, attr ):
		""" Allow easy attribute access 
		inode: the internal node 
		iplug: the internal plug 
		"""
		if attr == 'inode':
			return self[0]()
		if attr == 'iplug':
			return self[1]()
		
		# still here ? try to return a value on the original plug 
		return getattr( self.iplug, attr )
		
	def __str__( self ):
		return "FP(%s.%s)" % (self.inode, self.iplug)
	
	#} END object overridden methods
	
	
	#{ Interface
	
	def getINodeAttrName( self ):
		"""@return: name of attribute that stores our instance on our inode"""
		pred = lambda m: m == self.iplug
		for attrname,member in inspect.getmembers( self.inode.__class__, predicate = pred ):
			return attrname
		raise AssertionError( "Could not find own plug %r in members of %s" % ( repr( self.iplug ), self.inode ) )
	#} END interface
	
	#{ iPlug Interface 
	
	def affects( self, otherplug ):
		"""Affects relationships will be set on the original plug only"""
		return self.iplug.affects( otherplug )
		
	def getAffected( self ):
		"""Walk the internal affects using an internal plugshell
		@return: tuple containing affected plugs ( plugs that are affected by our value )"""
		raise NotImplementedError()
		
	def getAffectedBy( self ):
		"""@return: tuple containing plugs that affect us ( plugs affecting our value )"""
		raise NotImplementedError()
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations"""
		raise NotImplementedError()
		return self.iplug.__class__.providesOutput( self )		# use our affects check though, but their special implementation 
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		raise NotImplementedError()
		return self.iplug.__class__.providesInput( self )
		
	#}
	
	
#} END plugs 
