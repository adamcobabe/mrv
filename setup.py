import os
ospd = os.path.dirname
import sys
import __builtin__

from distutils.core import setup
from distutils.dist import Distribution as BaseDistribution
from distutils import log


import distutils.command
from distutils.cmd import Command
from distutils.command.build_py import build_py
from distutils.command.bdist_dumb import bdist_dumb
from distutils.command.sdist import sdist

from itertools import chain
import subprocess
import fnmatch
import re

try:
	from setuptools import find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import find_packages
# END get find_packages


#{ Distutils Fixes 

def __init__(self, dist):
	"""Okay, its getting interesting: cmd checks for the type of dist - we 
	have derived from it and provide our own type. Distribution is an oldstyle class
	which doesn't even work with isinstance - to workaround this, we derive from object
	as well. In the moment we call __init__ on the BaseDistribution part of our instance, 
	it claims not to be an instance of type Distribution(Base) anymore. Something is 
	fishy here. As a workaround, we get rid of the typecheck in the command base."""
	self.distribution = dist
	self.initialize_options()
	self._dry_run = None
	self.verbose = dist.verbose
	self.force = None
	self.help = 0
	self.finalized = 0

distutils.cmd.Command.__init__ = __init__

#} END Distutils fixes


#{ Commands 


class _GitMixin(object):
	"""Provides functionality to add files and folders within a base directory 
	into the **root** of a git repository of our choice"""
	
	#{ Configuration
	# name of symbolic reference which keeps the previous reference name to which 
	# HEAD pointed before we changed HEAD
	prev_head_name = 'DIST_ORIG_HEAD'
	
	branch_suffix = None
	#} END configuration 
	
	def __new__(cls, *args, **kwargs):
		"""Because of our old-style bases, new needs to be overridden to 
		call the object constructor without arguments"""
		self = object.__new__(cls)
		# have to manually call init on all bases because the old-style classes
		# don't really cut it here
		for c in cls.mro():
			c.__init__(self, *args, **kwargs)
		return self
	
	def __init__(self, *args, **kwargs):
		"""Allows to configure some details, such as 
		* remote name - name of the remote for which branches should be created/updated"""
		self.root_remotes = list()
		self.dist_remotes = list()
	
	def finalize_options(self):
		"""Assure our args are of the correct type"""
		self.root_remotes = self.distribution.fixed_list_arg(self.root_remotes)
		self.dist_remotes = self.distribution.fixed_list_arg(self.dist_remotes)
	
	#{ Utilities
	
	@classmethod
	def adjust_user_options(cls, options):
		"""Append git specific user options to the given options"""
		options.append(('dist-remotes=', 'd', "Default remotes to push the distribution branches to"))
		options.append(('root-remotes=', 'r', "Default remotes to push the the main source branch to"))
	
	def branch_name(self):
		""":return: name of the branch identifying our current release configuration"""
		root_name = self.distribution.rootmodule.__name__
		if self.branch_suffix is None:
			raise ValueError("Branch suffix is not set")
		return root_name + self.branch_suffix
		
	def set_head_to(self, repo, head_name):
		"""et our head to point to the given head_name. If possible, 
		update the index to represent the tree the head points to
		
		:return: Head named head_name
		:note: In the worst case, the head points to non-existing ref, as the 
			repository is still empty"""
		import git
		
		# store the previous ref in a new symbolic ref
		git.SymbolicReference.create(repo, self.prev_head_name, repo.head.ref, force=True)
		
		
		# if the head ref exists or not, we want to change the branch to the one
		# we define. This is why we do this explicitly here. Resetting the index
		# and setting the head will just set the current branch to the commit we 
		# reset to
		head_ref = git.Head(repo, git.Head.to_full_path(head_name))
		repo.head.ref = head_ref
		
		if head_ref.is_valid():
			repo.index.reset(head_ref, working_tree=False, head=False)
		# END handle index
			
		# END head exists handling
		return head_ref
	
	def item_chooser(self, description, items):
		"""Utility allowing the user to easily select items from the items list
		:param items: objects that can be converted into a string
		:return: list of selected items"""
		if not items:
			return list()
		
		assert sys.stdout.isatty(), "Need a tty for item chooser"
		
		while True:
			print description
			print "Type the numbers to select the items, i.e. 1,2,5 or 0 to select all"
			print ""
			print "0 == All Items"
			for i, item in enumerate(items):
				print "%i == %s" % (i+1, item)
			# END for each item to print
			
			indices = list()
			sel_items = list()
			while True:
				try:
					answer = raw_input("Choice: " )
					indices.extend(int(i.strip()) for i in answer.split(','))
					break
				except Exception:
					print "Failed to parse your choice, please try again: %s" % answer
					continue
				# END excpetion handling
			# END parse loop
			
			if not indices:
				asw = 'abort'
				print "No item selected - would you like to abort ?"
				answer = raw_input("%s/continue [%s]" % (asw, asw)) or asw
				if answer == asw:
					print "User aborted selection"
					return list()
				else:
					continue
				# END handle answer
			# END handle nothing choosen
			
			# gather indices
			if 0 in indices:
				sel_items.extend(items)
			else:
				for index in indices:
					try:
						sel_items.append(items[index-1])
					except IndexError:
						pass
					# END handle invalid indices
				# END for each index
			# END for each 
			
			# present the selection
			if sel_items:
				print "Your selection: "
				for item in sel_items:
					print str(item)
				# END for each item
			else:
				print "You didn't select anything"
			# END present items
			asw = "proceed"
			print "Would you like to proceed or re-select ?"
			answer = raw_input("%s/reselect [%s]: " % (asw, asw)) or asw
			
			if answer != asw:
				continue
			
			return sel_items
		# END while user is unhappy
		
		return items
	
	def push_to_remotes(self, repo, heads=list(), remotes=list()):
		"""Push the given branchs to the given remotes.
		If one of the lists is empty, it the respective items 
		will be queried from the user"""
		_heads = heads
		_remotes = remotes
		all_remotes = repo.remotes
		
		if not _remotes:
			_remotes = all_remotes
		if not _heads:
			_heads = repo.heads
		
		if not _remotes or not _heads:
			return
		# END skip empty remotes
		
		# cannot push if we don't know exactly what to do ( and if we cannot
		# ask the user )
		have_tty = sys.stdout.isatty()
		if not have_tty and (not heads or not remotes):
			log.info("Skipped push to %r as no push information was provided" % repo)
			return
		# END handle tty
		
		if have_tty:
			asw = "yes"
			man = 'manual'
			print "\nWould you like to push your changes in repo %s ?" % repo
			print "Currently selected heads: %s" % ', '.join(str(h) for h in heads) or 'None'
			print "Currently selected remotes: %s" % ', '.join(str(r) for r in remotes) or 'None'
			print "You can the given values, force manual (re)selection or skip this ?"
			answer = raw_input("%s/%s/skip [%s]: " % (asw, man, asw)) or asw
			if answer == man:
				remotes = list()
				heads = list()
			elif answer != asw:
				print "You can push your changes manually any time"
				return 
			# END see if the user wants to push
		# END last query
		
		if not remotes:
			desc = "Please choose the remotes to push to"
			_remotes = self.item_chooser(desc, _remotes)
		# END query if not given
		
		if not heads:
			desc = "Please choose your branches to push to the selected remotes" 
			_heads = self.item_chooser(desc, _heads)
		# END query if not given 
		 
		if not _remotes or not _heads:
			print "No remotes or heads selected - won't push anything"
			return
		# END abort if there is nothing to do
		
		tags = repo.tags
		tag_map = dict((tag.commit, tag) for tag in tags)
		
		# walk the history of all branches and select all tags on the way
		actual_tags = list()
		for head in _heads:
			curcommit = head.commit
			while True:
				if curcommit in tag_map:
					actual_tags.append(tag_map[curcommit])
				# END found tag
				if not curcommit.parents:
					break
				curcommit = curcommit.parents[0]
			# END pseudo do-while
		# END for each branch
		
		# prep refspec
		specs = list()
		for item in chain(_heads, actual_tags):
			specs.append("%s:%s" % (item.path, item.path))
		# END for each item to push
		
		# do the operation
		for remote in _remotes:
			# might be a string if it was a preconfigured remote - hence we 
			# retrieve the object no matter what
			remote = all_remotes[str(remote)]
			
			print "Pushing to %s: %s ..." % (remote, ", ".join(str(i) for i in chain(_heads, actual_tags)))
			remote.push(specs)
			print "Done"
		# END for each remote to push to

	def add_files_and_commit(self, root_repo, repo, root_dir, root_tag):
		"""
		Add all files recursively to the index as found below root_dir and commit the
		index.
		
		As a special ability, we will rewrite their paths and thus add them relative
		to the root directory, even though the git repository might be on another level.
		It also sports a simple way to determine whether the commit already exists, 
		so it will not recommit data that has just been committed.
		
		:param root_repo: Repository containing the data of the main project
		:param repo: dedicated repository containing the distribution data
		:return: tuple(root_original_head, (Created)Commit object) The head to which
			the root repository pointed before we changed it to our distribution head, 
			and the commit object we possible created in the distribution repository"""
		import git
		
		# the path to cut is (root_dir - repo.working_dir)
		cut_path = os.path.abspath(root_dir)[len(os.path.abspath(repo.working_tree_dir))+1:]
		def path_rewriter(entry):
			# remove the root portion of the path as it is supposed to be relative
			# to the repository. 
			return entry.path[len(cut_path)+1:]	# +1 to cut the separator
		# END path rewriter
		
		def path_generator():
			for root, dirs, files in os.walk(root_dir):
				for f in files:
					yield os.path.join(root, f)
				# END for each file
			# END for each iteration
		# END path generator
		
		# clear out the original index by deleting it
		try:
			os.remove(repo.index.path)
		except OSError:
			# it doesn't even exist
			pass
		# END remove index
		
		# add all files, rewriting their paths accordingly
		repo.index.add(path_generator(), path_rewriter=path_rewriter)
		
		# finalize the commit, advancing the head
		# Provide a good comment that helps associating the distribution commit
		# with the current repository commit. We handle the case that the distribution
		# repository is the root repository, hence the last actual head reference is 
		# stored in a temporary symbolic ref. It will not exist of root_repo and repo
		# are different repositories
		prev_root_head = git.SymbolicReference(root_repo, self.prev_head_name)
		root_commit = None
		suffix = ''
		if not prev_root_head.is_valid():
			prev_root_head = root_repo.head
		# END get actual commit reference
		root_commit = prev_root_head.commit
		
		if root_repo.is_dirty(index=False, working_tree=True, untracked_files=False):
			suffix = "-dirty"
		# END handle suffix
		
		commit = repo.index.commit("%s@%s%s" % (self.distribution.get_fullname(), root_commit, suffix), head=True)
		
		# check whether the commit encapsulates new information - did the tree change ?
		if commit.parents and commit.parents[0].tree == commit.tree:
			log.info("Dropped created commit %s as it contained the same tree as its parent commit" % commit)
			commit = commit.parents[0] 
			repo.head.commit = commit
		# END check duplicate data and drop commit if required
		
		# finally, create a tag which is unique for the branches and the actual version
		# If the commit didn't change anything, it might already exist, but we 
		# don't care about that
		# In case the user managed to adjust data and create a new tree, but kept 
		# the version the same for some reason ( you could do that if you really 
		# want to ), we force the tag creation to update it in these cases
		# If the user wants it, we do it, no questions asked
		tag_name = "%s-%s" % (self.branch_name(), root_tag.name)
		git.Tag.create(repo, tag_name, force=True)
			 
		return prev_root_head, commit
		
	#} END utilities
	
	#{ Interface 
	def update_git(self, root_dir):
		"""Put the contents in the root_dir into the configured git repository
		Its important to note that the actual relative location of root_dir does not
		matter as long as it is inside the git repository. The later object paths
		within the git repository will all be relative to root_dir."""
		if not self.distribution.use_git:
			return
		
		from mrv.util import CallOnDeletion
		try:
			import git
		except ImportError:
			raise ImportError("Could not import git, please make sure that gitpython is available in your installation")
		# END end 
		
		# searches for closest available repo in parent dirs, might end up in 
		# the developers dir which is okay as well.
		repo = git.Repo(root_dir)
		root_repo = self.distribution.root_repo
		
		dirty_kwargs = dict(index=True, working_tree=False, untracked_files=False)
		if root_repo.is_dirty(**dirty_kwargs):
			raise EnvironmentError("Please commit your changes in index of repository %s and try again" % root_repo)
		
		if repo.is_dirty(**dirty_kwargs):
			raise EnvironmentError("Cannot operate on a dirty index - please have a look at git repository at %s" % repo)
		# END abort on dirty index
		
		
		# we require the current commit to be tagged
		root_tag = self.distribution.handle_version_and_tag()
		
		try:
			prev_head_ref = repo.head.ref
			__IndexCleanup = CallOnDeletion(lambda : self.set_head_to(repo, prev_head_ref))
		except TypeError:
			# ignore detached heads
			pass 
		# END handle head is detached
		
		
		# checkout the target branch gently ( index and head only )
		branch_name = self.branch_name()
		head_ref = self.set_head_to(repo, branch_name)
		assert repo.head.ref == head_ref
		
		# add our all files below our root
		root_head, commit = self.add_files_and_commit(root_repo, repo, root_dir, root_tag)
		
		# PUSH CHANGES
		##############
		# allow to auto-push to all or given remotes for both repositories
		# fill in defaults
		root_head = (root_head.is_detached and root_head) or root_head.ref
		self.push_to_remotes(root_repo, [root_head], self.root_remotes)
		self.push_to_remotes(repo, [head_ref], self.dist_remotes)
		
	
	#} END interface 
	

