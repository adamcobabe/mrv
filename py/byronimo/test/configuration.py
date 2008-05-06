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
		
		memfile.seek( 0 )
		
		# reread the configuration
		cca = ConfigAccessor( )
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
		inifps = inifps = _getprefixedinifps( 'invalid' )
		ca = ConfigAccessor( )
		for ini in inifps: 
			self.failUnlessRaises( ConfigParsingError, ca.readfp, ini ) 
	
	def test_iterators( self ):
		"""ConfigAccessor: assure that the provided iterators for sections and keys work """
		inifps = inifps = _getprefixedinifps( 'valid_4keys' )
		ca = ConfigAccessor( )
		ca.readfp( inifps )
		self.failUnless( len( list( ca.getSectionIterator( ) ) ) == 2 )
		self.failUnless( len( list( ca.getKeyIterator( ) ) ) == 4 )

		
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
		
def _getPrefixedINIFileNames( prefix ):
	""" Return full paths to INI files of files with the given prefix
		
		They must be in the same path as this test file, and end with .ini
	"""
	from glob import glob
	import os.path as path
	return glob( os.path.join( path.dirname( __file__ ), prefix+"*.ini" ) )

def _tofp( filenamelist, mode='r' ):
	return [ ConfigFile( filename, mode ) for filename in filenamelist ]
	
def _getprefixedinifps( prefix, mode='r' ):
	return _tofp( _getPrefixedINIFileNames( prefix ), mode=mode )



#} END GROUP
