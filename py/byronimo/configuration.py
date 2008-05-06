"""B{byronimo.configuration}

Contains implementation of the configuration system allowing to flexibly control
the programs behaviour.

	- read and write section=[key=value]* pairs from INI style file-like objects !
		- Wrappers for these file-like objects allow virtually any source for the operation
	- configuration inheritance
		- allow precise control over the inheritance behaviour and inheritance
		  defaults
		- final results of the inheritance operation will be cached into the respective
		  class
		- Environment Variables can serve as final instance to override values
	- Creation and Maintenance of individual configuration files as controlled by
	  submodules of the application
			- These configuration go to a default location, or to the given file-like object
	- embed more complex data to be read by specialised classes using URLs
	- its safe and easy to write back possibly altered values even if complex inheritance
		schemes are applied

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

                                                        
from ConfigParser import (	RawConfigParser,	
							NoSectionError, 
							NoOptionError, 
							ParsingError)
from byronimo.exceptions import ByronimoError
import copy
import re
import sys


#{ Exceptions
################################################################################
class ConfigParsingError( ByronimoError ):
	""" Indicates that the parsing failed """
	pass



#} End Exceptions


#{ INI File Converters
################################################################################
# Wrap arbitary sources and implicitly convert them to INI files when read
import StringIO
class DictToINIFile( StringIO.StringIO ):
	""" Wraps a dictionary into an objects returning an INI file when read

	This class can be used to make configuration information as supplied by os.environ
	natively available to the configuration system

	@note: writing back values to the object will not alter the original dict
	@note: the current implementation caches the dict's INI representation, data
	is not generated on demand
	@note: implementation speed has been preferred over runtime speed """
	@staticmethod
	def _checkstr( string ):
		"""
		@return: unaltered string if there was not issue
		@raise ValueError: if string contains newline """
		if string.find( '\n' ) != -1:
			raise ValueError( "Strings in INI files may not contain newline characters: %s" % string )
		return string

	def __init__( self, option_dict, section = 'DEFAULT', description = "" ):
		"""Initialize the file-like object
		@param option_dict: dictionary with simple key-value pairs - the keys and
		values must translate to meaningful strings ! Empty dicts are allowed
		@param section: the parent section of the key-value pairs
		@param description: will be used as comment directly below the section, it
		must be a single line only

		@raise ValueError: if the description - newlines are generally not allowed
		though and will cause a parsing error later on """
		StringIO.StringIO.__init__( self )
		
		self.write( '[' + str(section) + ']\n' )
		if len(description):
			self.write( '#'+ DictToINIFile._checkstr( description ) + "\n" )
		for k in option_dict:
			self.write( str(k) + " = " + str( option_dict[k] ) + "\n" )

		# reset the file to the beginning
		self.seek( 0 )


#} END GROUP


#{ Configuration Access
################################################################################
# Classes that allow direct access to the respective configuration

class ConfigAccessor( object ):
	""" Provides full access to the Configuration
	
	Differences to ConfigParser
	===========================
	As the functionality and featureset is very different from the original 
	ConfigParser implementation, this class does not support the interface directly.
	It contains functions to create original ConfigParser able to fully write and alter
	the contained data in an unchecked manner.
	
	Additional Exceptions have been defined to cover extended functionality
	
	Commonalities to ConfigParser
	=============================
	Terms used to describe INI files and most exception. 
	
	Additional Information
	======================
	The term configuration is rather complex though:
		- configuration is based on an extended INI file format
			- its not fully compatible, but slightly more narrow regarding allowed input
			  to support extended functionality
		- this configuration is read from file-like objects
		- a list of file-like objects creates a configuration chain
		- keys have properties attached to them defining how they behave during 
		  inheritance
		- once all the INI configurations have been read and processed, one can access
		  the configuration as if it was just in one file.
		- L{SectionAccessor}s are used to gain direct access to the given section """
	
	def __init__( self ):
		""" Initialize instance variables """
		self._configChain = ConfigChain( )  # keeps configuration from different sources
		
	def __repr__( self ):
		stream = ConfigStringIO()
		fca = self.flatten( stream )
		fca.write( close_fp = False )
		return stream.getvalue()
		
	#{ IO Interface
	def readfp( self, filefporlist, close_fp = True ):
		""" Read the INI file from the file like object(s) 
		@param filefporlist: single file like object or list of such
		@param close_fp: if True, the file-like object will be closed before the method returns, 
		but only for file-like objects that have actually been processed 
		
		@raise ConfigParsingError: """
		fileobjectlist = filefporlist
		if not isinstance( fileobjectlist, (list,tuple) ):
			fileobjectlist = ( filefporlist, )
			
		# create one parser per file, append information to our configuration chain
		tmpchain = ConfigChain( )			# to be stored later if we do not have an exception
	
		for fp in fileobjectlist:
			try:
				node = ConfigNode( fp )
				tmpchain.append( node )
				node.parse()
			finally:
				if close_fp:
					fp.close()
			
		# keep the chain - no error so far	
		self._configChain = tmpchain
		
		
	@typecheck_rval( list )
	def write( self, close_fp=True ):
		""" Write current state back to files 
		During initialization in readfp, ExtendedFileInterface objects have been passed in - these
		will now be used to write back the current state of the configuration.
		
		@param close_fp: close the file-object after writing to it
		@return: list of names of files that have actually been written
		""" 
		writtenFiles = []
		
		# for each node put the information into the parser and write to the node's
		# file object after assuring it is opened
		for cn in self._configChain:
			try:
				writtenFiles.append( cn.write( RawConfigParser(), close_fp=close_fp ) )
			except IOError:
				pass
				
		return writtenFiles
		
	#} END GROUP
	
	
	#{Transformations
	# type checking does not work for ourselves as we are not yet defined - need baseclass !
	# But I cannot introduce it just for that purpose ... 
	# @typecheck_rval( object, ExtendedFileInterface )
	def flatten( self, fp ):
		"""Copy all our members into a new ConfigAccessor which only has one node, instead of x
		
		By default, a configuration can be made up of several different sources that create a chain
		Each source can redefine and alter values previously defined by other sources.
		
		A flattened chain though does only conist of one node containing concrete values that 
		can quickly be accessed
		@param fp: file-like object that will be used as storage once the configuration is written
		@return: Flattened copy of self"""
		# create config node 
		ca = ConfigAccessor( )
		ca._configChain.append( ConfigNode( fp ) )
		cn = ca._configChain[0]
		
		# transfer copies of sections and keys - requires knowledge of internal 
		# data strudctures
		for mycn in self._configChain:
			for mysection in mycn._sections:
				section = cn.getSectionDefault( mysection.name )[0]
				
				# handle section properties
				for mykey in mysection.keys: 
					key,created = section.getKeyDefault( mykey.name, 1 )
					if created:
						key._values = []	# reset the value if key has been newly created
					
					# merge the keys 
					#@todo: merge properly, default is setting the values
					key._values.extend( mykey._values )
					
		return ca
		
	#} END GROUP
	
	#{ Section Access 
	def __iter__( self ):
		""" @return: iterator for all our sections """
		import itertools
		return itertools.chain( *[ iter( node._sections ) for node in self._configChain ] )
	
	@typecheck_param( object, basestring )
	def getSection( self, section ):
		""" @return: section with name, or raise 
		@raise NoSectionError: """
		for node in self._configChain:
			if section in node._sections:
				return node.getSection( section )
				
		raise NoSectionError( section )
		
	@typecheck_param( object, basestring )
	def getSectionDefault( self, section ):
		"""@return: section with given name,
		@raise IOError: If the configuration cannot be written to 
		@note: the section will be created if it does not yet exist
		"""
		try: 
			return self.getSection( section )
		except:
			pass
			
		# find the first writable node and create the section there 
		for node in self._configChain:
			if node.writable:
				return node.getSectionDefault( section )
		
		# we did not find any writable node - fail
		raise IOError( "Could not find a single writable configuration file" )
		
		
	#} END GROUP
	
#}END GROUP




#{Extended File Classes
class ExtendedFileInterface( ):
	""" Define additional methods required by the Configuration System 
	@warning: Additionally, readline and write must be supported - its not mentioned
	here for reasons of speed
	@note: override the methods with implementation"""
	
	def isWritable( self ):
		""" @return: True if the file can be written to """ 
		raise False
		
	def isClosed( self ):
		""" @return: True if the file has been closed, and needs to be reopened for writing """
		raise NotImplementedError
	
	def getName( self ):
		""" @return: a name for the file object """ 
		raise NotImplementedError

	def openForWriting( self ):
		""" Open the file to write to it
		@raise IOError: on failure"""
		raise NotImplementedError
	
	
class ConfigFile( file, ExtendedFileInterface ): 
	""" file object implementation of the ExtendedFileInterface """
	__slots__ = [ '_writable' ]
	
	def __init__( self, *args, **kvargs ):
		""" Initialize our caching values """
		file.__init__( self, *args, **kvargs )
		self._writable = self._isWritable( )
		
	def _modeSaysWritable( self ):
		return ( self.mode.find( 'w' ) != -1 ) or ( self.mode.find( 'a' ) != -1 )
	
	def _isWritable( self ):
		""" Check whether the file is effectively writable by opening it for writing 
		@todo: evaluate the usage of stat instead - would be faster, but I do not know whether it works on NT with user rights etc."""
		if self._modeSaysWritable( ): 
			return True
			
		wasClosed = self.closed
		lastMode = self.mode
		pos = self.tell()
		
		if not self.closed:
			self.close()
				
		# open in write append mode
		rval = True
		try: 
			file.__init__( self, self.name, "a" )
		except IOError:
			rval = False
		
		# reset original state
		if wasClosed: 
			self.close()
			self.mode = lastMode
		else:
			# reopen with changed mode
			file.__init__( self, self.name, lastMode )
			self.seek( pos )
			
		return rval
	
	def isWritable( self ):
		"""@return: True if the file is truly writable"""
		# return our cached value 
		return self._writable
		
	def isClosed( self ):
		return self.closed
		
	def getName( self ):
		return self.name	
		
	def openForWriting( self ):
		if self.closed or not self._modeSaysWritable():
			file.__init__( self, self.name, 'w' )
		
		# update writable value cache 
		self._writable = self._isWritable(  )
			
class DictConfigINIFile( ExtendedFileInterface, DictToINIFile ):
	""" dict file object implementation of ExtendedFileInterface """
	def isClosed( self ):
		return self.closed
		
	def getName( self ):
		""" We do not have a real name """
		return 'DictConfigINIFile'
		
	def openForWriting( self ):
		""" We cannot be opened for writing, and are always read-only """
		raise IOError( "DictINIFiles do not support writing" )

class ConfigStringIO( ExtendedFileInterface, StringIO.StringIO ):
	""" cStringIO object implementation of ExtendedFileInterface """
	def isWritable( self ):
		""" Once we are closed, we are not writable anymore """
		return not self.closed
	
	def isClosed( self ):
		return self.closed
		
	def getName( self ):
		""" We do not have a real name """
		return 'ConfigStringIO'

	def openForWriting( self ):
		""" We if we are closed already, there is no way to reopen us """
		if self.closed:
			raise IOError( "cStringIO instances cannot be written once closed" )

#} 


#{Private Utility Classes
class ConfigChain( list ):
	""" A chain of config nodes 
	
	This utility class keeps several L{ConfigNode} objects, but can be operated
	like any other list.                    
	
	@note: this solution is mainly fast to implement, but a linked-list like 
	behaviour is intended """
	#{ List Overridden Methods
	def __init__( self ):
		""" Assures we can only create plain instances """
		list.__init__( self )
	
	@staticmethod
	def _checktype( node ):	
		if not isinstance( node, ConfigNode ):
			raise TypeError( "A ConfigNode instance is required", node )
		
		
	def append( self, node ):
		""" Append a L{ConfigNode} """	
		ConfigChain._checktype( node )
		list.append( self, node )
		
		
	def insert( self, node, index ):
		""" Insert L?{ConfigNode} before index """
		ConfigChain._checktype( node )
		list.insert( self, node, index )
		
	def extend( self, *args, **kvargs ):
		""" @raise NotImplementedError: """
		raise NotImplementedError
		
	def sort( self, *args, **kvargs ):
		""" @raise NotImplementedError: """
		raise NotImplementedError
	#}
	


def _checkString( string, re ):
	"""Check the given string with given re for correctness
	@param re: must match the whole string for success
	@return: the passed in and stripped string
	@raise ValueError: """
	string = string.strip()
	if not len( string ):
		raise ValueError( "string must not be empty" )
	
	match = re.match( string )
	if match is None or match.end() != len( string ):
		raise ValueError( _("'%s' Syntax Error") % string )
	
	return string
		
def _excmsgprefix( msg ):
	""" Put msg in front of current exception and reraise 
	@warning: use only within except blocks"""
	exc = sys.exc_info()[1]
	exc.message = msg + exc.message
	
class BasicSet( set ):
	""" Set with ability to return the key which matches the requested one 
	
	This functionality is the built-in in default STL sets, and I do not understand
	why it is not provided here ! Of course I want to define custom objects with overridden 
	hash functions, put them into a set, and finally retrieve the same object again !
	
	@note: indexing a set is not the fastest because the matching key has to be searched.
	Good news is that the actual 'is k in set' question can be answered quickly """
	def __getitem__( self, item ):
		# assure we have the item
		if not item in self:
			raise KeyError()
			
		# find the actual keyitem
		for key in iter( self ):
			if key == item:
				return key
				
		# should never come here !
		raise AssertionError( "Should never have come here" )
		

class Properties( object ):
	""" Define a set of properties 
		Properties currently are nothing more than flags that can either be 
		set or not """
	__slots__ = [ 'flags' ]
	
	def __init__( self, flagset=BasicSet() ):
		""" Basic Field Initialization """
		self.flags = flagset
		

class Key( object ):
	""" Key with an associated values and an optional set of propterties 
	
	@note: a key's value will be always be stripped if its a string
	@note: a key's name will be stored stripped only, must not contain certain chars
	@todo: add support for escpaing comas within quotes - currently it split a 
	at the coma, no matter what"""
	__slots__ = [ '_name','_values','properties','order' ]
	validchars = r'\w'
	_re_checkName = re.compile( validchars+r'+' )			# only word characters are allowed in key names
	# _re_checkValue = re.compile( '('+validchars+'+)|(\w{3,}:[/\w]+)' )			# currently we are as restrictive as it gets
	_re_checkValue = re.compile( '\S+' )			# currently we are as restrictive as it gets
	
	@typecheck_param( object, str, object, int )
	def __init__( self, name, value, order ):
		""" Basic Field Initialization 
		@param order: -1 = will be written to end of list, or to given position otherwise """
		self._name			= ''				
		self.name 			= name
		self._values 		= []				# value will always be stored as a list
		self.properties 	= Properties()
		self.order 			= order
		self.values 		= value				# store the value
	
	def __hash__( self ):
		return self._name.__hash__()
	
	def __eq__( self, other ):
		return self._name == str( other )
		
	def __repr__( self ):
		""" @return: ini string representation """
		return self._name + " = " + ','.join( [ str( val ) for val in self._values ] )
		
	def __str__( self ):
		""" @return: key name """
		return self._name
		
	@staticmethod
	def _parseObject( valuestr ):
		""" @return: int,float or str from valuestring """
		types = [ long, float ]
		for numtype in types:
			try:
				val = numtype( valuestr )
				return val
			except ValueError:
				continue
		
		if not isinstance( valuestr, basestring ):
			raise TypeError( "Invalid value type: only int, long, float and str are allowed", valuestr )
		
		return _checkString( valuestr, Key._re_checkValue )	
	
	
	def _excPrependNameAndRaise( self ):
		_excmsgprefix( "Key = " + self._name + ": " )
		raise
		
	def _setName( self, name ):
		""" Set the name
		@raise ValueError: incorrect name"""
		try:
			self._name = _checkString( name, Key._re_checkName )
		except (TypeError,ValueError):
			self._excPrependNameAndRaise()
			
	def _getName( self ):
		"""@return: the key's name"""		
		return self._name
	
	def _setValue( self, value ): 
		"""@note: internally, we always store a list
		@raise TypeError: 
		@raise ValueError: """
		validvalues = value
		if not isinstance( value, ( list, tuple ) ):
			validvalues = [ value ]
		
		for i in xrange( 0, len( validvalues ) ):
			try:
				validvalues[i] = Key._parseObject( validvalues[i] )
			except (ValueError,TypeError):
				 self._excPrependNameAndRaise()
				
		self._values = validvalues
		
	def _getValue( self ): return self._values
	
	def getValueString( self ):
		""" Convert our value to a string suitable for the INI format """
		strtmp = [ str( v ) for v in self._values ]
		return ','.join( strtmp )
	
	#{Properties
	name = property( _getName, _setName )
	values = property( _getValue, _setValue )
	#}
	

	
