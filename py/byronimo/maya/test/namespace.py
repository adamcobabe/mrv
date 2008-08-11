"""B{byronimo.maya.test.namespace}

Test the namespace methods  

@newfield revision: Revision
@newfield id: SVN Id
"""
                                            
__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
import byronimo.maya.test as common
from byronimo.maya.scene import Scene
from byronimo.maya.namespace import *
import byronimo.maya as bmaya
import os

class TestReferenceRunner( unittest.TestCase ):
	""" Test the database """
	
	def test_checkNamespaces( self ):
		"""byronimo.maya.namespace: test all namespace functionality """
		bmaya.Scene.open( common.get_maya_file( "namespace.ma" ), force=True )
		
