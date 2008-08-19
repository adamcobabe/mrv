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


############################
#### Methods 		  	####
##########################

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

############################
#### Classes 		  	####
##########################

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
		self.callableobj( )
		

class iDagItem( object ):
	""" Describes interface for a DAG item.
	Its used to unify interfaces allowing to access objects in a dag like graph
	Of the underlying object has a string representation, the defatult implementation 
	will work natively.
	
	Otherwise the getParent and getChildren methods should be overwritten
	@note: all methods of this class are abstract and need to be overwritten
	@note: this class expects the attribute '_sep' to exist containing the 
	separator at which your object should be split ( for default implementations ).
	This works as the passed in pointer will belong to derived classes that can 
	define that attribute on instance or on class level"""
	
	kOrder_DepthFirst, kOrder_BreadthFirst = range(2)
	
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
		out = []
		curpath = self
		while True:
			parent = curpath.getParent( )
			if not parent:
				break
			
			out.append( parent )
			curpath = parent
		# END while true
		
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
		
	#} END Query Methods

	#{ Name Generation
	def getFullChildName( self, childname ):
		"""Add the given name to the string version of our instance
		@return: string with childname added like name _sep childname"""
		sname = str( self )
		if not sname.endswith( self._sep ):
			sname += self._sep
		if childname.startswith( self._sep ):
			childname = childname[1:]
			
		return sname + childname		
	
	#} END name generation

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
		"""args must contain the filter methods to be AND'ed"""
		self.functions = args
		
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