class Section( object ):
	""" Class defininig an indivual section of a configuration file including 
	all its keys and section properties 
	
	@note: name will be stored stripped and must not contain certain chars """
	__slots__ = [ '_name', 'keys', 'properties','order' ]
	_re_checkName = re.compile( r'\+?\w+(:' + Key.validchars+ r'+)?' )
	
	@typecheck_param( object, str, int )
	def __init__( self, name, order ):
		"""Basic Field Initialization
		@param order: -1 = will be written to end of list, or to given position otherwise """
		self._name 			= ''
		self.name 			= name
		self.keys 			= BasicSet()
		self.properties 	= Properties()
		self.order 			= order					# define where we are - for later writing
	
	def __hash__( self ):
		return self._name.__hash__()
	
	def __eq__( self, other ):
		return self._name == str( other )
	
	def __str__( self ):
		""" @return: section name """
		return self._name
	
	def _excPrependNameAndRaise( self ):
		_excmsgprefix( "Section = " + self._name + ": " )
		raise
		
	def _setName( self, name ):
		"""@raise ValueError: if name contains invalid chars"""
		try:
			self._name = _checkString( name, Section._re_checkName )
		except (ValueError,TypeError):
			self._excPrependNameAndRaise()
			
	def _getName( self ):
		"""@return: the key's name"""		
		return self._name
	
	#{ Properties
	name = property( _getName, _setName )
	#}
	
	
	#{Key Access
	@typecheck_rval( Key )
	def getKey( self, name ):
		"""@return: L{Key} with name
		@raise NoOptionError: """
		try:
			return self.keys[ name ]
		except KeyError:
			raise NoOptionError( name, self.name )
	
	@typecheck_rval( ( Key,bool ) )	
	def getKeyDefault( self, name, value ):
		"""@param value: anything supported by L{setKey}
		@return: tuple: 0 = L{Key} with name, create it if required with given value, 1 = true if newly created, false otherwise"""
		try: 
			return ( self.getKey( name ), False )
		except NoOptionError:
			key = Key( name, value, -1 )
			self.keys.add( key )
			return ( key, True )
			
	def setKey( self, name, value ):
		""" Set the value to key with name, or create a new key with name and value 
		@param value: int, long, float, string or list of any of such
		@raise ValueError: if key has incorrect value
		"""
		k = self.getKeyDefault( name, value )[0]
		k.values = value
	#}                                               
	
	
	
	
