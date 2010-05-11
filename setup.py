import os
import sys
import __builtin__

from distutils.core import setup
from distutils.dist import Distribution as BaseDistribution
from distutils import log


import distutils.command
from distutils.command.build_py import build_py
from distutils.command.bdist_dumb import bdist_dumb
from distutils.command.sdist import sdist

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


#{ Utilities

def get_root_package():
	"""Make sure the root package is in the python path
	:return: root package object"""
	ospd = os.path.dirname
	packageroot = ospd((os.path.realpath(os.path.abspath(__file__))))
	root_package_name = os.path.basename(packageroot)
	try:
		return __import__(root_package_name)
	except ImportError:
		sys.path.append(ospd(packageroot))
		try:
			return __import__(root_package_name)
		except ImportError:
			del(sys.path[-1])
			raise ImportError("Failed to import MRV as it could not be found in your syspath, nor could it be deduced"); 
		# END second attempt exception handling
	# END import exception handling
#} END utilities


#{ Decorators


#} END decorators 

#{ Commands 


class _GitMixin(object):
	"""Provides functionality to add files and folders within a base directory 
	into the **root** of a git repository of our choice"""
	
	#{ Configuration
	# default name of the remote with which to interact
	remote_name = 'distro'
	
	# name of symbolic reference which keeps the previous reference name to which 
	# HEAD pointed before we changed HEAD
	prev_head_name = 'DIST_ORIG_HEAD'
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
		self.remote_name = kwargs.pop('remote_name', 'distro')
	
	#{ Utilities
	
	def branch_name(self):
		"""
		:return: name of the branch identifying our current release configuration
			The branch will be populated with the respective tags that in fact include 
			a version. The branch does not include a version."""
		root_name = self.distribution.root.__name__
		suffix = '_src'
		build_py_cmd = self.distribution.get_command_obj('build_py', create=False)
		
		if build_py_cmd and build_py_cmd.needs_compilation:
			suffix = '_py'+sys.version[:3]
		# END handle suffix
		
		return root_name + suffix
	
	def tag_name(self, repo):
		""":return: name for the tag we should use once we are done
		:param repo: repository with the distribution branch set as HEAD
		:note: this method assumes our head is already set to the distribution branch"""
		# use the actual version as base version, but increment the minor 
		# version based on the last tag in our revision history
		version_info = self.distribution.root.version_info
		return "%sv%i.%i.%i" % (self.branch_name(),) + version_info[:3]
		
	def set_head_to(self, repo, head_name):
		"""et our head to point to the given head_name. If possible, 
		update the index to represent the tree the head points to
		
		:return: Head named head_name
		:note: In the worst case, the head points to non-existing ref, as the 
			repository is still empty"""
		import git
		
		head_ref = git.Head(repo, git.Head.to_full_path(head_name))
		if head_ref.is_valid():
			repo.index.reset(head_ref, working_tree=False, head=False)
			
			# store the previous ref in a new symbolic ref
			git.SymbolicReference.create(repo, self.prev_head_name, head_ref, force=True)
		# END handle index
			
		# if the head ref exists or not, we want to change the branch to the one
		# we define. This is why we do this explicitly here. Resetting the index
		# and setting the head will just set the current branch to the commit we 
		# reset to 
		repo.head.ref = head_ref
		# END head exists handling
		
		return head_ref
		
	def add_files_and_commit(self, root_repo, repo, root_dir):
		"""
		Add all files recursively to the index as found below root_dir and commit the
		index.
		
		As a special ability, we will rewrite their paths and thus add them relative
		to the root directory, even though the git repository might be on another level.
		It also sports a simple way to determine whether the commit already exists, 
		so it will not recommit data that has just been committed.
		
		:param root_repo: Repository containing the data of the main project
		:param repo: dedicated repository containing the distribution data
		:return: Commit object """
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
		prev_head = git.SymbolicReference(root_repo, self.prev_head_name)
		root_commit = root_repo.head.commit
		suffix = ''
		if prev_head.is_valid():
			root_commit = prev_head.commit
		# END get actual commit reference
		
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
			 
		return commit
		
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
		
		
	def handle_version_and_tag(self, root_repo):
		"""Assure our current commit in the main repository is tagged properly
		If so, continue, if not, try to create a tag with the current version.
		If the version was already tagged before, help the user to adjust his 
		version string in the root module, make a commit, and finally create 
		the tag we were so desperate for. The main idea is to enforce a unique 
		version each time we make a release, and to make that easy
		
		:return: TagReference object created
		:raise EnvironmentError: if we could not get a valid tag"""
		import git
		
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
		target_tag = version_tag(self.distribution.root.version_info)
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
		init_file = os.path.join(os.path.dirname(self.distribution.root.__file__), "__init__.py")
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
		
		
	
	#} END utilities
	
	#{ Interface 
	def update_git(self, root_dir):
		"""Put the contents in the root_dir into the configured git repository
		Its important to note that the actual relative location of root_dir does not
		matter as long as it is inside the git repository. The later object paths
		within the git repository will all be relative to root_dir."""
		from mrv.util import CallOnDeletion
		try:
			import git
		except ImportError:
			raise ImportError("Could not import git, please make sure that gitpython is available in your installation")
		# END end 
		
		# searches for closest available repo in parent dirs, might end up in 
		# the developers dir which is okay as well.
		repo = git.Repo(root_dir)
		root_repo = git.Repo(os.path.dirname(self.distribution.root.__file__))
		assert root_repo != repo, "Aborting as I shouldn't be working in the main repository: %s" % repo
		
		if root_repo.is_dirty(index=True, working_tree=False, untracked_files=False):
			raise EnvironmentError("Please commit your changes in index of repository %s and try again" % root_repo)
		
		if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
			raise EnvironmentError("Cannot operate on a dirty index - please have a look at git repository at %s" % repo)
		# END abort on dirty index
		
		
		# we require the current commit to be tagged
		root_tag = self.handle_version_and_tag(root_repo)
		
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
		commit = self.add_files_and_commit(root_repo, repo, root_dir)
		
	
	#} END interface 
	

