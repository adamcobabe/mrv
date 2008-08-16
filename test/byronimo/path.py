"""B{byronimo.test.path}
Test path methods

@todo: actual implementation of path tests - currently it is just a placeholder assuring 
that the module can at least be imported
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


import os
import unittest
import byronimo.path

class TestPath( unittest.TestCase ):
	
	
	def test_instantiate( self ):
		"""path: test intatiation"""
		p = byronimo.path.Path( os.path.expanduser( "~" ) ) 
		
	
