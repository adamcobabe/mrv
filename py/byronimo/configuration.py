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
import StringIO

#{ Exceptions
################################################################################
class ConfigParsingError( ByronimoError ):
	""" Indicates that the parsing failed """
	pass

	
class ConfigParsingPropertyError( ConfigParsingError ):
	""" Indicates that the property(ies) parsing encountered a problem """
	pass 
#} End Exceptions




#{ INI File Converters
################################################################################
# Wrap arbitary sources and implicitly convert them to INI files when read
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
	
	Additional Exceptions have been defined to cover extended functionality.
	
	Sources and Nodes
	=================
	Each input providing configuration data is stored in a node. This node 
	knows about its writable state. Nodes that are not writable can be altered in memory, 
	but the changes cannot be written back to the source. 
	This does not impose a problem though as changes will be applied as long as there is 
	one writable node in the chain - due to the inheritance scheme applied by the configmanager, 
	the final configuration result will match the changes applied at runtime.
	
	@note: The configaccessor should only be used in conjunction with the L{ConfigManager}
	
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
		- Direct access is obtained though L{Key} and L{Section} objects 
		- Keys and Sections have property attributes of type L{Section}
		  - Their keys and values are used to further define key merging behaviour for example """
	
	def __init__( self ):
		""" Initialize instance variables """
		self._configChain = ConfigChain( )  # keeps configuration from different sources
		
	def __repr__( self ):
		stream = ConfigStringIO()
		fca = self.flatten( stream )
		fca.write( close_fp = False )
		return stream.getvalue()
	
	@staticmethod
	def _isProperty( propname ):
		""" @return: true if propname appears to be an attribute """
		return propname.startswith( '+' )
		
	@staticmethod 
	def _getNameTuple( propname ):
		"""@return: [sectionname,keyname], sectionname can be None"""
		tokens = propname[1:].split( ':' )	# cut initial + sign
		
		if len( tokens ) == 1:		# no fully qualified name
			tokens.insert( 0, None )
		return tokens
		
	def _parseProperties( self ):
		"""Analyse the freshly parsed configuration chain and add the found properties
		to the respective sections and keys
		
		@note: we are userfriendly regarding the error handling - if there is an invlid 
		property, we warn and simply ignore it - for the system it will stay just a key and will 
		thus be written back to the file as required
		@raise ConfigParsingPropertyError: """
		sectioniter = self._configChain.getSectionIterator()
		exc = ConfigParsingPropertyError( ) 
		for section in sectioniter:
			if not ConfigAccessor._isProperty( section.name ):
				continue
				
			# handle attributes
			propname = section.name
			targetkeytokens = ConfigAccessor._getNameTuple( propname ) # fully qualified property name
			
			# find all keys matching the keyname !
			keymatchtuples = self.getKeysByName( targetkeytokens[1] )
			
			# SEARCH FOR KEYS primarily !
			propertytarget = None		# will later be key or section
			lenmatch = len( keymatchtuples )
			excmessage = ""				# keeps exc messages until we know whether to keep them or not
			
			if lenmatch == 0:
				excmessage += "Key '" + propname + "' referenced by property was not found\n"
				# continue searching in sections
			else:
				# here it must be a key - failure leads to continuation
				if targetkeytokens[0] != None:
					# search the key matches for the right section
					for fkey,fsection in keymatchtuples:
						if not fsection.name == targetkeytokens[0]: continue
						else: propertytarget = fkey
						
					if propertytarget is None:
						exc.message += ( "Section '" + targetkeytokens[0] + "' of key '" + targetkeytokens[1] + 
										"' could not be found in " + str(lenmatch) + " candiate sections\n" )
						continue
				else:
					# section is not qualified - could be section or keyname
					# prefer keynames
					if lenmatch == 1:
						propertytarget = keymatchtuples[0][0]	# [ (key,section) ] 
					else: 
						excmessage += "Key for property section named '" + propname + "' was found in " + str(lenmatch) + " sections and needs to be qualified as in: 'sectionname:"+propname+"'\n"
						# continue searching - perhaps we find a section that fits perfectly
						
					                                                                           
			# could be a section property 
			if propertytarget is None:
				try:
					propertytarget = self.getSection( targetkeytokens[1] )
				except NoSectionError:
					# nothing found - skip it 
					excmessage += "Property '" + propname + "' references unknown section or key\n"
					
			# safety check 
			if propertytarget is None:
				exc.message += excmessage
				continue
			
			propertytarget.properties.mergeWith( section )
			
		# finally raise our report-exception if required
		if len( exc.message ):
			raise exc
			
		
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
		
		try:
			self._parseProperties( )
		except ConfigParsingPropertyError:
			self._configChain = ConfigChain()	# undo changes and reraise
			raise		
		
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
				writtenFiles.append( cn.write( FixedConfigParser(), close_fp=close_fp ) )
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
		count = 0
		for mycn in self._configChain:
			for mysection in mycn._sections:
				section = cn.getSectionDefault( mysection.name )
				section.order = count
				count += 1
				section.mergeWith( mysection )
		return ca
		
	#} END GROUP
	
	#{ Iterators
	def getSectionIterator( self ):
		"""@return: iterator returning all sections"""
		return self._configChain.getSectionIterator()
		
	def getKeyIterator( self ):
		"""@return: iterator returning tuples of (key,section) pairs"""
		return self._configChain.getKeyIterator()
		
	#} END GROUP
	
	
	#{ General Access ( disregarding writable state )
	
	def hasSection( self, name ):
		"""@return: True if the given section exists"""
		try:
			self.getSection( name )
		except NoSectionError:
			return False
		
		return True
		
	@typecheck_param( object, basestring )
	def getSection( self, section ):
		""" @return: section with name, or raise 
		@raise NoSectionError: """
		for node in self._configChain:
			if section in node._sections:
				return node.getSection( section )
				
		raise NoSectionError( section )
		
	def getKeyDefault( self, sectionname,keyname, value ):
		"""Convenience Function: get keyname in sectionname with the key's value or your 'value' if it did not exist 
		@param sectionname: thekeyname of the sectionname the key is supposed to be in - it will be created if needed
		@param keyname: thekeyname of the key you wish to find
		@param value: the value you wish to receive as as default if the key has to be created
		@return: L{Key}"""
		return self.getSectionDefault( sectionname ).getKeyDefault(keyname, value )[0]
			
	@typecheck_rval( list )
	@typecheck_param( object, basestring )
	def getKeysByName( self, name ):
		"""@param name: the name of the key you wish to find
		@return: List of  (L{Key},L{Section}) tuples of key matching name found in section, or empty list"""
		# note: we do not use iterators as we want to use sets for faster search !
		return list( self._configChain.iterateKeysByName( name ) )
	
	#} END GROUP
	
	#{ Structure Adjustments Respecting Writable State
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
	
	def removeSection( 	self, name ):
		"""Completely remove the given section name from our list
		@return: the number of nodes that did NOT allow the section to be removed as they are read-only, thus 
		0 will be returned if everything was alright"""
		numReadonly = 0
		for node in self._configChain:
			if not node.hasSection( name ):
				continue
				
			# can we write it ?
			if not node._isWritable( ):
				numReadonly += 1
				continue
				
			node._sections.remove( name )
				
		return numReadonly
		
		
	def mergeSection( self, section ):
		"""Merge and/or add the given section into our chain of nodes. The first writable node will be used
		@raise IOError: if no writable node was found
		@return: name of the file source that has received the section"""
		for node in self._configChain:
			if node._isWritable():
				node.getSectionDefault( str( section ) ).mergeWith( section )
				return node._fp.getName( )
				
		raise IOError( "No writable section found for merge operation" )
	
	
	#} END GROUP
	

class ConfigManager( object ):
	""" Cache Configurations for fast access and provide a convenient interface
	
	As the normal implementation of the ConfigAccessor has limited speed due
	to the hierarchical nature of configuration chains.
	
	The config manager flattens the chain providing fast access. Once it is being
	deleted or asked, it will find the differences between the fast cached 
	configuration and the original one, and apply the changes back to the original chain, 
	which will then write the changes back ( if possible ).
	
	This class should be preferred over the direct congiguration accessor, but this 
	class allows direct access to the cached configuraion accessor if required. 
	
	This class mimics the ConfigAccessor inteface as far as possible to improve ease of use
	
	Use self.config to directly access the configuration through the L{ConfigAccessor} interface"""
	
	def __init__( self, filePointers, write_back_on_desctruction=True, close_fp = True ):
		"""Initialize the class with a list of Extended File Classes 
		@param filePointers: Point to the actual configuration to use
		@type filePointers: L{ExtendedFileInterface}
		
		@param close_fp: if true, the files will be closed and can thus be changed.
		This should be the default as files might be located on the network as shared resource
		
		@param write_back_on_desctruction: if True, the config chain and possible 
		changes will be written once this instance is being deleted. If false, 
		the changes must explicitly be written back using the write method"""
		self.__config = ConfigAccessor( )
		self.config = None					# will be set later 
		self._writeBackOnDestruction = write_back_on_desctruction
		self._closeFp = close_fp
		
		self.readfp( filePointers, close_fp=close_fp )
			
			
	def __del__( self ):
		""" If we are supposed to write back the configuration, after merging 
		the differences back into the original configuration chain"""
		if self._writeBackOnDestruction:
			# might trow - python will automatically ignore these issues
			self.write( )
			
		pass		
	
	#{ IO Methods 
	def write( self ):
		""" Write the possibly changed configuration back to its sources
		@raise IOError: if at least one node could not be properly written
		@note: It could be the case that all nodes are marked read-only and 
		thus cannot be written - this will also raise as the request to write 
		the changes could not be accomodated.
		@return: the names of the files that have been written as string list"""
	
		diff = ConfigDiffer( self.__config, self.config )
		
		# apply the changes done to self.config to the original configuration
		try:
			report = diff.applyTo( self.__config )
			outwrittenfiles = self.__config.write( close_fp = self._closeFp )
			return outwrittenfiles
		except: 
			raise 
			# for now we reraise
			# TODO: raise a proper error here as mentioned in the docs
			# raise IOError()			 
		
	def readfp( self, filefporlist, close_fp=True ):
		""" Read the configuration from the file pointers
		@raise ConfigParsingError: 
		@return: the configuration that is meant to be used for accessing the configuration"""
		self.__config.readfp( filefporlist, close_fp = close_fp )
		
		# flatten the list and attach it
		self.config = self.__config.flatten( ConfigStringIO() )
		return self.config
		
	#}
	
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


#{Utility Classes
class FixedConfigParser( RawConfigParser ):
	"""The RawConfigParser stores options lowercase - but we do not want that 
	and keep the case - for this we just need to override a method"""
	def optionxform( self, option ):
		return option
		
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
	
	#{ Iterators 
	def getSectionIterator( self ):
		"""@return: section iterator for whole configuration chain """
		return ( section for node in self for section in node._sections )
	
	def getKeyIterator( self ):
		"""@return: iterator returning tuples of (key,section) pairs"""
		return ( (key,section) for section in self.getSectionIterator() for key in section )
	
	def iterateKeysByName( self, name ):
		"""@param name: the name of the key you wish to find
		@return: Iterator yielding (L{Key},L{Section}) of key matching name found in section"""
		# note: we do not use iterators as we want to use sets for faster search !
		return ( (section.keys[name],section) for section in self.getSectionIterator() if name in section.keys )
	#} END ITERATORS
	


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
		

class PropertyHolder( object ):
	"""Simple Base defining how to deal with properties
	@note: to use this interface, the subclass must have a 'name' field"""
	__slots__ = [ 'properties' ]
	
	def __init__( self ):
		# assure we do not get recursive here
		self.properties = None
		try:
			if not isinstance( self, PropertySection ):
				self.properties = PropertySection( "+" + self.name, self.order+1 ) # default is to write our properties after ourselves		# will be created on demand to avoid recursion on creation
		except:
			pass
			

		
class Key( PropertyHolder ):
	""" Key with an associated values and an optional set of propterties 
	
	@note: a key's value will be always be stripped if its a string
	@note: a key's name will be stored stripped only, must not contain certain chars
	@todo: add support for escpaing comas within quotes - currently it split at 
	comas, no matter what"""
	__slots__ = [ '_name','_values','order' ]
	validchars = r'\w'
	_re_checkName = re.compile( validchars+r'+' )			# only word characters are allowed in key names
	_re_checkValue = re.compile( '\S+' )			# currently we are as restrictive as it gets
	
	@typecheck_param( object, str, object, int )
	def __init__( self, name, value, order ):
		""" Basic Field Initialization 
		@param order: -1 = will be written to end of list, or to given position otherwise """
		self._name			= ''				
		self.name 			= name				# this assures the type check is being run
		self._values 		= []				# value will always be stored as a list
		self.order 			= order				# defines the order of the key in the file
		self.values 		= value				# store the value
		PropertyHolder.__init__( self )
	
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
			except (ValueError,TypeError):
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
				
		# assure we have always a value - if we write zero values to file, we
		# throw a parse error - thus we may not tolerate empty values
		if len( validvalues ) == 0:
			raise ValueError( "Key: " + self.name + " must have a value - remove the key if no value is required" )
			
		self._values = validvalues
		
	def _getValue( self ): return self._values
	
	def _getValueSingle( self ): return self._values[0]
	
	def _addRemoveValue( self, value, mode ):
		"""Append or remove value to/from our value according to mode
		@param mode: 0 = remove, 1 = add"""
		tmpvalues = value
		if not isinstance( value, (list,tuple) ):
			tmpvalues = ( value, )
		
		finalvalues = self._values[:]
		if mode:
			finalvalues.extend( tmpvalues )
		else:
			for val in tmpvalues:
				if val in finalvalues:
					finalvalues.remove( val )
					
		self.values = finalvalues
		
		
	#{Utilities
	def appendValue( self, value ):
		"""Append the given value or list of values to the list of current values
		@param value: list, tuple or scalar value
		@todo: this implementation could be faster ( costing more code )"""
		self._addRemoveValue( value, True )
	
	def removeValue( self, value ):
		"""remove the given value or list of values from the list of current values
		@param value: list, tuple or scalar value
		@todo: this implementation could be faster ( costing more code )"""
		self._addRemoveValue( value, False )
		
	def getValueString( self ):
		""" Convert our value to a string suitable for the INI format """
		strtmp = [ str( v ) for v in self._values ]
		return ','.join( strtmp )
	
	def mergeWith( self, otherkey ):
		"""Merge self with otherkey according to our properties
		@note: self will be altered"""
		# merge properties 
		if self.properties != None: 
			self.properties.mergeWith( otherkey.properties )
		
		#@todo: merge properly, default is setting the values
		self._values = otherkey._values[:]
		
	#}
	
	#{Properties
	name = property( _getName, _setName )
	""" Access the name of the key"""
	values = property( _getValue, _setValue )
	""" read: values of the key as list 
	write: write single values or llist of values """
	value = property( _getValueSingle, _setValue )
	"""read: first value if the key's values
	write: same effect as write of 'values' """
	#}
	

	
class Section( PropertyHolder ):
	""" Class defininig an indivual section of a configuration file including 
	all its keys and section properties 
	
	@note: name will be stored stripped and must not contain certain chars """
	__slots__ = [ '_name', 'keys','order' ]
	_re_checkName = re.compile( r'\+?\w+(:' + Key.validchars+ r'+)?' )
	
	def __iter__( self ):
		"""@return: key iterator"""
		return iter( self.keys )
	
	@typecheck_param( object, str, int )
	def __init__( self, name, order ):
		"""Basic Field Initialization
		@param order: -1 = will be written to end of list, or to given position otherwise """
		self._name 			= ''
		self.name 			= name
		self.keys 			= BasicSet()
		self.order 			= order					# define where we are - for later writing
		PropertyHolder.__init__( self )
		
	def __hash__( self ):
		return self._name.__hash__()
	
	def __eq__( self, other ):
		return self._name == str( other )
	
	def __str__( self ):
		""" @return: section name """
		return self._name
	
	#def __getattr__( self, keyname ):
		"""@return: the key with the given name if it exists
		@raise NoOptionError: """
	#	return self.getKey( keyname )
	
	#def __setattr__( self, keyname, value ):
		"""Assign the given value to the given key  - it will be created if required"""
	#	self.getKeyDefault( keyname, value ).values = value
		
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
	
	def mergeWith( self, othersection ):
		"""Merge our section with othersection
		@note:self will be altered"""
		# adjust name - the default name is mostly not going to work - property sections
		# possibly have non-qualified property names
		self.name = othersection.name
		
		# merge properties
		if othersection.properties != None:
			self.properties.mergeWith( othersection.properties )
		
		for fkey in othersection.keys: 
			key,created = self.getKeyDefault( fkey.name, 1 )
			if created:
				key._values = []	# reset the value if key has been newly created
			
			# merge the keys 
			key.mergeWith( fkey )
	
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
			# set properties None if we are a propertysection ourselves
			if isinstance( self, PropertySection ):
				key.properties = None
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
	


class PropertySection( Section ):
	"""Define a section containing keys that make up properties of somethingI"""
	__slots__ = []
	
	
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
		return self._fp.isWritable()
		
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
			section = self.getSectionDefault( sname )
			section.order = i*2		# allows us to have ordering room to move items in - like properties
			for k,v in items:
				section.setKey( k, v.split(',') )	
			validsections.append( section )
			
		self._sections.update( set( validsections ) )
		
		
	@typecheck_param( object )
	def parse( self ):
		""" parse default INI information into the extended structure
		
		Parse the given INI file using a FixedConfigParser, convert all information in it
		into an internal format 
		@raise ConfigParsingError: """
		rcp = FixedConfigParser( )
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
		
	@staticmethod
	def _check_and_append( sectionsforwriting, section ):
		"""Assure we ignore empty sections
		@return: True if section has been appended, false otherwise"""
		if section != None and len( section.keys ):
			sectionsforwriting.append( section )
			return True
		return False
		
	@typecheck_param( object, RawConfigParser )
	def write( self, rcp, close_fp=True ):
		""" Write our contents to our file-like object
		@param rcp: RawConfigParser to use for writing
		@return: the name of the written file
		@raise IOError: if we are read-only"""
		if not self._fp.isWritable( ):
			raise IOError( self._fp.getName() + " is not writable" )
			
		sectionsforwriting = []		# keep sections - will be ordered later for actual writing operation
		for section in iter( self._sections ):
			# skip 'old' property sections - they have been parsed to the 
			# respective object ( otherwise we get duplicate section errors of rawconfig parser )
			if ConfigAccessor._isProperty( section.name ):
				continue
				
			# append section and possibly property sectionss
			ConfigNode._check_and_append( sectionsforwriting, section )
			ConfigNode._check_and_append( sectionsforwriting, section.properties )
			
			# append key sections
			# NOTE: we always use fully qualified property names if they have been 
			# automatically generated
			# Autogenerated ones are not in the node's section list
			for key in section.keys:
				if ConfigNode._check_and_append( sectionsforwriting, key.properties ):
					# autocreated ?
					if not key.properties in self._sections:
						key.properties.name = "+"+section.name+":"+key.name
				
				
		# sort list and add sorted list 
		sectionsforwriting = sorted( sectionsforwriting, key=lambda x: -x.order )	# inverse order

		for section in sectionsforwriting:
			rcp.add_section( section.name )
			for key in section.keys:
				rcp.set( section.name, key.name, key.getValueString( ) )
				
			
		self._fp.openForWriting( )
		rcp.write( self._fp )
		if close_fp:
			self._fp.close()
			
		return self._fp.getName()

	#{Section Access
			
	@typecheck_rval( list )
	def listSections( self ):
		""" @return: [] with string names of available sections 
		@todo: return an iterator instead"""
		out = []
		for section in self._sections: out.append( str( section ) )
		return out
		
	
	@typecheck_rval( Section )
	def getSection( self, name ):
		"""@return: L{Section} with name
		@raise NoSectionError: """
		try:
			return self._sections[ name ]
		except KeyError:
			raise NoSectionError( name )
			
	def hasSection( self, name ):
		"""@return: True if the given section exists"""
		return name in self._sections
	
	@typecheck_rval( Section )	
	def getSectionDefault( self, name ):
		"""@return: L{Section} with name, create it if required"""
		name = name.strip()
		try: 
			return self.getSection( name )
		except NoSectionError:
			sectionclass = Section
			if ConfigAccessor._isProperty( name ):
				sectionclass = PropertySection
			
			section = sectionclass( name, -1 )
			self._sections.add( section )
			return section
			
		
	#}
	

#} END GROUP


		
#{ Configuration Diffing Classes

class DiffData( object ): 
	""" Struct keeping data about added, removed and/or changed data 
	Subclasses should override some private methods to automatically utilize some 
	basic functionality"""
	__slots__ = [ 'added', 'removed', 'changed', 'unchanged','properties','name' ]
	
	"""#@ivar added: Copies of all the sections that are only in B ( as they have been added to B )"""
	"""#@ivar removed: Copies of all the sections that are only in A ( as they have been removed from B )"""
	"""@ivar changed: Copies of all the sections that are in A and B, but with changed keys and/or properties"""
		
	def __init__( self , A, B ):
		""" Initialize this instance with the differences of B compared to A """
		self.properties = None
		self.added = list()
		self.removed = list()
		self.changed = list()
		self.unchanged = list()
		self.name = ''
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
					if len( self.name ):
						out += "In '" + self.name + "':\n"
					for item in attrobj:
						out += "'" + str( item ) + "'\n"
			except:
				raise
				# out += attr + " " + typename + " is not set\n"
				
		# append properties
		if self.properties != None:
			out += "-- Properties --\n" 
			out += str( self.properties )
			
		return out
	
	def _populate( self, A, B ):
		""" Should be implemented by subclass """
		pass
		
	def hasDifferences( self ):
		"""@return: true if we have stored differences ( A  is not equal to B )"""
		return  ( len( self.added ) or len( self.removed ) or len ( self.changed ) or \
				( self.properties != None and self.properties.hasDifferences() ) )
				