class BuildPython(_GitMixin, build_py):
	"""Customize the command preparing python modules in order to skip copying 
	original py files if compile is specified. Additionally we allow the python 
	interpreter to be specified as the bytecode is incompatible between the versions"""
	
	description="Implements byte-compilation with different python interpreter versions"
	
	#{ Configuration
	
	# if we are to byte-compile the code, the test suite ( everything in the 
	# /test/ directory ) will be excluded automatically
	exclude_compiled_test_suite = True
	
	#} END configuration 
	
	#{ Internals
	def handle_test_suite(self):
		"""Remove test-suite related packages from our package array if required"""
		if not self.exclude_compiled_test_suite or not self.needs_compilation:
			return
		# END check early abort
		
		# remove all .test. packages
		token = '.test'
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
		
	#} END internals
	
	#{ Overridden Methods 
	
	def initialize_options(self):
		build_py.initialize_options(self)
		self.py_version = None
		self.maya_version = None		# set later by distutils
		self.needs_compilation = None
		
	def finalize_options(self):
		build_py.finalize_options(self)
		
		self.maya_version = self.distribution.maya_version
		self.py_version = self.distribution.py_version
		self.needs_compilation = self.compile or self.optimize
		
		self.handle_test_suite()
		
	def byte_compile( self, files, **kwargs):
		"""If we are supposed to compile, remove the original file afterwards"""
		
		if self.needs_compilation and self.py_version is None:
			raise ValueError("If compilation is requested, the'%s' option must be specified" % self.distribution.opt_maya_version)
		# END handle errors
		
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
				log.info("Removing original file after byte compile: %s" % py_file)
				os.remove(py_file)
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
		if patterns:
			cl = len(src_dir) + 1	# cut length including path separator 
			for pt in patterns[:]:
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
		
	def run(self):
		"""Perform the main operation, and handle git afterwards
		:note: It is done at a point where the py modules as well as the executables
		are available. In case there are c-modules, these wouldn't be availble here."""
		build_py.run(self)
		
		# HANDLE GIT
		############
		# this works ... checked their code which seems hacky, so we continue with the 
		# hackiness
		package_dir = os.path.join(self.build_lib, self.distribution.root.__name__)
		self.update_git(package_dir)

	#} END overridden methods 


class GitSourceDistribution(_GitMixin, sdist):
	"""Instead of creating an archive, we put the source tree into a git repository"""
	#{ Overridden Functions
	
	def make_archive(self, base_name, format, root_dir=None, base_dir=None):
		self.update_git(root_dir)
		super(_GitMixin, self).make_archive(base_name, format, root_dir, base_dir)
		
	#} END overridden functions


class GitBinaryDistribution(_GitMixin, bdist_dumb):
	"""Instead of creating an archive, the built data will be put into a git repository."""


class Distribution(object, BaseDistribution):
	"""Customize available options and behaviour to work with mrv and derived projects"""
	
	#{ Configuration
	# root package module, will be set by the main routine, must be set 
	# for this class to work
	root = None 
	
	# if True, every package in the 'ext' folder will be included in the distribution as well
	# .git repository data will be pruned
	include_external = True
	
	
	# requires map - lists additional includes for different distribution outputs
	requires_map = dict(	sdist = [ 'nose', 'epydoc', 'sphinx', 'gitpython' ], 
							bdist = list() ) 
	
	#} END configuration
	
	
	# Additional Global Options
	opt_maya_version = 'maya-version'
	BaseDistribution.global_options.extend(
		( ('%s=' % opt_maya_version, 'm', "Specify the maya version to operate on"), )
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
			
	#} END Internals 
	
	
	#{ Path Generators
	
	def _rootpath(self):                   
		""":return: path to the root of the rootpackage, which includes all modules
		and subpackages directly"""
		return os.path.dirname(os.path.abspath(self.root.__file__)) 
	
	#} END path generators

	
	#{ Interface
	
	def get_packages(self):
		""":return: list of all packages in rootpackage in __import__ compatible form"""
		base_packages = [self.root.__name__] + [ self.root.__name__ + '.' + pkg for pkg in find_packages(self._rootpath()) ]
		
		# add external packages - just pretent its a package even though it it just 
		# a path in external
		ext_path = os.path.join(os.path.dirname(__file__), 'ext')
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
					base_packages.append(self.root.__name__+"."+os.path.join(root, dir).replace(os.sep, '.'))
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
		
		# at this point, the options have not yet been parsed
		self.py_version = float(sys.version[:3])
		self.maya_version = None
		
		if not self.packages:
			if self.root is None:
				raise ValueError("Root package is not set - it should be set in setup.main()")
			
			# assure we get all packages we need, including external if desired
			self.packages = self.get_packages()
		# END auto-generate packages if not explicitly set
		
		# Override Commands
		self.cmdclass[build_py.__name__] = BuildPython
		self.cmdclass[sdist.__name__] = GitSourceDistribution
		
	def __del__(self):
		"""undo monkey patches"""
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

		self.postprocess_metadata()

		return rval
	
	#} END overridden methods


#} END commands



def main(root, args, distclass=Distribution):
	distclass.root = root
	distclass.modifiy_sys_args()
	
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
	root = get_root_package()
	main(root, sys.argv[1:])
