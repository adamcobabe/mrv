# -*- coding: utf-8 -*-
"""Contains parser allowing to retrieve dependency information from maya ascii files
and convert it into an easy-to-use networkx graph with convenience methods
"""
import mayarv				# assure we have the main module initialized
from networkx import DiGraph, NetworkXError
from networkx.readwrite import gpickle
from util import iterNetworkxGraph
from itertools import chain

import getopt
import sys
import os
import re

class MayaFileGraph( DiGraph ):
	"""Contains dependnecies between maya files including utility functions
	allowing to more easily find what you are looking for"""
	kAffects,kAffectedBy = range( 2 )

	refpathregex = re.compile( '.*-r .*"(.*)";' )

	invalidNodeID = "__invalid__"
	invalidPrefix = ":_iv_:"

	#{ Edit
	@classmethod
	def createFromFiles( cls, fileList, **kwargs ):
		"""@return: MayaFileGraph providing dependency information about the files
		in fileList and their subReference.
		@param fileList: iterable providing the filepaths to be parsed and added
		to this graph
		@param **kwargs: alll arguemnts of L{addFromFiles} are supported """
		graph = cls( )
		graph.addFromFiles( fileList, **kwargs )
		return graph


	def _addInvalid( self, invalidfile ):
		"""Add an invalid file to our special location
		@note: we prefix it to assure it does not popup in our results"""
		self.add_edge( ( self.invalidNodeID, self.invalidPrefix + str( invalidfile ) ) )

	@classmethod
	def _parseReferences( cls, mafile, allPaths = False ):
		"""@return: list of reference strings parsed from the given maya ascii file
		@raise IOError: if the file could not be read"""
		outrefs = list()
		filehandle = open( os.path.expandvars( mafile ), "r" )

		num_rdi_paths = 0		# amount of -rdi paths we found - lateron we have to remove the items
								# at the respective position as both lists match

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

			match = cls.refpathregex.match( line )

			if match:
				outrefs.append( match.group(1) )
			# END -r path match

			# see whether we can abort early
			if not allPaths and line.startswith( "requires" ):
				break
		# END for each line

		filehandle.close()

		return outrefs

	def _parseDepends( self, mafile, allPaths ):
		"""@return: list of filepath as parsed from the given mafile.
		@param allPaths: if True, the whole file will be parsed, if False, only
		the reference section will be parsed"""
		outdepends = list()
		print "Parsing %s" % ( mafile )

		try:
			outdepends = self._parseReferences( mafile, allPaths )
		except IOError,e:
			# store as invalid
			self._addInvalid( mafile )
			sys.stderr.write( "Parsing Failed: %s\n" % str( e ) )
		# END exception handlign
		return outdepends


	def addFromFiles( self, mafiles, parse_all_paths = False,
					to_os_path = lambda f: os.path.expandvars( f ),
					os_path_to_db_key = lambda f: f,
					ignorelist=None ):
		"""Parse the dependencies from the given maya ascii files and add them to
		this graph
		@note: the more files are given, the more efficient the method can be
		@param parse_all_paths: if True, default False, all paths found in the file will be used.
		This will slow down the parsing as the whole file will be searched for references
		instead of just the header of the file
		@param to_os_path: functor returning an MA file from given posssibly parsed file
		that should be existing on the system parsing the files.
		The passed in file could also be an mb file ( which cannot be parsed ), thus it
		would be advantageous to return a corresponding ma file
		This is required as references can have environment variables inside of them
		@param os_path_to_db_key: converts the given path as used in the filesystem into
		a path to be used as key in the database. It should be general.
		Ideally, os_path_to_db_key is the inverse as to_os_path.
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
				curfile = to_os_path( depfiles.pop() )

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
				valid_depends = list()
				for depfile in curfiledepends:
					# only valid files may be adjusted - we keep them as is otherwise
					dbdepfile = to_os_path( depfile )

					if os.path.exists( dbdepfile ):
						valid_depends.append( depfile )				# store the orig path - it will be converted later
						dbdepfile = os_path_to_db_key( dbdepfile )		# make it db key path
					else:
						dbdepfile = depfile								# invalid - revert it
						self._addInvalid( depfile )						# store it as invalid, no further processing

					self.add_edge( ( dbdepfile, os_path_to_db_key( curfilestr ) ) )

				# add to stack and go on
				depfiles.extend( valid_depends )
			# END dependency loop
		# END for each file to parse

		#} END edit

	#{ Query
	def getDepends( self, filePath, direction = kAffects,
				   to_os_path = lambda f: os.path.expandvars( f ),
					os_path_to_db_key = lambda f: f, return_unresolved = False,
				   invalid_only = False, **kwargs ):
		"""@return: list of paths ( converted to os paths ) that are related to
		the given filePath
		@param direction: specifies search direction, either :
		kAffects = Files that filePath affects
		kAffectedBy = Files that affect filePath
		@param to_os_path,os_path_to_db_key: see L{addFromFiles}
		@param **kwargs: correspon to L{iterNetworkxGraph}
		@param return_unresolved: if True, the output paths will not be translated to
		an os paths and you get the paths as stored in the graph.
		Please not that the to_os_path function is still needed to generate
		a valid key, depending on the format of filepaths stored in this graph
		@param invalid_only: if True, only invalid dependencies will be returned, all
		including the invalid ones otherwise"""
		kwargs[ 'direction' ] = direction
		kwargs[ 'ignore_startitem' ] = 1			# default
		kwargs[ 'branch_first' ] = 1		# default

		keypath = os_path_to_db_key( to_os_path( filePath ) )	# convert key
		invalid = set( self.getInvalid() )

		if return_unresolved:
			to_os_path = lambda f: f

		outlist = list()

		try:
			for f in iterNetworkxGraph( self, keypath, **kwargs ):
				is_valid = f not in invalid
				f = to_os_path( f )		# remap only valid paths

				if is_valid and invalid_only:	# skip valid ones ?
					continue

				outlist.append( f )
			# END for each file in dependencies
		except NetworkXError:
			sys.stderr.write( "Path %s ( %s ) unknown to dependency graph\n" % ( filePath, keypath ) )

		return outlist

	def getInvalid( self ):
		"""@return: list of filePaths that could not be parsed, most probably
		because they could not be found by the system"""
		lenp = len( self.invalidPrefix  )

		try:
			return [ iv[ lenp : ] for iv in self.successors( self.invalidNodeID ) ]
		except NetworkXError:
			return list()
		# END no invalid found exception handling
	#} END query


def main( fileList, **kwargs ):
	"""Called if this module is called directly, creating a file containing
	dependency information
	@param kwargs: will be passed directly to L{createFromFiles}"""
	return MayaFileGraph.createFromFiles( fileList, **kwargs )


def _usageAndExit( msg = None ):
	print """bpython mdepparse.py [-shortflags ] [--longflags] file_to_parse.ma [file_to_parse, ...]

