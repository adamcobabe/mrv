"""B{byronimo.ui.layouts}

Contains the most important mel-layouts wrapped into easy to use python classes

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



#{ Exceptions
################################################################################


#} End Exceptions






class _Layout( object ):
	""" Structural base  for all Layouts allowing general queries and name handling """
	
	def __init__( self, name=None ):
		""" 
		Initialize the layout
		@param name: name of layout, several class instances can exist with the
		same name - it will be adjusted for maya as it requires unique names for each 
		layout.
		"""
		self._children = []
		pass 
	
	def _get_children( self ):
		""" @return: children of this layout """
		# return a copy - assure no one tries to alter this array
		return self._children[:]
		

	def _get_parent( self ):
		""" @return: parent of this instance or None """
		raise NotImplementedError()

	@typecheck_param( _Layout )
	def add( layout ):
		""" Add layout class as child to this layout """
		self._children.append( layout )
	
	
	#{ Properties
	children = property( _get_children )
	#} End Properties
	
	
	
class FormLayout( _Layout ):
	""" Wrapper class for maya form layout """
	
	class FormConstraint( object ): 
		""" defines the way a child is constrained, possibly to other children """ 
		
	
	def add( layout, **kvargs ):
		""" Add layout as child, kvargs specify the binding of the layout"""
		pass 
