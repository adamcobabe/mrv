"""B{byronimo.maya.test.reference}

Test the reference methods  

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
import byronimo.maya.test as common
from byronimo.maya.scene import Scene
import maya.OpenMaya as om
import maya.cmds as cmds 
from byronimo.maya.reference import *
from byronimo.maya.namespace import *
import byronimo.maya as bmaya
from byronimo.util import RegexHasMatch
import re
import os

	
class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """
	

	def test_listAndQuery( self ):
		"""byronimo.maya.reference: list some references and query their information """
		bmaya.Scene.open( common.get_maya_file( "refbase.ma" ) )
		allRefs = Scene.lsReferences( )
		self.failUnless( len( allRefs ) != 0 )
		
		for ref in allRefs:
			ref.getChildrenDeep( )		# try function
			
			self.failUnless( isinstance( ref.p_copynumber, int ) )
			self.failUnless( isinstance( ref.p_namespace, Namespace ) )
			
			# change root reference namespaces
			if ref.isRoot( ):
				curNS = ref.p_namespace
				ref.setNamespace( curNS.getBasename( ) + "_renamed" )
				self.failUnless( str( ref.getNamespace( ) ).endswith( "_renamed" ) )
			# END if is root
			
			# get children 
			
			def childTest( refobj ):
				subrefs = refobj.getChildren( )
				for subref in subrefs:
					self.failUnless( subref.getParent( ) )
					self.failUnless( not subref.isRoot() )
					childTest( subref )
			# END childTest
			
			childTest( ref )
			
			# load-unload test
			self.failUnless( ref.isLoaded( ) )
			ref.p_loaded = False
			self.failUnless( not ref.p_loaded )
			ref.p_loaded = True
			self.failUnless( ref.p_loaded )
			
			# lock test 
			self.failUnless( ref.isLocked( ) == False )
			ref.p_locked = True
			self.failUnless( ref.p_locked == True )
			ref.p_locked = False
			self.failUnless( ref.p_locked == False )
			
			ref.cleanup( )
			ref.cleanup( unresolvedEdits=False )
			
		# END for each reference
		
	def test_referenceCreation( self ):
		"""byronimo.maya.reference: create , delete and replace references"""
		# create some new references
		filenames = [ "sphere.ma", "cube.ma", "empty.ma", "cylinder.ma", "subrefbase.ma" ]
		newrefs = []
		for load in range( 2 ):
			for filename in filenames:
				newreffile = common.get_maya_file( filename )
				ref = FileReference.create( newreffile , load = load )
				self.failUnless( ref.p_loaded == load )
				self.failUnless( ref == newreffile )
				
				# try to create a reference with the same namespace
				self.failUnlessRaises( ValueError, ref.create, ref, load = load, namespace = ref.p_namespace )
				newrefs.append( ref )
			# END for each filename
		# END for load state 
		
		# delete all unloaded files
		loadedrefs = filter( lambda x: x.isLoaded(), newrefs )
		unloadedrefs = set( newrefs ) - set( loadedrefs )
		for ref in unloadedrefs:
			ref.remove( )
			self.failUnlessRaises( RuntimeError, ref.getNamespace )
			
		# cross-replace references
		for i in range( 0, 4, 2 ):
			ref = loadedrefs[ i ]
			oref = loadedrefs[ i + 1 ]
			refpath = str( ref )
			
			refreplace = ref.replace( oref )
			self.failUnless( refreplace == oref )
			
			orefreplace = oref.replace( refpath )
			self.failUnless( orefreplace == refpath )
		# END for each 2nd loaded ref
		
		
		# import references
		subrefbases = Scene.lsReferences( predicate = RegexHasMatch( re.compile( ".*subrefbase.ma" ) ) )
		self.failUnless( len( subrefbases ) == 3 )			# check predicate works 
		
		# slowly import step by step 
		firstsubref = subrefbases[0]
		childrefs = firstsubref.importRef( depth = 1 )
		self.failUnless( not cmds.objExists( firstsubref._refnode ) )
		self.failUnless( len( childrefs ) == 4 )
		
		# import alltogehter
		sndsubref = subrefbases[1]
		childrefs = sndsubref.importRef( depth = 0 )
		self.failUnless( len( childrefs ) == 0 )
		
		# final test
		finalsubref = subrefbases[2]
		self.failUnless( len( finalsubref.importRef( depth = 2 ) ) != 0 )
		
		

	
