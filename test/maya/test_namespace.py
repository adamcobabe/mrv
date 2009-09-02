# -*- coding: utf-8 -*-
"""
Test the namespace methods



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
import mayarv.test.maya as common
from mayarv.maya.scene import Scene
from mayarv.maya.namespace import *
import mayarv.maya as bmaya
import maya.cmds as cmds
import os

class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """

	def test_checkNamespaces( self ):
		"""mayarv.maya.namespace: test all namespace functionality """
		bmaya.Scene.open( common.get_maya_file( "namespace.ma" ), force=True )

		rootns = Namespace( Namespace.rootNamespace )
		childns = rootns.getChildren( )
		self.failUnless( rootns.isRoot() )
		self.failUnless( len( childns ) == 3 )

		for ns in childns:
			self.failUnless( ns.getParent( ) == rootns )
			self.failUnless( ns.isAbsolute() )
			allChildren = ns.getChildrenDeep( )
			self.failUnless( len( allChildren ) == 2 )

			for child in allChildren:
				self.failUnless( len( child.getParentDeep() ) )

		# end for each childns

		self.failUnlessRaises( ValueError, rootns.delete )


		# create a few namespaces
		for ns in [ "newns", "newns:child", "longer:namespace",":hello:world:here" ]:
			curns = Namespace.getCurrent()
			newns = Namespace.create( ns )
			self.failUnless( newns.exists() )
			self.failUnless( Namespace.getCurrent() == curns )

			# test undo: creation
			cmds.undo()
			self.failUnless( not newns.exists() )
			cmds.redo()
			self.failUnless( newns.exists() )

			# test undo: change current
			newns.setCurrent()
			self.failUnless( Namespace.getCurrent() == newns )
			cmds.undo()
			self.failUnless( Namespace.getCurrent() == curns )




		# rename all children
		for ns in childns:
			newname = str( ns ) + "_renamed"
			renamedns = ns.rename( newname )
			self.failUnless( renamedns == renamedns )
			self.failUnless( renamedns.exists() )

		# delete all child namepaces
		childns = rootns.getChildren()

		# check relative namespace
		for ns in childns:
			self.failUnless( not ns.getRelativeTo( rootns ).isAbsolute() )

		for ns in childns:
			allchildren = ns.getChildrenDeep()
			ns.delete( move_to_namespace = rootns )
			self.failUnless( not ns.exists() )
			for child in allChildren:
				self.failUnless( not child.exists() )


		# ITER ROOT NAMESPACE - REAL OBJECTS
		curns = Namespace.getCurrent()
		numobjs = 0
		for obj in Namespace( ":" ).iterObjects( depth = 0 ):
			numobjs += 1
		self.failUnless( numobjs != 0 )
		self.failUnless( Namespace.getCurrent() == curns )

		# ITER STRINGS
		newnumobjs = 0
		for obj in Namespace( ":" ).listObjectStrings( depth = 0, as_strings = 1 ):
			newnumobjs += 1

		self.failUnless( Namespace.getCurrent() == curns )
		self.failUnless( newnumobjs == numobjs )

		# empty namespace must come out as root
		ns = Namespace( "" )
		self.failUnless( ns == Namespace.rootNamespace )

		# TEST SPLIT
		###########
		t = Namespace.splitNamespace( "hello:world" )
		self.failUnless( t[0] == ":hello" and t[1] == "world" )

		t = Namespace.splitNamespace( ":hello:world:there" )
		self.failUnless( t[0] == ":hello:world" and t[1] == "there" )


		# TEST TORELATIVE
		#################
		self.failUnless( Namespace( "hello" ).toRelative( ) == "hello" )
		self.failUnless( Namespace( ":hello" ).toRelative( ) == "hello" )

		# TEST REPLACEMENT
		#####################
		rootrel,rootabs,nsrel,nsabs,multins,multinabs = "rootnsrel", ":rootnsabs", "ns:relns", ":ns:absolutens", "ns1:ns2:multinsrel",":ns1:ns2:ns3:ns2:multinabs"
		rootns,ns,ns2 = Namespace( "" ),Namespace("ns",absolute=False),Namespace( "ns2",absolute=False )
		newnssingle = Namespace( "nns" )
		newnsmulti = Namespace( "nns1:nns2" )

		self.failUnless( rootns.substitute( rootrel, newnssingle ) == ":nns:rootnsrel" )
		self.failUnless( rootns.substitute( rootrel, newnsmulti ) == ":nns1:nns2:rootnsrel" )

		self.failUnless( rootns.substitute( rootabs, newnssingle ) == ":nns:rootnsabs" )
		self.failUnless( rootns.substitute( rootabs, newnsmulti ) == ":nns1:nns2:rootnsabs" )

		self.failUnless( ns2.substitute( multins, newnssingle ) == "ns1:nns:multinsrel" )
		self.failUnless( ns2.substitute( multins, newnsmulti ) == "ns1:nns1:nns2:multinsrel" )

		self.failUnless( ns2.substitute( multinabs, newnssingle ) == ":ns1:nns:ns3:nns:multinabs" )
		self.failUnless( ns2.substitute( multinabs, newnsmulti ) == ":ns1:nns1:nns2:ns3:nns1:nns2:multinabs" )

		# empty replacement - remove ns
		self.failUnless( ns2.substitute( multins, "" ) == "ns1:multinsrel" )
		self.failUnless( ns.substitute( nsabs, "" ) == ":absolute" )
