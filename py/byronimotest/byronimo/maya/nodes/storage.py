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
		storagenode = nodes.createNode( "storage", "StorageNode" )
		
		# Check multuple values
		####################
		# fail as it does not yet exist
		self.failUnlessRaises( AttributeError, storagenode.getValueElement, "test", 0 )
		pyValue = storagenode.getValueElement( "test", 0, autoCreate = True )
		
		print pyValue
		
		# get another plug 
		#otherplug = storage.makePlug( "other" )
		#self.failUnless( testmainplug != otherplug and testmainplug.getLogicalIndex() != otherplug.getLogicalIndex() )
		
		# save and load !
		#################
		
		# ascii 
		
		# binary
		
		
		
		
