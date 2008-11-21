"""B{byronimo.ui.controls}

Contains the most controls like buttons and sliders for more convenient use 

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


import base as uibase
import maya.cmds as cmds
import byronimo.util as util
import byronimo.maya.util as mutil
import util as uiutil


#{ Bases

class LabelBase( uibase.SizedControl ):
	"""Base class for elements having labels"""
	_properties_ = ( "l", "label", "al", "align" , "rs", "recomputeSize" )

class SliderBase( uibase.SizedControl ):
	"""Class contributing Simple Slider Events"""
	_events_ = ( "cc", "changeCommand", "dc", "dragCommand" )
	_properties_ = ( 	"min", "minValue", "max", "maxValue", "v", "value", 
						"s", "step", "hr", "horizontal" )

class BooleanBase( LabelBase ):
	"""Base class for boolean controls"""
	_events_ = ( "onCommand", "offCommand", "changeCommand", "cc", "onc", "ofc" )

class GroupBase( uibase.SizedControl ):
	"""Base allowing access to all grouped controls
	@note: using short property names to ... keep it sane """
	
	_properties_ = [ 	"cw", "columnWidth", 
						"cat", "columnAttach", 
						"rat", "rowAttach",
						"cal", "columnAlign",
						"adj", "adjustableColumn" ]
	
	# setup evil multi attributes 
	for flag in ( 	"cw","columnWidth", "ct", "columnAttach", 
				  	"co", "columnOffset", "cl", "columnAlign", 
					"ad", "adjustableColumn" ):
		start = 1
		if flag in ( "cl", "columnAlign", "ad", "adjustableColumn" ):
			start = 2
			
		for i in range( start, 7 ):
			_properties_.append( flag + str( i ) )
	# END for each flag 
				   	
	
class SliderGroupBase( GroupBase, SliderBase ):
	"""base class for all sliders"""
	pass

class BooleanGroupBase( GroupBase, BooleanBase ):
	"""base class for all boolean groups"""
	_events_ = list()
	
	# setup evil multi attributes 
	for flag in ( 	"on","onCommand", 
				  	"of", "offCommand", 
					"cc", "changeCommand" ):
	
		for i in range( 1, 5 ):
			_events_.append( flag + str( i ) )
	# END for event each flag 
	
	_properties_ = list() 
	
	for flag in ( 	"en","enable", 
				  	"da", "data", 
					"l", "label", 
					"la","labelArray" ):
	
		start = 1
		if flag in ( "la", "labelArray" ):
			start = 2
			
		for i in range( start, 5 ):
			_properties_.append( flag + str( i ) )
	# END for event each flag
	
	
#} END bases



class Button( LabelBase ):
	""" Simple button interface 
	@note: you can only use either the onpress or the onrelease event, both 
	together apparently do not work"""
	_properties_ = ( "actionIsSubstitute" ) 
	
	e_pressed = uiutil.CallbackBaseUI.UIEvent( "command", actOnPress=True )
	e_released = uiutil.CallbackBaseUI.UIEvent( "command", actOnPress=False )
	
	
		
		
	
