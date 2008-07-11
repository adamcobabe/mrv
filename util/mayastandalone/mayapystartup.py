import maya.standalone
maya.standalone.initialize()

# init ipython - needs to be available in your local python installation
try: 
	import IPython
	IPython.Shell.start().mainloop()
except:
	print "Warning: Failed to load ipython - please install it for more convenient maya python interaction"
