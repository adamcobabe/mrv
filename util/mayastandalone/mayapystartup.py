import maya.standalone
maya.standalone.initialize()

import os

# try to load custom settings
try: 
	filepath = os.environ[ "PYMAYASTD_CONFIG" ]
	execfile( filepath )
except:
	print "Set PYMAYASTD_CONFIG to point to python script doing additional setup"


# init ipython - needs to be available in your local python installation
try: 
	import IPython
	IPython.Shell.start().mainloop()
except:
	print "Warning: Failed to load ipython - please install it for more convenient maya python interaction"