class ConfigNode( object ):
	""" Represents node in the configuration chain
	
	It keeps information about the origin of the configuration and all its data.
	Additionally, it is aware of it being element of a chain, and can provide next
	and previous elements respectively """
	#{Construction/Destruction
	@typecheck_param( object, interface( ExtendedFileInterface ) )
	def __init__( self, fp ):
		""" Initialize Class Instance"""
		self._sections	= BasicSet()			# associate sections with key holders
		self._fp		= fp					# file-like object that we can read from and possibly write to 
	#}
	
	
	def _isWritable( self ):
		""" @return: True if the instance can be altered """
		return self.fp.isWritable()
		
	#{Properties
	writable = property( _isWritable )		# read-only attribute
	#}
	
	def _update( self, configparser ):
		""" Update our data with data from configparser """
		# first get all data 
		snames = configparser.sections()
		validsections = []
		
		for i in xrange( 0, len( snames ) ):
			sname = snames[i]
			items = configparser.items( sname )
			section = self.getSectionDefault( sname )[0]
			section.order = i
			for k,v in items:
				section.setKey( k, v.split(',') )	
			validsections.append( section )
			
		self._sections.update( set( validsections ) )
		
	@typecheck_param( object )
	def parse( self ):
		""" parse default INI information into the extended structure
		
		Parse the given INI file using a RawConfigParser, convert all information in it
		into an internal format 
		@raise ConfigParsingError: """
		rcp = RawConfigParser( )
		try: 
			rcp.readfp( self._fp )
			self._update( rcp )
		except (ValueError,TypeError,ParsingError):
			name = self._fp.getName()
			exc = sys.exc_info()[1]
			# if error is ours, prepend filename
			if not isinstance( exc, ParsingError ):
				_excmsgprefix( "File: " + name + ": " )
			raise ConfigParsingError( exc.message )
			
		# cache whether we can possibly write to that destination x
		
	@typecheck_param( object, RawConfigParser )
	def write( self, rcp, close_fp=True ):
		""" Write our contents to our file-like object
		@param rcp: RawConfigParser to use for writing
		@return: the name of the written file
		@raise IOError: if we are read-only"""
		if not self._fp.isWritable( ):
			raise IOError( self._fp.getName() + " is not writable" )
			
		
		for section in iter( self._sections ):
			# TODO: write section properties 
			rcp.add_section( section.name )
			for key in section.keys:
				rcp.set( section.name, key.name, key.getValueString( ) )
				# TODO: write section properties
				
		self._fp.openForWriting( )
		rcp.write( self._fp )
		if close_fp:
			self._fp.close()
			
		return self._fp.getName()
		
	@typecheck_rval( list )
	def listSections( self ):
		""" @return: [] with string names of available sections 
		@todo: return an iterator instead"""
		out = []
		for section in self._sections: out.append( str( section ) )
		return out
		
	#{Section Access
	@typecheck_rval( Section )
	def getSection( self, name ):
		"""@return: L{Section} with name
		@raise NoSectionError: """
		try:
			return self._sections[ name ]
		except KeyError:
			raise NoSectionError( name )
	
	@typecheck_rval( ( Section, bool ) )	
	def getSectionDefault( self, name ):
		"""@return: tuple: 0 = L{Section} with name, create it if required, 1 = True if newly created"""
		try: 
			return ( self.getSection( name ), False )
		except NoSectionError:
			section = Section( name, -1 )
			self._sections.add( section )
			return ( section, True )
	#}
	