class DiffKey( DiffData ): 
	""" Implements DiffData on Key level """
	
	def __str__( self ):
		return self.toStr( "Key-Value" )
	
	@staticmethod
	def _subtractLists( a, b ):
		"""Subtract the values of b from a, return the list with the differences"""
		acopy = a[:]
		for val in b:
			try:
				acopy.remove( val )
			except ValueError:
				pass
				
		return acopy
		
	@staticmethod
	def _matchLists( a, b ):
		"""@return: list of values that are common to both lists"""
		badded = DiffKey._subtractLists( b, a )
		return DiffKey._subtractLists( b, badded )
		
	@typecheck_param( object, Key, Key )
	def _populate( self, A, B ):
		""" Find added and removed key values 
		@note: currently the implementation is not index based, but set- and thus value based
		@note: changed has no meaning in this case and will always be empty """
		
		# compare based on string list, as this matches the actual representation in the file
		avals = frozenset( str( val ) for val in A._values  )
		bvals = frozenset( str( val ) for val in B._values  )
		
		# we store real 
		self.added = DiffKey._subtractLists( B._values, A._values )
		self.removed = DiffKey._subtractLists( A._values, B._values )
		self.unchanged = DiffKey._subtractLists( B._values, self.added )	# this gets the commonalities
		self.changed = list()			# always empty -
		self.name = A.name
		
		# diff the properties
		if A.properties != None:
			propdiff = DiffSection( A.properties, B.properties )	
			self.properties = propdiff			# attach propdiff no matter what

			
	def applyTo( self, key ):
		"""Apply our changes to the given Key"""
		
		# simply remove removed values
		for removedval in self.removed:
			try:
				key._values.remove( removedval )
			except ValueError:
				pass 
		
		# simply add added values
		key._values.extend( self.added )
		
		# there are never changed values as this cannot be tracked
		# finally apply the properties if we have some
		if self.properties != None:
			self.properties.applyTo( key.properties )
			
			