class BuildPython(_GitMixin, build_py):
	"""Customize the command preparing python modules in order to skip copying 
	original py files if compile is specified. Additionally we allow the python 
	interpreter to be specified as the bytecode is incompatible between the versions"""
	
	re_script_first_line = re.compile('^(#!.*python)[0-9.]*([ \t].*)?$')
	description="Implements byte-compilation with different python interpreter versions"
	
	#{ Configuration
	
	# A sequence of modules to exclude, i.e. '.modulename' or 'this.that'
	exclude_modules = ( '.test', '.doc' )
	
	# if set, pyo will be renamed to pyc, for some reason the pyo extension is not
	# common and not properly supported by python itself
	rename_pyo_to_pyc = True
	
	build_py.user_options.extend(
	[('exclude-from-compile', 'e', "Exclude the given comma separated list of file(globs) from being compiled")]
									)
	
	_GitMixin.adjust_user_options(build_py.user_options)
	#} END configuration 
	
	#{ Internals
	
	def _exclude_items(self, package_name):
		"""Exclude the given package name from our packages and datafiles
		:param package_name: The name of the package, i.e. '.test'"""
		token = package_name
		if self.packages:
			self.packages = [ p for p in self.packages if token not in p ]
		if self.py_modules:
			self.py_modules = [ p for p in self.py_modules if token not in p ]
			
		# additionally, remove all data files which appear to be tests
		if self.data_files:
			# its sooo terrible that it is named 'data_files', but in fact contains
			# a tuple with much more information !
			# Besides, every module we build is represented in here, even though 
			# there are no 'data files' ... !
			self.data_files = [ 	(package, src_dir, build_dir, filenames) 
									for package, src_dir, build_dir, filenames in self.data_files 
									if token not in package ]
		# END handle data files
	
	def handle_exclusion(self):
		"""Apply the exclusion patterns"""
		for exclude_pattern in self.exclude_modules:
			self._exclude_items(exclude_pattern)
		
	#} END internals
	
	#{ Overridden Methods 
	
	def initialize_options(self):
		build_py.initialize_options(self)
		self.py_version = None
		self.maya_version = None		# set later by distutils
		self.needs_compilation = None
		self.exclude_from_compile = list()
		
	def finalize_options(self):
		build_py.finalize_options(self)
		_GitMixin.finalize_options(self)
		
		self.maya_version = self.distribution.maya_version
		self.py_version = self.distribution.py_version
		self.needs_compilation = self.compile or self.optimize
		self.exclude_from_compile = self.distribution.fixed_list_arg(self.exclude_from_compile)
		
		self.handle_exclusion()
		
		# HANDLE BRANCH SUFFIX
		if self.needs_compilation:
			self.branch_suffix = '-py'+sys.version[:3]
		else:
			self.branch_suffix = '-pyany'
		# END handle suffix
		
	def byte_compile( self, files, **kwargs):
		"""If we are supposed to compile, remove the original file afterwards"""
		
		if self.needs_compilation and self.py_version is None:
			raise ValueError("If compilation is requested, the'%s' option must be specified" % self.distribution.opt_maya_version)
		# END handle errors
		
		# MAKE EXCLUSION
		for exclude_pattern in self.exclude_from_compile:
			remove_files = fnmatch.filter(files, exclude_pattern)
			for f in remove_files:
				files.remove(f)
			# END remove all matched files
		# END for each exclude pattern to apply
		
		# assure we byte-compile in a standalone interpreter, manipulating the 
		# sys.executable as it will be used later
		prev_debug = __debug__
		prev_executable = sys.executable
		if self.needs_compilation:
			# this forces to use a standalone process
			__builtin__.__debug__ = False
			
			# which is hopefully in the path
			sys.executable = "python%g" % self.py_version
		# END preparation
		
		rval = build_py.byte_compile(self, files, **kwargs)
		
		if self.needs_compilation:
			# restore original values
			__builtin__.__debug__ = prev_debug
			sys.executable = prev_executable
			
			# super class implementation handles the compilation and optimization 
			# as if it was a totally separate case and duplicates code for whichever 
			# reason 
			for py_file in (f for f in files if f.endswith('.py')):
				log.debug("Removing original file after byte compile: %s" % py_file)
				os.remove(py_file)
				
				if self.rename_pyo_to_pyc:
					base, ext = os.path.splitext(py_file)
					pyo_file = base + ".pyo"
					if os.path.isfile(pyo_file):
						pyc_file = base + ".pyc"
						os.rename(pyo_file, pyc_file)
						log.debug("Renamed %s to %s" % (pyo_file, pyc_file))
					# END check and rename
				# END rename file
			# END for each python file to remove
		# END post processing
		
		
		return rval
	
	def find_data_files(self, package, src_dir):
		"""Fixes the underlying method by allowing to specify whole directories
		whose files will be copied recursively. Thanks python for not even providing 
		the bare mininum so people end up reimplementing parts of the 'distribution system'"""
		# ALLOW DIRECTORY RECURSION
		# preprocess the globs listing in package data: If it is not a glob, but 
		# appears to be a directory, expand the directory tree and simple append
		# the respective files ourselves
		patterns = self.package_data.get(package, None)
		add_files = list()
		ignore_patterns = list()
		if patterns:
			cl = len(src_dir) + 1	# cut length including path separator 
			for pt in patterns[:]:
				if pt.startswith('!'):
					patterns.remove(pt)
					ignore_patterns.append(pt[1:])
					continue
				# END handle ignore pattern
				d = os.path.join(src_dir, pt)
				if os.path.isdir(d):
					patterns.remove(pt)		# remove original
					for root, dirs, files in os.walk(d):
						for f in files:
							add_files.append(os.path.join(root, f))
						# END for each actual directory
					# END for each directory to walk
				# END expand directory
			# END for each patterm
		# END handle expand patterns
		
		files = build_py.find_data_files(self, package, src_dir)
		
		if ignore_patterns:
			for pt in ignore_patterns:
				for flist in (files, add_files):
					ignored_files = fnmatch.filter(flist, pt)
					print pt
					print flist
					for f in ignored_files:
						flist.remove(f)
					# END brute force remove files
				# END for list to handle
			# END for each ignore pattern
		# END remove ignored files
		
		# FIX DIRECTORIES
		# additionally ... prune out items which are directories, as the system
		# is as stupid as it gets, so it ends up trying to copy a directory as 
		# if it was a file
		for f in files[:]:
			if os.path.isdir(f):
				files.remove(f)
			# END remove directories
		# END for each file
		
		return files + add_files
		
	def fix_scripts(self):
		"""Check what the user classified as script and fix the first line
		to point to the right python interpreter version (only if we are compiling).
		Additionally, make the file executable on linux"""
		out_dir = self._build_dir()
		scripts_abs = [ os.path.join(out_dir, s) for s in self.distribution.scripts ]
		scripts_abs = [ s for s in scripts_abs if os.path.isfile(s) ]	# skip pruned
		if not scripts_abs:
			return
		# END early abort
		
		if self.needs_compilation:
			for file in scripts_abs:
				lines = open(file).readlines()
				if not lines:
					continue
				# END skip empty
				
				m = self.re_script_first_line.match(lines[0])
				if not m:
					continue
				# END skip if no shebang
				
				lines[0] = "%s%s%s\n" % (m.group(1), sys.version[:3], m.group(2) or '')
				open(file, 'wb').writelines(lines)
			# END for each file
		# END fix first line
		
		if os.name == 'posix':
			for file in scripts_abs:
				oldmode = os.stat(file).st_mode & 07777
				newmode = (oldmode | 0555)
				if newmode != oldmode:
					log.info("changing mode of %s from %o to %o", file, oldmode, newmode)
					os.chmod(file, newmode)
				# END change mode
			# END for each script
		# END make executable
		
		
	def _build_dir(self):
		""":return: directory into which all files will be put"""
		# this works ... checked their code which seems hacky, so we continue with the 
		# hackiness
		return os.path.join(self.build_lib, self.distribution.rootmodule.__name__)
		
	def run(self):
		"""Perform the main operation, and handle git afterwards
		:note: It is done at a point where the py modules as well as the executables
		are available. In case there are c-modules, these wouldn't be availble here."""
		build_py.run(self)
		
		# FIX SCRIPTS
		##############
		self.fix_scripts()
		
		# HANDLE GIT
		############
		self.update_git(self._build_dir())

	#} END overridden methods 


