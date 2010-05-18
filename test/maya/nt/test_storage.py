# -*- coding: utf-8 -*-
""" Test storage system and storage node """
from mrv.test.maya import *
import mrv.maya.nt as nt
import mrv.maya as mrvmaya
from mrv.path import Path

import maya.cmds as cmds

import tempfile

class TestStorage( unittest.TestCase ):
	@with_undo
	@with_persistence
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

		def fix_ascii_file(filepath):
			"""Unfortunately, on windows and osx and maya2011, 
			ascii's tend to corrupt themselves by writing ',' 
			into floats which should be a '.'. Could be something
			related to the locale too. Nonetheless, we have to 
			fix it and do a stupid find a replace"""
			if filepath.ext() != '.ma':
				return
			
			tmpfile = Path(tempfile.mktemp())
			ofh = open(tmpfile, 'wb')
			for line in open(filepath):
				ofh.write(line.replace(',', '.'))
			# END for each line
			ofh.close()
			
			filepath.remove()
			tmpfile.move(filepath)
	

		did = "test"
		for filetype in [ ".ma", ".mb" ]:
			mrvmaya.Scene.new( force = True )

			# BASIC DATA CREATION AND EDITING
			####################################
			storagenode = nt.createNode( "storage", "storageNode" )
			refcomparator = nt.createNode( "trans", "transform" )

			pyval = storagenode.pythonData( did, autoCreate = True )

			# adjust the value - will be changed in place
			setTestValue( pyval )

			# SAVE AND LOAD !
			#################
			# ascii and binary ( including reference test )
			filepath = tmpdir / ( "storagetest" + filetype )
			mrvmaya.Scene.save( filepath )
			fix_ascii_file(filepath)

			# reload
			mrvmaya.Scene.open( filepath, force=True )

			# get and test data
			storagenode = nt.Node( "storage" )
			pyvalloaded = storagenode.pythonData( did, autoCreate = False )
			checkTestValue( self, pyvalloaded )


			# CLEAR NON-EMPTY DATA WITH UNDO
			##################################
			storagenode.clearData( did )
			pydatacleared = storagenode.pythonData( did, autoCreate =False )
			assert not pydatacleared.has_key( "string" ) 

			cmds.undo()
			pydataundone = storagenode.pythonData( did, autoCreate =False )
			assert pydataundone.has_key( "string" ) 


			# CREATE REFERENCE
			##################
			mrvmaya.Scene.new( force = True )
			mrvmaya.ref.createReference( filepath, namespace="referenced" )

			refstoragenode = nt.Node( "referenced:storage" )
			refcomparator = nt.Node( "referenced:trans" )
			pyval = refstoragenode.pythonData( did )

			# adjust values
			pyval[ "refchange" ] = "changed in reference"
			refcomparator.tx.msetFloat( 5.5 )

			# save reference
			filewithrefpath = tmpdir / ( "refstoragetest" + filetype )
			mrvmaya.Scene.save( filewithrefpath )
			fix_ascii_file(filewithrefpath)
			mrvmaya.Scene.open( filewithrefpath, force = True )

			# check test value and the newly written one
			refstoragenode = nt.Node( "referenced:storage" )
			pyval = refstoragenode.pythonData( did )

			checkTestValue( self, pyval )
			sval = pyval[ 'refchange' ]
			assert sval == "changed in reference" 


			# DUPLICATION
			###############
			for is_shallow in range( 2 ):
				duplicate = refstoragenode.duplicate( shallow = is_shallow )
				ddata = duplicate.pythonData( did )
				data = refstoragenode.pythonData( did )
				checkTestValue( self, ddata )

				# assure that its a real copy , not just something shallow
				if not is_shallow:
					data[ 'other' ] = 2
					assert not ddata.has_key( 'other' ) 
			# END for each copy type

		# END for each filetype


	@with_persistence
	def test_storageAttributeHanlding( self ):
		mrvmaya.Scene.new( force = True )
		snode = nt.createNode( "storage",  "storageNode" )

		# autocreate off
		self.failUnlessRaises( AttributeError, snode.pythonData, "test" )

		data = snode.dta
		val = snode.pythonData( "test", autoCreate=True )
		oval = snode.pythonData( "othertest", autoCreate=True )
		assert len( data ) == 2 
		# have two right now, no prefix
		assert len( snode.dataIDs() ) == 2 

		# CLEAR EMPTY DATA
		######################
		snode.clearData( "test" )


		# PREFIXES
		############
		snode._attrprefix = "prefix"				# must create new one
		pval = snode.pythonData( "othertest", autoCreate=True )
		assert len( data ) == 3 
		assert pval._plug.mparent().mchildByName('id').asString() == "prefixothertest" 

		# now that we have a prefix, we only see prefixed attributes
		assert len( snode.dataIDs() ) == 1 

		# STORAGE PLUGS ( MAIN PLUG )
		# contains connection plug too
		mainplug = snode.findStoragePlug( "othertest" )
		assert mainplug == pval._plug.mparent() 


		# CONNECTION PLUGS
		###################
		persp = nt.Node( "persp" )

		conarray = mainplug.mchildByName('dmsg')
		for c in range( 10 ):
			nextplug = conarray.elementByLogicalIndex( c )
			persp.message.mconnectTo(nextplug)
			assert persp.message.misConnectedTo(nextplug) 
		assert len( conarray ) == 10 
		assert len( persp.message.moutputs() ) == 10 

	@with_undo
	@with_persistence
	def test_storageSetHandling( self ):
		mrvmaya.Scene.new( force = True )
		snode = nt.createNode( "storage",  "storageNode" )

		# SIMPLE SET
		did = "objset"
		
		# error checking 
		
		objset = snode.objectSet( did, 0, autoCreate = True )
		assert isinstance( objset, nt.ObjectSet ) 
		assert len(snode.setsByID(did)) == 1

		# does not exist anymore
		cmds.undo()
		self.failUnlessRaises( AttributeError, snode.objectSet, did, 0, autoCreate = False )

		# objset should be valid again
		cmds.redo()
		assert objset.isValid() and objset.isAlive() 

		# del set
		snode.deleteObjectSet( did, 0 )
		assert not objset.isValid() and objset.isAlive() 
		self.failUnlessRaises( AttributeError, snode.objectSet, did, 0, False ) 
		cmds.undo()
		assert objset.isValid() 
		assert snode.objectSet(did, 0, False) == objset
		cmds.redo()
		assert not objset.isValid() 
		self.failUnlessRaises( AttributeError, snode.objectSet, did, 0, False )
		cmds.undo()	# undo deletion after all
		assert objset.isValid()
		assert snode.objectSet(did, 0, False) == objset
		# SIMPLE OBJSET OPERATIONS

		# MULTIPLE SETS


		# PARTITION HANDLING
		#######################
		partition = snode.setPartition( did, True )
		assert snode.partition( did ) is not None 
		cmds.undo()
		assert snode.partition( did ) is None 
		cmds.redo()	# set is available again

		# delete the single set we have, partition should be gone as well
		snode.deleteObjectSet( did, 0 )
		assert not partition.isValid() 
		cmds.undo()
		assert partition.isValid() 

		# disable partition
		snode.setPartition( did, False )
		assert snode.isAlive() and snode.isValid() 		# recently it would be deleted
		assert snode.partition( did ) is None 
		snode.setPartition( did, True )

		# new set, check partition
		oset = snode.objectSet( did, 1, autoCreate = 1 )
		assert isinstance( oset, nt.ObjectSet ) 
		assert len( oset.partitions() ) == 1 
		assert oset.partitions()[0] == snode.partition( did ) 

		cmds.undo()
		assert len( oset.partitions() ) == 0 
		cmds.redo()

		# set is in multiple partitions, some from us, some from the user
		myprt = nt.createNode( "mypartition", "partition" )
		myprt.addSets( oset )
		assert myprt != snode.partition( did ) 
		snode.setPartition( did, False )
		assert myprt.sets( )[0] == oset 
		assert len( oset.partitions() ) == 1 

		# undo / redo
		cmds.undo()
		assert len( oset.partitions() ) == 2 
 		cmds.redo()
		assert len( oset.partitions() ) == 1 




