"""B{Full.import.module.path}

One line module description

More detailled, multi-
line description

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author$'
__contact__='you@somedomain.tld'
__version__=1
__license__='GPL'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"



class classname( object ):
	"""
	B{single line description}
	
	MultiLine description
	"""
	
	x = 20
	#@cvav x: my class variable
	
	#{ Overridden Object Methods
	def __init__(self):
		""" Single line Method description
		
		Multi Line Description
		@param self: this is just for demonstration purposes
		@type self: L{classname} 
		"""
		pass
	#}



