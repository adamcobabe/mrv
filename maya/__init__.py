# -*- coding: utf-8 -*-
""" Inialize the mrv.maya sub-system and startup maya as completely as possible or configured """
import os, sys                                                                         
from mrv import init_modules
from mrv.util import capitalize, DAGTree
from mrv.exc import MRVError
from mrv.path import Path

from itertools import chain
import logging
log = logging.getLogger("mrv.maya")

# initialize globals
if not hasattr( sys,"_dataTypeIdToTrackingDictMap" ):
	sys._dataTypeIdToTrackingDictMap = dict()			 # DataTypeId : tracking dict


__all__ = ("registerPluginDataTrackingDict", )

############################
#### COMMON   			####
##########################

#{ Common

def registerPluginDataTrackingDict( dataTypeID, trackingDict ):
	"""Using the given dataTypeID and tracking dict, nt.PluginData can return
	self pointers belonging to an MPxPluginData instance as returned by MFnPluginData.
	Call this method to register your PluginData information to the mrv system.
	Afterwards you can extract the self pointer using plug.masData().data()"""
	sys._dataTypeIdToTrackingDictMap[ dataTypeID.id() ] = trackingDict

#} End Common


#{ Internal Utilities
def dag_tree_from_tuple_list( tuplelist ):
	""":return: DagTree from list of tuples [ (level,name),...], where level specifies
	the level of items in the dag.
	:note: there needs to be only one root node which should be first in the list
	:return: `DagTree` item allowing to easily query the hierarchy """
	tree = None
	lastparent = None
	lastchild = None
	lastlevel = 0

	for no,item in enumerate( tuplelist ):
		level, name = item

		if level == 0:
			if tree != None:
				raise MRVError( "Ui tree must currently be rooted - thus there must only be one root node, found another: " + name )
			else:
				tree = DAGTree(  )		# create root
				tree.add_node( name )
				lastparent = name
				lastchild = name
				continue

		direction = level - lastlevel
		if direction > 1:
			raise MRVError( "Can only change by one down the dag, changed by %i in item %s" % ( direction, str( item ) ) )

		lastlevel = level
		if direction == 0:
			pass
		elif direction == 1 :
			lastparent = lastchild
		elif direction == -1:
			lastparent = tree.parent( lastparent )
		elif direction < -1:		# we go many parents back, find the parent at level
			lastparent = list( tree.parent_iter( lastparent ) )[ -level ]

		tree.add_edge( lastparent, name )
		lastchild = name
	# END for each line in hiearchy map

	return tree

def tuple_list_from_file( filepath ):
	"""Create a tuple hierarchy list from the file at the given path
	:return: tuple list suitable for dag_tree_from_tuple_list"""
	lines = Path( filepath ).lines( retain = False )

	hierarchytuples = []
	# PARSE THE FILE INTO A TUPLE LIST
	for no,line in enumerate( lines ):
		item = ( line.count( '\t' ), line.lstrip( '\t' ) )
		hierarchytuples.append( item )

	return hierarchytuples

def initWrappers( mdict, types, metacreatorcls, force_creation = False ):
	""" Create standin classes that will create the actual class once creation is
	requested.
	:param mdict: module dictionary object from which the latter classes will be imported from, 
	can be obtained using ``globals()`` in the module
	:param types: iterable containing the names of classnames ( they will be capitalized
	as classes must begin with a capital letter )"""
	from mrv.maya.util import StandinClass

	# create dummy class that will generate the class once it is first being instatiated
	standin_instances = list()
	for uitype in types:
		clsname = capitalize( uitype )

		# do not overwrite hand-made classes
		if clsname in mdict:
			continue

		standin = StandinClass( clsname, metacreatorcls )
		mdict[ clsname ] = standin

		if force_creation:
			standin_instances.append(standin)
	# END for each uitype
	
	# delay forced creation as there may be hierarchical relations between 
	# the types
	for standin in standin_instances:
		standin.createCls( )


def parse_maya_env( envFilePath ):
	"""
	Parse the key-value pairs out of the maya environment file given in
	envFilePath
	:todo: remove this obsolete method
	:return: dict( "Variable":"Value" )
	"""
	out = dict()

	# parse key-value pairs
	for line in open( envFilePath,'r' ).readlines():
		line = line.strip()
		if line.startswith( "//" ):
			continue

		# assume a key-value pair
		tokens = line.split( '=' )
		if len( tokens ) != 2:
			continue

		out[ tokens[0].strip() ] = tokens[1].strip()

	# end for each line

	# expand the variables
	environ_bak = os.environ
	os.environ = out

	for var,value in out.iteritems():
		out[var] = os.path.expandvars( value )

	os.environ = environ_bak
	return out

def move_vars_to_environ( ):
	"""Move the maya vars as set in the shell into the os.environ to make them available to python"""
	import maya.cmds as cmds
	import subprocess
	envcmd = "env"

	if cmds.about( nt=1 ):
		envcmd = "set"

	p = subprocess.Popen( envcmd, shell=True, stdout=subprocess.PIPE )

	for line in p.stdout:
		try:
			var,value = line.split("=")
		except:
			continue
		else:
			os.environ[ var ] = value.strip()
		# END try to split line
	# END for each line from process' stdout 
#} END internal utilities



############################
#### INITIALIZATION   ####
#########################