OUTPUT
------
All actual information goes to stdout, everything else to stderr

EDIT
-----
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

--to-fs-map	tokenmap
	map one part of the path to another in order to make it a valid path
	in the filesystem, i.e:
	--to-fs-map source=target[=...]
	--to-fs-map c:\\=/mnt/data/
	sort it with the longest remapping first to assure no accidential matches.
	Should be used if environment variables are used which are not set in the system
	or if there are other path inconsistencies

--to-db-map tokenmap
	map one part of the fs path previously remapped by --to-fs-map to a
	more general one suitable to be a key in the dependency database.
 	The format is equal to the one used in --to-fs-map

-o	output the dependency database as dot file at the given path, so it can
	be read by any dot reader and interpreted that way.
	If input arguments are given, only the affected portions of the database
	will be available in the dot file. Also, the depths of the dependency information
	is lost, thus there are only direct connections, although it might in
	fact be a sub-reference.

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

-v				enable more verbose output

"""
	if msg:
		print msg

	sys.exit( 1 )


def tokensToRemapFunc( tokenstring ):
	"""Return a function applying remapping as defined by tokenstring
	@note: it also applies a mapping from mb to ma, no matter what.
	Thus we currently only store .ma files as keys even though it might be mb files"""
	tokens = tokenstring.split( "=" )
	if len( tokens ) % 2 != 0:
		raise ValueError( "Invalid map format: %s" % tokenstring )

	remap_tuples = zip( tokens[0::2], tokens[1::2] )

	def path_replace( f ):
		for source, dest in remap_tuples:
			f = f.replace( source, dest )
		return f

	return path_replace



# COMMAND LINE INTERFACE
############################
if __name__ == "__main__":
	# parse the arguments as retrieved from the command line !
	try:
		opts, rest = getopt.getopt( sys.argv[1:], "iat:s:ld:benvo:", [ "affects", "affected-by",
								   										"to-fs-map=","to-db-map=" ] )
	except getopt.GetoptError,e:
		_usageAndExit( str( e ) )


	if not opts and not rest:
		_usageAndExit()

	opts = dict( opts )
	fromstdin = "-i" in opts

	# PREPARE KWARGS_CREATEGRAPH
	#####################
	allpaths = "-a" in opts
	kwargs_creategraph = dict( ( ( "parse_all_paths", allpaths ), ) )
	kwargs_query = dict()

	# PATH REMAPPING
	##################
	# prepare ma to mb conversion
	# by default, we convert from mb to ma hoping there is a corresponding
	# ma file in the same directory
	for kw,flag in ( "to_os_path","--to-fs-map" ),( "os_path_to_db_key", "--to-db-map" ):
		if flag not in opts:
			continue

		remap_func = tokensToRemapFunc( opts.get( flag ) )
		kwargs_creategraph[ kw ] = remap_func
		kwargs_query[ kw ] = remap_func			# required in query mode as well
	# END for each kw,flag pair


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
	verbose = "-v" in opts

	if not sourceFile:
		graph = main( filelist, **kwargs_creategraph )
	else:
		if verbose:
			print "Reading dependencies from: %s" % sourceFile
		graph = gpickle.read_gpickle( sourceFile )



	# SAVE ALL DEPENDENCIES ?
	#########################
	# save to target file
	if targetFile:
		if verbose:
			print  "Saving dependencies to %s" % targetFile
		gpickle.write_gpickle( graph, targetFile )


	# QUERY MODE
	###############
	return_invalid = "-b" in opts
	depth = int( opts.get( "-d", -1 ) )
	as_edge = "-e" in opts
	nice_mode = "-n" in opts
	dotgraph = None
	dotOutputFile = opts.get( "-o", None )
	kwargs_query[ 'invalid_only' ] = return_invalid		# if given, filtering for invalid only is enabled

	if dotOutputFile:
		dotgraph = MayaFileGraph()

	queried_files = False
	for flag, direction in (	( "--affects", MayaFileGraph.kAffects ),
								("--affected-by",MayaFileGraph.kAffectedBy ) ):
		if not flag in opts:
			continue

		# PREPARE LEAF FUNCTION
		prune = lambda i,g: False
		if "-l" in opts:
			degreefunc = ( ( direction == MayaFileGraph.kAffects ) and MayaFileGraph.out_degree ) or MayaFileGraph.in_degree
			prune = lambda i,g: degreefunc( g, i ) != 0

		listcopy = list()			# as we read from iterators ( stdin ), its required to copy it to iterate it again


		# write information to stdout
		for filepath in filelist:
			listcopy.append( filepath )
			queried_files = True			# used as flag to determine whether filers have been applied or not
			filepath = filepath.strip()		# could be from stdin
			depends = graph.getDepends( filepath, direction = direction, prune = prune,
									   	visit_once=1, branch_first=1, depth=depth,
										return_unresolved=0, **kwargs_query )

			# skip empty depends
			if not depends:
				continue

			# FILTERED DOT OUTPUT ?
			#########################
			if dotgraph is not None:
				for dep in depends:
					dotgraph.add_edge( ( filepath, dep ) )

			# match with invalid files if required
			if nice_mode:
				depthstr = "unlimited"
				if depth != -1:
					depthstr = str( depth )

				affectsstr = "is affected by: "
				if direction == MayaFileGraph.kAffects:
					affectsstr = "affects: "

				headline = "\n%s ( depth = %s, invalid only = %i )\n" % ( filepath, depthstr, return_invalid )
				sys.stdout.write( headline )
				sys.stdout.write( "-" * len( headline ) + "\n" )

				sys.stdout.write( affectsstr + "\n" )
				sys.stdout.writelines( "\t - " + dep + "\n" for dep in depends )
			else:
				prefix = ""
				if as_edge:
					prefix = "%s->" % filepath
				sys.stdout.writelines( ( prefix + dep + "\n" for dep in depends )  )
			# END if not nice modd
		# END for each file in file list

		# use copy after first iteration
		filelist = listcopy

	# END for each direction to search

	# ALL INVALID FILES OUTPUT
	###########################
	if not queried_files and return_invalid:
		invalidFiles = graph.getInvalid()
		sys.stdout.writelines( ( iv + "\n" for iv in invalidFiles ) )


	# DOT OUTPUT
	###################
	if dotOutputFile:
		if verbose:
			print "Saving dot file to %s" % dotOutputFile
		try:
			import networkx.drawing.nx_pydot as pydot
		except ImportError:
			sys.stderr.write( "Required pydot module not installed" )
		else:
			if queried_files and dotgraph is not None:
				pydot.write_dot( dotgraph, dotOutputFile )
			else:
				pydot.write_dot( graph, dotOutputFile )
	# END dot writing
