"""B{byronimo.maya}

Inialize the byronimo.maya sub-system and assure and startup maya natively

@todo: more documentation
@todo: logger !
@todo: configuration support 

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2008 Sebastian Thiel'


import os, sys


def parse_maya_env( envFilePath ):
	"""
	Parse the key-value pairs out of the maya environment file given in 
	envFilePath
	@todo: remove this obsolete method
	@return: dict( "Variable":"Value" )
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

def moveVarsToEnviron( ):
	"""Move the maya vars as set in the shell into the os.environ to make them available to python"""
	import maya.cmds as cmds
	from popen2 import popen2
	envcmd = "env"
	
	if cmds.about( nt=1 ):
		envcmd = "set"
	
	stdout,stdin = popen2( envcmd )
	
	for line in stdout:
		try: 
			var,value = line.split("=")
		except:
			continue
		else:
			os.environ[ var ] = value.strip()



def init_system( ):
	""" 
	Check if we are stuited to import the maya namespace and try to set it 
	up such we can use the maya standalone package.
	If running within maya or whith maya py, this is true, otherwise we have to 
	use the MAYA_LOCATION to get this to work.
	"""
	# RUNNING WITHIN MAYA ? Then we have everything
	binBaseName = os.path.split( sys.executable )[1].split( '.' )[0]
	if binBaseName[0:4].lower() == 'maya':
		return 
	
	
	# try to setup the paths to maya accordingly 
	locvar = 'MAYA_LOCATION'
	if not os.environ.has_key( locvar ):
		raise EnvironmentError( locvar + " was not set - it must point to the maya installation directory" )
		
	# EXTRACT VERSION INFORMATION IF POSSIBLE
	##########################################
	mayalocation = os.environ[locvar]
	mayabasename = os.path.split( mayalocation )[-1]
	
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
		
		if mayaversion not in [ '8.5', '2008','2009' ]:
			raise EnvironmentError( "Requires Maya 8.5 or higher for python support, found " + mayaversion + ", or maya version is not implemented" )
		
		if  ( mayaversion == "8.5" and pyminor != 4 ) or \
			( mayaversion == "2008" and pyminor != 5 ) or \
			( mayaversion == "2009" and pyminor != 6 ): 
			raise EnvironmentError( "Maya " + mayaversion + " python interpreter requirements not met" )
		
		
	
	# FINALLY INIALIZE MAYA TO TO MAKE USE OF MAYA STANDALONE
	###########################################################
	pyversionstr = str( pymayaversion[0] ) + "." + str( pymayaversion[1] )
	mayapylibpath = os.path.join( mayalocation, "lib/python" + pyversionstr + "/site-packages" )
	sys.path.append( mayapylibpath )
	
	# NOTE: Perhaps one should add an LD library path check on linux  - without it the modules will not load
	
	# DID IT WORK ? 
	try: 
		import maya
	except: 
		raise EnvironmentError( "Failed to import maya - check this script or assure LD_LIBRARY path is set accordingly" )
	
	
	# FINALLY STARTUP MAYA
	########################
	# This will also set all default path environment variables and read the 
	# maya environment file
	try:
		import maya.standalone
		maya.standalone.initialize()
	except:
		print "ERROR: Failed initialize maya"
		raise 
	
		
	# COPY ENV VARS 
	###############
	# NOTE: this might have to be redone in your own package dependent on when 
	# we are called - might be too early here 
	moveVarsToEnviron( )
		
	# RUN USER SETUP
	###################
	# TODO: This should be an option in the configuration !
	# TODO: white the code that runs it once it can be disbled
	
	# FINISHED
	return 
	
	
# END INIT SYSTEM


def init_singletons( ):
	""" Initialize singleton classes and attach them direclty to our module """
	global Scene
	global Mel
	
	module = __import__( "byronimo.maya.scene" , globals(), locals(), [ "scene" ] )
	Scene = module.Scene()
	
	module = __import__( "byronimo.maya.util" , globals(), locals(), [ "util" ] )
	Mel = module.Mel()
	


if 'init_done' not in locals():
	init_done = False
	


if not init_done:
	# assure we do not run several times
	init_system( )
	init_singletons( )
	

init_done = True