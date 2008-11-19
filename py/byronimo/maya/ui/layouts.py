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



ui = __import__( "byronimo.maya.ui",globals(), locals(), ['ui'] )
import base as uibase
import maya.cmds as cmds
import byronimo.util as util
import byronimo.maya.util as mutil

class Layout( ui.NamedUI ):
	""" Structural base  for all Layouts allowing general queries and name handling
	Layouts may track their children
	"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	def __init__( self, *args, **kwargs ):
		"""  Initialize the layout
		@param name: name of layout, several class instances can exist with the
		same name - it will be adjusted for maya as it requires unique names for each 
		layout. """
		ui.NamedUI.__init__( self, *args, **kwargs )
	
	#{ Layout Hierarchy  
	def getChildren( self ):
		""" @return: children of this layout """
		childnames = mutil.noneToList( cmds.layout( self, q=1, ca=1 ) )
		return uibase.wrapUI( childnames )
		
	def setParentActive( self ):
		"""Set the parent ( layout ) of this layout active - newly created items 
		will be children of the parent layout
		@note: can safely be called several times """
		cmds.setParent( self.getParent( ) )
		
	def setActive( self ):
		"""Set this layout active, such that newly created items will be children 
		of this layout"""
		cmds.setParent( self )
	#} END Layout Hierarchy
	
	
	#{ Properties
	p_children = property( getChildren )			# overwrite super class property
	#} End Properties


class FormLayout( Layout ):
	""" Wrapper class for maya form layout """
	__metaclass__ = ui.MetaClassCreatorUI
	
	class FormConstraint( object ): 
		""" defines the way a child is constrained, possibly to other children """ 
		
	
	def add( layout, **kwargs ):
		""" Add layout as child, kwargs specify the binding of the layout"""
		pass 


class FrameLayout( Layout ):
	"""Simple wrapper for a frame layout"""
	__metaclass__ = ui.MetaClassCreatorUI
	_properties_ = (	"borderVisible", "borderStyle", "collapse", "collapsable",
					   "label", "labelWidth", "labelVisible", "labelAlign", "labelIndent", "labelFont",
					   "marginWidth", "marginHeight" )

	_events_ = ( "collapseCommand", "expandCommand", "preCollapseCommand", "preExpandCommand" )

class ColumnLayout( Layout ):
	"""Wrapper class for a simple column layout"""
	__metaclass__ = ui.MetaClassCreatorUI
	
	_properties_ = ( 	"adjustableColumn", "columnAlign", "columnAttach", "columnOffset", 
						"columnWidth", "rowSpacing" )
	
