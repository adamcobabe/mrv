"""Imports all utility functions into the same module
"""

__author__='$Author$'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date$"
__revision__="$Revision$"
__id__="$Id$"
__copyright__='(c) 2009 Sebastian Thiel'

from helpers import *
# needs to stay in a module, otherwise nose will pick up the runTest method 
# from the TestCase class which is just a string - its odd 
import unittest 