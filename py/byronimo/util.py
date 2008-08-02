"""B{byronimo.util}
All kinds of utility methods and classes that are used in more than one modules

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-07-16 22:41:16 +0200 (Wed, 16 Jul 2008) $"
__revision__="$Revision: 22 $"
__id__="$Id: configuration.py 22 2008-07-16 20:41:16Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

class Singleton(object) :
	""" Singleton classes can be derived from this class,
		you can derive from other classes as long as Singleton comes first (and class doesn't override __new__ ) """
	def __new__(cls, *p, **k):
		if not '_the_instance' in cls.__dict__:
			cls._the_instance = super(Singleton, cls).__new__(cls)
		return cls._the_instance

