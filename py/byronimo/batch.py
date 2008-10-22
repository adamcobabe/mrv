"""B{byronimo.batch}
This modules contains utilities to do opeations in batch mode.
The module can be used from within python if required, but is more commonly used 
from the commandline, possibly wrapped by a shell script to specialize its usae

@newfield revision: Revision
@newfield id: SVN Id
"""
import sys
from collections import deque

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: configuration.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


def process( cmd, args, inputList, errorstream = None, donestream = None, inputsPerProcess = 1 ):
	"""Launch process at cmd with args and a list of input objects from inputList appended to args
	@param cmd: full path to tool you wish to start, like /bin/bash
	@param args: List of all argument strings to be passed to cmd
	@param inputList: list of input files to be passed as input to cmd
	@param errorstream: stream to which errors will be written to as they occour if not None
	@param donestream: stream to which items from input list will be passed once they 
	have been processed if not None. Items are newline terminated 
	@param inputsPerProcess: pass the given number of inputs to the cmd, or less if there 
	are not enough items on the input list
	""" 
	pass 



#{ Command Line Tool 

def _usageAndExit( msg = None ):
	"""Print usage"""
	print """python ../byronimo/batch.py inputarg [inputarg ...] [-E fileForErrors|-] [-D fileForFinishedOutput|-] [-s numInputsPerProcess] -e cmd [cmdArg ...] 
-E|D - 	means to use the default stream, either stderr or stdout
-e 	ends the parsing of commandline arguments for the batch process tool 
	and uses the rest of the commandline as direct input for your command
-s	defines how many input arguments will be passed per command invocation"""
	if msg:
		print msg
		
	sys.exit( 1 )
	

def _toStream( arg, stream ):
	"""@return: stream according to arg
	@param stream: stream to return if arg sais so """
	if arg == "-":
		return stream
	# stream handling 
	
	# arg should be a file
	try:
		return open( arg, "w" )
	except IOError:
		_usageAndExit( "Stream at %s could not be opened for writing" % arg )
		

def _popleftchecked( argv, errmsg ):
	"""pop an arg from argv and return with an error message on error"""
	try:
		return argv.popleft()
	except IndexError:
		_usageAndExit( errmsg )

if __name__ == "__main__":
	inputList = list()
	streams = list( ( None, None ) )
	
	inputsPerProcess = 1
	cmd = None
	cmdargs = list()
	
	
	# PARSE ARGUMENTS
	##################
	argv = deque( sys.argv[1:] )
	while argv:
		arg = argv.popleft()
		
		# COMAMND TO EXECUTE 
		#####################
		if arg == "-e":
			cmd = _popleftchecked( argv, "-e must be followed by the command to execute" )
			
			# get cmd args 
			for rarg in argv:
				cmdargs.append( rarg )
				
			# done processing 
			break 
		# END -e 
		
		# STREAMS 
		############
		flagfound = False 
		for i,(flag,stream) in enumerate( ( ( "-E",sys.stderr ), ( "-D", sys.stdout ) ) ): 
			if arg == flag:
				argval = _popleftchecked( argv, "%s must be followed by - or a filepath" % flag )
				streams[ i ] = _toStream( argval, stream )
				flagfound = True
				break
			# END if arg matches
		# END for each stream arg
		
		if flagfound: continue 	
		
		if arg == "-s":
			msg = "-s must be followed by a number > 0"
			inputsPerProcess = int( _popleftchecked( argv, msg ) )
			flagfound = True
			if inputsPerProcess < 1:
				_usageAndExit( msg )
		# END -s
		
		if flagfound: continue
		
		# its an input argument 
		inputList.append( arg )
		
	# END for each argument 
	
	
	if not cmd:
		_usageAndExit( "No command to execute - add it after the -e flag" )
	
	
	# have everything, transfer control to the actual batch method
	process( cmd, cmdargs, inputList, streams[0], streams[1], inputsPerProcess )
	

#} END command line tool 
