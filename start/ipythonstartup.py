import maya.standalone
maya.standalone.initialize()

import os

# try to load custom settings
if "PYMAYASTD_CONFIG" in os.environ:
	filepath = os.environ[ "PYMAYASTD_CONFIG" ]
	try:
		execfile( filepath )
	except Exception:
		print "Failed to run configuration script"
else:
	print "Set PYMAYASTD_CONFIG to point to python script doing additional setup"

# init ipython - needs to be available in your local python installation
try: 
	import IPython
	IPython.Shell.start().mainloop()
except:
	print "Warning: Failed to load ipython - please install it for more convenient maya python interaction"

