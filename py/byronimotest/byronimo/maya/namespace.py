"""B{byronimo.maya.test.namespace}

Test the namespace methods  

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
import byronimotest.byronimo.maya as common
from byronimo.maya.scene import Scene
from byronimo.maya.namespace import *
import byronimo.maya as bmaya
import maya.cmds as cmds 
import os

class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """
	
	def test_checkNamespaces( self ):
		"""byronimo.maya.namespace: test all namespace functionality """
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
		for ns in [ "newns", "newns:child", "longer:namespace",":hello:world:here", ":" ]:
			curns = Namespace.getCurrent()
			newns = Namespace.create( ns )
			self.failUnless( newns.exists() )
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
		
		
		# empty namespace must come out as root 
		ns = Namespace( "" )
		self.failUnless( ns == Namespace.rootNamespace )