#{ Initialization
def init_system( ):
	"""
	Check if we are suited to import the maya namespace and try to set it
	up such we can use the maya standalone package.
	If running within maya or whith maya py, this is true, otherwise we have to
	use the MAYA_LOCATION to get this to work.
	"""
	# RUNNING WITHIN MAYA ? Then we have everything
	# if being launched in mayapy, we need initialization though !
	binBaseName = os.path.split( sys.executable )[1].split( '.' )[0]
	if binBaseName[0:4].lower() == 'maya' and binBaseName[0:6].lower() != 'mayapy':
		return


	# try to setup the paths to maya accordingly
	locvar = 'MAYA_LOCATION'
	if not os.environ.has_key( locvar ):
		raise EnvironmentError( locvar + " was not set - it must point to the maya installation directory" )

	# EXTRACT VERSION INFORMATION IF POSSIBLE
	##########################################
	mayalocation = os.environ[locvar]
	splitpos = -1

	# OS X special case
	if mayalocation.endswith( "Contents" ):
		splitpos = -3

	mayabasename = mayalocation.split( os.sep )[ splitpos ]

	# currently unused
	bits = 32
	if mayabasename.endswith( '64' ):
		bits = 64

	mayabasename = mayabasename.replace( "-x64", "" )	# could be mayaxxxx-x64
	mayaversion = mayabasename[4:]				# could be without version, like "maya"


	# PYTHON COMPATABILITY CHECK
	##############################
	pymayaversion = sys.version_info[0:2]
	if len( mayaversion ):
		pyminor = pymayaversion[1]

		if mayaversion not in [ '8.5', '2008', '2009', '2010' ]:
			raise EnvironmentError( "Requires Maya 8.5 or higher for python support, found " + mayaversion + ", or maya version is not implemented" )

		if  ( mayaversion == "8.5" and pyminor != 4 ) or \
			( mayaversion == "2008" and pyminor != 5 ) or \
			( mayaversion == "2009" and pyminor != 5 ) or \
			( mayaversion == "2010" and pyminor != 6 ):
			raise EnvironmentError( "Maya " + mayaversion + " python interpreter requirements not met" )



	# FINALLY INIALIZE MAYA TO TO MAKE USE OF MAYA STANDALONE
	###########################################################
	if os.name == "nt":
		osspecific = os.path.join("Python", "lib")
	else:
		pyversionstr = str( pymayaversion[0] ) + "." + str( pymayaversion[1] )
		osspecific = os.path.join("lib", "python" + pyversionstr, "site-packages")
		
	mayapylibpath = os.path.join( mayalocation, osspecific, "site-packages" )
	sys.path.append( mayapylibpath )

	# NOTE: Perhaps one should add an LD library path check on linux  - without it the modules will not load

	# DID IT WORK ?
	try:
		import maya
	except Exception, e:
		raise EnvironmentError( "Failed to import maya - check this script or assure LD_LIBRARY path is set accordingly: " + str( e ) )


	# FINALLY STARTUP MAYA
	########################
	# This will also set all default path environment variables and read the
	# maya environment file
	try:
		import maya.standalone
		maya.standalone.initialize()
	except:
		log.error("ERROR: Failed initialize maya")
		raise
	# END handle maya standalone initialization


	# COPY ENV VARS
	###############
	# NOTE: this might have to be redone in your own package dependent on when
	# we are called - might be too early here
	move_vars_to_environ( )

	# RUN USER SETUP
	###################
	# TODO: This should be an option in the configuration !
	# TODO: write the code that runs it once it can be disbled

	# FINISHED
	return

# END INIT SYSTEM


def init_singletons( ):
	""" Initialize singleton classes and attach them direclty to our module"""
	global Scene
	global Mel

	import scene
	Scene = scene.Scene()

	import util
	Mel = util.Mel()


def init_standard_output( ):
	"""Assure that logging can print to stdout and stderr which get overwritten
	by special maya versions which lack the 'flush' method"""
	
	class PassOnOrDummy(object):
		def __init__(self, obj):
			self.obj = obj
		
		def does_nothing(self, *args, **kwargs):
			return
		
		def __getattr__(self, attr):
			try:
				return getattr(self.obj, attr)
			except AttributeError:
				return self.does_nothing
			# END handle object retrieval
	# END utility class
	
	for channame in ('stdout', 'stderr'):
		chan = getattr(sys, channame)
		if hasattr(chan, 'flush'):
			continue
		# END skip channels that would work
		
		# patch the curently established channel
		fixedchan = PassOnOrDummy(chan)
		setattr(sys, channame, fixedchan)
		
		# find all loggers so far and patch up their logging objects
		for l in chain((logging.root, ), logging.root.manager.loggerDict.values()):
			if not isinstance(l, logging.Logger):
				continue
			# END skip placeholders
			for handler in l.handlers:
				if isinstance(handler, logging.StreamHandler) and handler.stream is chan:
					handler.stream = fixedchan
				# END if stream needs fixing
			# END for each handler
		# END for each logger
	# END for each channel
	

#} Initialization

if 'init_done' not in locals():
	init_done = False



if not init_done:
	# assure we do not run several times
	init_system( )
	init_standard_output( )
	init_modules( __file__, "mrv.maya" )
	init_singletons( )


init_done = True