#} END GROUP


		
#{ Configuration Diffing Classes


class DiffData( object ): 
	""" Struct keeping data about added, removed and/or changed data """
	__slots__ = [ 'added', 'removed', 'changed', 'unchanged' ]
	
	"""#@ivar added: Copies of all the sections that are only in B ( as they have been added to B )"""
	"""#@ivar removed: Copies of all the sections that are only in A ( as they have been removed from B )"""
	"""@ivar changed: Copies of all the sections that are in A and B, but with changed keys and/or properties"""
		
	def __init__( self , A, B ):
		""" Initialize this instance with the differences of B compared to A """
		self._populate( A, B )
	
	def toStr( self, typename ):
		""" Convert own data representation to a string """
		out = ''
		attrs = [ 'added','removed','changed','unchanged' ]
		for attr in attrs:
			attrobj = getattr( self, attr )
			try: 
				if len( attrobj ) == 0: 
					# out += "No " + attr + " " + typename + "(s) found\n"
					pass 
				else:
					out += str( len( attrobj ) ) + " " + attr + " " + typename + "(s) found\n" 
					for item in attrobj:
						out += str( item ) + "\n"
			except:
				raise
				# out += attr + " " + typename + " is not set\n"
				
		return out
		
	def _populate( self, A, B ):
		""" Must be implemented by subclass """
		raise NotImplementedError
		
	def hasDifferences( self ):
		"""@return: true if we have stored differences ( A  is not equal to B )"""
		return ( len( self.added ) or len( self.removed ) or len ( self.changed ) )
	

