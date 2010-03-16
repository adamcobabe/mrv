# -*- coding: utf-8 -*-
""" Test storage system and storage node """
from mayarv.test.maya import *
import mayarv.maya.nt as nt
import mayarv.maya as bmaya
from mayarv.path import Path
import maya.cmds as cmds
import tempfile


class TestStorage( unittest.TestCase ):
	def test_storagePickleData( self ):
		tmpdir = Path( tempfile.gettempdir() )

		def setTestValue( mydict ):
			mydict['string'] = "hello world"
			mydict[1] = 3.0
			mydict["list"] = ["this", 2, 45.0]

		def checkTestValue( self, mydict ):
			sval = mydict.get( "string" )
			assert sval == "hello world" 

			fval = mydict.get( 1 )
			assert fval == 3.0 

			lval = mydict.get( "list" )
			assert len( lval ) == 3 


		for filetype in [ ".ma", ".mb" ]:
			bmaya.Scene.new( force = True )

			# BASIC DATA CREATION AND EDITING
			####################################
			storagenode = nt.createNode( "storage", "storageNode" )
			refcomparator = nt.createNode( "trans", "transform" )

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
			storagenode = nt.Node( "storage" )
			pyvalloaded = storagenode.getPythonData( "test", autoCreate = False )

			checkTestValue( self, pyvalloaded )


			# CLEAR NON-EMPTY DATA WITH UNDO
			##################################
			storagenode.clearData( "test" )
			pydatacleared = storagenode.getPythonData( "test", autoCreate =False )
			assert not pydatacleared.has_key( "string" ) 

			cmds.undo()
			pydataundone = storagenode.getPythonData( "test", autoCreate =False )
			assert pydataundone.has_key( "string" ) 


			# CREATE REFERENCE
			##################
			bmaya.Scene.new( force = True )
			bmaya.ref.createReference( filepath, namespace="referenced" )

			refstoragenode = nt.Node( "referenced:storage" )
			refcomparator = nt.Node( "referenced:trans" )
			pyval = refstoragenode.getPythonData( "test" )

			# adjust values
			pyval[ "refchange" ] = "changed in reference"
			refcomparator.tx.mrvsetFloat( 5.5 )

			# save reference
			filewithrefpath = tmpdir / ( "refstoragetest" + filetype )
			bmaya.Scene.save( filewithrefpath )
			bmaya.Scene.open( filewithrefpath, force = True )

			# check test value and the newly written one
			refstoragenode = nt.Node( "referenced:storage" )
			pyval = refstoragenode.getPythonData( "test" )

			checkTestValue( self, pyval )
			sval = pyval[ 'refchange' ]
			assert sval == "changed in reference" 


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
					assert not ddata.has_key( 'other' ) 
			# END for each copy type




		# END for each filetype


	def test_storageAttributeHanlding( self ):
		bmaya.Scene.new( force = True )
		snode = nt.createNode( "storage",  "storageNode" )

		# autocreate off
		self.failUnlessRaises( AttributeError, snode.getPythonData, "test" )

		data = snode.dta
		val = snode.getPythonData( "test", autoCreate=True )
		oval = snode.getPythonData( "othertest", autoCreate=True )
		assert len( data ) == 2 
		# have two right now, no prefix
		assert len( snode.getDataIDs() ) == 2 

		# CLEAR EMPTY DATA
		######################
		snode.clearData( "test" )


		# PREFIXES
		############
		snode._attrprefix = "prefix"				# must create new one
		pval = snode.getPythonData( "othertest", autoCreate=True )
		assert len( data ) == 3 
		assert pval._plug.mrvgetParent().mrvgetChildByName('id').asString() == "prefixothertest" 

		# now that we have a prefix, we only see prefixed attributes
		assert len( snode.getDataIDs() ) == 1 

		# STORAGE PLUGS ( MAIN PLUG )
		# contains connection plug too
		mainplug = snode.findStoragePlug( "othertest" )
		assert mainplug == pval._plug.mrvgetParent() 


		# CONNECTION PLUGS
		###################
		persp = nt.Node( "persp" )

		conarray = mainplug.mrvgetChildByName('dmsg')
		for c in range( 10 ):
			nextplug = conarray.getElementByLogicalIndex( c )
			persp.message.mrvconnectTo(nextplug)
			assert persp.message.mrvisConnectedTo(nextplug) 
		assert len( conarray ) == 10 
		assert len( persp.message.mrvgetOutputs() ) == 10 

	def test_storageSetHandling( self ):
		bmaya.Scene.new( force = True )
		snode = nt.createNode( "storage",  "storageNode" )

		# SIMPLE SET
		did = "objset"
		
		# error checking 
		
		objset = snode.getObjectSet( did, 0, autoCreate = True )
		assert isinstance( objset, nt.ObjectSet ) 
		assert len(snode.getSetsByID(did)) == 1

		# does not exist anymore
		cmds.undo()
		self.failUnlessRaises( AttributeError, snode.getObjectSet, did, 0, autoCreate = False )

		# objset should be valid again
		cmds.redo()
		assert objset.isValid() and objset.isAlive() 

		# del set
		snode.deleteObjectSet( did, 0 )
		assert not objset.isValid() and objset.isAlive() 
		self.failUnlessRaises( AttributeError, snode.getObjectSet, did, 0, False ) 
		cmds.undo()
		assert objset.isValid() 
		assert snode.getObjectSet(did, 0, False) == objset
		cmds.redo()
		assert not objset.isValid() 
		self.failUnlessRaises( AttributeError, snode.getObjectSet, did, 0, False )
		cmds.undo()	# undo deletion after all
		assert objset.isValid()
		assert snode.getObjectSet(did, 0, False) == objset
		# SIMPLE OBJSET OPERATIONS

		# MULTIPLE SETS


		# PARTITION HANDLING
		#######################
		partition = snode.setPartition( did, True )
		assert snode.getPartition( did ) is not None 
		cmds.undo()
		assert snode.getPartition( did ) is None 
		cmds.redo()	# set is available again

		# delete the single set we have, partition should be gone as well
		snode.deleteObjectSet( did, 0 )
		assert not partition.isValid() 
		cmds.undo()
		assert partition.isValid() 

		# disable partition
		snode.setPartition( did, False )
		assert snode.isAlive() and snode.isValid() 		# recently it would be deleted
		assert snode.getPartition( did ) is None 
		snode.setPartition( did, True )

		# new set, check partition
		oset = snode.getObjectSet( did, 1, autoCreate = 1 )
		assert isinstance( oset, nt.ObjectSet ) 
		assert len( oset.getPartitions() ) == 1 
		assert oset.getPartitions()[0] == snode.getPartition( did ) 

		cmds.undo()
		assert len( oset.getPartitions() ) == 0 
		cmds.redo()

		# set is in multiple partitions, some from us, some from the user
		myprt = nt.createNode( "mypartition", "partition" )
		myprt.addSets( oset )
		assert myprt != snode.getPartition( did ) 
		snode.setPartition( did, False )
		assert myprt.getSets( )[0] == oset 
		assert len( oset.getPartitions() ) == 1 

		# undo / redo
		cmds.undo()
		assert len( oset.getPartitions() ) == 2 
 		cmds.redo()
		assert len( oset.getPartitions() ) == 1 




