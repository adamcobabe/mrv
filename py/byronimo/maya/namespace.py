"""B{byronimo.maya.namespace}

Allows convenient access and handling of namespaces in an object oriented manner
@todo: more documentation

@newfield revision: Revision
@newfield id: SVN Id
"""
                                            
__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

from byronimo.util import iDagItem
import maya.cmds as cmds 

class Namespace( iDagItem ):
	""" Represents a Maya namespace
	Namespaces follow the given nameing conventions:
	   - Paths starting with a column are absolute
	      - :absolute:path
	   - Path separator is ':'
	@note: internally namespaces are always handled as absolute paths """
	
	#{ Overridden Methods
		
	def __init__( self, namespacepath ):
		""" Initialize the namespace with the given namespace path
		@param namespacepath: the namespace to wrap - it should be absolut to assure
		relative namespaces will not be interpreted in an unforseen manner ( as they 
		are relative to the currently set namespace
		@raise ValueError: if the given namespace path does not exist"""
		
		if not namespacepath.startswith( ":" ):
			namespacepath = ":" + namespacepath
			
		if namespacepath.endswith( ":" ):
			namespacepath = namespacepath[:-1]
		
		# TODO: test if the path exists
		self._fullpath = namespacepath
		
		return iDagItem.__init__( self, separator=":" )
	
	def __repr__( self ):
		return self._fullpath
	
	
	def __cmp__( self, other ):
		""" Compare Namespaces for equality """
		if self._fullpath == other._fullpath:
			return 0
		if self._fullpath < other._fullpath:
			return -1 
		if self._fullpath > other._fullpath:
			return 1
		
	#}END Overridden Methods 	
	
	#{Query Methods
	
	def getChildren( self, predicate = lambda x: True ):
		"""@return: list of child namespaces
		@param predicate: return True to include x in result"""
		raise NotImplementedError() 
		
	#} END query methods 