class GitSourceDistribution(_GitMixin, sdist):
	"""Instead of creating an archive, we put the source tree into a git repository"""
	#{ Configuration 
	branch_suffix = '-src'
	#} END configuration
	
	_GitMixin.adjust_user_options(sdist.user_options)
	
	#{ Overridden Functions
	
	def finalize_options(self):
		"""As the inheritance hierarchy is screwed up with old-style classes, 
		we have to forward to the call manually to our bases ... """
		sdist.finalize_options(self)
		_GitMixin.finalize_options(self)
	
	def make_archive(self, base_name, format, root_dir=None, base_dir=None):
		self.update_git(base_dir)
		super(_GitMixin, self).make_archive(base_name, format, root_dir, base_dir)
		
	#} END overridden functions


class DocCommand(_GitMixin, Command):
	"""Build the documentation, and include everything into the git repository if 
	required."""
	
	cmdname = 'docdist'
	
	#{ Configuration
	user_options = [ 
					('zip-archive', 'z', "If set, a zip archive will be created")
					]
					
	branch_suffix = '-doc'
	
	_GitMixin.adjust_user_options(user_options)
	#} END configuration
	
	def __init__(self, *args):
		self.docgen = None
		self.dist_dir = None
		self.zip_archive = False
	
	def initialize_options(self):
		# this needs to be here or we get an error because of the bitchy base class
   	   pass
   
	def finalize_options(self):
		_GitMixin.finalize_options(self)
		# documentation generator instance, only set if docs should be included
		self.docgen = None
		if self.dist_dir is None:
			self.dist_dir = self.distribution.dist_dir
		self._init_doc_generator()
	
	def run(self):
		if not self.distribution.use_git and not self.zip_archive:
			raise ValueError("Please specify to use git or to generate a zip-archive")
		# END assert config
		
		html_out_dir, was_built = self.build_documentation()
		
		if self.zip_archive:
			self.create_zip_archive(html_out_dir)
		# END create zip
	
		if self.distribution.use_git:
			self.update_git(html_out_dir)
		# END handle git
	
	#{ Interface
	
	def create_zip_archive(self, html_out_dir):
		"""Create a zip archive from the data in the html output directory
		:return: path to the created zip file"""
		fname = "%s-doc" % self.distribution.get_fullname()
		base_name = os.path.join(self.dist_dir, fname)
		
		zfile = self.make_archive(base_name, "zip", base_dir='.', root_dir=html_out_dir)
		self.distribution.dist_files.append((self.cmdname, '', zfile))
		return zfile
	
	def build_documentation(self):
		"""Build the documentation with our current version tag - this allows
		it to be included in the release as it has been updated
		:return: tuple(html_base, Bool) tuple with base directory containing all html
		files ( possibly with subdirectories ), and a boolean which is True if 
		the documentation was build, False if it was still uptodate """
		base_dir = self._init_doc_generator()
		
		# CHECK IF BUILD IS REQUIRED
		############################
		html_out_dir = self.docgen.html_output_dir()
		index_file = html_out_dir / 'index.html'
		needs_build = True
		if index_file.isfile():
			needs_build = False
			# version file for sphinx really should exist at least, its the main 
			# documentation no matter what
			st = 'sphinx'
			if not self.docgen.version_file_name(st, basedir=base_dir).isfile():
				needs_build = True
			# END check existing version info
			
			if not needs_build:
				for token in ('coverage', 'epydoc', st):
					# check if the docs need to be rebuild
					try:
						self.docgen.check_version('release', token)
					except EnvironmentError:
						needs_build = True
					# END docs don't need to be build
				# END for each token
			# END additional search
		# END check version as index exists
		
		if not needs_build:
			log.info("Skipped building documentation as it was uptodate and complete")
			return (html_out_dir, False)
		# END skip build
		
		# when actually creating the docs, we start the respective script as it 
		# might as well be re-implemented in a derived project, and is probably 
		# safest to do
		import mrv.cmd.base
		makedocpath = mrv.cmd.base.find_mrv_script('makedoc')
		
		# makedoc must be started from the doc directory - adjust makedoc
		p = self.spawn_python_interpreter((makedocpath.basename(), ), cwd=base_dir)
		if p.wait():
			raise ValueError("Building of Documentation failed")
		# END wait for build to complete
		
		return (html_out_dir, True)
	#} END interface 
	
	#{ Internal
	def _init_doc_generator(self):
		"""initialize the docgen instance, and return the base_dir at which 
		it operates"""
		base_dir = os.path.join('.', 'doc')
		if self.docgen is not None:
			return base_dir
		# END handle duplicate calls 
		
		# try to use an overriden docgenerator, then our own one
		GenCls = None
		try:
			docbase = __import__("%s.doc.base" % self.rootmodule.__name__, fromlist=['doesntmatter'])
			GenCls = docbase.DocGenerator
		except (ImportError, AttributeError):
			import mrv.doc.base as docbase
			GenCls = docbase.DocGenerator
		# END get doc generator class
		
		if not os.path.isdir(base_dir):
			raise EnvironmentError("Cannot build documentation as '%s' directory does not exist" % base_dir)
		# END check doc dir exists
		
		self.docgen = GenCls(base_dir=base_dir)
		return base_dir
	
	#} END internal

