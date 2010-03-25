# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
import mrv.maya.mdb as mdb
from mrv.path import *
from mrv.util import DAGTree
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
				
				mmap = MFnMemberMap(dbpath)
				
				assert len(mmap)
				for fname, entry in mmap.iteritems():
					assert isinstance(fname, basestring)
					assert isinstance(entry, MFnMethodDescriptor)
				# END for functionname, entry pair
				
				# we know that MFnMesh needs MObject iniitalization
				if mfnclsname == "MFnMesh":
					assert mmap.flags & PythonMFnCodeGenerator.kMFnNeedsMObject
				# END special global flags check
			# END for each mfn cls 
		# END for each apimod
		
		
		# test code generator - generate code in all possible variants - 
		# function doesn't matter as its not actually called.
		import maya.OpenMaya as api
		mmap = MFnMemberMap(mfnDBPath("MFnBase"))
		mfncls = api.MFnBase
		mfn_fun_name = 'setObject'
		mfn_fun = mfncls.__dict__[mfn_fun_name]
		_discard, mdescr = mmap.entry(mfn_fun_name)
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
								mdescr.rvalfunc = rvalwrapname
								try:
									fun_code_string = cgen.generateMFnClsMethodWrapper(source_fun_name, mfn_fun_name, mfn_fun_name, mdescr, flags)
								except ValueError:
									continue
								# END ignore incorrect value flags
								
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
		
	def _DISABLED_test_mfncachebuilder( self ):
		"""Rewrite the mfn db cache files - should be done with each new maya version"""
		import mrv.maya.mdb as mdb
		mdb.writeMfnDBCacheFiles( )


