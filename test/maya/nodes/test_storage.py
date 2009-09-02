# -*- coding: utf-8 -*-
"""
Test storage system and storage node



"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import mayarv.maya.nodes.storage as storage
import mayarv.maya.nodes as nodes
import maya.OpenMaya as api
import mayarv.maya as bmaya
import maya.cmds as cmds
import tempfile
from mayarv.path import Path
import sys
import mayarv.test.maya.nodes as ownpackage

class TestStorage( unittest.TestCase ):
	""" Test general maya framework """


	def test_storagePickleData( self ):
		"""mayarv.maya.nodes.storage: test pickle data"""
		if not ownpackage.mayRun( "storage" ): return
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
			bmaya.Scene.save( filepath )

			# reload
			bmaya.Scene.open( filepath, force=True )

			# get and test data
			storagenode = nodes.Node( "storage" )
			pyvalloaded = storagenode.getPythonData( "test", autoCreate = False )

			checkTestValue( self, pyvalloaded )


			# CLEAR NON-EMPTY DATA WITH UNDO
			##################################
			storagenode.clearData( "test" )
			pydatacleared = storagenode.getPythonData( "test", autoCreate =False )
			self.failUnless( not pydatacleared.has_key( "string" ) )

			cmds.undo()
			pydataundone = storagenode.getPythonData( "test", autoCreate =False )
			self.failUnless( pydataundone.has_key( "string" ) )


			# CREATE REFERENCE
			##################
			bmaya.Scene.new( force = True )
			bmaya.Scene.createReference( filepath, namespace="referenced" )

			refstoragenode = nodes.Node( "referenced:storage" )
			refcomparator = nodes.Node( "referenced:trans" )
			pyval = refstoragenode.getPythonData( "test" )

			# adjust values
			pyval[ "refchange" ] = "changed in reference"
			refcomparator.translate['tx'].setFloat( 5.5 )

			# save reference
			filewithrefpath = tmpdir / ( "refstoragetest" + filetype )
			bmaya.Scene.save( filewithrefpath )
			bmaya.Scene.open( filewithrefpath, force = True )

			# check test value and the newly written one
			refstoragenode = nodes.Node( "referenced:storage" )
			pyval = refstoragenode.getPythonData( "test" )

			checkTestValue( self, pyval )
			sval = pyval[ 'refchange' ]
			self.failUnless( sval == "changed in reference" )


			# DUPLICATION
			###############
			for is_shallow in range( 2 ):
				duplicate = refstoragenode.duplicate( shallow = is_shallow )
				ddata = duplicate.getPythonData( "test" )
				data = refstoragenode.getPythonData( "test" )
				checkTestValue( self, ddata )

				# assure that its a real copy , not just something shallow
				if not is_shallow:
					data[ 'other' ] = 2
					self.failUnless( not ddata.has_key( 'other' ) )
			# END for each copy type




		# END for each filetype


	def test_storageAttributeHanlding( self ):
		"""mayarv.maya.nodes.storage: test of the attribute accesss on storages is working"""
		if not ownpackage.mayRun( "storage" ): return
		bmaya.Scene.new( force = True )
		snode = nodes.createNode( "storage",  "StorageNode" )

		# autocreate off
		self.failUnlessRaises( AttributeError, snode.getPythonData, "test" )

		data = snode.dta
		val = snode.getPythonData( "test", autoCreate=True )
		oval = snode.getPythonData( "othertest", autoCreate=True )
		self.failUnless( len( data ) == 2 )
		# have two right now, no prefix
		self.failUnless( len( snode.getDataIDs() ) == 2 )

		# CLEAR EMPTY DATA
		######################
		snode.clearData( "test" )


		# PREFIXES
		############
		snode._attrprefix = "prefix"				# must create new one
		pval = snode.getPythonData( "othertest", autoCreate=True )
		self.failUnless( len( data ) == 3 )
		self.failUnless( pval._plug.getParent()['id'].asString() == "prefixothertest" )

		# now that we have a prefix, we only see prefixed attributes
		self.failUnless( len( snode.getDataIDs() ) == 1 )

		# STORAGE PLUGS ( MAIN PLUG )
		# contains connection plug too
		mainplug = snode.findStoragePlug( "othertest" )
		self.failUnless( mainplug == pval._plug.getParent() )


		# CONNECTION PLUGS
		###################
		persp = nodes.Node( "persp" )

		conarray = mainplug['dmsg']
		for c in range( 10 ):
			nextplug = conarray.getByLogicalIndex( c )
			persp.message >> nextplug
			self.failUnless( persp.message >= nextplug )
		self.failUnless( len( conarray ) == 10 )
		self.failUnless( len( persp.message.p_outputs ) == 10 )

	def test_storageSetHandling( self ):
		"""mayarv.maya.nodes.storage: test built-in sethandling"""
		if not ownpackage.mayRun( "storage" ): return
		bmaya.Scene.new( force = True )
		snode = nodes.createNode( "storage",  "StorageNode" )

		# SIMPLE SET
		did = "objset"
		objset = snode.getObjectSet( did, 0, autoCreate = True )
		self.failUnless( isinstance( objset, nodes.ObjectSet ) )

		# does not exist anymore
		cmds.undo()
		self.failUnlessRaises( AttributeError, snode.getObjectSet, did, 0, autoCreate = False )

		# objset should be valid again
		cmds.redo()
		self.failUnless( objset.isValid() and objset.isAlive() )

		# del set
		snode.deleteObjectSet( did, 0 )
		self.failUnless( not objset.isValid() and objset.isAlive() )
		cmds.undo()
		self.failUnless( objset.isValid() )
		cmds.redo()
		self.failUnless( not objset.isValid() )
		cmds.undo()	# undo deletion after all

		# SIMPLE OBJSET OPERATIONS

		# MULTIPLE SETS




		# PARTITION HANDLING
		#######################
		partition = snode.setPartition( did, True )
		self.failUnless( snode.getPartition( did ) is not None )
		cmds.undo()
		self.failUnless( snode.getPartition( did ) is None )
		cmds.redo()	# set is available again

		# delete the single set we have, partition should be gone as well
		snode.deleteObjectSet( did, 0 )
		self.failUnless( not partition.isValid() )
		cmds.undo()
		self.failUnless( partition.isValid() )

		# disable partition
		snode.setPartition( did, False )
		self.failUnless( snode.isAlive() and snode.isValid() )		# recently it would be deleted
		self.failUnless( snode.getPartition( did ) is None )
		snode.setPartition( did, True )

		# new set, check partition
		oset = snode.getObjectSet( did, 1, autoCreate = 1 )
		self.failUnless( isinstance( oset, nodes.ObjectSet ) )
		self.failUnless( len( oset.getPartitions() ) == 1 )
		self.failUnless( oset.getPartitions()[0] == snode.getPartition( did ) )

		cmds.undo()
		self.failUnless( len( oset.getPartitions() ) == 0 )
		cmds.redo()

		# set is in multiple partitions, some from us, some from the user
		myprt = nodes.createNode( "mypartition", "partition" )
		myprt.addSets( oset )
		self.failUnless( myprt != snode.getPartition( did ) )
		snode.setPartition( did, False )
		self.failUnless( myprt.getSets( )[0] == oset )
		self.failUnless( len( oset.getPartitions() ) == 1 )

		# undo / redo
		cmds.undo()
		self.failUnless( len( oset.getPartitions() ) == 2 )
 		cmds.redo()
		self.failUnless( len( oset.getPartitions() ) == 1 )




