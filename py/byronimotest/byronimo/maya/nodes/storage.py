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
import maya.cmds as cmds 
import tempfile
from byronimo.path import Path
import sys

class TestStorage( unittest.TestCase ):
	""" Test general maya framework """
	
	
	def test_storagePickleData( self ):
		"""byronimo.maya.nodes.storage: test pickle data"""
		tmpdir = Path( tempfile.gettempdir() )
		
		def setTestValue( mydict ):
			mydict['string'] = "hello world"
			mydict[1] = 3.0
			mydict["list"] = ["this", 2, 45.0]
			
		def checkTestValue( self, mydict ):
			sval = mydict.get( "string" )
			self.failUnless( sval == "hello world" )
			
			fval = mydict.get( 1 )
			self.failUnless( fval == 3.0 )
							  
			lval = mydict.get( "list" )
			self.failUnless( len( lval ) == 3 )
		
		
		for filetype in [ ".ma", ".mb" ]:
			bmaya.Scene.new( force = True )
			
			# BASIC DATA CREATION AND EDITING 
			####################################
			storagenode = nodes.createNode( "storage", "StorageNode" )
			refcomparator = nodes.createNode( "trans", "transform" )
		
			# fail as it does not yet exist
			pyval = storagenode.getPythonData( "test", autoCreate = True )


			# adjust the value - will be changed in place
			setTestValue( pyval )

			# SAVE AND LOAD !
			#################
			# ascii and binary ( including reference test )
			filepath = tmpdir / ( "storagetest" + filetype )
			print "testing %s" % filepath
			bmaya.Scene.save( filepath )
		
			# reload 
			bmaya.Scene.open( filepath, force=True )
			
			# get and test data 
			storagenode = nodes.Node( "storage" )
			pyvalloaded = storagenode.getPythonData( "test", autoCreate = False )
			
			checkTestValue( self, pyvalloaded )
			
			# CREATE REFERENCE
			##################
			bmaya.Scene.new( force = True )
			bmaya.Scene.createReference( filepath, namespace="referenced" )
			
			refstoragenode = nodes.Node( "referenced:storage" )
			refcomparator = nodes.Node( "referenced:trans" )
			pyval = refstoragenode.getPythonData( "test" )
			
			# adjust values 
			pyval[ "refchange" ] = "changed in reference"
			refcomparator.translate.tx.setFloat( 5.5 )

			# save reference 
			filewithrefpath = tmpdir / ( "refstoragetest" + filetype )
			bmaya.Scene.save( filewithrefpath )
			bmaya.Scene.open( filewithrefpath, force = True )
			print "referencetestfile: %s " % filewithrefpath
			
			# check test value and the newly written one 
			refstoragenode = nodes.Node( "referenced:storage" )
			pyval = refstoragenode.getPythonData( "test" )
			
			checkTestValue( self, pyval )
			sval = pyval[ 'refchange' ]
			self.failUnless( sval == "changed in reference" )
		# END for each filetype 
		
	
	def test_storageAttributeHanlding( self ):
		"""byronimo.maya.nodes.storage: test of the attribute accesss on storages is working"""
		bmaya.Scene.new( force = True )
		snode = nodes.createNode( "storage",  "StorageNode" )
		
		# autocreate off
		self.failUnlessRaises( AttributeError, snode.getPythonData, "test" )
		
		data = snode.dta
		val = snode.getPythonData( "test", autoCreate=True )
		oval = snode.getPythonData( "othertest", autoCreate=True )
		self.failUnless( len( data ) == 2 )
		
		# PREFIXES
		############
		snode._attrprefix = "prefix"				# must create new one 
		pval = snode.getPythonData( "othertest", autoCreate=True )
		self.failUnless( len( data ) == 3 )
		self.failUnless( pval._plug.getParent().id.asString() == "prefixothertest" )
		
		
		# STORAGE PLUGS ( MAIN PLUG )
		# contains connection plug too 
		mainplug = snode.findStoragePlug( "othertest" )
		self.failUnless( mainplug == pval._plug.getParent() )
		
		
		# CONNECTION PLUGS 
		###################
		persp = nodes.Node( "persp" )
		
		conarray = mainplug.dmsg
		for c in range( 10 ):
			nextplug = conarray.getByLogicalIndex( c )
			persp.message >> nextplug 
			self.failUnless( persp.message >= nextplug )
		self.failUnless( len( conarray ) == 10 )
		self.failUnless( len( persp.message.p_outputs ) == 10 )
		
	def test_storageSetHandling( self ):
		"""byronimo.maya.nodes.storage: test built-in sethandling"""
		bmaya.Scene.new( force = True )
		snode = nodes.createNode( "storage",  "StorageNode" )
		
		# SIMPLE SET 
		did = "objset"
		objset = snode.getObjectSet( did, 0, autoCreate = True )
		self.failUnless( isinstance( objset, nodes.ObjectSet ) )
		
		# does not exist anymore
		cmds.undo()
		self.failUnlessRaises( ValueError, snode.getObjectSet, did, 0, autoCreate = False )
		
		# objset should be valid again
		cmds.redo()
		self.failUnless( objset.isValid() and objset.isAlive() )
		
		# SIMPLE OBJSET OPERATIONS 
		
		# MULTIPLE SETS 
		
		
		
		# PARTITION HANDLING 
		snode.setPartition( did, 1 )
		self.failUnless( snode.getPartition( did ) != None )
		
		snode.setPartition( did, 0 )
		self.failUnless( snode.getPartition( did ) is None )
		
		
		
		
