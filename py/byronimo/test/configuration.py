"""B{byronimo.test.configuration}
Test all aspects of the configuration management system

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


import unittest
import os
import sys
from ConfigParser import *
from byronimo.configuration import *
from itertools import *
import shutil
import tempfile
from glob import glob

class _ConverterLibrary( ):
	""" For use with Converter Test Cases - contains different dictionaries for INI conversion """
	simple_dict = { "key" : "value", 
					"integer" : 20,
					"integer2" : 400,
					"float": 2.3242 }
	nlkey_dict = { 'invalid\nkey' : 'value' }
	nlval_dict = { 'key' : 'invalid\nvalue' }
	
	environ = os.environ
	gooddictslist = [ simple_dict, environ ]
	
	
	
class TestDictConverter( unittest.TestCase ):
	""" Tests the DictToINI converter"""
	
	
	def test_allValidDicts( self ):
		"""DictToINIFile:Tests whether default dicts can actually be handled by the converter """
		head = 'DEFAULT'
		for dictionary in _ConverterLibrary.gooddictslist:
			dictconverted = DictToINIFile( dictionary, section=head )
			cp = RawConfigParser()
			cp.readfp( dictconverted )
			
			# check that all values are there
			for k in dictionary:
				self.failUnless( cp.has_option( head, k ) )
				self.failUnless( cp.get( head, k ) == str(dictionary[k]).strip() )
		
	def test_valuecheck( self ):
		""" DictToINIFile:Tests whether malformed strings trigger exceptions if malformed
			This is part of the classes sanity checks """
		sdarg = [ _ConverterLibrary.simple_dict ]
		args = [ 
				( sdarg, { 'description' : "DESC\nnewline" } ),
				]
				
		for argvals in args:
			self.failUnlessRaises( ValueError, DictToINIFile, *argvals[0],**argvals[1] )
		
	
			
class TestConfigAccessor( unittest.TestCase ):
	""" Test the ConfigAccessor Class and all its featuers"""
	#{ Helper Methods
	
	
	@typecheck_param( object, ConfigAccessor, list )
	def _verifiedRead( self, ca, fileobjectlist, close_fp = True ):
		"""ConfigAccessor: Assure that the given list of file objects can be read properly
		without loosing information.
		@param fileobjectlist: list of fileobjects
			- A simple differ is used to accomplish this
			- assure file object is closed after read
		Fail otherwise
		"""
		ca.readfp( fileobjectlist, close_fp = close_fp )
		
		# verify its closed
		testlist = fileobjectlist
		if not isinstance( fileobjectlist, ( list, tuple ) ):
			testlist = [ fileobjectlist ]
		for fileobject in testlist:
			self.failUnless( fileobject.closed, fileobject)
		
		# flatten the file ( into memory )
		memfile = ConfigStringIO()
		fca = ca.flatten( memfile )
		fca.write( close_fp = False )
		
		# diff flattened list with original one
		diff = ConfigDiffer( ca, fca )
		self.failIf( diff.hasDifferences() )
		
		
		# reread the configuration
		cca = ConfigAccessor( )
		memfile.seek( 0 )
		cca.readfp( memfile )
		
		# diff the configurations
		diff = ConfigDiffer( cca, fca )
		self.failIf( diff.hasDifferences( ) )
		
	#}
	
	def test_readValidINI( self ):
		"""ConfigAccessor: Tests whether non-malformed INI files can be read ( single and multi )"""
		ca = ConfigAccessor()
		inifps = _getprefixedinifps( 'valid' )
		inifps.append( DictConfigINIFile( os.environ ) )
		for ini in inifps:
			self._verifiedRead( ca, [ ini ] )  
		
		# try to read all files in a row 
		self._verifiedRead( ca, _getprefixedinifps( 'valid' ) )	
		
		
	def test_readInvalidINI( self ):
		"""ConfigAccessor: Tests whether malformed INI files raise """
		ca = ConfigAccessor( )
		inifps = _getprefixedinifps( 'invalid' )
		
		for ini in inifps: 
			self.failUnlessRaises( ConfigParsingError, ca.readfp, ini ) 
	
	def test_iterators( self ):
		"""ConfigAccessor: assure that the provided iterators for sections and keys work """
		ca = _getca( 'valid_4keys' )
		self.failUnless( len( list( ca.getSectionIterator( ) ) ) == 2 )
		self.failUnless( len( list( ca.getKeyIterator( ) ) ) == 4 )
		
	def test_keypropertyparsing( self ):
		"""ConfigAccessor.Properties: Assure that key properties can be parsed"""
		ca = _getca( 'valid_keyproperty' )
		self.failUnless( ca.getKeysByName( "my_key_with_property" )[0][0].properties.getKey( 'property' ).value =='value' )
		
	def test_sectionprortyparsing( self ):
		"""ConfigAccessor.Properties: Assure that section properties can be parsed"""
		ca = _getca( 'valid_sectionproperty' )
		self.failUnless( ca.getSection( "section" ).properties.getKey( 'property' ).value =='value' )
			
	def test_sectionkeyprortyparsing( self ):
		"""ConfigAccessor.Properties: Assure that section and key properties can be parsed"""
		ca = _getca( 'valid_sectionandkeyproperty' )
		self.failUnless( ca.getSection( "section" ).properties.getKey( 'property' ).value =='value' )
		self.failUnless( ca.getKeysByName( "key_with_property" )[0][0].properties.getKey( 'property' ).value =='value' )
		
	def test_propertyundefiniedpropertyattribute( self ):
		"""ConfigAccessor.Properties: Property attribute of property must not be set"""
		ca = _getca( 'valid_sectionandkeyproperty' )
		self.failUnless( ca.getSection( "section" ).properties.properties == None )
		self.failUnless( ca.getKeysByName( "key_with_property" )[0][0].properties.getKey( 'property' ).properties == None )
			
	def test_property_auto_qualification_on_write( self ):
		"""ConfigAccessor.Properties: if properties are set at runtime, the propertysections might need long names for qualification when written"""
		ca = _getca( 'valid_4keys' )
		key = ca.getKeyDefault( "section", "key", "doesntmatter" )
		key_prop = key.properties.getKeyDefault( "new_property", "value" )			# this creates a new physical attribute key
		
		# write to memfile
		memfile = ConfigStringIO()
		fca = ca.flatten( memfile )
		fca.write( close_fp = False )
		
		# create a new configaccessor and assure we have a fully qualified property name
		nca = ConfigAccessor()
		memfile.seek( 0 )
		nca.readfp( memfile )
		self.failUnless( nca.getKeyDefault( "section", "key", "" ).properties.name == "+section:key" )
		
	def test_multi_flatten( self ):
		"""ConfigAccessor:If a configuration gets flattened several times, the result must always match with the original"""
		last_ca = _getca( 'valid_allfeatures' )
		numruns = 5
		for i in range( numruns ):
			memfile = ConfigStringIO()
			ca_flattened = last_ca.flatten( memfile )
			diff = ConfigDiffer( last_ca, ca_flattened )
			self.failIf( diff.hasDifferences( ) )
			
			last_ca = ca_flattened
			
		
class TestConfigManagerr( unittest.TestCase ):
	""" Test the ConfigAccessor Class and all its featuers"""
	
	def __init__( self, testcasenames ):
		unittest.TestCase.__init__( self , testcasenames )
		self.testpath = os.path.join( tempfile.gettempdir(), "tmp_configman" )
		
	def setUp( self ):
		""" Copy valid files into seprate working directory as we want to alter them"""
		
		dirWithTests = os.path.join( os.path.dirname( __file__ ), "configman_inis" )
		try:
			shutil.rmtree( self.testpath, ignore_errors=False )
		except:
			pass
		shutil.copytree( dirWithTests, self.testpath )
		
	def test_access_read_write( self ):
		"""ConfigManager: Simple read and alter values in the Configuration Manager, and write them back """
		inifps = _getprefixedinifps( 'valid', dirname=self.testpath )
		
		cm = ConfigManager( inifps, write_back_on_desctruction=False )
		
		# create new secttion
		cm.config.getSectionDefault("myNewSection").getKeyDefault( "myNewKey", "thisDefault" )[0].value = "this"
		
		# remove a section completely - all are writable, they must be no failed node
		self.failIf( cm.config.removeSection( "section_to_be_removed" ) != 0 )
		
		# add keys to existing section 
		key,created = cm.config.getSection( "section" ).getKeyDefault( "anotherNewKey", "thisDefaultValue" )
		
		# remove keys - this one is garantueed to exist
		cm.config.getSection( "section_removekey_2" ).keys.remove( "key_2" )
		cm.config.getSection( "section_nonunique" ).keys.remove( "key_nonunique" )
		
		# add values to existing key
		cm.config.getSection( "section_addkeyvals" ).getKey( "key3" ).appendValue( "appendedValue" )
		cm.config.getSection( "section_addkeyvals" ).getKey( "key4" ).appendValue( [ "appendedValue2", "anotherappendedValue" ] )

		# remove a value 
		cm.config.getSection( "section_removeval" ).getKey( "key_rmval" ).removeValue( "val2" )
		
		# manaully force the writeback - if it happens in the destructor, errors will be cought automatically 
		cm.write( )
		
		
		
		# read all the files back and assure the changes have really been applied
		############################################################################
		inifps = _getprefixedinifps( 'valid', dirname=self.testpath )
		cm = ConfigManager( inifps, write_back_on_desctruction=False )
		
		# check created section
		cm.config.getSection( "myNewSection" ).getKey( "myNewKey" )
		
		# assure removed section is not there
		self.failUnlessRaises( NoSectionError, cm.config.getSection, *["section_to_be_removed"] )
		
		# check added key
		self.failUnless( cm.config.getSection( "section" ).getKey( "anotherNewKey" ).value == "thisDefaultValue" )
		
		# assure removed keys are gone
		self.failUnlessRaises( NoOptionError, cm.config.getSection( "section_removekey_2" ).getKey, *[ "key_2" ] )
		# this key may be there as it is used in two writable section in different nodes
		# we only apply changed sections to the first section we find
		cm.config.getSection( "section_nonunique" ).getKey( "key_nonunique" )
		
		
		# check appended values
		self.failUnless( "appendedValue" in cm.config.getSection( "section_addkeyvals" ).getKey( "key3" ).values )
		for val in ( "appendedValue2", "anotherappendedValue" ):
			self.failUnless( val in cm.config.getSection( "section_addkeyvals" ).getKey( "key4" ).values )
		
			
		# check removed value
		self.failUnless( "val2" not in cm.config.getSection( "section_removeval" ).getKey( "key_rmval" ).values )
		
		
	def tearDown( self ):
		""" Remove the temporary working files """ 
		#shutil.rmtree( self.testpath, ignore_errors=False )
		
		
		

class TestConfigDiffer( unittest.TestCase ):
	""" Test the ConfigDiffer Class and all its featuers"""
	

	def _getDiff( self, testid ):
		"""@param testid: the name of the test, it looks for 'valid_${id}_a|b" respectively
		@return: ConfigDiffer initialized to the A and B files of test with id """
		pre = "valid_"
		filenames = []
		for char in 'ab':
			filenames.extend( _getPrefixedINIFileNames( pre + testid + "_" + char ) )
		
		self.assertEquals( len( filenames ) , 2 )
		filefps = _tofp( filenames )
		accs = ( ConfigAccessor(), ConfigAccessor() )
		for ca,fp in izip( accs, filefps ):
			ca.readfp( fp )
			
		return ConfigDiffer( accs[0], accs[1] )
	
	def _checkLengths( self, diff, assertadded, assertremoved, assertchanged, assertunchanged ):
		""" Helper checking de length of the given diff delta lists 
		Fail test if the given numbers do not match the actual numbers """
		# print str(diff)
		self.failUnless( len( diff.added ) == assertadded and len( diff.removed ) == assertremoved and 
						 len( diff.changed ) == assertchanged and len( diff.unchanged )== assertunchanged )
		
		
	def test_sectionAdded( self ):
		"""ConfigDiffer: Assure diffing will detect removed sections """
		self._checkLengths( self._getDiff( "sectionremoved" ), 0, 1, 0, 1 ) 
	
	def test_sectionAddedRemoved( self ):                              
		"""ConfigDiffer: Assure diffing will detect removed and added sections """
		self._checkLengths( self._getDiff( "sectionaddedremoved" ), 0, 1, 0, 1 )
		
	def test_sectionAddedRemoved( self ):
		"""ConfigDiffer: Assure diffing will detect removed and added sections """
		self._checkLengths( self._getDiff( "sectionaddedremoved" ), 1, 1, 0, 1 ) 
	
	def test_sectionMultiChange( self ):
		"""ConfigDiffer: Assure diffing will detect removed and added sections, no unchanged sections """
		self._checkLengths( self._getDiff( "sectionmultichange" ), 2, 1, 0, 0 )
		
	def test_keyadded( self ):
		"""ConfigDiffer: Assure added keys are detected"""
		diff = self._getDiff( "keyadded" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		# get changed section and assure there is exactly one key
		self.failUnless( len( iter( diff.changed ).next().added ) )
		
	def test_keyremoved( self ):
		"""ConfigDiffer: Assure removed keys are detected"""
		diff = self._getDiff( "keyremoved" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		# get changed section and assure there is exactly one key
		self.failUnless( len( diff.changed[0].removed ) )
		
	def test_keyvalueremoved( self ):
		"""ConfigDiffer: Assure removed key-values are detected"""
		diff = self._getDiff( "valueremoved" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		# get changed section and assure there is exactly one key
		self.failUnless( len( diff.changed[0].changed[0].removed ) )
	
	def test_keyvalueadded( self ):
		"""ConfigDiffer: Assure added key-values are detected"""
		diff = self._getDiff( "valueadded" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		# get changed section and assure there is exactly one key
		self.failUnless( len( diff.changed[0].changed[0].added ) )
	
	def test_keyvaluechanged( self ):
		"""ConfigDiffer: Assure changed key-values are detected as a removed and added value"""
		diff = self._getDiff( "valueaddedremoved" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		# get changed section and assure there is exactly one key
		key = diff.changed[0].changed[0]
		self.failUnless( len( key.added ) and len( key.removed ) )
		
	def test_propertydiffing( self ):
		"""ConfigDiffer: Assure that changes in properties are being detected"""
		diff = self._getDiff( "property_changes" )
		self._checkLengths( diff, 0, 0, 1, 0 )
		
		self.failUnless( len( diff.changed[0].changed[1].properties.added ) )	 # added key-property value
		self.failUnless( len( diff.changed[0].changed[0].properties.removed ) )	 # removed key-property value
		self.failUnless( len( diff.changed[0].properties.changed[0].removed ) )	 # section property value changed ( removed )
		self.failUnless( len( diff.changed[0].properties.changed[0].added ) )	 # section property value changed ( added ) 
		
		
		
	
		
def _getPrefixedINIFileNames( prefix, dirname = os.path.dirname( __file__ ) ):
	""" Return full paths to INI files of files with the given prefix
		
		They must be in the same path as this test file, and end with .ini
	"""
	return glob( os.path.join( dirname, prefix+"*.ini" ) )

def _tofp( filenamelist, mode='r' ):
	return [ ConfigFile( filename, mode ) for filename in filenamelist ]
	
def _getprefixedinifps( prefix, mode='r', dirname = os.path.dirname( __file__ ) ):
	return _tofp( _getPrefixedINIFileNames( prefix, dirname=dirname ), mode=mode )


def _getca( prefix ):
	"""@return: config accessor initialized with all files matching the given prefix"""
	ca = ConfigAccessor( ) 
	ca.readfp( _getprefixedinifps( prefix ) )
	return ca


#} END GROUP
