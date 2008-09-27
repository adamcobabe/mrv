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
from byronimo.util import iDuplicatable

from dgengine import NodeBase
from dgengine import _PlugShell
from dgengine import iPlug
from dgengine import Attribute

#{ Shells 


class _OIShellMeta( type ):
	"""Metaclass building the method wrappers for the _FacadeShell class - not 
	all methods should be overridden, just the ones important to use"""
	
	@classmethod
	def createUnfacadeMethod( cls, funcname ):
		def unfacadeMethod( self, *args, **kwargs ):
			return getattr( self._toIShell(), funcname )( *args, **kwargs )
		return unfacadeMethod
	
	@classmethod
	def createFacadeMethod( cls, funcname ):
		"""in our case, connections just are handled by our own OI plug, staying 
		in the main graph"""
		return None
	
	@classmethod
	def getMethod( cls,funcname, facadetype ):
		method = None
		if facadetype == "unfacade":
			method = cls.createUnfacadeMethod( funcname )
		else:
			method = cls.createFacadeMethod( funcname )
		
		if method: # could be none if we do not overwrite the method 	
			method.__name__ = funcname
			
		return method
	

	def __new__( metacls, name, bases, clsdict ):
		unfacadelist = clsdict.get( '__unfacade__' )
		facadelist = clsdict.get( '__facade__' )
		
		# create the wrapper functions for the methods that should wire to the 
		# original shell, thus we unfacade them
		for funcnamelist, functype in ( ( unfacadelist, "unfacade" ), ( facadelist, "facade" ) ):
			for funcname in funcnamelist:
				method = metacls.getMethod( funcname, functype )
				if method:
					clsdict[ funcname ] = method
			# END for each funcname in funcnamelist 
		# END for each type of functions 
			
		return type.__new__( metacls, name, bases, clsdict )
		
		
class _IOShellMeta( _OIShellMeta ):
	"""Metaclass wrapping all unfacade attributes on the plugshell trying 
	to get an input connection """

	@classmethod
	def createUnfacadeMethod( cls,funcname ):
		"""@return: wrapper method for funcname """
		method = None
		if funcname == "clearCache":
			def unfacadeMethod( self, *args, **kwargs ):
				"""Clear caches of all output plugs as well"""
				for shell in self._getShells( "output" ):
					getattr( shell, funcname )( *args, **kwargs )
			# END unfacade method 
			method = unfacadeMethod	
		else:
			def unfacadeMethod( self, *args, **kwargs ):
				"""apply to the input shell"""
				return getattr( self._getShells( "input" )[0], funcname )( *args, **kwargs )
			method = unfacadeMethod
		# END funk type handling 
		return method
	
	@classmethod
	def createFacadeMethod( cls, funcname ):
		"""Call the main shell's function"""
		def facadeMethod( self, *args, **kwargs ):
			return getattr( self._getOriginalShell( ), funcname )( *args, **kwargs )
		return facadeMethod
		

class _OIShell( _PlugShell ):
	"""All connections from and to the FacadeNode must actually start and end there.
	Iteration over internal plugShells is not allowed.
	Thus we override only the methods that matter and assure that the call is handed 
	to the acutal internal plugshell.
	We know everything we require as we have been fed with an IOPlug
	
		- .node = facacde node 
		- .plug = ioplug containing inode and iplug ( internal node and internal plug )
			 - The internal node allows us to hand in calls to the native internal shell
	"""
	# list all methods that should not be a facade to our facade node 
	__unfacade__ = [ 'get', 'clearCache' ]
	
	# keep this list uptodate - otherwise a default shell will be used for the missing 
	# function
	# TODO: parse the plugshell class itself to get the functions automatically 
	__facade__ = [ 'setCache', 'getCache', 'hasCache','set', 'connect','disconnect','getInput',
					'getOutputs','iterShells','getConnections' ]
	
	__metaclass__ = _OIShellMeta
	
	def __init__( self, *args ):
		"""Sanity checking"""
		if not isinstance( args[1], OIFacadePlug ):
			raise AssertionError( "Invalid PlugType: Need %r, got %r" % ( OIFacadePlug, args[1].__class__ ) )
			
		super( _OIShell, self ).__init__( *args )
	
	
	def __repr__ ( self ):
		"""Cut away our name in the possible ioplug ( printing an unnecessary long name then )"""
		plugname = str( self.plug )
		nodename = str( self.node )
		plugname = plugname.replace( nodename+'.', "" )
		return "%s.%s" % ( nodename, plugname )
	
	def _toIShell( self ):
		"""@return: convert ourselves to the real shell actually behind this facade plug"""
		# must return original shell, otherwise call would be handed out again
		return self.plug.inode.shellcls.origshellcls( self.plug.inode, self.plug.iplug )
		
		
