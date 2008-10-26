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
from networkx import DiGraph, NetworkXError
from networkx.readwrite import gpickle
from byronimo.util import iterNetworkxGraph
from itertools import chain

import getopt
import sys
import os 
import re

class MayaFileGraph( DiGraph ):
	"""Contains dependnecies between maya files including utility functions 
	allowing to more easily find what you are looking for"""
	
	refpathregex = re.compile( '.*-r .*"(.*)";' )
	kAffects,kAffectedBy = range( 2 )
	invalidNodeID = "__invalid__"
	invalidPrefix = ":_iv_:"
	
	#{ Edit 
	@staticmethod
	def createFromFiles( fileList, **kwargs ):
		"""@return: MayaFileGraph providing dependency information about the files 
		in fileList and their subReference.
		@param fileList: iterable providing the filepaths to be parsed and added 
		to this graph
		@param **kwargs: alll arguemnts of L{addFromFiles} are supported """
		graph = MayaFileGraph( )
		graph.addFromFiles( fileList, **kwargs )
		return graph
		
		
	def _parseDepends( self, mafile, allPaths ):
		"""@return: list of filepath as parsed from the given mafile.
		@param allPaths: if True, the whole file will be parsed, if False, only
		the reference section will be parsed"""
		outdepends = list()
		print "Parsing %s ( all paths = %i )" % ( mafile, allPaths )
		
		try:
			filehandle = open( os.path.expandvars( mafile ), "r" )
		except IOError,e:
			# store as invalid 
			self.add_edge( ( self.invalidNodeID, self.invalidPrefix + str( mafile ) ) )
			sys.stderr.write( "Parsing Failed: %s\n" % str( e ) )
			return outdepends
		
		# parse depends 
		for line in filehandle:
			
			# take the stupid newlines into account !
			line = line.strip()
			if not line.endswith( ";" ):
				try:
					line = line + filehandle.next()
				except StopIteration:
					break
			# END newline special handling 
			
			match = MayaFileGraph.refpathregex.match( line )
			
			if match:
				outdepends.append( match.group(1) )
			
			# see whether we can abort early
			if not allPaths and line.startswith( "requires" ):
				break
		# END for each line 
		
		filehandle.close()
		return outdepends
	
	def addFromFiles( self, mafiles, parse_all_paths = False, 
					path_remapping = lambda f: f, ignorelist=None ):
		"""Parse the dependencies from the given maya ascii files and add them to 
		this graph
		@note: the more files are given, the more efficient the method can be
		@param parse_all_paths: if True, default False, all paths found in the file will be used.
		This will slow down the parsing as the whole file will be searched for references
		instead of just the header of the file
		@param path_remapping: functor returning a matching MA file for the given 
		MB file ( type Path ) or a valid path from a possibly invalid path.
		This parser can parse references only from MA files, and the path_remapping 
		function should ensure that the given file can be read. It will always 
		be applied 
		@param ignorelist: global ignore list that can be passed in to allow us 
		to skip files that have already been proecss
		@note: if the parsed path contain environment variables you must start the 
		tool such that these can be resolved by the system. Otherwise files might 
		not be found
		@todo: parse_all_paths still to be implemented"""
		files_parsed = set()					 # assure we do not duplicate work
		for mafile in mafiles:
			depfiles = [ mafile.strip() ]
			while depfiles:
				curfile = path_remapping( depfiles.pop() )
				
				# ASSURE MA FILE 
				if os.path.splitext( curfile )[1] != ".ma":
					sys.stderr.write( "Skipped non-ma file: %s\n" % curfile )
					continue
				# END assure ma file 
				
				if curfile in files_parsed:
					continue
				
				curfiledepends = self._parseDepends( curfile, parse_all_paths )
				files_parsed.add( curfile )
				
				# create edges
				curfilestr = str( curfile )
				for depfile in curfiledepends:
					self.add_edge( ( path_remapping( depfile ), curfilestr ) )
					
				# add to stack and go on 
				depfiles.extend( curfiledepends )
			# END dependency loop
		# END for each file to parse 
		
		#} END edit 
		
	#{ Query 
	def getDepends( self, filePath, direction = kAffects, **kwargs ):
		"""@return: list of paths that are related to the given filePath
		@param direction: specifies search direction, either :
		kAffects = Files that filePath affects
		kAffectedBy = Files that affect filePath
		@param **kwargs: correspon to L{iterNetworkxGraph}"""
		kwargs[ 'direction' ] = direction
		kwargs[ 'ignore_startitem' ] = 1			# default
		kwargs[ 'branch_first' ] = 1		# default 	
		try:
			return list( iterNetworkxGraph( self, filePath, **kwargs ) )
		except NetworkXError:
			sys.stderr.write( "Path %s unknown to dependency graph\n" % filePath )
		return list()
	
	def getInvalid( self ):
		"""@return: list of filePaths that could not be parsed, most probably 
		because they could not be found by the system"""
		lenp = len( self.invalidPrefix  )
		return [ iv[ lenp : ] for iv in self.successors( self.invalidNodeID ) ]
	#} END query 
		
		
def main( fileList, **kwargs ):
	"""Called if this module is called directly, creating a file containing 
	dependency information
	@param kwargs: will be passed directly to L{createFromFiles}"""
	return MayaFileGraph.createFromFiles( fileList, **kwargs )
	
	
