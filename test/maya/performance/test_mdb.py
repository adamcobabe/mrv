# -*- coding: utf-8 -*-
""" Test maya node database """
from mrv.test.maya import *
# test import all
from mrv.maya.mdb import *
import mrv.maya.mdb as mdb
import mrv.maya.nt.typ as typ

import time
import sys
from itertools import chain

# helps to prevent duplicate runs of prefetch
_prefetched = False

class TestMDB( unittest.TestCase ):
	def test_prefetch(self):
		global _prefetched
		if _prefetched:
			return
		st = time.time()
		nm = typ.prefetchMFnMethods()
		elapsed = time.time() - st
		_prefetched = True
		print >>sys.stderr, "Pre-fetched %i methods in %f s ( %f methods / s)" % ( nm, elapsed, nm / elapsed )
		
	def _run_compilation_test(self, dry_run=True):
		""":return: number of fetched methods"""
		num_fetched = 0
		rvalwrapper = lambda x: x
		
		cgen = PythonMFnCodeGenerator(locals())
		
		for typename, mfncls in typ.nodeTypeToMfnClsMap.iteritems():
			try:
				nodetype = typ._nodesdict[typ.capitalize(typename)]
			except KeyError:
				continue
			# END handle type exceptions
			mfnname = mfncls.__name__
			mfndb = typ.MetaClassCreatorNodes._fetchMfnDB(nodetype, mfncls)
			fstatic, finst = extractMFnFunctions(mfncls)
			
			for fun in chain(fstatic, finst):
				fname = fun.__name__
				if fname.startswith(mfnname):
					fname = fname[len(mfnname)+1:]
				# END handle name prefix
				
				# we expect an entry actually, database should be complete
				_discard, mdescr = mfndb.methodByName(fname)
				
				for directCall in (0, cgen.kDirectCall):
					for isMObject in (0, cgen.kIsMObject):
						for isDagNode in (0, cgen.kIsDagNode):
							for withDocs in (0, cgen.kWithDocs):
								for rvalwrapname in ('None', 'rvalwrapper'):
									flags = directCall|isMObject|isDagNode|withDocs
									source_fun_name = fname
									if directCall:
										source_fun_name = "_api_"+fname
									# END create source function name
									prevval = mdescr.rvalfunc 
									mdescr.rvalfunc = rvalwrapname
									
									# generate the actual method
									try:
										try:
											if not dry_run:
												fun = cgen.generateMFnClsMethodWrapperMethod(source_fun_name, fname, mfncls, fun, mdescr, flags)
											# END handle dry run
										except ValueError:
											continue
										else:
											num_fetched += 1
										# END handle incorrect arguments
									finally:
										mdescr.rvalfunc = prevval
									# END assure to reset our changes
								# END for each rvalwrapper type
							# END for each withDocs state
						# END for each isDagNode state
					# END for each isMObject state
				# END for each direct call state
			# END for each function
		# END for each nodetype/mfncls pair
		return num_fetched
		
	def test_compilation(self):
		global _prefetched
		
		# prefetch to assure loading of whole database
		if not _prefetched:
			# this way, we at least get a real timing 
			self.test_prefetch()
		# END prefetch everything
		
		# dry run to determine base overhead, excluding generation of methods
		st = time.time()
		self._run_compilation_test(dry_run = True)
		baseelapsed = time.time() - st
		
		# do the actual run
		st = time.time()
		nm = self._run_compilation_test(dry_run = False)
		elapsed = time.time() - st
		
		vals = (nm, elapsed, nm/elapsed, elapsed-baseelapsed, 100 - ((elapsed-baseelapsed) / elapsed)*100, baseelapsed)
		print >> sys.stderr, "Compiled %i methods in %f s ( %f methods/s ), pure compilation time is %f, equaling a non-compilation overhead of %f %% (%f s)" % vals
		
	def test_header_parser(self):
		# brutally work through all headers - we shouldn't fail at least
		base = mdb.headerPath('MFn').parent()
		headers = sorted(base.files(pattern="*.h"))
		nh = len(headers)
		parser = mdb.CppHeaderParser()
		
		st = time.time()
		for hfile in headers:
			parser.parseAndExtract(hfile)
		# END for each file
		elapsed = time.time() - st
		
		print >> sys.stderr, "Parsed %i header files in %f s ( %f headers / s)" % ( nh, elapsed, nh/elapsed )
		
		
