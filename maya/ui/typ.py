# -*- coding: utf-8 -*-
"""
Module containing helpers to create the UI types at runtime.
@todo: more documentation
"""


import mayarv.maya as bmaya
from mayarv.util import capitalize, uncapitalize
import mayarv.maya.util as mutil
from mayarv.path import Path
_thismodule = __import__( "mayarv.maya.ui", globals(), locals(), ['ui'] )
import maya.cmds as mcmds
from util import CallbackBaseUI, propertyQE



############################
#### CACHES		 	   ####
#########################
_typetree = None
_typemap = { "floatingWindow" : "window" }


############################
#### INITIALIZATION   ####
#########################


def init_classhierarchy( ):
	""" Read a simple hiearchy file and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent / "cache/UICommandsHierachy"

	# STORE THE TYPE TREE
	global _typetree
	_typetree = bmaya._dagTreeFromTupleList( bmaya._tupleListFromFile( mfile ) )


def init_wrappers( ):
	""" Create Standin Classes that will delay the creation of the actual class till
	the first instance is requested"""
	global _typetree
	global _thismodule
	bmaya._initWrappers( _thismodule, _typetree.nodes_iter(), MetaClassCreatorUI )


#####################
#### META 		####
##################

class MetaClassCreatorUI( mutil.MetaClassCreator ):
	""" Builds the base hierarchy for the given classname based on our
	typetree
	Additional support for :
	* AUTOMATIC PROPERTY GENERATION *
	  - if flags are simple get and set properties, these can be listed in the
	    _properties_ attribute ( list ). These must be queriable and editable
	  - Properties will be available as:
	  	inst.p_myProperty to access myProperty ( equivalent to cmd -q|e -myProperty
	  - This only works if our class knows it's mel command in the __melcmd__ member
		variable - inheritance for it does not work

	* AUTOMATIC UI-EVENT GENERATION *
	  - define names of mel events in _events_ as list of names
	  - these will be converted into _UIEvents sitting at attribute names like
	  	e_eventName ( for even called 'eventName'
	  - assign an event:
	    windowinstance.e_restoreCommand = func
		whereas func takes: func( windowinstance, *args, **kwargs )

	* ADDITIONAL CONFIGURAITON *
		- strong_event_handlers
		 	- if True, defeault class default, events will use strong references to their handlers
	  """

	melcmd_attrname = '__melcmd__'


	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global _typetree
		global _thismodule

		# HANDLE MEL COMMAND
		#######################
		cmdname = uncapitalize( name )
		if hasattr( mcmds, cmdname ):
			melcmd = getattr( mcmds, cmdname )
			clsmelcmd = staticmethod( melcmd )
			clsdict['__melcmd__'] = clsmelcmd
		else:
			pass # don't bother, can be one of our own classes that will
			#raise ValueError( "Did not find command for " + cmdname )

		# HANDLE PROPERTIES
		####################
		# read the properties attribute to find names to automatically create
		# query and edit properties
		propertynames = clsdict.get( "_properties_", list() )
		for pname in propertynames:
			attrname = "p_%s" % pname
			# allow user overrides
			if attrname not in clsdict:
				clsdict[ attrname ] = propertyQE( pname )
		# END for each property

		# HANDLE EVENTS
		##################
		# read the event description and create _UIEvent instances that will
		# register themselves on first use, allowing multiple listeners per maya event
		eventnames = clsdict.get( "_events_", list() )
		event_kwargs = dict()
		if clsdict.get( "strong_event_handlers", False ):
			event_kwargs[ "weak" ] = False

		for ename in eventnames:
			attrname = "e_%s" % ename
			# allow user overrides
			if attrname not in clsdict:
				clsdict[ attrname ] = CallbackBaseUI._UIEvent( ename, **event_kwargs )
		# END for each event name

		newcls = super( MetaClassCreatorUI, metacls ).__new__( _typetree, _thismodule,
																metacls, name, bases, clsdict )

		# print newcls.mro()
		return newcls


