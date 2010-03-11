# -*- coding: utf-8 -*-
""" Test the reference methods """
import unittest
import mayarv.test.maya as common
import maya.cmds as cmds
from mayarv.maya.ref import *
from mayarv.maya.ns import *
import mayarv.maya as bmaya
from mayarv.util import RegexHasMatch
import re
import os


class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """


	def test_listAndQuery( self ):
		"""mayarv.maya.ref: list some references and query their information """
		bmaya.Scene.open( common.get_maya_file( "refbase.ma" ), force=True )
		allRefs = FileReference.ls( )

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

			refnode = ref.getReferenceNode( )
			self.failUnless( not isinstance( refnode, basestring ) )

			# it should always find our reference as well
			self.failUnless( FileReference.find( [ref] )[0] == ref )
			self.failUnless( FileReference.find( [ref], ignore_extension = True )[0] == ref )

		# END for each reference

	def test_referenceCreation( self ):
		"""mayarv.maya.ref: create , delete and replace references"""
		# create some new references
		bmaya.Scene.open( common.get_maya_file( "refbase.ma" ), force=True )
		filenames = [ "sphere.ma", "cube.ma", "empty.ma", "cylinder.ma", "subrefbase.ma" ]
		newrefs = []
		for load in range( 2 ):
			for filename in filenames:
				newreffile = common.get_maya_file( filename )
				ref = FileReference.create( newreffile , load = load )
				
				# quick iteration
				for node in ref.iterNodes( asNode = 1 ):
					pass

				self.failUnless( ref.p_loaded == load )
				
				# on windows inner maya paths use slash and paths outside of maya use backslash
				# would prefer to use normpath but python 2.5 is buggy with slash-backslash conversion here
				self.failUnless( os.path.abspath(ref) == newreffile ) 
				self.failUnless( ref.exists() )

				# try to create a reference with the same namespace
				#self.failUnlessRaises( ValueError, ref.create, ref, load = load, namespace = ref.p_namespace )
				newrefs.append( ref )

				# should found newref
				findresult = FileReference.find( [ ref ] )
				self.failUnless( len( findresult ) == 1 and findresult[0] == ref )
				self.failUnless( ref in findresult )	# see that >in< operator works


				# iterate the objects
				for node in ref.getNamespace( ).iterNodes( ):
					if node.getApiType() != api.MFn.kReference:
						filename = node.getReferenceFile( )
						self.failUnless( FileReference( filepath=filename ) == ref )
				# END for each node in filename

			# END for each filename
		# END for load state

		# delete all unloaded files
		loadedrefs = filter( lambda x: x.isLoaded(), newrefs )
		unloadedrefs = set( newrefs ) - set( loadedrefs )

		for ref in unloadedrefs:
			ref.remove( )
			self.failUnless( not ref.exists() )
			self.failUnlessRaises( RuntimeError, ref.getNamespace )

		# cross-replace references
		for i in range( 0, 4, 2 ):
			ref = loadedrefs[ i ]
			oref = loadedrefs[ i + 1 ]
			refpath = str( ref )

			refreplace = ref.replace( oref )
			self.failUnless( refreplace == str( oref ) )	# comparison with fileref might fail due to copy numbers

			orefreplace = oref.replace( refpath )
			self.failUnless( orefreplace == refpath )
		# END for each 2nd loaded ref


		# import references
		subrefbases = FileReference.ls( predicate = RegexHasMatch( re.compile( ".*subrefbase.ma" ) ) )
		self.failUnless( len( subrefbases ) == 2 )			# check predicate works

		# slowly import step by step
		firstsubref = subrefbases[0]
		childrefs = firstsubref.importRef( depth = 1 )
		self.failUnless( not cmds.objExists( firstsubref._refnode ) )
		self.failUnless( len( childrefs ) == 4 )

		# import alltogehter
		sndsubref = subrefbases[1]
		childrefs = sndsubref.importRef( depth = 0 )
		self.failUnless( len( childrefs ) == 0 )

		# NOTE: only have two  - the test changed
		# final test
		# finalsubref = subrefbases[2]
		# self.failUnless( len( finalsubref.importRef( depth = 2 ) ) != 0 )




