# -*- coding: utf-8 -*-
"""
Contains the most important mel-layouts wrapped into easy to use python classes
These are specialized and thus more powerful than the default wraps

@todo: more documentation



"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import base as uibase
import maya.cmds as cmds
import mayarv.util as util
import mayarv.maya.util as mutil
import util as uiutil


class Layout( uibase.SizedControl, uiutil.UIContainerBase ):
	""" Structural base  for all Layouts allowing general queries and name handling
	Layouts may track their children
	"""
	_properties_ = ( "nch", "numberOfChildren" )

	def __init__( self, *args, **kwargs ):
		"""  Initialize the layout
		@param name: name of layout, several class instances can exist with the
		same name - it will be adjusted for maya as it requires unique names for each
		layout. """
		super( Layout, self ).__init__( *args, **kwargs )

	def __getitem__( self, key ):
		"""Implemented by L{UIContainerBase}"""
		return uiutil.UIContainerBase.__getitem__( self, key )

	#{ Layout Hierarchy

	def getChildren( self ):
		""" @return: children of this layout """
		childnames = mutil.noneToList( cmds.layout( self, q=1, ca=1 ) )
		# assure we have long names to ensure uniqueness
		return uibase.wrapUI( [ "%s|%s" % ( self, c ) for c in childnames ] )

	def setParentActive( self ):
		"""Set the parent ( layout ) of this layout active - newly created items
		will be children of the parent layout
		@note: can safely be called several times """
		cmds.setParent( self.getParent( ) )

	#} END Layout Hierarchy


	#{ Properties
	p_children = property( getChildren )			# overwrite super class property
	p_ca = p_children
	p_childArray = p_children
	#} End Properties


class FormLayout( Layout ):
	""" Wrapper class for maya form layout """
	# tuple with side strings - to quickly define your attachments, assign it to letters
	# like : t,b,l,r = kSides
	# and use the letters accordingly to save space and make the layout easier to read
	kSides = ( "top", "bottom", "left", "right" )

	class FormConstraint( object ):
		""" defines the way a child is constrained, possibly to other children
		@todo: proper constraint system, but could be complicated to make it really easy to use"""

	def setup( self, **kwargs ):
		"""Apply the given setup to the form layout, specified using kwargs
		@param **kwargs: arguments you would set use to setup the form layout"""
		self.__melcmd__( self, e=1, **kwargs )


class FrameLayout( Layout ):
	"""Simple wrapper for a frame layout"""
	_properties_ = (	"bw", "borderVisible",
					   	"bs",  "borderStyle",
						"cl", "collapse",
						"cll", "collapsable",
						"l", "label",
						"lw", "labelWidth",
						"lv", "labelVisible",
						"la", "labelAlign",
						"li", "labelIndent",
						"fn", "font",
						"mw", "marginWidth",
						"mh", "marginHeight" )

	_events_ = ( 	"cc", "collapseCommand",
					"ec", "expandCommand",
					"pcc", "preCollapseCommand",
					"pec", "preExpandCommand" )


class RowLayout( Layout ):
	"""Wrapper for row column layout"""
	_properties_ = [ 	"columnWidth", "cw",
						"columnAttach", "cat",
						"rowAttach", "rat",
					  	"columnAlign", "cal",
						"adjustableColumn", "adj",
					  	"numberOfColumns", "nc" ]

	for flag in ( 	"columnWidth", "cw", "columnAttach", "ct", "columnOffset",
				  	"co", "columnAlign", "cl", "adjustableColumn", "ad" ):
		for i in range( 1, 7 ):
			_properties_.append( flag + str( i ) )


class ColumnLayoutBase( Layout ):
	_properties_ = (   	"columnAlign", "cal",
						"columnAttach", "cat",
						"columnOffset", "co" ,
						"columnWidth", "cw",
						"rowSpacing", "rs" )

class RowColumnLayout( ColumnLayoutBase ):
	"""Wrapper for row column layout"""
	_properties_ = ( 	"numberOfColumns", "nc",
					  	"numberOfRows", "nr",
						"rowHeight", "rh",
						"rowOffset", "ro",
					  	"rowSpacing", "rs" )


class ColumnLayout( ColumnLayoutBase ):
	"""Wrapper class for a simple column layout"""

	_properties_ = ( 	"adjustableColumn", "adj" )

class ScrollLayout( Layout ):
	"""Wrapper for a scroll layout"""
	_properties_ = ( 	"scrollAreaWIdth", "saw",
					  	"scrollAreaHeight", "sah",
						"scrollAreaValue", "sav",
						"minChildWidth", "mcw",
						"scrollPage", "sp",
						"scrollByPixel", "sbp"	)

	_event_ = ( "resizeCommand", "rc" )

