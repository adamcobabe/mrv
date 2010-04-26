# -*- coding: utf-8 -*-
"""Contains routines required to initialize mrv"""
import optparse
import os
import sys

__docformat__ = "restructuredtext"

#{ Globals
_maya_to_py_version_map = {
	8.5 : 2.4, 
	2008: 2.5, 
	2009: 2.5, 
	2010: 2.6,
	2011: 2.6
}

#}

#{ Maya-Intiialization
	
def is_supported_maya_version(version):
	""":return: True if version is a supported maya version
	:param version: float which is either 8.5 or 2008 to 20XX"""
	if version == 8.5:
		return True
		
	return str(version)[:2] == "20"
	
def parse_maya_version(arg, default):
	""":return: tuple(bool, version) tuple of bool indicating whether the version could 
	be parsed and was valid, and a float representing the parsed or default version.
	:param default: The desired default maya version"""
	candidate = default
	parsed = False
	try:
		candidate = float(arg)
	except ValueError:
		pass
	# END exception handling
	
	if is_supported_maya_version(candidate):
		parsed = True
	# END verify candidate
	
	return (parsed, candidate)
	
def python_version_of(maya_version):
	""":return: python version matching the given maya version
	:raise EnvironmentError: If there is no known matching python version"""
	try:
		return _maya_to_py_version_map[maya_version]
	except KeyError:
		raise EnvironmentError("Do not know python version matching the given maya version %s" % maya_version) 
	
def update_env_path(environment, env_var, value, append=False):
	"""Set the given env_var to the given value, but append the existing value
	to it using the system path separator
	
	:param append: if True, value will be appended to existing values, otherwise it will 
		be prepended"""
	curval = environment.get(env_var, None)
	if curval is not None:
		if append:
			value = curval + os.pathsep + value
		else:
			value = value + os.pathsep + curval
		# END handle append
	# END handle existing value
	environment[env_var] = value
	
def maya_location(maya_version):
	""":return: string path to the existing maya installation directory for the 
	given maya version
	:raise EnvironmentError: if it was not found"""
	mayaroot = None
	suffix = ''
	
	if sys.platform.startswith('linux'):
		mayaroot = "/usr/autodesk/maya"
		if os.path.isdir('/lib64'):
			suffix = "-x64"
		# END handle 64 bit systems
	elif sys.platform == 'darwin':
		mayaroot = "/Applications/Autodesk/maya"
	elif sys.platform.startswith('win'):
		raise NotImplementedError("todo windows")
	# END os specific adjustments
	
	if mayaroot is None:
		raise EnvironmentError("Current platform %r is unsupported" % sys.platform)
	# END assure existance of maya root
	
	mayalocation = "%s%g%s" % (mayaroot, maya_version, suffix)
	
	# OSX special handling
	if sys.platform == 'darwin':
		mayalocation=os.path.join(mayalocation, 'Maya.app', 'Contents')
	
	if not os.path.isdir(mayalocation):
		raise EnvironmentError("Could not find maya installation at %r" % mayalocation)
	# END verfy maya location
	
	return mayalocation
		
	
