# -*- coding: utf-8 -*-
"""Contains basic classes and functionaliy"""
__docformat__ = "restructuredtext"

import os
import sys
import optparse
import subprocess
import shutil

import mrv
import mrv.doc

from mrv.path import Path



__all__ = [ "DocGenerator" ]

class DocGenerator(object):
	"""Encapsulates all functionality required to create sphinx/epydoc documentaiton"""

	#{ Configuration 
	forbidden_dirs = ['test', 'ext', 'doc', '.']
	
	# PATHS
	source_dir = Path('source')
	source_downloads_dir = source_dir / 'download'
	
	build_dir = Path('build')
	
	index_rst_path = source_dir / "index.rst"
	html_dir = build_dir / 'html'
	downloads_dir = html_dir / '_downloads'
	 
	#} END configuration

	def __init__(self, sphinx=True, coverage=True, epydoc=True, *args):
		"""Initialize the instance
		
		:param sphinx: If True, sphinx documentation will be produced
		:param coverage: If True, the coverage report will be generated
		:param epydoc: If True, epydoc documentation will be generated"""
		self._sphinx = sphinx
		self._coverage = coverage
		self._epydoc = epydoc
		
		# these directories are used for navigation
		# Currently we assume that we are being started in the docs 
		# directory
		assert Path(os.getcwd()).basename() == 'doc', "Need to run in the 'doc' directory"
		self._base_dir = Path('.')
		self._project_dir = Path(self._base_dir / "..")
	
	#{ Public Interface
	
	@classmethod
	def parser(cls):
		""":return: OptionParser instance suitable to parse commandline arguments
		with which to initialize our instance"""
		usage = """%prog [options]
		
		Make documentation or remove the generated files."""
		parser = optparse.OptionParser(usage=usage)
		
		hlp = """Specifies sphinx documentation. It will include the epydoc pages, whether 
		they exist or not"""
		parser.add_option('-s', '--sphinx', dest='sphinx', type='int',default=1,
							help=hlp, metavar='STATE')
		
		hlp = """Specifies epydoc documentation"""
		parser.add_option('-e', '--epydoc', dest='epydoc', type='int', default=1, 
							help=hlp, metavar='STATE')
		
		hlp = """Specifies a coverage report. It will be referenced from within the 
		sphinx documentation"""
		parser.add_option('-c', '--coverage', dest='coverage', type='int', default=1, 
							help=hlp, metavar='STATE')
		
		return parser
	
	def generate(self):
		"""Geneate the documentation according to our configuration
		
		:note: respects the options given during construction"""
		if self._coverage:
			self._make_coverage()
		
		if self._epydoc:
			self._make_epydoc()
		
		if self._sphinx:
			self._make_sphinx_index()
			self._make_sphinx_autogen()
			# self._make_sphinx()
		# END make sphinx
	
	def clean(self):
		"""Clean the generated files by removing them
		:note: Must respect the options the same way as done by the ``generate``
		method"""
		if self._coverage:
			import mrv.test.cmds as cmds
			bdd = self._build_downloads_dir()
			csdd = self._source_downloads_coverage_dir()
			coverage_dir = Path(self._project_dir / cmds.tmrv_coverage_dir)
			
			# delete all files we copied from the coverage dir
			for fpath in coverage_dir.files():
				tfpath = bdd / fpath.basename()
				if tfpath.isfile():
					tfpath.remove()
				# END remove file
			# END for each coverage file to remove
			
			try:
				shutil.rmtree(csdd)
			except OSError:
				pass
			# END exceptionhandlint
			
		# END clean coverage 
		
		if self._epydoc:
			try:
				shutil.rmtree(self._epydoc_target_dir())
			except OSError:
				pass
			# END ignore errors if directory doesnt exist
		# END clean epydoc
		
		if self._sphinx:
			ip = self._index_rst_path()
			if ip.isfile():
				ip.remove()
		# END clean sphinx
	#} END public interface
	
	#{ Utilities
	def _index_rst_path(self):
		""":return: Path to index rst file"""
		return self._base_dir / self.index_rst_path
		
	def _build_downloads_dir(self):
		""":return: Path to the build downloads directory"""
		return self._base_dir / self.downloads_dir
		
	def _source_downloads_dir(self):
		""":return: Path to the source downloads directory"""
		return self._base_dir / self.source_downloads_dir
		
	def _source_downloads_coverage_dir(self):
		""":return: Path to coverage related downloads"""
		return self._source_downloads_dir() / 'coverage'
		
	def _epydoc_target_dir(self):
		""":return: Path to directory to which epydoc will write its output"""
		return self._base_dir / self.html_dir / 'generated' / 'api'
		
	def _mrv_maya_version(self):
		""":return: maya version with which mrv subcommands should be started with"""
		import mrv.cmds.base as cmdsbase
		return cmdsbase.available_maya_versions()[-1]
		
	def _epydoc_cfg(self):
		""":return: string which can be written out as epydoc.cfg file. It will be used
		to define what epydoc will do for us"""
		return """[epydoc]
name: MRV Development Framework
url: http://wiki.byronimo.de/mrv

sourcecode: yes
modules: unittest
modules: pydot,pyparsing
modules: ../,../ext/networkx/networkx

exclude: mrv.test,mrv.doc,mrv.cmds.ipythonstartup

output: html"""
		
	def _call_python_script(self, *args, **kwargs):
		"""Wrapper of subprocess.call which assumes that we call a python script.
		On windows, the python interpreter needs to be called directly
		:return: return value of call """
		if sys.platform.startswith('win'):
			args[0].insert(0, "python")
		# END handle windows
		print ' '.join(str(i) for i in args[0])
		return subprocess.call(*args, **kwargs)
		
	#} END utilities
	
	#{ Protected Interface

	def _make_sphinx_index(self):
		"""Generate the index.rst file according to the modules and packages we
		actually have"""
		import mrv
		
		indexpath = self._index_rst_path()
		ifp = open(indexpath, 'wb')
		# write header
		ifp.write((indexpath+'.header').bytes())
		
		basepath = os.path.join(self._base_dir, "..")
		for root, dirs, files in os.walk(basepath):
			remove_dirs = list()
			for dirname in dirs:
				if dirname in self.forbidden_dirs:
					remove_dirs.append(dirname)
				# END for each forbidden dir
			# END for each directory
			
			for dirname in remove_dirs:
				del(dirs[dirs.index(dirname)])
			# END for each dirname to remove
			
			for fname in files:
				if not fname.endswith('.py') or fname.startswith('_'):
					continue
				filepath = os.path.join(root, fname)
				
				# + 1 as there is a trailing path separator
				modulepath = "%s.%s" % (mrv.__name__, filepath[len(basepath)+1:-3].replace(os.path.sep, '.'))
				ifp.write("\t%s\n" % modulepath)
			# END for each file
		# END for each file
		
		# finalize it, write the footer
		ifp.write((indexpath+'.footer').bytes())
		ifp.close()
	
	def _make_coverage(self):
		"""Generate a coverage report and make it available as download"""
		import mrv.test.cmds as cmds
		import mrv.test
		ospd = os.path.dirname
		tmrvpath = os.path.join(ospd(ospd(cmds.__file__)), 'bin', 'tmrv')
		
		# for some reason, the html output can only be generated if the current 
		# working dir is in the project root. Its something within nose's coverage 
		# module apparently
		prevcwd = os.getcwd()
		os.chdir(self._project_dir)
		
		try:
			rval = self._call_python_script([tmrvpath, str(self._mrv_maya_version()), cmds.tmrv_coverage_flag])
		finally:
			os.chdir(prevcwd)
		# END handle cwd
		
		if rval:
			raise SystemError("tmrv reported failure")
		# END handle return value
		
		bdd = self._build_downloads_dir()
		csdd = self._source_downloads_coverage_dir()
		for dir in (bdd, csdd):
			if not dir.isdir():
				dir.makedirs()
			# END if dir doesnt exist, create it
		# END for each directory 
		
		# coverage was generated into the current working dir
		# index goes to downloads in the source directory as it is referenced
		# by the docs
		coverage_dir = Path(self._project_dir / cmds.tmrv_coverage_dir)
		cindex = coverage_dir / 'index.html'
		shutil.copy(cindex, csdd)
		
		# all coverage html files go to the downlods directory
		for html in coverage_dir.files():
			shutil.copy(html, bdd)
		# END for each html
		
		
	def _make_sphinx_autogen(self):
		"""Instruct sphinx to generate the autogen rst files"""
		
	def _make_sphinx(self):
		"""Generate the sphinx documentation"""
		import sphinx.cmdline
		
		# adjust commandline arguments
		
		sphinx.cmdline.main(sys.argv[:])
		
	def _make_epydoc(self):
		"""Generate epydoc documentation"""
		import mrv
		mrvpath = os.path.join(os.path.dirname(mrv.__file__), 'bin', 'mrv')
		
		# start epydocs in a separate process
		# as maya support is required
		epytarget = self._epydoc_target_dir()
		if not epytarget.isdir():
			epytarget.makedirs()
		# END assure directory exists
		
		# write epydoc.cfg file temporarily
		epydoc_cfg_file = "epydoc.cfg"
		open(epydoc_cfg_file, 'wb').write(self._epydoc_cfg())
		
		args = [mrvpath, str(self._mrv_maya_version()), 
				'-c', 'import epydoc.cli; import mrv.maya; epydoc.cli.cli()', 
				'-q', '-q', '--config', epydoc_cfg_file,
				'--debug',
				'-o', str(epytarget)]
		try:
			self._call_python_script(args)
		finally:
			os.remove(epydoc_cfg_file)
		# END handle epydoc config file
		

	#} END protected interface