class _IOShell( _PlugShell ):
	"""This callable class, when called, will create a IOShell using the 
	actual facade node, not the one given as input. This allows it to have the 
	facade system handle the plugshell, or simply satisfy the original request"""
	
	__unfacade__ = _OIShell.__unfacade__
	__facade__ = _OIShell.__facade__
	__metaclass__ = _IOShellMeta
	
	def __init__( self, *args ):
		"""Initialize this instance - we can be in creator mode or in shell mode.
		ShellMode: we behave like a shell but apply customizations, true if 3 args ( node, plug, origshellcls )  
		CreatorMode: we only create shells of our type in ShellMode, true if 2 args )
		@param origshellcls[0]: the shell class used on the manipulated node before we , must always be set as last arg
		@param facadenode[1]: the facadenode we are connected to 
		@todo: optimize by creating the unfacade methods exactly as we need them and bind the respective instance 
		methods - currently this is solved with a simple if conditiion.
		"""
		# find whether we are in shell mode or in class mode - depending on the
		# types of the args
		# CLASS MODE 
		if hasattr( args[0], '__call__' ) or isinstance( args[0], type ):
			self.origshellcls = args[0]
			self.facadenode = args[1]
			self.iomap = dict() 							# plugname -> ioplug
			super( _IOShell, self ).__init__(  )			# initialize empty
		# END class mode
		else:
			# we do not do anything special in shell mode ( at least value-wise
			super( _IOShell, self ).__init__( *args )	# init base 
		# END INSTANCE ( SHELL ) MODE 
		
	def __call__( self, *args ):
		"""This equals a constructor call to the shell class on the wrapped node.
		Simply return an ordinary shell at its base, but we catch some callbacks 
		This applies to everything but connection handling
		@note: the shells we create are default ones with some extra handlers 
		for exceptions"""
		return self.__class__( *args )
		
	#{ Helpers 	
	
	def _getIOPlug( self ):
		"""@return: ioplug suitable for this shell or None"""
		try:
			# cannot use weak references, don't want to use strong references 
			# ioplugname = self.node.shellcls.iomap[ self.plug.getName() ]	# don't want to use strong - but have to for now 
			# ioplug = getattr( self.node.shellcls.facadenode, ioplugname ) # expensive call without cache !
			return self.node.shellcls.iomap[ self.plug.getName() ]
			# print "FOUND IOPLUG %r for %s" % ( ioplug, self.plug.getName() )
		except KeyError:
			# plug not on facadenode - this is fine as we get always called
			pass 
		#except AttributeError:
		# TODO: take that back in once we use weak references or proper ids again ... lets see
		#	# facade node does not know an io plug - assure we do not try again
		#	del( self.node.shellcls[ self.plug.getName() ] )
			
		return None
	
	def _getOriginalShell( self ):
		"""@return: instance of the original shell class that was replaced by our instance"""
		return self.node.shellcls.origshellcls( self.node, self.plug )
	
	def _getShells( self, shelltype ):
		"""@return: list of ( outside ) shells, depending on the shelltype and availability.
		If no outside shell is avaiable, return the actual shell only
		@param shelltype: "input" - outside input shell
							"output" - output shells, and the default shell"""
		if not isinstance( self.node.shellcls, _IOShell ):
			raise AssertionError( "Shellclass of %s must be _IOShell, but is %s" % ( self.node, type( self.node.shellcls ) ) )
		
		# get the ioplug on our node  
		ioplug = self._getIOPlug( )
		print "GETTING IOSHELL FOR: %r "  % repr( self )
		if not ioplug:
			# plug not on facadenode, just ignore and return the original shell 
			return [ self._getOriginalShell( ) ]
			
		# Use the facade node shell type - it will not handle connections
		facadeNodeShell = self.node.shellcls.facadenode.toShell( ioplug )
		
		if shelltype == "input":
			inputShell = facadeNodeShell.getInput( )
			
			# if we have an input shell, use it 
			if inputShell:
				print "BACK TRACK: '%s' <- '%s'" % ( repr( inputShell ), repr( facadeNodeShell ) )
				return inputShell
			else:
				# no 'outside world' inputShell found, use the internal handler instead
				# Always use the stored class - using self.node.toShell would create our shell again !
				return [ self._getOriginalShell( ) ]
		# END ioplug handling 
		else:
			outshells = facadeNodeShell.getOutputs()
			outshells.append( self._getOriginalShell() )
			return outshells
			
		# END outside shell handling 
		
		
		raise AssertionError( "Should never have reached this point!" )	
	
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
	shellcls = _OIShell		# overriden from NodeBase 
	
	
	#{ Object Overridden Methods
	def __init__( self, *args, **kwargs ):
		""" Initialize the instance"""
		NodeBase.__init__( self, *args, **kwargs )
		
	
	def __getattr__( self, attr ):
		"""@return: shell on attr made from our plugs - we do not have real ones, so we 
		need to call getPlugs and find it by name
		@note: to make this work, you should always name the plug names equal to their 
		class attribute"""
		check_ambigious = not attr.startswith( OIFacadePlug._fp_prefix )	# non long names are not garantueed to be unique
		
		candidates = list()
		for plug in self.getPlugs( ):
			if plug.getName() == attr or plug.iplug.getName() == attr:
				shell = self.toShell( plug )
				if not check_ambigious:
					return shell
				candidates.append( shell )
			# END if plugname matches
		# END for each of our plugs 
		
		if not candidates:
			raise AttributeError( "Attribute %s does not exist on %s" % (attr,self) )
			
		if len( candidates ) == 1:
			return candidates[0]
		
		# must be more ... 
		raise AttributeError( "More than one plug with the local name %s exist on %s - use the long name, i.e. %snode_attr" % ( attr, self, OIFacadePlug._fp_prefix ) )
		
		
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
		L{_OIShell}
		@raise ValueError: if the virtualplug is unknown.
		@note: iterShells may actually traverse the plug-internal affects relations and 
		possibly return a shell to a client that your derived class has never seen before.
		You should take that into consideration and raise L{ValueError} if you do not know 
		the plug"""
		#  raise NotImplementedError( "_toRealShell needs to be implemented by the subclass" )
	                                  
	def _getNodePlugs( self ):
		"""Implement this as if it was your getPlugs method - it will be called by the 
		base - your result needs processing before it can be returned
		@return: list( tuple( node, plug ) )
		if you have an existing node that the plug or shell  you gave is from, 
		return it in the tuple, otherwise set it to a node with a shell that allows you 
		to handle it - the only time the node is required is when it is used in and with 
		the shells of the node's own shell class.
		
		The node will be altered slightly to allow input of your facade to be reached
		from the inside
		@note: a predicate is not supported as it must be applied on the converted 
		plugs, not on the ones you hand out"""
		raise NotImplementedError( "Needs to be implemented in SubClass" )
	# END to be subclass implemented 
						
	
	#{ Nodebase Methods 
	def getPlugs( self, **kwargs ):
		"""Calls L{_getNodePlugs} method to ask you to actuallly return your 
		actual nodes and plugs or shells.
		We prepare the returne value to assure we are being called in certain occasion, 
		which actually glues outside and inside worlds together """
		print "getplugs" * 10
		yourResult = self._getNodePlugs( )
		
		# check args - currently only predicate is supported
		predicate = kwargs.pop( 'predicate', lambda x: True )
		if kwargs:		# still args that we do not know ?
			raise AssertionError( "Unhandled arguments found  - update this method: %s" % kwargs.keys() )
		
		def toFacadePlug( node, plug ):
			if isinstance( plug, OIFacadePlug ):
				return plug
			return OIFacadePlug( node, plug )
		# END to facade plug helper
		
		# print "START PROCESSING" * 8
		finalres = list()
		for orignode, plug in yourResult:			
			ioplug = toFacadePlug( orignode, plug )
			
			# drop it ? 
			if not predicate( ioplug ):
				continue 
			finalres.append( ioplug )
			
			
			# MODIFY NODE INSTANCE
			##################################################
			# Allowing us to get callbacks once the node is used inside of the internal 
			# structures
			
			# ADD FACADE SHELL CLASS
			############################
			if not isinstance( orignode.shellcls, _IOShell ):
				classShellCls = orignode.shellcls
				print "SETTING SHELLCLS on %s" % orignode
				orignode.shellcls = _IOShell( classShellCls, self )
				# END for each shell to reconnect 
			# END if we have to swap in our facadeIOShell
			
			
			print "FACADING PLUG: %s on %s " % ( ioplug.iplug.getName(), orignode )
			# update facade shell class ( inst ) cache so that it can map our internal 
			# plug to the io plug on the outside node 
			# cannot create weakref to tuple type unfortunately - use name instead 
			orignode.shellcls.iomap[ ioplug.iplug.getName() ] = ioplug	 
			
			
			# UPDATE CONNECTIONS ( per plug, not per node )
			##########################
			# update all connections with the new shells - they are required when 
			# walking the affects tree, as existing ones will be taken instead of
			# our new shell then.
			facadeshell = orignode.toShell( ioplug.iplug )
			all_shell_cons = facadeshell.getConnections( 1, 1 )	 				# now we get old shells
			
			
			# disconnect and reconnect with new
			for edge in all_shell_cons:
				nedge = list( ( None, None ) )
				created_shell = False
				
				for i,shell in enumerate( edge ):
					nedge[ i ] = shell
					if not isinstance( shell, _IOShell ):
						nedge[ i ] = shell.node.toShell( shell.plug )
						created_shell = True
				# END for each shell in edge 
				
				if created_shell:
					print "UPDATING CONNECTION: %r -> %r" % ( edge[0],edge[1] )
					edge[0].disconnect( edge[1] )
					print "WITH %r -> %r" % ( nedge[0],nedge[1] )
					nedge[0].connect( nedge[1] )
				# END new shell needs connection
			# END for each edge to update 
		# END for each orignode,plug in result 
		
		# print "END PROCESSING" * 8
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
	
	def _getNodePlugs( self ):
		"""@return: all plugs on nodes we wrap ( as node,plug tuple )"""
		outlist = list()

		for node in self._iterNodes():
			plugresult = node.getPlugs(  )
			outlist.extend( ( (node,plug) for plug in plugresult ) )
			# END update lut map
		# END for node in nodes 
		
		# the rest of the nitty gritty details, the base class will deal 
		return outlist
	
	#} end NodeBase methods
		
#} END nodes


#{ Plugs
class OIFacadePlug( tuple , iPlug ):
	"""Facade Plugs are meant to be stored on instance level overriding the respective 
	class level plug descriptor.
	If used directly, it will facade the internal affects relationships and just return 
	what really is affected on the facade node
	
	Additionally they are associated to a node instance, and can thus be used to 
	find the original node once the plug is used in an OI facacde shell
	
	Its a tuple as it will be more memory efficient that way. Additionally one 
	automatically has a proper hash and comparison if the same objects come together
	"""
	_fp_prefix = "_FP_"
	
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
		
		Thus we must:
			- Act as IOFacade returning additional information
			- Act as original plug for attribute access
		This will work as long as the method names are unique 
		"""
		if attr == 'inode':
			return self[0]()
		if attr == 'iplug':
			return self[1]()
		
		# still here ? try to return a value on the original plug
		return getattr( self.iplug, attr )
		
	#} END object overridden methods
	
		
	#{ iPlug Interface 
	
	def getName( self ):
		"""@return: name of (internal) plug - must be a unique key, unique enough
		to allow connections to several nodes of the same type"""
		return "%s%s_%s" % ( self._fp_prefix, self.inode, self.iplug )
		
	
	def _getAffectedList( self, direction ):
		"""@return: list of all ioplugs looking in direction, if 
		plugtestfunc says: False, do not prune the given shell"""
		these = lambda shell: shell.plug is self.iplug or not isinstance( shell, _IOShell ) or shell._getIOPlug() is None   
		iterShells = self.inode.toShell( self.iplug ).iterShells( direction=direction, prune = these, visit_once=True )
		outlist = [ shell._getIOPlug() for shell in iterShells ]
		
		return outlist
	
	def affects( self, otherplug ):
		"""Affects relationships will be set on the original plug only"""
		return self.iplug.affects( otherplug )
		
	def getAffected( self ):
		"""Walk the internal affects using an internal plugshell
		@note: only output plugs can be affected - this is a rule followed throughout the system
		@return: tuple containing affected plugs ( plugs that are affected by our value )"""
		return self._getAffectedList( "down" )
		
	def getAffectedBy( self ):
		"""Walk the graph upwards and return all input plugs that are being facaded 
		@return: tuple containing plugs that affect us ( plugs affecting our value )"""
		return self._getAffectedList( "up" )
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations """
		return self.iplug.providesOutput( )
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations"""
		return self.iplug.providesInput( )
		
	#}
	
	
#} END plugs 
