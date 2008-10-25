"""B{byronimo.automation.mdepparse}
Contains parser allowing to retrieve dependency information from maya ascii files
and convert it into an easy-to-use networkx graph with convenience methods

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

import byronimo				# assure we have the main module !
from networkx import DiGraph
from networkx.readwrite import gpickle
from byronimo.path import Path
from itertools import chain

import getopt
import sys
import os 
import re

class MayaFileGraph( DiGraph ):
	"""Contains dependnecies between maya files including utility functions 
	allowing to more easily find what you are looking for"""
	refpathregex = re.compile( '.*-r .*"(.*)";' ) 
	
	
	@staticmethod
	def createFromFiles( fileList, **kwargs ):
		"""@return: MayaFileGraph providing dependency information about the files 
		in fileList and their subReference.
		@param fileList: iterable providing the filepaths to be parsed and added 
		to this graph
		@param **kwargs: alll arguemnts of L{addFromFile} are supported """
		graph = MayaFileGraph( )
		
		
		for mayafile in fileList:
			graph.addFromFile( mayafile.strip(), **kwargs )
		# END for each file to parse
		
		
		return graph
		
		
	@staticmethod
	def _parseDepends( mafile, allPaths ):
		"""@return: list of filepath as parsed from the given mafile.
		@param allPaths: if True, the whole file will be parsed, if False, only
		the reference section will be parsed"""
		outdepends = list()
		print "Parsing %s" % mafile
		
		try:
			filehandle = open( os.path.expandvars( mafile ), "r" )
		except IOError,e:
			print "Parsing Failed: %s" % str( e )
			return outdepends
		
		# parse depends 
		for line in filehandle:
			match = MayaFileGraph.refpathregex.match( line )
			
			if not match:
				continue
				
			outdepends.append( match.group(1) )
			
			# see whether we can abort early 
			if not allPaths and line.startswith( "requires" ):
				break
		# END for each line 
		
		filehandle.close()
		return outdepends
	
	def addFromFile( self, mafile, parse_all_paths = False, 
					path_remapping = lambda f: f ):
		"""Parse the dependencies from the given maya ascii file and add them to 
		this graph
		@param parse_all_paths: if True, default False, all paths found in the file will be used.
		This will slow down the parsing as the whole file will be searched for references
		instead of just the header of the file
		@param path_remapping: functor returning a matching MA file for the given 
		MB file ( type Path ) or a valid path from a possibly invalid path.
		This parser can parse references only from MA files, and the path_remapping 
		function should ensure that the given file can be read. It will always 
		be applied 
		@note: if the parsed path contain environment variables you must start the 
		tool such that these can be resolved by the system. Otherwise files might 
		not be found"""
		depfiles = [ mafile ]
		files_parsed = set()					 # assure we do not duplicate work
		while depfiles:
			curfile = path_remapping( depfiles.pop() )
			
			# ASSURE MA FILE 
			if os.path.splitext( curfile )[1] != ".ma":
				print "Skipped non-ma file: %s" % curfile
				continue
			# END assure ma file 
			
			if curfile in files_parsed:
				continue
			
			curfiledepends = self._parseDepends( curfile, parse_all_paths )
			files_parsed.add( curfile )
			
			# create edges
			curfilestr = str( curfile )
			for depfile in curfiledepends:
				self.add_edge( ( curfilestr, depfile ) )
				
			# add to stack and go on 
			depfiles.extend( curfiledepends )
		# END dependency loop
		
		
		
def main( fileList, **kwargs ):
	"""Called if this module is called directly, creating a file containing 
	dependency information
	@param kwargs: will be passed directly to L{createFromFiles}"""
	return MayaFileGraph.createFromFiles( fileList, **kwargs )
	
	
def _usageAndExit( msg = None ):
	print """bpython mdepparse.py [-i] file_to_parse.ma [file_to_parse, ...]
	
-t	Target file used to store the parsed dependency information
	If not given, the command will automatically be in query mode
	
-i	if given, a list of input files will be read from stdin. The tool will start 
	parsing the files as the come through the pipe
	
-a	if given, all paths will be parsed from the input files. This will take longer 
	than just parsing references as the whole file needs to be read
	
-m	map one value in the string to another, i.e:
	-m source=target[=...]
	-m c:\\=/mnt/data/
	sort it with the longest remapping first to assure no accidential matches"""
	if msg:
		print msg
		
	sys.exit( 1 )
	
	
if __name__ == "__main__":
	# parse the arguments as retrieved from the command line !
	try:
		opts, rest = getopt.getopt( sys.argv[1:], "iam:t:", ( "affects", "affected-by" ) )
	except getopt.GetoptError,e:
		_usageAndExit( str( e ) )
		
	
	if not opts and not rest:
		_usageAndExit()
		
	opts = dict( opts )
	fromstdin = "-i" in opts
	if not fromstdin and not rest:
		_usageAndExit( "Please specify the files you wish to parse or query" )
	
	# PREPARE KWARGS 
	#####################
	allpaths = "-a" in opts
	kwargs = dict( ( ( "parse_all_paths", allpaths ), ) )
	
	
	# PATH REMAPPING 
	##################
	# prepare ma to mb conversion
	# by default, we convert from mb to ma hoping there is a corresponding 
	# ma file in the same directory 
	def mb_to_ma( f ):
		path,ext = os.path.splitext( f ) 
		if ext == ".mb":
			return path + ".ma"
		return f
	
	remap_func = mb_to_ma
	if "-m" in opts:
		tokens = opts.get( "-m" ).split( "=" )
		remap_tuples = zip( tokens[0::2], tokens[1::2] )
		
		def path_replace( f ):
			f = mb_to_ma( f )
			for source, dest in remap_tuples:
				f = f.replace( source, dest )
			return f
		remap_func = path_replace
	# END remap func 
	
	kwargs[ 'path_remapping' ] = remap_func
	
	# PREPARE FILELIST 
	###################
	filelist = rest
	if fromstdin:
		filelist = chain( sys.stdin, rest )
	
	
	targetFile = opts.get( "-t", None )
	
	
	# WRITE MODE ? 
	##############
	if targetFile:
		graph = main( filelist, **kwargs )
		
		# save to target file
		print  "Saving dependencies to %s" % targetFile 
		gpickle.write_gpickle( graph, targetFile )
		
	else:
		# QUERY MODE 
		###############
		pass 
	
		
	
	
