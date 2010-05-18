# -*- coding: utf-8 -*-
""" Test the namespace methods """
from mrv.test.maya import *
from mrv.maya.ns import *
import mrv.maya as mrvmaya

import maya.cmds as cmds

class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """

	@with_undo
	@with_scene('namespace.ma')
	def test_checkNamespaces( self ):
		rootns = Namespace( Namespace.rootpath )
		childns = rootns.children( )
		assert rootns.isRoot() 
		assert len( childns ) == 3 

		for ns in childns:
			assert ns.parent( ) == rootns 
			assert ns.isAbsolute()
			assert ns.exists()
			allChildren = ns.childrenDeep( )
			assert len( allChildren ) == 2 

			for child in allChildren:
				assert len( child.parentDeep() ) 

		# end for each childns

		# cannot delete root namespace
		self.failUnlessRaises( ValueError, rootns.delete )
		
		# default constructor creates root namesapce
		assert Namespace() == RootNamespace


		# create a few namespaces
		for ns in [ "newns", "newns:child", "longer:namespace",":hello:world:here" ]:
			curns = Namespace.current()
			newns = Namespace.create( ns )
			assert newns.exists() 
			assert Namespace.current() == curns 

			# test undo: creation
			cmds.undo()
			assert not newns.exists() 
			cmds.redo()
			assert newns.exists() 

			# test undo: change current
			assert newns.setCurrent() == newns
			assert Namespace.current() == newns 
			cmds.undo()
			assert Namespace.current() == curns 




		# rename all children
		for ns in childns:
			newname = str( ns ) + "_renamed"
			renamedns = ns.rename( newname )
			assert renamedns == renamedns 
			assert renamedns.exists() 

		# delete all child namepaces
		childns = rootns.children()

		# check relative namespace
		for ns in childns:
			assert not ns.relativeTo( rootns ).isAbsolute() 

		for ns in childns:
			allchildren = ns.childrenDeep()
			ns.delete( move_to_namespace = rootns )
			assert not ns.exists() 
			for child in allChildren:
				assert not child.exists() 


		# ITER ROOT NAMESPACE - REAL OBJECTS
		curns = Namespace.current()
		numobjs = 0
		for obj in RootNamespace.iterNodes( depth = 0 ):
			numobjs += 1
		assert numobjs != 0 
		assert Namespace.current() == curns 

		# ITER STRINGS
		newnumobjs = 0
		for obj in Namespace( ":" ).iterNodes( depth = 0, asNode = 0 ):
			newnumobjs += 1

		assert newnumobjs == numobjs
		assert Namespace.current() == curns 
		 

		# empty namespace must come out as root
		ns = Namespace( "" )
		assert ns == Namespace.rootpath 

		# TEST SPLIT
		###########
		t = Namespace.splitNamespace( "hello:world" )
		assert t[0] == ":hello" and t[1] == "world" 

		t = Namespace.splitNamespace( ":hello:world:there" )
		assert t[0] == ":hello:world" and t[1] == "there" 


		# TEST TORELATIVE
		#################
		assert Namespace( "hello" ).toRelative( ) == "hello" 
		assert Namespace( ":hello" ).toRelative( ) == "hello" 

		# TEST REPLACEMENT
		#####################
		rootrel,rootabs,nsrel,nsabs,multins,multinabs = "rootnsrel", ":rootnsabs", "ns:relns", ":ns:absolutens", "ns1:ns2:multinsrel",":ns1:ns2:ns3:ns2:multinabs"
		rootns,ns,ns2 = Namespace( "" ),Namespace("ns",absolute=False),Namespace( "ns2",absolute=False )
		newnssingle = Namespace( "nns" )
		newnsmulti = Namespace( "nns1:nns2" )

		assert rootns.substitute( rootrel, newnssingle ) == ":nns:rootnsrel" 
		assert rootns.substitute( rootrel, newnsmulti ) == ":nns1:nns2:rootnsrel" 

		assert rootns.substitute( rootabs, newnssingle ) == ":nns:rootnsabs" 
		assert rootns.substitute( rootabs, newnsmulti ) == ":nns1:nns2:rootnsabs" 

		assert ns2.substitute( multins, newnssingle ) == "ns1:nns:multinsrel" 
		assert ns2.substitute( multins, newnsmulti ) == "ns1:nns1:nns2:multinsrel" 

		assert ns2.substitute( multinabs, newnssingle ) == ":ns1:nns:ns3:nns:multinabs" 
		assert ns2.substitute( multinabs, newnsmulti ) == ":ns1:nns1:nns2:ns3:nns1:nns2:multinabs" 

		# empty replacement - remove ns
		assert ns2.substitute( multins, "" ) == "ns1:multinsrel" 
		assert ns.substitute( nsabs, "" ) == ":absolute" 
		
		# namespaces have slots
		self.failUnlessRaises( AttributeError, setattr, ns, "myattr", 2 )
