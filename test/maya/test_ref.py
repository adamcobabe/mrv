# -*- coding: utf-8 -*-
""" Test the reference methods """
import unittest
import mayarv.test.maya as common
import maya.cmds as cmds
from mayarv.maya.ref import *
from mayarv.maya.ns import *
import mayarv.maya as bmaya
import re
import os


class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """


	def test_listAndQuery( self ):
		"""mayarv.maya.ref: list some references and query their information """
		bmaya.Scene.open( common.get_maya_file( "refbase.ma" ), force=True )
		allRefs = FileReference.ls( )

		assert len( allRefs ) != 0 

		for ref in allRefs:
			ref.getChildrenDeep( )		# try function


			assert isinstance( ref.p_copynumber, int ) 
			assert isinstance( ref.p_namespace, Namespace ) 

			# change root reference namespaces
			if ref.isRoot( ):
				curNS = ref.p_namespace
				ref.setNamespace( curNS.getBasename( ) + "_renamed" )
				assert str( ref.getNamespace( ) ).endswith( "_renamed" ) 
			# END if is root

			# get children

			def childTest( refobj ):
				subrefs = refobj.getChildren( )
				for subref in subrefs:
					assert subref.getParent( ) 
					assert not subref.isRoot() 
					childTest( subref )
			# END childTest

			childTest( ref )

			# load-unload test
			assert ref.isLoaded( ) 
			ref.p_loaded = False
			assert not ref.p_loaded 
			ref.p_loaded = True
			assert ref.p_loaded 

			# lock test
			assert ref.isLocked( ) == False 
			ref.p_locked = True
			assert ref.p_locked == True 
			ref.p_locked = False
			assert ref.p_locked == False 

			ref.cleanup( )
			ref.cleanup( unresolvedEdits=False )

			refnode = ref.getReferenceNode( )
			assert not isinstance( refnode, basestring ) 

			# it should always find our reference as well
			assert FileReference.fromPaths( [ref] )[0] == ref 
			assert FileReference.fromPaths( [ref], ignore_extension = True )[0] == ref 

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

				assert ref.p_loaded == load 
				
				# on windows inner maya paths use slash and paths outside of maya use backslash
				# would prefer to use normpath but python 2.5 is buggy with slash-backslash conversion here
				assert os.path.abspath(ref.getPath()) == newreffile  
				assert ref.exists() 

				# try to create a reference with the same namespace
				#self.failUnlessRaises( ValueError, ref.create, ref, load = load, namespace = ref.p_namespace )
				newrefs.append( ref )
				
				# check getPath and copy number
				if ref.getCopyNumber() != 0:
					assert ref.getPath(copynumber=1) != ref.getPath(copynumber=0)
				# END check copy number

				# should found newref
				findresult = FileReference.fromPaths( [ ref ] )
				assert len( findresult ) == 1 and findresult[0].getPath() == ref.getPath() 
				assert ref.getPath() in findresult 	# see that >in< operator works


				# iterate the objects
				for node in ref.getNamespace( ).iterNodes( ):
					if node.getApiType() != api.MFn.kReference:
						filename = node.getReferenceFile( )
						assert FileReference( filepath=filename ) == ref 
				# END for each node in filename

			# END for each filename
		# END for load state
		
		assert len(newrefs) == len(filenames) * 2	# one for each load state
		
		# check hashing 
		newrefsset = set(newrefs)
		assert len(newrefsset) == len(newrefs)
		assert len(newrefsset | newrefsset) == len(newrefs)

		# delete all unloaded files
		loadedrefs = filter( lambda x: x.isLoaded(), newrefs )
		unloadedrefs = set( newrefs ) - set( loadedrefs )

		for ref in unloadedrefs:
			ref.remove( )
			assert not ref.exists() 
			self.failUnlessRaises( RuntimeError, ref.getNamespace )

		# cross-replace references
		for i in range( 0, 4, 2 ):
			ref = loadedrefs[ i ]
			oref = loadedrefs[ i + 1 ]
			refpath = str( ref )

			refreplace = ref.replace( oref )
			assert refreplace == str(oref)

			orefreplace = oref.replace( refpath )
			assert orefreplace == str(refpath)		# copy numbers may change things 
		# END for each 2nd loaded ref


		# import references
		subrefbases = FileReference.ls( predicate = lambda r: r.getPath().endswith("subrefbase.ma"))
		assert len( subrefbases ) == 2 			# check predicate works

		# slowly import step by step
		firstsubref = subrefbases[0]
		childrefs = firstsubref.importRef( depth = 0 )
		assert not cmds.objExists( firstsubref._refnode ) 
		assert len( childrefs ) == 4 

		# import alltogehter
		sndsubref = subrefbases[1]
		childrefs = sndsubref.importRef( depth = -1 )
		assert len( childrefs ) == 0 

