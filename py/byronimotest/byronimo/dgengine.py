"""B{byronimotest.byronimo.util}
Test dependency graph engine


@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-06 12:45:38 +0200 (Tue, 06 May 2008) $"
__revision__="$Revision: 8 $"
__id__="$Id: decorators.py 8 2008-05-06 10:45:38Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
from networkx import DiGraph
from byronimo.dgengine import *

nodegraph = DiGraph()
A = Attribute

#{ TestNodes 
class SimpleAttrs( NodeBase ):
	"""Create some simple attributes"""
	#{ Plugs 
	outRand = plug( "outRand", A( int, A.readable ) )
	inInt = plug( "inInt", A( int, A.writable ) )
	inFloat = plug( "inFloat", A( float, A.readable, default = 2.0 ) )
	inFloat.affects( outRand )
	#} 
	
	
	def __init__( self ):
		super( NodeBase, self ).__init__( nodegraph )


#}


class TestDAGTree( unittest.TestCase ):
	
	def test_simpleConnection( self ):
		"""dgengine: create some simple connections"""
		pass