class DiffSection( DiffData ):
	""" Implements DiffData on section level """
	
	def __str__( self ):
		return self.toStr( "Key" )
		
	def _populate( self, A, B  ):
		""" Find the difference between the respective """
		# get property diff if possible
		if A.properties != None:
			propdiff = DiffSection( A.properties, B.properties )	
			self.properties = propdiff			# attach propdiff no matter what
		else:
			self.properties = None	# leave it Nonw - one should simply not try to get propertydiffs of property diffs
		
		self.added = list( copy.deepcopy( B.keys - A.keys ) )
		self.removed = list( copy.deepcopy( A.keys - B.keys ) )
		self.changed = list()
		self.unchanged = list()
		self.name = A.name
		# find and set changed keys
		common = A.keys & B.keys
		for key in common:
			akey = A.getKey( str( key ) )
			bkey = B.getKey( str( key ) )
			dkey = DiffKey( akey, bkey )
			
			if dkey.hasDifferences( ): self.changed.append( dkey )
			else: self.unchanged.append( key )
		
	@staticmethod
	def _getNewKey( section, keyname ):
		"""@return: key from section - either existing or properly initialized without default value"""
		key,created = section.getKeyDefault( keyname, "dummy" )
		if created: key._values = []			# reset value if created to assure we have no dummy values in there
		return key 
		
	def applyTo( self, targetSection ):
		"""Apply our changes to targetSection"""
		# properties may be None
		if targetSection is None:
			return
		
		# add added keys - they could exist already, which is why they are being merged
		for addedkey in self.added:
			key = DiffSection._getNewKey( targetSection, addedkey.name )
			key.mergeWith( addedkey )
			
		# remove moved keys - simply delete them from the list
		for removedkey in self.removed:
			if removedkey in targetSection.keys:
				targetSection.keys.remove( removedkey )
				
		# handle changed keys - we will create a new key if this is required
		for changedKeyDiff in self.changed:
			key = DiffSection._getNewKey( targetSection, changedKeyDiff.name )
			changedKeyDiff.applyTo( key ) 
			
		# apply section property diff
		if self.properties != None:
			self.properties.applyTo( targetSection.properties )
	
	
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
		  	  items that actually changed 
			  		
	Data Structure
	==============
	- every object in the diffing structure has a 'name' attribute
	- ConfigDiffer.added|removed|unchanged: L{Section} objects that have been added, removed 
	  or kept unchanged respectively
	- ConfigDiffer.changed: L{DiffSection} objects that indicate the changes in respective section
	  - DiffSection.added|removed|unchanged: L{Key} objects that have been added, removed or kept unchanged respectively
	  - DiffSection.changed: L{DiffKey} objects that indicate the changes in the repsective key
	    - DiffKey.added|removed: the key's values that have been added and/or removed respectively
		- DiffKey.properties: see DiffSection.properties
	  - DiffSection.properties:None if this is a section diff, otherwise it contains a DiffSection with the respective differences
	"""
					
	def __str__( self ):
		""" Print its own delta information - useful for debugging purposes """
		return self.toStr( 'section' )
	
	@staticmethod 
	def _getMergedSections( configaccessor ):
		""" NOTE: within config nodes, sections must be unique, between nodes, 
		this is not the case - sets would simply drop keys with the same name
		leading to invalid results - thus we have to merge equally named sections
		@return: iterable with merged sections
		@todo: make this algo work on sets instead of individual sections for performance"""
		sectionlist = list( configaccessor.getSectionIterator() )
		if len( sectionlist ) < 2:
			return sectionlist
		
		out = BasicSet( )				# need a basic set for indexing
		for section in sectionlist:
			# skip property sections - they have been parsed into properties, but are 
			# still available as ordinary sections
			if ConfigAccessor._isProperty( section.name ):
				continue
				
			section_to_add = section
			if section in out: 
				# get a copy of A and merge it with B
				# assure the merge works left-to-right - previous to current
				# NOTE: only the first copy makes sense - all the others that might follow are not required ... 
				merge_section = copy.deepcopy( out[ section ] )	# copy section and all keys - they will be altered
				merge_section.mergeWith( section )
				
				#remove old and add copy
				out.remove( section )
				section_to_add = merge_section
			out.add( section_to_add )
		return out
			
	@typecheck_param( object, ConfigAccessor, ConfigAccessor )
	def _populate( self, A, B ):
		""" Perform the acutal diffing operation to fill our data structures 
		@note: this method directly accesses ConfigAccessors internal datastructures """
		
		# diff sections  - therefore we actually have to treat the chains 
		#  in a flattened manner 
		# built section sets !
		asections = BasicSet( ConfigDiffer._getMergedSections( A ) )
		bsections = BasicSet( ConfigDiffer._getMergedSections( B ) )
		
		# assure we do not work on references !
		self.added = list( copy.deepcopy( bsections - asections ) )
		self.removed = list( copy.deepcopy( asections - bsections ) )
		self.changed = list( )
		self.unchanged = list( )
		self.name = ''
		
		common = asections & bsections		# will be copied later later on key level
		
		# get a deeper analysis of the common sections - added,removed,changed keys
		for section in common:
			# find out whether the section has changed 
			asection = asections[ section ]
			bsection = bsections[ section ]
			dsection = DiffSection( asection, bsection )
			
			if dsection.hasDifferences( ): self.changed.append( dsection )
			else: self.unchanged.append( asection )
			


		
		
	@typecheck_param( object, ConfigAccessor )
	def applyTo( self, ca ):
		"""Apply the stored differences in this ConfigDiffer instance to the given ConfigAccessor
		
		If our diff contains the changes of A to B, then applying 
		ourselves to A would make A equal B.
		
		@note: individual nodes reqpresenting an input source ( like a file )
		can be marked read-only. This means they cannot be altered - thus it can 
		be that section or key removal fails for them. Addition of elements normally
		works as long as there is one writable node.
		
		@param ca: The configacceesor to apply our differences to
		@return: tuple of lists containing the sections that could not be added, removed or get 
		their changes applied
		 - [0] = list of L{Section}s failed to be added
		 - [1] = list of L{ection}s failed to be removed
		 - [2] = list of L{DiffSection}s failed to apply their changes """
		
		# merge the added sections - only to the first we find 
		rval = ([],[],[])
		for addedsection in self.added:
			try: 
				ca.mergeSection( addedsection )
			except IOError:
				rval[0].append( addedsection )
			
		# remove removed sections - everywhere possible
		# This is because diffs will only be done on merged lists
		for removedsection in self.removed:
			numfailedremoved = ca.removeSection( removedsection.name )
			if numfailedremoved:
				rval[1].append( removedsection )
			
		# handle the changed sections - here only keys or properties have changed
		# respectively
		for sectiondiff in self.changed:
			# note: changes may only be applied once ! The diff works only on 
			# merged configuration chains - this means one secion only exists once
			# here we have an unmerged config chain, and to get consistent results, 
			# the changes may only be applied to one section - we use the first we get
			try: 
				targetSection = ca.getSectionDefault( sectiondiff.name )
				sectiondiff.applyTo( targetSection )
			except IOError:
				rval[2].append( sectiondiff )
				
		return rval
				
#}


#} END GROUP

