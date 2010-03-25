# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
from mrv.maya.util import MEnumeration
import mrv.maya.mdb as mdb
from mrv.path import *
from mrv.util import DAGTree

import maya.OpenMayaUI as apiui 

import inspect

# test import all
from mrv.maya.mdb import *

class TestMDB( unittest.TestCase ):
	def test_base(self):
		assert len(getApiModules())
		
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
		for apimod in getApiModules():
			for mfnclsname in ( n for n in dir(apimod) if n.startswith('MFn') ):
				mfncls = getattr(apimod, mfnclsname)
				dbpath = mfnDBPath(mfnclsname)
				if not dbpath.isfile():
					continue
				
				mfndb = MMemberMap(dbpath)
				
				assert len(mfndb)
				for fname, entry in mfndb.iteritems():
					assert isinstance(fname, basestring)
					assert isinstance(entry, MMethodDescriptor)
				# END for functionname, entry pair
				
				# we know that MFnMesh needs MObject iniitalization
				if mfnclsname == "MFnMesh":
					assert mfndb.flags & PythonMFnCodeGenerator.kMFnNeedsMObject
				# END special global flags check
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
			for needsMObject in (0, cgen.kMFnNeedsMObject):
				for isMObject in (0, cgen.kIsMObject):
					for isDagNode in (0, cgen.kIsDagNode):
						for withDocs in (0, cgen.kWithDocs):
							for rvalwrapname in ('None', 'rvalwrapper'):
								flags = directCall|needsMObject|isMObject|isDagNode|withDocs
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
			# END for each needsMObject state
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
		
		
	def _DISABLED_test_mfncachebuilder( self ):
		"""Rewrite the mfn db cache files - should be done with each new maya version"""
		import mrv.maya.mdb as mdb
		mdb.writeMfnDBCacheFiles( )


