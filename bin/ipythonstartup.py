# assure site is properly setup
import sys
import site
# assure all sitelibs are available, important for OSX
for syspath in sys.path:
	if syspath.endswith('site-packages'):
		site.addsitedir(syspath, set(sys.path))
# END for each syspath

# init maya
import mayarv.maya

import os

# try to load custom settings
if "IMAYARV_CONFIG" in os.environ:
	filepath = os.environ[ "IMAYARV_CONFIG" ]
	try:
		execfile( filepath )
	except Exception:
		print "Failed to run configuration script"
else:
	print "Set IMAYARV_CONFIG to point to python script doing additional setup"

# init ipython - needs to be available in your local python installation
try: 
	import IPython
	IPython.Shell.start().mainloop()
except:
	print "Warning: Failed to load ipython - please install it for more convenient maya python interaction"

