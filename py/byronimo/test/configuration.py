"""B{byronimo.test.configuration}
Test all aspects of the configuration management system

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='you@somedomain.tld'
__version__=1
__license__='GPL'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"


import unittest
import os
import sys
from ConfigParser import *
from byronimo.configuration import *


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
		""" Tests whether default dicts can actually be handled by the converter """
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
		""" Tests whether malformed strings trigger exceptions if malformed
			This is part of the classes sanity checks
		"""
		sdarg = [ _ConverterLibrary.simple_dict ]
		args = [ 
				( sdarg, { 'description' : "DESC\nnewline" } ),
				]
				
		for argvals in args:
			self.failUnlessRaises( ValueError, DictToINIFile, *argvals[0],**argvals[1] )
		
	
			
class TestConfigAccessor( unittest.TestCase ):
	""" Test the ConfigAccessor Class and all its featuers"""
	#{ Helper Methods
	@staticmethod
	def _getPrefixedINIFileNames( prefix ):
		""" Return full paths to INI files of files with the given prefix
			
			They must be in the same path as this test file, and end with .ini
		"""
		from glob import glob
		import os.path as path
		return glob( os.path.join( path.dirname( __file__ ), prefix+"*.ini" ) )
	
	@staticmethod
	def _tofp( filenamelist, mode='r' ):
		return [ ConfigFile( filename, mode ) for filename in filenamelist ]
		
	@staticmethod
	def _getprefixedinifps( prefix, mode='r' ):
		return TestConfigAccessor._tofp( TestConfigAccessor._getPrefixedINIFileNames( prefix ), mode=mode )
		
	@typecheck_param( object, ConfigAccessor, list )
	def _verifiedRead( self, ca, fileobjectlist, close_fp = True ):
		""" Assure that the given list of file objects can be read properly by ca
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
		
		print cca
		# diff the configurations
		
	#}
	
	def test_readValidINI( self ):
		"""Tests whether non-malformed INI files can be read """
		ca = ConfigAccessor()
		inifps = TestConfigAccessor._getprefixedinifps( 'valid' )
		inifps.append( DictConfigINIFile( os.environ ) )
		for ini in inifps:
			self._verifiedRead( ca, [ ini ] )  
		
		# try to read all files in a row 
		self._verifiedRead( ca, TestConfigAccessor._getprefixedinifps( 'valid' ) )	
		
		
	def test_readmultiValidINI( self ):
		""" Test whether configuration chains can be read """
		pass 
		
	def test_readInvalidINI( self ):
		""" Tests whether malformed INI files raise """
		pass
	
