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

#{ Shells 


class _FacadeShellMeta( type ):
	"""Metaclass building the method wrappers for the _FacadeShell class - not 
	all methods should be overridden, just the ones important to use"""
	
	@classmethod
	def getUnfacadeMethod( cls,funcname ):
		def unfacadeMethod( self, *args, **kwargs ):
			return getattr( self._toShell(), funcname )( *args, **kwargs )
			
		unfacadeMethod.__name__ = funcname
		return unfacadeMethod
		
	def __new__( metacls, name, bases, clsdict ):
		unfacadelist = clsdict.get( '__unfacade__' )
		newcls = type.__new__( metacls, name, bases, clsdict )
		
		# create the wrapper functions for the methods that should wire to the 
		# original shell, thus we unfacade them
		for funcname in unfacadelist:
			setattr( newcls, funcname, metacls.getUnfacadeMethod( funcname ) )
		# END for each unfacade method name 
		return newcls
		
		
class _FacadeInOutMeta( _FacadeShellMeta ):
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
	

class _FacadePlugShell( _PlugShell ):
	"""All connections from and to the FacadeNode must actually start and end there.
	Iteration over internal plugShells is not allowed.
	Thus we override only the methods that matter and assure that the call is handed 
	to the acutal plugShell
	"""
	# list all methods that should not be a facade to our facade node 
	__unfacade__ = [ 'get', 'set', 'hasCache', 'setCache', 'getCache', 'clearCache' ]
	__metaclass__ = _FacadeShellMeta
	
	def _toShell( self ):
		"""@return: convert ourselves to the real shell actually behind this facade plug"""
		return self.node._realShell( self.plug )
		
