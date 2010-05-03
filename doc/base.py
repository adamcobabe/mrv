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

import mrv.test.cmd as cmd

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
	
	rootpackage = 'mrv'
	epydoc_cfg = """[epydoc]
name: MRV Development Framework
url: http://wiki.byronimo.de/mrv

sourcecode: yes
modules: unittest
modules: pydot,pyparsing
modules: ../,../ext/networkx/networkx

exclude: mrv.test,mrv.doc,mrv.cmd.ipythonstartup

output: html"""

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
		
	@classmethod
	def makedoc(cls, args):
		"""Produce the actual docs using this type"""
		p = cls.parser()
		
		hlp = """If specified, previously generated files will be removed. Works in conjunction 
		with the other flags, which default to True, hence %prog --clean will remove all 
		generated files by default"""
		p.add_option('--clean', dest='clean', action='store_true', default=False, help=hlp)
		
		options, args = p.parse_args(args)
		clean = options.clean
		del(options.clean)
		
		dgen = cls(*args, **options.__dict__)
		if clean:
			dgen.clean()
		else:
			dgen.generate()
		# END handle mode
	
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
			self._make_sphinx()
		# END make sphinx
	
	def clean(self):
		"""Clean the generated files by removing them
		:note: Must respect the options the same way as done by the ``generate``
		method"""
		if self._coverage:
			bdd = self._build_downloads_dir()
			csdd = self._source_downloads_coverage_dir()
			coverage_dir = Path(self._project_dir / cmd.tmrv_coverage_dir)
			
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
			# END remove generated index
			
			out_dir = self._html_output_dir()
			dt_dir = self._doctrees_dir()
			agp = self._autogen_output_dir()
			for dir in (agp, out_dir, dt_dir):
				if dir.isdir():
					shutil.rmtree(dir)
				# END remove html dir
			# END for each directory
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
		return self._html_output_dir() / 'generated' / 'api'
		
	def _html_output_dir(self):
		""":return: html directory to receive all output"""
		return self._base_dir / self.html_dir
		
	def _autogen_output_dir(self):
		""":return: directory to which sphinx-autogen will write its output to"""
		return self._base_dir / self.source_dir / 'generated'
		
	def _doctrees_dir(self):
		""":return: Path to doctrees directory to which sphinx writes some files"""
		return self._base_dir / self.build_dir / 'doctrees'
		
	def _mrv_maya_version(self):
		""":return: maya version with which mrv subcommands should be started with"""
		import mrv.cmd.base as cmdbase
		return cmdbase.available_maya_versions()[-1]
		
	def _mrv_bin_path(self):
		""":return: Path to mrv binary"""
		import mrv
		return Path(os.path.join(os.path.dirname(mrv.__file__), 'bin', 'mrv'))
		
	def _tmrv_bin_path(self):
		""":return: Path to tmrv binary"""
		ospd = os.path.dirname
		return Path(os.path.join(ospd(ospd(cmd.__file__)), 'bin', 'tmrv'))
		
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
		
		basepath = self._base_dir / ".."
		rootmodule = basepath.abspath().basename()
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
				modulepath = "%s.%s" % (rootmodule, filepath[len(basepath)+1:-3].replace(os.path.sep, '.'))
				ifp.write("\t%s\n" % modulepath)
			# END for each file
		# END for each file
		
		# finalize it, write the footer
		ifp.write((indexpath+'.footer').bytes())
		ifp.close()
	
	def _make_coverage(self):
		"""Generate a coverage report and make it available as download"""
		tmrvpath = self._tmrv_bin_path()
		
		# for some reason, the html output can only be generated if the current 
		# working dir is in the project root. Its something within nose's coverage 
		# module apparently
		prevcwd = os.getcwd()
		os.chdir(self._project_dir)
		
		try:
			rval = self._call_python_script([tmrvpath, str(self._mrv_maya_version()), 
											"%s=%s" % (cmd.tmrv_coverage_flag, self.rootpackage)])
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
		coverage_dir = Path(self._project_dir / cmd.tmrv_coverage_dir)
		cindex = coverage_dir / 'index.html'
		shutil.copy(cindex, csdd)
		
		# all coverage html files go to the downlods directory
		for html in coverage_dir.files():
			shutil.copy(html, bdd)
		# END for each html
		
		
	def _make_sphinx_autogen(self):
		"""Instruct sphinx to generate the autogen rst files"""
		# will have to run it in a separate process for maya support
		mrvpath = self._mrv_bin_path()
		
		code = "import sphinx.ext.autosummary.generate as sas; sas.main()"
		agp = self._autogen_output_dir()
		
		# make sure its clean, otherwise we will reprocess the same files
		if agp.isdir():
			shutil.rmtree(agp)
			agp.makedirs()
		# END handle existing directory
		
		args = [mrvpath, str(self._mrv_maya_version()), '-c', code, 
				'-o', agp, 
				self._index_rst_path()]
		
		self._call_python_script(args)
		
		# POST PROCESS
		##############
		# Add :api:module.name which gets picked up by extapi, inserting a 
		# epydoc link to the respective file.
		for rstfile in agp.files("*.rst"):
			# insert module link
			lines = rstfile.lines()
			modulename = lines[0][6:-2]	# skip `\n
			lines.insert(2, ":api:`%s`\n" % modulename)
			
			# insert :api: links to the autoclasses
			i = 0
			l = len(lines)
			while i < l:
				line = lines[i]
				if line.startswith('.. autoclass'):
					classname = line[line.rfind(' ')+1:-1]	# skip newline
					l += 1
					lines.insert(i, ':api:`%s.%s`\n\n' % (modulename, classname))
					i += 1
				# END if we have a class
				i += 1
			# END for each line
			
			rstfile.write_lines(lines)
		# END for each rst to process
		
		
	def _make_sphinx(self):
		"""Generate the sphinx documentation"""
		mrvpath = self._mrv_bin_path()
		out_dir = self._html_output_dir()
		
		for dir in (self.source_dir, out_dir):
			if not dir.isdir():
				dir.makedirs()
			# END assure directory exists
		# END for each directory
		
		args = [mrvpath, str(self._mrv_maya_version()),
				'-c', 'import sys, sphinx.cmdline; sphinx.cmdline.main(sys.argv)',
				'-b', 'html',
				'-D', 'latex_paper_size=a4', 
				'-D', 'latex_paper_size=letter', 
				'-d', self._doctrees_dir(),
				self.source_dir, 
				out_dir]
		
		self._call_python_script(args)
		
	def _make_epydoc(self):
		"""Generate epydoc documentation"""
		# start epydocs in a separate process
		# as maya support is required
		epytarget = self._epydoc_target_dir()
		if not epytarget.isdir():
			epytarget.makedirs()
		# END assure directory exists
		
		# write epydoc.cfg file temporarily
		epydoc_cfg_file = "epydoc.cfg"
		open(epydoc_cfg_file, 'wb').write(self.epydoc_cfg)
		
		args = ['epydoc', '-q', '-q', '--config', epydoc_cfg_file, '-o', str(epytarget)]
				
		origargs = sys.argv[:]
		del(sys.argv[:])
		sys.argv.extend(args)
		try:
			import epydoc.cli
			epydoc.cli.cli()
		finally:
			os.remove(epydoc_cfg_file)
			del(sys.argv[:])
			sys.argv.extend(origargs)
		# END handle epydoc config file
		

	#} END protected interface

