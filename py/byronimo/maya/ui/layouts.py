"""B{byronimo.ui.layouts}

Contains the most important mel-layouts wrapped into easy to use python classes
These are specialized and thus more powerful than the default wraps 

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

ui = __import__( "byronimo.maya.ui",globals(), locals(), ['ui'] )



class Layout( ui.NamedUI ):
	""" Structural base  for all Layouts allowing general queries and name handling """
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __init__( self, *args, **kvargs ):
		""" 
		Initialize the layout
		@param name: name of layout, several class instances can exist with the
		same name - it will be adjusted for maya as it requires unique names for each 
		layout. """
		ui.NamedUI.__init__( self, *args, **kvargs )
	
	def getChildren( self ):
		""" @return: children of this layout """
		# return a copy - assure no one tries to alter this array
		return self._children[:]
		

	def getParent( self ):
		""" @return: parent of this instance or None """
		raise NotImplementedError()

	
	def add( layout ):
		""" Add layout class as child to this layout """
		self._children.append( layout )
	
	
	#{ Properties
	children = property( getChildren )
	#} End Properties
	
	
	
class FormLayout( Layout ):
	""" Wrapper class for maya form layout """
	__metaclass__ = ui.MetaClassCreatorUI
	
	class FormConstraint( object ): 
		""" defines the way a child is constrained, possibly to other children """ 
		
	
	def add( layout, **kvargs ):
		""" Add layout as child, kvargs specify the binding of the layout"""
		pass 