class Distribution(object, BaseDistribution):
	"""Customize available options and behaviour to work with mrv and derived projects"""
	
	#{ Configuration
	# root package module, will be set by the main routine, must be set 
	# for this class to work
	rootmodule = None 
	
	# if True, every package in the 'ext' folder will be included in the distribution as well
	# .git repository data will be pruned
	include_external = True
	
	
	# requires map - lists additional includes for different distribution outputs
	requires_map = dict(	sdist = [ 'nose', 'epydoc', 'sphinx', 'gitpython' ], 
							bdist = list() ) 
	
	
	# directory to which all of our comamnds will store their distribution data
	dist_dir = 'dist'
	#} END configuration
	
	
	# Additional Global Options
	opt_maya_version = 'maya-version'
	
	BaseDistribution.global_options.extend(
		( ('%s=' % opt_maya_version, 'm', "Specify the maya version to operate on"),
		  ('regression-tests=', 't', "If set (default), the regression tests will be executed, distribution fails if one test fails"),
		  ('use-git=', 'g', "If set (default), the build results will be put into a git repository"), )
	)
	
	
	#{ Internals
	
	@classmethod 
	def modifiy_sys_args(cls):
		"""Parse our own arguments off the args list and modify the argument 
		stream accordingly.
		
		:note: needs to be called before setup of the distutils is called"""
		rargs = [sys.argv[0]]
		args = sys.argv[1:]
		while args:
			arg = args.pop(0)
			rargs.append(arg)
		# END while there are args
		
		del(sys.argv[:])
		sys.argv.extend(rargs)
	
	@classmethod
	def version_string(cls, version_info):
		""":return: version string from the given version info which is assumed to 
		be in the default python version_info format ( sys.version_info )"""
		base = "%i.%i.%i" % version_info[:3]
		if version_info[3]:
			base += "-%s" % version_info[3]
		return base
		
	def postprocess_metadata(self):
		"""Called after the commandline has been parsed. With all information available
		we can decide whether additional dependencies need to be specified"""
		
		# HANDLE DEPENDENCIES
		num_dist_commands = 0
		for key in sorted(self.requires_map.keys()):
			if key in self.commands:
				if self.metadata.requires is None:
					self.metadata.requires = list()
				# END assure we have a list
				
				# assign unique depends
				rlist = self.requires_map[key]
				self.metadata.set_requires(sorted(list(set(self.metadata.requires) | set(rlist)))) 
				num_dist_commands += 1
			# END if we have requirements for a command
		# END for each distribution command
		
		# for now, we can only handle one dist command at a time !
		# this could be improved though 
		if num_dist_commands > 1:
			raise AssertionError("Currently we can only process one distribution target per invocation")
		# END assure only one dist command per invocation
		
	def _query_user_token(self, tokens):
		"""Read tokens from user and finally return a token he picked
		:raise Exception: if user failed in some point.
		:return: tuple with version info in corresponding format"""
		ml = 5
		assert len(tokens) == ml, "invalid token format: %s" % str(tokens)
		
		while True:
			ot = list()
			
			# provide all tokens to the user and allow him to change each one
			print "The current version is: %s" % ', '.join(str(t) for t in tokens)
			print "Each version token will be presented to you in order, and you may provide an alternative"
			print "Once you are happy with the result, it will be written to the init file"
			print ""
			for count, (token, ttype) in enumerate(zip(tokens, (int, int, int, str, int))):
				while True:
					answer = raw_input("%s %i of %i == %s [%s]: " % (ttype.__name__, count+1, ml, token, token))
					if answer == '':
						answer = str(token)
					# END handle default answer
					
					try:
						converted = ttype(answer)
						if issubclass(ttype, basestring):
							converted = converted.strip()
							for char in "\"'":
								if converted.endswith(char): 
									converted = converted[:-1]
								if converted.startswith(char):
									converted = converted[1:]
							# END for each character to truncate
						# END handle strings
							
						ot.append(converted)
						break		# get out of the type loop
					except ValueError:
						print "Answer %r could not be converted to %s - please try again" % (answer, ttype.__name__)
						continue
					# END exception handline
				# END get type right loop
			# END for each token/type pair
			
			# present the version to the user, one last time
			print "The version you selected is: %s" % ', '.join(str(t) for t in ot)
			print "Continue with it or try again ?"
			asw = 'continue'
			answer = raw_input("%s/retry [%s]: " % (asw, asw)) or asw
			if answer != asw:
				tokens = ot
				continue
			# END handle retry
			
			return tuple(ot)
		# END while to determine user is happy
		
	def handle_version_and_tag(self):
		"""Assure our current commit in the main repository is tagged properly
		If so, continue, if not, try to create a tag with the current version.
		If the version was already tagged before, help the user to adjust his 
		version string in the root module, make a commit, and finally create 
		the tag we were so desperate for. The main idea is to enforce a unique 
		version each time we make a release, and to make that easy
		
		:return: TagReference object created
		:raise EnvironmentError: if we could not get a valid tag"""
		import git
		
		root_repo = self.root_repo
		root_head_commit = root_repo.head.commit
		tags = [ t for t in git.TagReference.iter_items(root_repo) if t.commit == root_head_commit ]
		if len(tags) == 1:
			return tags[0]
		# END tag existed
		
		
		msg = "Please create a tag at your main repository at your currently checked-out commit to mark your release"
		createexc = EnvironmentError(msg)
		if not sys.stdout.isatty():
			raise createexc
		# END abort if we cannot communicate
			
		def version_tag(vi):
			tag_name = 'v%i.%i.%i' % vi[:3]
			if vi[3]:
				tag_name += "-%s" % vi[3]
			# END append suffix
			
			out_tag = None
			return git.Tag.from_path(root_repo, git.Tag.to_full_path(tag_name))
		# END version tag creator 
		
		# CREATE TAG ?
		##############
		# from current version
		# ask the user to create a tag - make sure it does not yet exist 
		# before asking
		target_tag = version_tag(self.rootmodule.version_info)
		if not target_tag.is_valid():
			asw = "abort"
			msg = "Would you like me to create the tag %s in your repository at %s to proceed ?\n" % (target_tag.name, root_repo.working_tree_dir)
			msg += "yes/%s [%s]: " % (asw, asw)
			answer = raw_input(msg) or asw
			if answer != 'yes':
				raise createexc
			# END check query
			
			return git.TagReference.create(root_repo, target_tag.name, force=False)
		# END could create the tag with current version 
		
		# INCREMENT VERSION AND CREATE TAG
		##################################
		asw = "adjust version"
		msg = """Your current commit is not tagged - the automatically generated tag name %s does already exist at a previous commit.
Would you like to adjust your version_info or abort ?
%s/abort [%s]: """ % (target_tag.name, asw, asw) 
		answer = raw_input(msg) or asw
		if answer != asw:
			raise createexc
		# END abort automated creation
		
		# ASSURE INIT FILE UNCHANGED
		# parse the init script and adjust it - if there are changes in the 
		# working tree file, abort !
		init_file = os.path.join(ospd(self.rootmodule.__file__), "__init__.py")
		if len(root_repo.index.diff(None, paths=init_file)):
			raise EnvironmentError("The init file %r that would be changed contains uncommitted changes. Please commit them and try again" % init_file)
		# END assure init file unchanged
		
		out_lines = list()
		made_adjustment = False
		fmtexc = ValueError("Expecting following version_info format: version_info = (1, 0, 0, 'string', 0)")
		for line in open(init_file, 'r'):
			if not made_adjustment and line.strip().startswith('version_info'):
				# present the stripped strings separated by commas - it must be a tuple
				# fail on parsing errors
				sline = line.strip()
				if not sline.endswith(')'):
					raise fmtexc
					
				tokens = [ t.strip() for t in sline[sline.find('(')+1:-1].split(',') ]
				
				if len(tokens) != 5:
					raise fmtexc
				
				while True:
					tokens = self._query_user_token( tokens )
					
					# verify the version provides a unique tag name
					target_tag = version_tag(tokens)
					if not target_tag.is_valid():
						break
					# END have valid tag ( as it does not yet exist )
					
					asw = 'increment'
					print "The tag created according to your version info %r does already exist. Increment the minor version and retry ?" % target_tag.name
					answer = raw_input("%s/abort [%s]: " % (asw, asw)) or asw
					if answer != asw:
						raise createexc
					# END handle answer
					
					# increment minor
					ptl = list(tokens)
					ptl[2] += 1
					tokens = tuple(ptl)  
					print "\nIncremented minor version to %i" % ptl[2]
					print "You will be asked to verify the new version again, allowing you to adjust it manually as well\n"
				# END while user didn't provide a unique token
				
				# build a new line with our updated version info
				line = "version_info = ( %i, %i, %i, '%s', %i )\n" % tokens
				
				made_adjustment = True
			# END adjust version-info line with user help
			out_lines.append(line)
		# END for each line
		
		if not made_adjustment:
			raise fmtexc
		
		# query the commit message
		cmsg = "Adjusted version_info to %s " % target_tag.name[1:]
		
		print "The changes to the init file at %r will be committed." % init_file 
		print "Please enter your commit message or hit Ctrl^C to abort without a change to your file"
		cmsg = raw_input("[%s]: " % cmsg) or cmsg
		
		# write the file back - at this point the index is garantueed to be clean
		# so our init file is the only one that changes
		open(init_file, 'wb').writelines(out_lines)
		root_repo.index.add([init_file])
		commit = root_repo.index.commit(cmsg, head=True)
		
		# create tag on the latest head 
		git.TagReference.create(root_repo, target_tag.name, force=False)
		
		return target_tag
			
	def spawn_python_interpreter(self, args, cwd=None):
		"""Start the default python interpreter, and handle the windows special case
		:param args: passed to the python interpreter, must not include the executable
		:param cwd: if not None, it will be set for the childs working directory
		:return: Spawned Process
		:note: All output channels of our process will be connected to the output channels 
		of the spawned one"""
		import mrv.cmd.base
		py_executable = mrv.cmd.base.python_executable()
		
		actual_args = (py_executable, ) + tuple(args)
		log.info("Spawning: %s" % ' '.join(actual_args))
		proc = subprocess.Popen(actual_args, stdout=sys.stdout, stderr=sys.stderr, cwd=cwd)
		return proc
		
	def perform_regression_tests(self):
		"""Run regression tests and fail with a report if one of the regression 
		test fails""" 
		import mrv.cmd.base
		tmrvrpath = mrv.cmd.base.find_mrv_script('tmrvr')
		
		p = self.spawn_python_interpreter((tmrvrpath, ))
		if p.wait():
			raise ValueError("Regression Tests failed")
			
	#} END Internals 
	
	
	#{ Path Generators
	
	def _rootpath(self):                   
		""":return: path to the root of the rootpackage, which includes all modules
		and subpackages directly"""
		return ospd(os.path.abspath(self.rootmodule.__file__)) 
	
	#} END path generators

	
	#{ Interface
	
	@classmethod
	def fixed_list_arg(cls, value):
		"""As the comamndline parsing is as bad as it gets, it will not parse the 
		correct types, nor will it split ',' separated items into a list correctly.
		If options are provided via the comandline, they are generally screwed up
		as they are plain strings, so each and every command has to check and verify
		them by itself. Well done, could have been a nice base task job.
		We check value for a comman separated string, and return the parsed list
		if necessary, or the value itself if it is already a list or tuple"""
		if isinstance(value, (list, tuple)):
			return value
		return value.split(',')
	
	@classmethod
	def retrieve_root_module(cls, basedir='.'):
		"""Make sure the root package is in the python path and is set as our root
		:return: root package object"""
		packageroot = os.path.realpath(os.path.abspath(basedir))
		root_package_name = os.path.basename(packageroot)
		
		try:
			cls.rootmodule = __import__(root_package_name)
		except ImportError:
			sys.path.append(ospd(packageroot))
			try:
				cls.rootmodule = __import__(root_package_name)
			except ImportError:
				del(sys.path[-1])
				raise ImportError("Failed to import MRV as it could not be found in your syspath, nor could it be deduced"); 
			# END second attempt exception handling
		# END import exception handling
		
		return cls.rootmodule
		
	
	
	def get_packages(self):
		""":return: list of all packages in rootpackage in __import__ compatible form"""
		base_packages = [self.rootmodule.__name__] + [ self.rootmodule.__name__ + '.' + pkg for pkg in find_packages(self._rootpath()) ]
		
		# add external packages - just pretent its a package even though it it just 
		# a path in external
		ext_path = os.path.join(ospd(__file__), 'ext')
		if self.include_external and os.path.isdir(ext_path):
			for root, dirs, files in os.walk(ext_path):
				# remove hidden paths
				for dir in dirs[:]:
					if not dir.startswith('.'):
						continue
					try:
						dirs.remove(dir)
					except ValueError:
						pass
					# END exception handling
				# END for each path to check
				
				# process paths
				for dir in dirs:
					base_packages.append(self.rootmodule.__name__+"."+os.path.join(root, dir).replace(os.sep, '.'))
				# END for each remaining valid directory
			# END walking external dir
		# END if external directory exists
		
		return base_packages
		
	#} END interface 
	
	#{ Overridden Methods
	def __new__(cls, *args, **kwargs):
		"""Fix the objet.__new__ call with arguments that would occur. This
		is a serious issue, not only here but also for mixin classes that need 
		initialization - types don't know who derives from them, and which hierarchy
		they are in, and they have to call super to pass on the __init__ call to 
		possible mixins in the derived hierarchy"""
		return object.__new__(cls)
		
	def __init__(self, *args, **kwargs):
		"""Initialize base and set some useful defaults"""
		BaseDistribution.__init__(self, *args, **kwargs)
		if self.rootmodule is None:
			self.retrieve_root_module()
		# END assure root is set
		
		# at this point, the options have not yet been parsed
		self.py_version = float(sys.version[:3])
		self.maya_version = None
		self.regression_tests = True
		self.use_git = True
		self.root_repo = None
		
		if not self.packages:
			self.packages = self.get_packages()
		# END auto-generate packages if not explicitly set
		
		# Override Commands
		self.cmdclass[build_py.__name__] = BuildPython
		self.cmdclass[sdist.__name__] = GitSourceDistribution
		self.cmdclass[DocCommand.cmdname] = DocCommand
		
	def __del__(self):
		"""undo monkey patches"""
		if sys is None:
			return
		
		if hasattr(self, '_orig_sys_version'):
			sys.version = self._orig_sys_version
		
	def parse_command_line(self):
		"""Handle our custom options"""
		rval = BaseDistribution.parse_command_line(self)
		if self.maya_version is not None:
			import mrv.cmd.base
			try:
				self.py_version = mrv.cmd.base.python_version_of(float(self.maya_version))
				
				# APPLY MONKEY PATCHES
				# NOTE: There is a method called get_python_version, but it is not used
				# by all commands, so the safest thing is to override sys.version ... 
				# ... yeah, whatever
				self._orig_sys_version = sys.version
				sys.version = "%g" % (self.py_version)
			except ValueError:
				raise ValueError("Incorrect MayaVersion format: %s" % self.maya_version)
		# END handle python version
		
		# in install mode, we never use git or run regression tests
		if 'install' in self.commands:
			log.debug("Disabled usage of git and regression testing as install command is present")
			self.use_git = False
			self.regression_tests = False
		# END handle install mode
		
		self.postprocess_metadata()
		
		# handle evil types - the underlying systems puts strings into the variables
		# ... how can you ?
		self.use_git = int(self.use_git)
		self.regression_tests = int(self.regression_tests)
		
		# setup git if required
		if self.use_git:
			import git
			self.root_repo = git.Repo(ospd(self.rootmodule.__file__))
		# END init root repo


		return rval
		
	def run_commands(self):
		"""Perform required pre- and post-run actions"""
		if self.use_git:
			self.handle_version_and_tag()
		# END assure git tag is set correctly
		
		if self.regression_tests:
			self.perform_regression_tests()
		# END regression tests
		
		BaseDistribution.run_commands(self)
		
	
	#} END overridden methods


#} END commands



def main(args, distclass=Distribution):
	distclass.modifiy_sys_args()
	root = distclass.retrieve_root_module()
	
	setup(
	      distclass=distclass,
	      name = root.project_name,
		  version = distclass.version_string(root.version_info),
		  description = root.description,
		  author = root.author,
		  author_email = root.author_email,
		  url = root.url,
		  license = root.license,
		  package_dir = {root.__name__ : ''},
		  
		  **root.setup_kwargs
		  )
	

if __name__ == '__main__':
	main(sys.argv[1:])
