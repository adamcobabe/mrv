# -*- coding: utf-8 -*-
""" Test the reference methods """
import unittest
from mayarv.test.maya import *
import maya.cmds as cmds
from mayarv.maya.ref import *
from mayarv.maya.ns import *
import mayarv.maya as bmaya
import mayarv.maya.nodes as nodes
import re
import os


class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """

	@with_scene('refbase.ma')
	def _test_listAndQuery( self ):
		"""mayarv.maya.ref: list some references and query their information """
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

	@with_scene('refbase.ma')
	def _test_referenceCreation( self ):
		"""mayarv.maya.ref: create , delete and replace references"""
		# create some new references
		filenames = [ "sphere.ma", "cube.ma", "empty.ma", "cylinder.ma", "subrefbase.ma" ]
		newrefs = []
		for load in range( 2 ):
			for filename in filenames:
				newreffile = get_maya_file( filename )
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
		
	
	def _assert_iter_nodes(self, ref):
		# test all branches of node iteration
		for asNode in range(2):
			for dag in range(2):
				for dg in range(2):
					for assemblies in range(2):
						for air in range(2):
							for predicate_var in (True, False):
								predicate = lambda n: predicate_var
								try:
									node_list = list(ref.iterNodes(asNode=asNode, dag=dag, dg=dg, 
																assemblies=assemblies, assembliesInReference=air, 
																predicate=predicate ))
								except ValueError:
									continue
								# END handle unsupported combinations
								
								if asNode:
									for node in node_list:
										assert isinstance(node, nodes.Node)
										if dag: 
											assert isinstance(node, nodes.DagNode)
										# END check dag node
									# END for each node
								# END as Node
								if not predicate_var:
									assert len(node_list) == 0
							# END for each predicate value
						# END for each air value 
					# END for each assembly value
				# END for each dg value
			# END for each dag value
		# END for each asNode value
	
	
	def _assert_ref_node(self, rfn):
		assert isinstance(rfn, nodes.Reference)
		
		assert rfn.getFileReference().getReferenceNode() == rfn
	
	
	@with_scene('ref2re.ma')
	def test_misc(self):
		fr = FileReference
		# exactly two refs
		tlrs = fr.ls()
		assert len(tlrs) == 2
		
		# 4 subrefs each
		subrefs = set()
		for tlr in tlrs:
			subrefs.update(set(fr.ls(rootReference=tlr)))
			
			self._assert_iter_nodes(tlr)
		# END for each top level reference
		assert len(subrefs) == 4
		
		# ASSORTED QUERY
		for ref in subrefs:
			assert not ref.isLocked() and not ref.p_locked
			assert ref.exists()
			assert ref.isLoaded() and ref.p_loaded
			assert ref.getNamespace() == ref.p_namespace
			assert isinstance(ref.p_namespace, Namespace)
			assert len(ref.getChildren()) == 0
			assert isinstance(ref.getCopyNumber(), int)
			assert ref.getParent() in tlrs
			assert ref.getPath(unresolved=0) != ref.getPath(unresolved=1)
			self._assert_ref_node(ref.getReferenceNode())
			
			# cannot set namespace of subreferences
			self.failUnlessRaises(RuntimeError, ref.setNamespace, "something")
			self._assert_iter_nodes(ref)
		# END test simple query functions
		
		
		def assert_from_paths(p, **kwargs):
			# one item 
			match = fr.fromPaths([p], **kwargs)
			assert len(match) == 1 and match[0].getPath() == tlr.getPath()
			
			# two items
			match = fr.fromPaths([p, p], **kwargs)
			assert len(match) == 2 and tlrs[0] in match and tlrs[1] in match
			
			# three items, one is None
			match = fr.fromPaths([p, p, p], **kwargs)
			assert len(match) == 3 and match[-1] is None and tlrs[0] in match and tlrs[1] in match
		# END utility
		
		# fromPaths
		# we have two tlrs pointing to the same file
		tlr = tlrs[0]
		for tconv in (lambda r: r, str):
			assert_from_paths(tconv(tlr))
			
			if tconv is not str:
				basepath = tlr.getPath().splitext()[0]
				basepath += ".mb"
				
				# it should match even though mb is referenced
				assert_from_paths(basepath, ignore_extension=True)
			# END special ref test
		# END for each converter
		
		
		
		# predicate check
		allow_none = lambda x: False
		assert len(fr.ls(predicate=allow_none)) == 0
		
		# lsDeep
		assert len(fr.lsDeep()) == 6
		assert len(fr.lsDeep(rootReference=tlrs[0])) == 2	# doesnt return root
		
		# lsDeep predicate
		assert len(fr.lsDeep(predicate=allow_none)) == 0
		
		
		
		# import deep
		assert len(tlrs[0].importRef(depth=-1)) == 0
		assert not tlrs[0].exists()
		assert len(fr.ls()) == 1
		
		# import one, then remove remainders
		subrefs = tlrs[1].importRef()
		assert len(subrefs) == 2
		
		for sr in subrefs:
			assert sr.exists()
			sr.remove()
			assert not sr.exists()
		# END remove subref