class DiffKey( DiffData ): 
	""" Implements DiffData on Key level """
	
	def __str__( self ):
		return self.toStr( "Key-Value" )
	
	def _populate( self, A, B ):
		""" Find added and removed key values 
		@note: currently the implementation is not index based, but set- and thus value based
		@note: changed has no meaning in this case and will always be empty """
		
		# compare based on string list, as this matches the actual representation in the file
		avals = frozenset( str( val ) for val in A._values  )
		bvals = frozenset( str( val ) for val in B._values  )
		
		self.added = list( bvals - avals )
		self.removed = list( avals - bvals )
		self.unchanged = list( avals & bvals )
		self.changed = list()			# always empty -
		
		
class DiffSection( DiffData ):
	""" Implements DiffData on section level """
	
	def __str__( self ):
		return self.toStr( "Key" )
	
	def _populate( self, A, B  ):
		""" Find the difference between the respective """
		self.added = list( copy.deepcopy( B.keys - A.keys ) )
		self.removed = list( copy.deepcopy( A.keys - B.keys ) )
		self.changed = list()
		self.unchanged = list()
		
		# find and set changed keys
		common = A.keys & B.keys
		for key in common:
			akey = A.getKey( str( key ) )
			bkey = B.getKey( str( key ) )
			dkey = DiffKey( akey, bkey )
			
			if dkey.hasDifferences( ): self.changed.append( dkey )
			else: self.unchanged.append( key )
		
	

