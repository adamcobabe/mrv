# -*- coding: utf-8 -*-
"""Contains all processes """
from mayarv.automation.process import ProcessBase
import mayarv.util as util

#} Interface

def parseProcessesFromPackage( importBase, packageFile ):
	"""Parse all processes from the given package's sub-modules and add them to main
	processes module to make them available to the workflow system
	@param importBase: Something like: parentPackage.subpackage.mypackage, of your processes package
	@param packageFile: the pointing to your processes package, usually __file__ of your package
	"""
	isProcess = lambda cls: hasattr( cls, 'mro' ) and ProcessBase in cls.mro()
	processes = util.getPackageClasses( importBase, packageFile, predicate = isProcess )

	gd = globals()
	for pcls in processes:
		gd[pcls.__name__] = pcls
	# END for each process



def addProcesses( *args ):
	"""Add the given process classes to the list of known process types. They will be regeistered
	with their name obtained by str( processCls ).
	Workflows loaded from files will have access to the processes in this package
	@param *args: process classes to be registered to this module."""
	gd = globals();
	for pcls in args:
		if ProcessBase not in pcls.mro():
			raise TypeError( "%r does not support the process interface" % pcls )

		gd[pcls.__name__] = pcls
	# END for each arg

#} END interface

# assure we only do certain things once
if 'init_done' not in locals():
	init_done = False

# SYSTEM INITIALIZATION
if not init_done:
	pass
	# import everything into the processes module
	# currently there is nothing
	# from base import *
#} END initialization





