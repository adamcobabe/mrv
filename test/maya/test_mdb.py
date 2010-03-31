# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
from mrv.maya.util import MEnumeration
import mrv.maya as mrvmaya
import mrv.maya.mdb as mdb
from mrv.path import *
from mrv.util import DAGTree

import maya.OpenMayaUI as apiui 

import inspect
import os
import sys

# test import all
from mrv.maya.mdb import *

class TestMDB( unittest.TestCase ):
	def test_base(self):
		assert len(apiModules())
		
		# simple method testing
		assert mfnDBPath('MFnBase').isfile()
		
		for with_version in range(2):
			assert isinstance(cacheFilePath('file', 'ext', with_version), Path)
		# END for each version
		
		hnodes = createDagNodeHierarchy()
		ttmfnmap = createTypeNameToMfnClsMap()
		
		assert isinstance(hnodes, DAGTree)
		assert isinstance(ttmfnmap, dict)
		
		# test member map - all files should be readable
		for apimod in apiModules():
			for mfnclsname in ( n for n in dir(apimod) if n.startswith('MFn') ):
				mfncls = getattr(apimod, mfnclsname)
				dbpath = mfnDBPath(mfnclsname)
				if not dbpath.isfile():
					continue
				
				mfndb = MMemberMap(dbpath)
				
				if mfnclsname != 'MFn':	# its just an enum basically
					assert len(mfndb)
				for fname, entry in mfndb.iteritems():
					assert isinstance(fname, basestring)
					assert isinstance(entry, MMethodDescriptor)
				# END for functionname, entry pair
			# END for each mfn cls 
		# END for each apimod
		
		
		# test code generator - generate code in all possible variants - 
		# function doesn't matter as its not actually called.
		import maya.OpenMaya as api
		mfndb = MMemberMap(mfnDBPath("MFnBase"))
		mfncls = api.MFnBase
		mfn_fun_name = 'setObject'
		mfn_fun = mfncls.__dict__[mfn_fun_name]
		_discard, mdescr = mfndb.methodByName(mfn_fun_name)
		rvalwrapper = lambda x: x
		
		cgen = PythonMFnCodeGenerator(locals())
		for directCall in (0, cgen.kDirectCall):
			for isMObject in (0, cgen.kIsMObject):
				for isDagNode in (0, cgen.kIsDagNode):
					for withDocs in (0, cgen.kWithDocs):
						for rvalwrapname in ('None', 'rvalwrapper'):
							flags = directCall|isMObject|isDagNode|withDocs
							source_fun_name = mfn_fun_name
							if directCall:
								source_fun_name = "_api_"+source_fun_name
							# END create source function name
							prevval = mdescr.rvalfunc
							mdescr.rvalfunc = rvalwrapname
							try:
								try:
									fun_code_string = cgen.generateMFnClsMethodWrapper(source_fun_name, mfn_fun_name, mfn_fun_name, mdescr, flags)
								except ValueError:
									continue
								# END ignore incorrect value flags
							finally:
								mdescr.rvalfunc = prevval
							# END assure not to alter mfndb entries
							
							assert isinstance(fun_code_string, basestring)
							
							# generate the actual method 
							fun = cgen.generateMFnClsMethodWrapperMethod(source_fun_name, mfn_fun_name, mfncls, mfn_fun, mdescr, flags)
							assert inspect.isfunction(fun)
						# END for each rvalwrapper type
					# END for each withDocs state
				# END for each isDagNode state
			# END for each isMObject state
		# END for each direct call state
		
	def test_header_parser(self):
		
		# test enumeration parsing
		# has multiple enums, and multiple variants:
		# enum Type 
		# { 
		#	kInvalid = 0,  ... }
		# and without intitialization
		viewheader= mdb.headerPath('M3dView')
		enums, = mdb.CppHeaderParser.parseAndExtract(viewheader)
		assert len(enums) > 7		# could change with maya versions, 7 should be minimum
		
		for ed in enums:
			assert isinstance(ed, mdb.MEnumDescriptor)
			assert len(ed)
			assert isinstance(ed.name, basestring)
			
			# convert to MEnumeration
			enum = MEnumeration.create(ed, apiui.M3dView)
			assert isinstance(enum, MEnumeration)
			assert enum.name == ed.name
			assert len(enum) == len(ed)
			for em in ed:
				ev = getattr(enum, em)
				assert isinstance(ev, int)
				assert enum.nameByValue(ev) == em
			# END check each instance
			self.failUnlessRaises(ValueError, enum.nameByValue, -1)
			
		# END for each enum descriptor
		
		
	def test_init_new_maya_release_errchecking( self ):
		# for now, only test the failures
		
		# fails if at least one user setup variable is set - just one sample for now
		alpev = 'MRV_STANDALONE_AUTOLOAD_PLUGINS'
		prev_value = os.environ.get(alpev, None)
		os.environ[alpev] = "1"
		
		try:
			self.failUnlessRaises(EnvironmentError, mrvmaya.initializeNewMayaRelease)
		finally:
			if prev_value:
				os.environ[alpev] = prev_value
		# END assure os stays unharmed
		
		# fail in current version ( as it exists )
		self.failUnlessRaises(EnvironmentError, mrvmaya.initializeNewMayaRelease)

	def _DISABLED_test_init_new_maya_release(self):
		# NOTE: this test should only be run manually if you want to check 
		# the initializeNewMayaRelease method - it will change your local database
		# files which in turn might affect other tests !
		
		# rename original file
		nhf = mdb.nodeHierarchyFile()
		nhfr = nhf.rename(nhf + ".tmp")
		try:
			mrvmaya.initializeNewMayaRelease()
		finally:
			if not nhf.isfile():
				nhfr.rename(nhf)
			else:
				nhfr.remove()
			# END rename original file back if it wasnt affected
		# END cleanup state
		
	@with_scene('empty.ma')
	def _DISABLED_test_testWrappers( self ):
		# NOTE: This method needs not to run, but is part of the version initialization process.
		import mrv.maya.env as env
		import mrv.maya.nt as nt
		from mrv.util import capitalize, uncapitalize
		import maya.cmds as cmds
		
		missingTypesList = list()
		invalidInheritanceList = list()
		seen_types = set()		# keeps class names that we have seen already 
		for nodetypename, obj, mod in mdb._iterAllNodeTypes():
			mod.doIt()
			
			node = nt.NodeFromObj( obj )
			node.getMFnClasses()

			assert not node.object().isNull()
			if isinstance(node, nt.DagNode):
				node.dagPath()
				
			# skip duplicate types - it truly happens that there is the same typename
			# with a different parent class - we cannot handle this 
			if nodetypename in seen_types:
				continue
			seen_types.add( nodetypename )

			# assure we have all the parents we need
			parentClsNames = [ capitalize( typename ) for typename in cmds.nodeType( str(node), i=1 ) ]
			
			for pn in parentClsNames:
				token = ( node, parentClsNames )
				try:
					pcls = getattr( nt, pn )
				except AttributeError:
					invalidInheritanceList.append( token )
					break
				# END AttributeError
				
				# if its a standin class, try to create it 
				try:
					pcls = pcls.createCls()
				except AttributeError:
					pass 
					
				if not isinstance( node, pcls ):
					invalidInheritanceList.append( token )
					break
				# END if a parent class is missing
			# END for each parent class name
		# END for each type in file

		if len( missingTypesList ):
			nodecachefile = "nodeHierarchy%s.hf" % env.appVersion( )[0]
			for fn in missingTypesList:
				print fn
			
			print "Add these lines to the hierarchy file, using the parent information shown above" 
			for fn in missingTypesList:
				print uncapitalize( fn[1] )
			raise TypeError( "Add the following node types to the %r cache file at the respective post in the hierarchy:" % ( nodecachefile ) )
		# END missing types handling 
		
		if len( invalidInheritanceList ):
			for ( node, parentClsNames ) in invalidInheritanceList:
				print "Invalid inheritance of type %s, must be %s" % ( node.typeName(), parentClsNames )
			# END for each item tuple 
			raise AssertionError( "Class(es) with invalid inheritance found - see stdout" )
		# END invalid inheritance handling 

		# try to just use a suberclass directly
		for transname in cmds.ls( type="transform" ):
			node = nt.DagNode( transname )
			assert hasattr( node, "__dict__" ) 