class ConfigDiffer( DiffData ):
	"""Compares two configuration objects and allows retrieval of differences 
	
	Use this class to find added/removed sections or keys or differences in values
	and properties. 
	
	Example Applicance
	==================                        
		- Test use it to verify that reading and writing a ( possibly ) changed
		  configuration has the expected results
		- Programs interacting with the User by a GUI can easily determine whether
		  the user has actually changed something, applying actions only if required
			- alternatively, programs can simply be more efficient by acting only on 
		  	  items that actually changed """
					
	def __str__( self ):
		""" Print its own delta information - useful for debugging purposes """
		return self.toStr( 'section' )
		
	@typecheck_param( object, ConfigAccessor, ConfigAccessor )
	def _populate( self, A, B ):
		""" Perform the acutal diffing operation to fill our data structures 
		@note: this method directly accesses ConfigAccessors internal datastructures """
		
		# diff sections  - therefore we actually have to treat the chains 
		#  in a flattened manner 
		# built section sets !
		asections = frozenset( iter( A ) ) 
		bsections = frozenset( iter( B ) )
		
		# assure we do not work on references !
		self.added = list( copy.deepcopy( bsections - asections ) )
		self.removed = list( copy.deepcopy( asections - bsections ) )
		self.changed = list()
		self.unchanged = list()
		
		common = asections & bsections		# will be copied later later on key level
		
		# get a deeper analysis of the common sections - added,removed,changed keys
		for section in common:
			# find out whether the section has changed !
			asection = A.getSection( str( section ) )
			bsection = B.getSection( str( section ) )
			dsection = DiffSection( asection, bsection )
			
			if dsection.hasDifferences( ): self.changed.append( dsection )
			else: self.unchanged.append( dsection )
			

#}

#{Complex Data Handling
################################################################################
# Classes handling URLs and their protocols


#} END GROUP

