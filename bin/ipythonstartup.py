# -*- coding: utf-8 -*-
# assure site is properly setup
import sys
import os
import site
import logging

#{ Initialization 
# assure all sitelibs are available, important for OSX
def setup_syspath():
	"""Assure additional site-packages get initialized"""
	for syspath in sys.path[:]:
		if syspath.endswith('site-packages'):
			site.addsitedir(syspath, set(sys.path))
	# END for each syspath

def apply_user_configuration():
	"""Run optional user scripts"""
	# try to load custom settings
	if "IMRV_CONFIG" in os.environ:
		filepath = os.environ[ "IMRV_CONFIG" ]
		try:
			execfile( filepath )
		except Exception:
			print "Failed to run configuration script"
	else:
		print "Set IMRV_CONFIG to point to python script doing additional setup"

def setup_ipython():
	"""Perform additional ipython initialization"""
	import IPython
	
	# init maya
	import mrv.maya
	
	# make default imports
	ip = IPython.ipapi.get()
	ip.ex("from mrv.maya.all import *")
	
	# init logging
	logging.basicConfig(level=logging.INFO)
	
	# prefetch methods for convenience
	import mrv.maya.nt.typ as typ
	typ.prefetchMFnMethods()

def init_ipython():
	"""Get the main ipython system up and running"""
	# init ipython - needs to be available in your local python installation
	try: 
		import IPython
	except Exception, e:
		raise ImportError("Warning: Failed to load ipython - please install it for more convenient maya python interaction: %s" % str(e))
	# END exception handling
	
	ips = IPython.Shell.start()
	setup_ipython()
	apply_user_configuration()
	ips.mainloop()
	
# } END initialization


################
setup_syspath()
init_ipython()
################