def _usageAndExit( msg = None ):
	print """bpython mdepparse.py [-i] file_to_parse.ma [file_to_parse, ...]
	
-t	Target file used to store the parsed dependency information
	If not given, the command will automatically be in query mode.
	The file format is simply a pickle of the underlying Networkx graph
	
-s	Source dependency file previously written with -t. If specified, this file 
	will be read to quickly be read for queries. If not given, the information
	will be parsed first. Thus it is recommended to have a first run storing 
	the dependencies and do all queries just reading in the dependencies using 
	-s 
	
-i	if given, a list of input files will be read from stdin. The tool will start 
	parsing the files as the come through the pipe
	
-a	if given, all paths will be parsed from the input files. This will take longer 
	than just parsing references as the whole file needs to be read
	TODO: actual implementation
	
-m	map one value in the string to another, i.e:
	-m source=target[=...]
	-m c:\\=/mnt/data/
	sort it with the longest remapping first to assure no accidential matches

QUERY
-----
All values returned in query mode will be new-line separated file paths 
--affects 		retrieve all files that are affected by the input files
--affected-by 	retrieve all files that are affect the input files

-l				if set, only leaf paths, thus paths being at the end of the chain
				will be returned.
				If not given, all paths, i.e. all intermediate references, will
				be returned as well
				
-d int			if not set, all references and subreferences will be retrieved
				if 1, only direct references will be returned
				if > 1, also sub[sub...] references will returned
				
-b				if set and no input arg exists, return all bad or invalid files stored in the database
				if an input argument is given, it acts as a filter and only returns 
				filepaths that are marked invalid
				
-e				return full edges instead of only the successors/predecessors.
				This allows tools to parse the output and make more sense of it
				Will be ignored in nice mode
				
-n 				nice output, designed to be human-readable
"""
	if msg:
		print msg
		
	sys.exit( 1 )
	
	
if __name__ == "__main__":
	# parse the arguments as retrieved from the command line !
	try:
		opts, rest = getopt.getopt( sys.argv[1:], "iam:t:s:ld:ben", [ "affects", "affected-by" ] )
	except getopt.GetoptError,e:
		_usageAndExit( str( e ) )
		
	if not opts and not rest:
		_usageAndExit()
		
	opts = dict( opts )
	fromstdin = "-i" in opts
	return_invalid = "-b" in opts
	if not fromstdin and not rest and not return_invalid:
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
	sourceFile = opts.get( "-s", None )
	
	
	# GET DEPENDS 
	##################
	graph = None
	if not sourceFile:
		graph = main( filelist, **kwargs )
	else:
		print "Reading dependencies from: %s" % sourceFile
		graph = gpickle.read_gpickle( sourceFile )
	


	# WRITE MODE ? 
	##############
	# save to target file
	if targetFile:
		print  "Saving dependencies to %s" % targetFile 
		gpickle.write_gpickle( graph, targetFile )
		
	
	# QUERY MODE 
	###############
	invalidFiles = set()
	used_invalid_as_filter = False
	if return_invalid:
		invalidFiles = set( graph.getInvalid() )
		
	depth = int( opts.get( "-d", -1 ) )
	as_edge = "-e" in opts
	nice_mode = "-n" in opts 
	
	for flag, direction in (	( "--affects", MayaFileGraph.kAffects ),
								("--affected-by",MayaFileGraph.kAffectedBy ) ):
		if not flag in opts:
			continue
		
		# PREPARE LEAF FUNCTION
		prune = lambda i,g: False
		if "-l" in opts:
			degreefunc = ( ( direction == MayaFileGraph.kAffects ) and MayaFileGraph.out_degree ) or MayaFileGraph.in_degree 
			prune = lambda i,g: degreefunc( g, i ) != 0 
		
		# write information to stdout 
		for filepath in filelist:
			filepath = filepath.strip()		# could be from stdin
			depends = graph.getDepends( filepath, direction = direction, prune = prune, 
									   	visit_once=1, branch_first=1, depth=depth )
			
			if invalidFiles:
				depends = set( depends ) & invalidFiles
				used_invalid_as_filter = True		# prevents that we print all of them later
				
			# match with invalid files if required
			if nice_mode:
				depthstr = "unlimited"
				if depth != -1:
					depthstr = str( depth )
					
				affectsstr = "is affected by: "
				if direction == MayaFileGraph.kAffects:
					affectsstr = "affects: "
				
				headline = "%s ( depth = %s, invalid only = %i )\n" % ( filepath, depthstr, return_invalid )
				sys.stdout.write( headline )
				sys.stdout.write( "-" * len( headline ) + "\n" )
				
				sys.stdout.write( affectsstr + "\n" )
				sys.stdout.writelines( "\t - " + dep + "\n" for dep in depends )
			else:
				prefix = ""
				if as_edge:
					prefix = "%s->" % filepath
				sys.stdout.writelines( ( prefix + dep + "\n" for dep in depends )  )
	# END for each direction to search 
		
	if not used_invalid_as_filter and len( invalidFiles ):
		sys.stdout.writelines( ( iv + "\n" for iv in invalidFiles ) )
	