class _FacadeInToOutShellCreator( _PlugShell ):
	"""This callable class, when called, will create a FacadePlugShell using the 
	actual facade node, not the one given as input. This allows it to have the 
	facade system handle the plugshell, or simply satisfy the original request"""
	
	__unfacade__ = _FacadePlugShell.__unfacade__
	__metaclass__ = _FacadeInOutMeta
	
	def __init__( self, *args ):
		"""Initialize this instance - we can be in creator mode or in shell mode.
		ShellMode: we behave like a shell but apply customizations, true if 4 args ( node, plug, facadenode,origshellcls )  
		CreatorMode: we only create shells of our type in ShellMode, true if 2 args )
		@param arg[-2]: our facadenode parent managing the node we are customizing, must always be set on before last arg 
		@param origshellcls[-1]: the shell class used on the manipulated node before we , must always be set as last arg"""
		# get the last arguments - they are supposed to be ours
		myargs = list( args )	 # cannot pop tuple
		self.origshellcls = myargs.pop( )
		self.facadenode = myargs.pop( )
		
		if myargs:				# SHELL MODE 	- init base
			super( _FacadeInToOutShellCreator, self ).__init__( *myargs ) 
		
	def __call__( self, *args ):
		"""This equals a constructor call to the shell class on the wrapped node.
		We actually try a reverse mapping for all calls should be attempted to be handled
		by the facade node. If that works, its good, if not, we swap in the original 
		class creator and undo our modification, as this wrapped node has no 
		relation to the world of the facade node.
		This applies to everything but connection handling
		@note: the shells we create are default ones with some extra handlers 
		for exceptions"""
		myargs = list( args )		# tuple cannot be adjusted
		myargs.append( self.facadenode )
		myargs.append( self.origshellcls )
		return self.__class__( *myargs )
	
	#{ Helpers 	
	@staticmethod
	def _rmShellInstanceOverride( wrappednode ):
		"""No, we cannot remove the shells as we would remove it for all plugs at once.
		Once installed, we have to keep them on the instance"""
		return
		if isinstance( wrappednode.shellcls, _FacadeInToOutShellCreator ):
			print "REMOVED SHARADE SHELL on: %s" % wrappednode 
			del( wrappednode.shellcls )
			
	def _getInputShell( self ):
		"""Helper calling a function on the original shell"""
		# get input using default shell !
		facadeNodeShell = _PlugShell( self.facadenode, self.plug )
		inputShell = facadeNodeShell.getInput( )
		
		# if we have an input shell, use it 
		if inputShell:
			print "BACK TRACK: '%s' <- '%s'" % ( repr( inputShell ), repr( facadeNodeShell ) )
			return inputShell
			
		# no 'outside world' inputShell found, use the internal handler instead 
		# finally try original shell and remove ourselves - in this spot we cannot 
		# do anyhthing. If this changes ( by a connection ), we will be swapped back in 
		# anyway - its an optimization here to let the graph learn
		_FacadeInToOutShellCreator._rmShellInstanceOverride( self.node )
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
	returned by L{_getNodeByPlug} will be altered. Namely the instance will get a 
	shellcls override to allow our shells to be used instead. Thus you should have 
	your own instance of the node - otherwise things might stop working for others
	using the graph.
	
	@note: this class could also be used for facades Container nodes that provide 
	an interface to their internal nodes"""
	shellcls = _FacadePlugShell		# overriden from NodeBase
	
	
	#{ Internal Methods 
	def _realShell( self, virtualplug ):
		"""Called to get the real internal shell for a plug that has been 
		triggered on the facade node, thus the flow is 
		outside -> inside """
		node = None
		# try to get the actual internal shell by checking the cache
		try:
			internalnode = self._plugToNodeCache[ virtualplug ]
		except KeyError:
			# try to get the node from the parent class 
			internalnode = self._getNodeByPlug( virtualplug )
		# END get real node for virtual plug 
		
		# get the actual shell, we use whatever overidden method, to assure 
		# the shell can indeed handle itself. 
		if internalnode:
			# Keep the our wrapper on the node - we must assure that it works 
			# for all plugs that are still to come.
			# We could optimize it though by removing it from all nodes that 
			# have no facaded plug at all
			_FacadeInToOutShellCreator._rmShellInstanceOverride( internalnode )			
			return internalnode.toShell( virtualplug )
		# END we had an internal node 
		
		# no node ? - raise - it might be cought - plug cannot be associated with wrapped node 
		raise ValueError( "%r did not find matching node for plug %r" % ( self, virtualplug ) )
			
	#} END internal methods 
	
	#{ Object Overridden Methods
	def __init__( self, *args, **kwargs ):
		""" Initialize the instance"""
		self._plugToNodeCache = dict()		# plug -> node cache
		NodeBase.__init__( self, *args, **kwargs )
		
	
	def __getattr__( self, attr ):
		"""@return: shell on attr made from our plugs - we do not have real ones, so we 
		need to call getPlugs and find it by name
		@note: to make this work, you should always name the plug names equal to their 
		class attribute"""
		for shell in self.getPlugs( nodeInstance=self ):
			if shell.plug._name == attr:
				return shell
			
		raise AttributeError( "Attribute %s does not exist on %s" % (attr,self) )
		
	#} END Object Overridden Methods 
	
	
	
	#{ iDuplicatable Interface 
		
	def copyFrom( self, other ):
		"""Create a duplicate of the wrapped graph so that we have our unique one"""
		# As we do not know how the supernode handles this, we just keep our cache 
		# clear and thus ask the supernode everytime we need the original node, refilling 
		# the cache that way
		# like that we know everything the original instance knows about virtual plugs ! Correct !
		# as we are currently even in the same graph, this is correct
		# self._plugToNodeCache = other._plugToNodeCache.copy()	# shallow copy 
	# } END iDuplicatable
	
	
	
	#{ To be Subclass-Implemented
	def _getNodeByPlug( self, virtualplug ):
		"""Called when the facade class encounters a virtual plug that needs to be 
		converted to its real shell, thus the (node,plug) pair that originally owns the plug.
		Thus the method shall return a node owning the virtualplug. 
		It will only be called once a facade shell is supposed to be altered, see 
		L{_FacadePlugShell}
		@raise ValueError: if the virtualplug is unknown.
		@note: iterShells may actually traverse the plug-internal affects relations and 
		possibly return a shell to a client that your derived class has never seen before.
		You should take that into consideration and raise L{ValueError} if you do not know 
		the plug"""
		raise NotImplementedError( "_toRealShell needs to be implemented by the subclass" )
	                                  
	def _getNodePlugs( self, **kwargs ):
		"""Implement this as if it was your getPlugs method - it will be called by the 
		base - your result needs processing before it can be returned
		@return: list( tuple( node, plug ) ) or list( tuple( node, shell ) )
		if you have an existing node that the plug or shell  you gave is from, 
		return it in the tuple, otherwise set it None.
		The node will be altered slightly to allow input of your facade to be reached
		from the inside """
		raise NotImplementedError( "Needs to be implemented in SubClass" )
	# END to be subclass implemented 
						
	
	#{ Nodebase Methods 
	def getPlugs( self, **kwargs ):
		"""Calls the  _getNodePlugs method to ask you to actuallly return your 
		possibly virtual plugs or shells.
		The methods makes the shell work with the facade
		Here we also update our plugToNodeCache"""
		yourResult = self._getNodePlugs( **kwargs )
		
		finalres = list()
		for orignode, item in yourResult:			# item == (plug | shell)
			virtualplug = item						# used for cache
			
			if isinstance( item, _PlugShell ):
				# swap our node in - discard their shell, it will be recreated later
				orignode = item.node
				virtualplug = item.plug			
				item = self.shellcls( self, item.plug )
			# END shell handling 
			
			# MODIFY NODE INSTANCE
			###############################
			# Allowing us to get callbacks once the node is used inside of the internal 
			# structures
			if orignode:
				# WRAP VIRTUAL PLUG to the node 
				################################
				
				# ADD FACADE SHELL CLASS 
				if not isinstance( orignode.shellcls, _FacadeInToOutShellCreator ):
					classShellCls = orignode.shellcls
					orignode.shellcls = _FacadeInToOutShellCreator( self, classShellCls )
				# END if we have to swap in our facadeInToOutShell
				
				# update our node cache - check for ambivalency 
				if self._plugToNodeCache.has_key( virtualplug ) and self._plugToNodeCache[ virtualplug ] != orignode:
					raise AssertionError( 'Ambivalent VirtualPlug %s->%s, already stored as "->%s' % ( virtualplug, self._plugToNodeCache[ virtualplug ] , orignode ) )
					
				self._plugToNodeCache[ virtualplug ] = orignode
				
			# END orig node manipulation and cache update
			
			finalres.append( item )
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
	
	def _getNodeByPlug( self, virtualplug ):
		"""@return: node matching virtual plug according to our cache"""
		raise NotImplementedError( )
	
	def _getNodePlugs( self, **kwargs ):
		"""@return: all plugs on nodes we wrap ( as node,item tuple )"""
		outlist = list()
		hasInstance = kwargs.get( 'nodeInstance', None ) is not None

		for node in self._iterNodes():
			# swap in the given node if nodeInstance is requested - this afects 
			# the type of shells returned ( potentially )
			if hasInstance:
				kwargs[ 'nodeInstance' ] = node
				
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

class FacadePlug( object ):
	"""Facade Plugs are meant to be stored on instance level overriding the respective 
	class level plug descriptor.
	If used directly, it will facade the internal affects relationships and just return 
	what really is affected on the facade node
	
	Additionally they are associated to a node instance, 
	"""
	pass  
	
#} END plugs 
