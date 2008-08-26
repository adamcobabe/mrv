"""B{byronimotest.byronimo.maya.nodes.storage}

Test storage system and storage node

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import byronimo.maya.nodes.storage as storage
import byronimo.maya.nodes as nodes 
import maya.OpenMaya as api
import byronimo.maya as bmaya 

class TestStorage( unittest.TestCase ):
	""" Test general maya framework """
	
	def test_storageAccess( self ):
		"""byronimo.maya.nodes.iterators: todo"""
		storage = nodes.createNode( "storage", "StorageNode" )
		
		# TRY NUMERIC DATA
		####################
		numplug = storage.addAccept( "numeric" , MFnNumericData = api.MFnNumericData.kInt )
		
		# some sparse plug testing 
		n1 = numplug.getNextLogicalPlug()
		n1.setInt( 10 )
		self.failUnless( n1.getLogicalIndex( ) == 0 )
		self.failUnless( n1.asInt() == 10 )
		
		n2 = numplug.getNextLogicalPlug()
		n2.setInt( 20 )
		self.failUnless( n2.getLogicalIndex( ) == 1 )
		self.failUnless( n2.asInt() == 20 )
		
		# remove
		# NOTE: in 8.5, it seems not to be possible to remove numeric accepts - even if there is 
		# no child plug yet
		self.failUnlessRaises( RuntimeError , storage.removeAccept, "numeric", MFnNumericData = api.MFnNumericData.kInt )
		
		# remove nonexisting type
		# storage.removeAccept( "numeric", MFnNumericData = api.MFnNumericData.kShort )
		
		# remove on nonexisting plug 
		storage.removeAccept( "numericnoexist", MFnNumericData = api.MFnNumericData.kInt )
		
		# adding accepts twice fails
		self.failUnlessRaises( RuntimeError, storage.addAccept, "numeric" , MFnNumericData = api.MFnNumericData.kInt )
		
		
		# TRY TYPED DATA
		##################
		stringplug = storage.addAccept( "string" , MFnData = api.MFnData.kString )
		s1 = stringplug.getNextLogicalPlug( )
		
		sval = "hello world"
		s1.setString( sval )
		self.failUnless( s1.asString() == sval )
		
		stringplug.getNextLogicalPlug( ).setString( "another" )
		
		for elm in stringplug:
			print elm.asString( )
		
		# remove
		storage.removeAccept( "string", MFnData = api.MFnData.kString )
		
		# remove twice fails
		self.failUnlessRaises( RuntimeError, storage.removeAccept,  "string", MFnData = api.MFnData.kString )
		
		# TRY PLUGIN DATA
		
