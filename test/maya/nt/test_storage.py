# -*- coding: utf-8 -*-
""" Test storage system and storage node """
from mrv.test.maya import *
import mrv.maya.nt as nt
import mrv.maya.nt.persistence as persistence
import mrv.maya as mrvmaya
from mrv.path import Path
import maya.cmds as cmds
import tempfile


class StorageNetworkNodeWrong(nt.Network):
	# misses the __mrv_virtual_subtype__ attribute
	pass 
	
class StorageNetworkNode(nt.Network, nt.StorageBase):
	"""Implements a wrapper for a specially prepared Network node which has 
	StorageNode capabilities"""
	__mrv_virtual_subtype__ = 1
	
	def __init__(self, node):
		"""The overloaded initializer assures we do not wrap incompatible types"""
		if not hasattr(self, 'data'):
			raise TypeError("%r node is missing its data attribute" % self)
		# END handle type
		# assure we initialize our base - it requires some information to work
		super(StorageNetworkNode, self).__init__(node)
		
	@classmethod
	def create(cls):
		"""Create a new Network node with storage node capabilities"""
		n = nt.Network()
		n.addAttribute(persistence.createStorageAttribute(persistence.PyPickleData.kPluginDataId))
		return StorageNetworkNode(n.object())
		
	@classmethod
	def iter_instances(cls):
		for n in nt.iterDgNodes(nt.Node.Type.kAffect, asNode=False):
			try:
				yield StorageNetworkNode(n)
			except TypeError:
				continue
			# END try to wrap our type around
		# END for each network node
		
class TestStorage( unittest.TestCase ):
	
	@with_persistence
	def test_virtual_subtype(self):
		n = nt.Network()
		
		# types must define the __mrv_virtual_subtype__ attribute
		self.failUnlessRaises(TypeError, StorageNetworkNodeWrong, n.object())
		
		# make a StorageNetwork node 
		sn = StorageNetworkNode.create()
		assert isinstance(sn, StorageNetworkNode)
		
		# it cannot wrap ordinary network nodes - we implemented it that way
		self.failUnlessRaises(TypeError, StorageNetworkNode, n.object())
		
		# iteration works fine as well
		sns = list(StorageNetworkNode.iter_instances())
		assert len(sns) == 1 and isinstance(sns[0], StorageNetworkNode)
		assert sns[0] == sn
		
		# be sure we can use the storage interface
		assert isinstance(sn.dataIDs(), list)
		
	@with_persistence
	def test_replacing_default_node_types(self):
		n = nt.Network()
		sn = StorageNetworkNode.create()
		
		# REPLACING BUILTIN NODE TYPES
		##############################
		# if we want to play crazy, we can make all network nodes our special
		# storage node, be replacing the existing Network node type.
		# Any instantiation will fail as if its not one of our specialized nodes, 
		# but this is implementation defined of course.
		# Defining a new derived Type automatically puts it into the nt module
		OldNetwork = nt.Network
		class Network(StorageNetworkNode):
			def sayhello(self):
				print "hello"
		# yes, the official Network node is now our own one, automatically
		assert nt.Network is Network
		
		sn2 = nt.Node(str(sn))
		assert isinstance(sn2, StorageNetworkNode)
		assert isinstance(sn2.dataIDs(), list)
		
		# and it can say something
		sn2.sayhello()
		
		# we cannot wrap normal nodes as our initializer on StorageNetworkNode barks 
		# if the vital data plug cannot be found.
		self.failUnlessRaises(TypeError, nt.Node, str(n))
		
		# reset the old one, we affect everything within MRV now
		nt.removeCustomType(Network)
		nt.addCustomType(OldNetwork)
		
		# everything back to normal - we get plain old network nodes
		sn_network = nt.Node(sn.object())
		assert type(sn_network) is OldNetwork
		assert type(sn_network) is nt.Network
		
		# REPLACING BUILTIN NODES PROPERLY
		##################################
		class Network(OldNetwork, nt.StorageBase):
			def __init__(self, node):
				"""Implement the initializer such that we only initialize our base
				if we have the 'data' attribute. Otherwise we keep it uninitialized, so it 
				will not be functional"""
				try:
					super(Network, self).__init__(node)
				except TypeError:
					pass
				# END handle input type
				
			def sayaloha(self):
				print "aloha"
				
		# END better Super-Network implementation
		assert nt.Network is Network
		
		# now plain network nodes will be new Network nodes, but we are allowed
		# to create them
		# NodeFromObj works as well, just to be sure
		n2 = nt.NodeFromObj(n.object())
		assert type(n2) is Network
		
		# as the storage base has not been initialized, we cannot do anything 
		# with it. The actual point here though is that users who don't know the
		# interface will get a fully functional network node at least.
		# As we do not 'tighten' the interface, code that doesn't expect our type
		# will not get into trouble.
		self.failUnlessRaises(AttributeError, n2.dataIDs)
		assert isinstance(n2, OldNetwork)
		n2.sayaloha()
		
		# and storage network nodes will be 'Network' nodes whose additional
		# functions we can use
		sn2 = nt.Node(sn.object())
		assert type(sn2) is Network
		sn2.sayaloha()
		sn2.dataIDs()
		
		# once again, get rid of our custom type, reset the old one 
		nt.removeCustomType(Network)
		nt.addCustomType(OldNetwork)
		assert nt.Network is OldNetwork
		
	
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




