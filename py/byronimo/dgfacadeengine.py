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
		def unfacadeMethod( self, *args, **kwargs ):
			"""Wrap the actual call by obtaininng a possibly special shell, and making 
			the call there """
			return getattr( self._getInputShell( ), funcname )( *args, **kwargs )
		return unfacadeMethod
	
	@classmethod
	def createFacadeMethod( cls, funcname ):
		"""Call the main shell's function"""
		def facadeMethod( self, *args, **kwargs ):
			return getattr( self.origshellcls( self.node, self.plug ), funcname )( *args, **kwargs )
		return facadeMethod
		

class _OIShell( _PlugShell ):
	"""All connections from and to the FacadeNode must actually start and end there.
	Iteration over internal plugShells is not allowed.
	Thus we override only the methods that matter and assure that the call is handed 
	to the acutal internal plugshell.
	We know everything we require as we have been fed with an IOShell
	"""
	# list all methods that should not be a facade to our facade node 
	__unfacade__ = [ 'get', 'set', 'hasCache', 'setCache', 'getCache', 'clearCache' ]
	__facade__ = [ 'connect', 'disconnect', 'getInput', 'getOutputs', 'iterShells' ]
	__metaclass__ = _OIShellMeta
	
	def __init__( self, *args ):
		"""Sanity checking"""
		if not isinstance( args[1], IOFacadePlug ):
			raise AssertionError( "Invalid PlugType: Need %r, got %r" % ( IOFacadePlug, args[1].__class__ ) )
			
		super( _OIShell, self ).__init__( *args )
	
	
	def __repr__ ( self ):
		"""Cut away our name in the possible ioplug ( printing an unnecessary long name then )"""
		plugname = str( self.plug )
		nodename = str( self.node )
		plugname = plugname.replace( nodename+'.', "" )
		return "%s.%s" % ( nodename, plugname )
	
	def _toIShell( self ):
		"""@return: convert ourselves to the real shell actually behind this facade plug"""
		return self.plug.inode.toShell( self.plug )
		
		
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
				print "STORED IO PLUG to: %s " % str( myargs[1] )
				self.ioplug = myargs[1]
				myargs[1] = self.ioplug.iplug		# this is the internal plug on the internal node 
			# END ioplug checking
			else:
				print "myargs[0:2]: %s, %s" % (myargs[0], myargs[1] )
			
			super( _IOShell, self ).__init__( *myargs )
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
		for plug in self.getPlugs( ):
			if plug.getName() == attr:
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
		yourResult = self._getNodePlugs( )
		
		# check args - currently only predicate is supported
		predicate = kwargs.pop( 'predicate', lambda x: True )
		if kwargs:		# still args that we do not know ?
			raise AssertionError( "Unhandled arguments found  - update this method: %s" % kwargs.keys() )
		
		def toFacadePlug( node, plug ):
			if isinstance( plug, IOFacadePlug ):
				return plug
			return IOFacadePlug( node, plug )
		# END to facade plug helper
		
		print "START PROCESSING" * 8
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
				orignode.shellcls = _IOShell( self, classShellCls )
				# END for each shell to reconnect 
			# END if we have to swap in our facadeIOShell
			
			# WRAP VIRTUAL PLUG to the node 
			################################
			
			# have to set it as shell 
			origplugname = ioplug.iplug.getName()
			# print orignode.__dict__[ origplugname ]
			if isinstance( getattr( orignode, origplugname ), IOFacadePlug ):
				print "PLUG %s on %s was FACADED ALREADY" % ( origplugname, orignode )
				continue
			# END if plug already set ( as shell )
			
			print "FACADING PLUG: %s on %s " % ( ioplug.iplug.getName(), orignode )
			facadeshell = orignode.toShell( ioplug.iplug )
			setattr( orignode, origplugname, ioplug )
			
			
			
			
			# UPDATE CONNECTIONS ( per plug, not per node )
			######################
			# update all connections with the new shells - they are required when 
			# walking the affects tree, as existing ones will be taken instead of
			# our new shell then.
			all_shell_cons = facadeshell.getConnections( 1, 1 )	 # now we get old shells
			
			# disconnect and reconnect with new
			for sshell,eshell in all_shell_cons:
				print "UPDATING CONNECTION: %r -> %r" % (sshell,eshell)
				if isinstance( sshell, _IOShell ) and isinstance( eshell, _IOShell ):
					continue			# never operate twice on one connection 
					
				sshell.disconnect( eshell )
				newstartshell = getattr( sshell.node, sshell.plug.getName() ) # this already creates a shell
				newendshell = getattr( eshell.node, eshell.plug.getName() )	
				print "NEW START SHELL = %s(%s)" % ( repr( newstartshell ), type( newstartshell ) )
				print "NEW END SHELL = %s(%s)" % ( repr( newendshell ), type( newendshell ) )
				newstartshell.connect( newendshell )
			# END for each edge to update 
		# END for each item in result 
		
		print "END PROCESSING" * 8
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
		
		Besides, this plug is at the position of an instance attribute, but is supposed
		to act like the plug descriptor that it hides on class level. The class descriptor 
		returns a shell.
		Thus we must:
			- Act as IOFacade returning additional information
			- Act as original plug for attribute access
			- Act as shell of our node
		This will work as long as the method names are unique 
		"""
		if attr == 'inode':
			return self[0]()
		if attr == 'iplug':
			return self[1]()
		
		# still here ? try to return a value on the original plug
		try:
			return getattr( self.iplug, attr )
		except AttributeError:
			return getattr( self.inode.toShell( self.iplug ), attr )
		
	#} END object overridden methods
	
	
	#{ iPlug Interface 
	
	def getName( self ):
		"""@return: name of (internal) plug - must be a unique key, unique enough
		to allow connections to several nodes of the same type"""
		return "FP(%s.%s)" % ( self.inode, self.iplug )
		
	
	def _getAffectedList( self, direction, pruneshellfunc ):
		"""@return: list of all ioplugs looking in direction, if 
		plugtestfunc returns 1 for the plug in the shell being walked"""
		these = lambda shell: shell is self or not isinstance( shell, _IOShell ) or shell.ioplug is None or pruneshellfunc( shell )
		iterShells = self.inode.toShell( self.iplug ).iterShells( direction=direction, prune = these )
		outlist = [ shell.ioplug for shell in iterShells ]
		
		#print "AFFECTED LIST: %s on %s" % ( direction, self )
		#print outlist
		# print "ITERSHELL LIST %s " % direction
		# #print getattr( list( self.inode.toShell( self.iplug ).iterShells( direction=direction ) )[-1].node, 'shellcls' )
		# print list( self.inode.toShell( self.iplug ).iterShells( direction=direction ) )[-1]
		# for o in outlist: print o
		# print "DONE WITH OUTLIST"
		# print "DONE"
		return outlist
	
	def affects( self, otherplug ):
		"""Affects relationships will be set on the original plug only"""
		return self.iplug.affects( otherplug )
		
	def getAffected( self ):
		"""Walk the internal affects using an internal plugshell
		@note: only output plugs can be affected - this is a rule followed throughout the system
		@return: tuple containing affected plugs ( plugs that are affected by our value )"""
		return self._getAffectedList( "down",  lambda shell: not shell.plug.providesOutput() )
		
	def getAffectedBy( self ):
		"""Walk the graph upwards and return all input plugs that are being facaded 
		@return: tuple containing plugs that affect us ( plugs affecting our value )"""
		return self._getAffectedList( "up",  lambda shell: not shell.plug.providesInput() )
		
	def providesOutput( self ):
		"""@return: True if this is an output plug that can trigger computations
		@note: this should be the same implementation as the one of the wrapped plug - unfortunately
		that is not fully possible, lets just hope that the logic does not change 
		@todo: revise """
		return bool( len( self.getAffectedBy() ) != 0 or self.attr.flags & Attribute.computable )
		
	def providesInput( self ):
		"""@return: True if this is an input plug that will never cause computations
		@note: this should actually be the same implementation as the one of the wrapped 
		plug - but we are incompatible class wise - update this once the base changes !
		@todo: revise """
		return not self.providesOutput( )
		
	#}
	
	
#} END plugs 