def create_maya_environment(maya_version):
	"""Configure os.environ to allow Maya to run in standalone mode
	:return: Dictionary with environment based on a copy of the environment of this process
	:param maya_version: The maya version to prepare to run, either 8.5 or 2008 to 
	20XX. This requires the respective maya version to be installed in a default location.
	:raise EnvironmentError: If the platform is unsupported or if the maya installation could not be found"""
	py_version = python_version_of(maya_version)
	
	pylibdir = None
	envppath = "PYTHONPATH"
	
	if sys.platform.startswith('linux'):
		pylibdir = "lib"
	elif sys.platform == 'darwin':
		pylibdir = "Frameworks/Python.framework/Versions/Current/lib"
	elif sys.platform.startswith('win'):
		raise NotImplementedError("todo windows")
	# END os specific adjustments
	
	
	# GET MAYA LOCATION
	###################
	mayalocation = maya_location(maya_version)
	
	if not os.path.isdir(mayalocation):
		raise EnvironmentError("Could not find maya installation at %r" % mayalocation)
	# END verfy maya location
	
	
	env = os.environ.copy()
	
	# ADJUST LD_LIBRARY_PATH or PATH
	################################
	# Note: if you need something like LD_PRELOAD or equivalent, add the respective
	# variables to the environment of this process before starting it
	if sys.platform.startswith('linux'):
		envld = "LD_LIBRARY_PATH"
		ldpath = os.path.join(mayalocation, 'lib')
		update_env_path(env, envld, ldpath)
	elif sys.platform == 'darwin':
		# adjust maya location to point to the actual directtoy
		mayalocation=os.path.join(mayalocation, 'Maya.app', 'Contents')
		
		dldpath = os.path.join(mayalocation, 'MacOS')
		update_env_path(env, "DYLD_LIBRARY_PATH", dldpath)
		
		dldframeworkpath = os.path.join(mayalocation, 'Frameworks')
		update_env_path(env, "DYLD_FRAMEWORK_PATH", dldframeworkpath)
		
		env['MAYA_NO_BUNDLE_RESOURCES'] = 1
		
		# on osx, python will only use the main frameworks path and ignore 
		# its own sitelibraries. We put them onto the PYTHONPATH for that reason
		# MayaRV will take care of the initialization
		ppath = "/Library/Python/%s/site-packages" % py_version
		update_env_path(env, envppath, ppath, append=True)
		
	elif sys.platform.startswith('win'):
		raise NotImplementedError("todo win PATH")
	else:
		raise EnvironmentError("Current platform %s is unsupported" % sys.platform)
	# END handle os's
	
	
	# ADJUST PYTHON PATH
	####################
	# mrv is already in the path, we just make sure that the respective path can 
	# be found in the python path. We add additional paths as well
	ospd = os.path.dirname
	ppath = os.path.join(mayalocation, pylibdir, "python%s"%py_version, "site-packages")
	ppath += os.pathsep + ospd(ospd(ospd(__file__)))
	update_env_path(env, envppath, ppath, append=True)
	
	# SET MAYA LOCATION
	###################
	# its important to do it here as osx adjusts it 
	env['MAYA_LOCATION'] = mayalocation 
	
	# export the actual maya version to allow scripts to pick it up even before maya is launched
	env['MRV_MAYA_VERSION'] = "%g" % maya_version
	
	return env

def arg_parser():
	""":return: Argument parser initialized with all arguments supported by mrv"""
	usage = """usage: %prog [mayaversion] [python interpreter arguments]
	
	mayaversion = Defaults to 8.5, valid valid values are 8.5 and 2008 to 20XX """
	parser = optparse.OptionParser(usage=usage)
	return parser

def exec_python_interpreter(args, maya_version):
	"""Replace this process with a python process as determined by the given options.
	This will either be the respective python interpreter, or mayapy.
	If it works, the function does not return
	
	:param args: remaining arguments which should be passed to the process
	:param maya_version: float indicating the maya version to use
	:raise EnvironmentError: If no suitable executable could be started"""
	py_version = python_version_of(maya_version)
	py_executable = "python%s" % py_version
	
	args = tuple(args)
	actual_args = (py_executable, ) + args
	
	try:
		os.execvp(py_executable, actual_args)
	except OSError:
		print "Python interpreter named %r not found, trying mayapy ..." % py_executable
		mayalocation = maya_location(gsion)
		mayapy_executable = os.path.join(mayalocation, "bin", "mayapy")
		
		actual_args = (mayapy_executable, ) + args
		try:
			os.execv(mayapy_executable, actual_args)
		except OSError:
			raise EnvironmentError("Could not find suitable python interpreter at %r or %r" % (py_executable, mayapy_executable))
		# END final exception handling
	# END exception handling
	
#} END Maya initialization





