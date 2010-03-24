# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
import mrv.maya.mdb as mdb
from mrv.path import *
from mrv.util import DAGTree

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
		
		cgen = PythonMFnCodeGenerator(globals())
		
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
					
					# test code generator
					
				# END for functionname, entry pair
				
				# we know that MFnMesh needs MObject iniitalization
				if mfnclsname == "MFnMesh":
					assert mmap.flags & PythonMFnCodeGenerator.kMFnNeedsMObject
				# END special global flags check
			# END for each mfn cls 
		# END for each apimod
		
		
		
		
	def _DISABLED_test_mfncachebuilder( self ):
		"""Rewrite the mfn db cache files - should be done with each new maya version"""
		import mrv.maya.mdb as mdb
		mdb.writeMfnDBCacheFiles( )


