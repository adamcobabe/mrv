# -*- coding: utf-8 -*-
"""Test path methods

@todo: actual implementation of path tests - currently it is just a placeholder assuring
that the module can at least be imported


"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-06 12:45:38 +0200 (Tue, 06 May 2008) $"
__revision__="$Revision: 8 $"
__id__="$Id: decorators.py 8 2008-05-06 10:45:38Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import os
import unittest
from mayarv.path import Path

class TestPath( unittest.TestCase ):


	def test_instantiate( self ):
		p = Path( os.path.expanduser( "~" ) )

	def test_set( self ):
		# paths pointing to the same object after all should
		# compare equal in sets, thus they will not allow to be duplicated in it
		homevar = "$HOME"
		if os.name == "nt":
			homevar = "$USERPROFILE"
		# END figure out home variable
		
		user = Path( homevar )
		userexp = user.expandvars()
		
		s = set( ( user, userexp ) )	# same path after all
		self.failUnless( len( s ) == 1 )

		self.failUnless( len( list( userexp.iterParents() ) ) )
		self.failUnless( len( list( userexp.getChildren() ) ) )
		
	def test_expand_or_raise(self):
		self.failUnlessRaises( ValueError, Path("$doesnt_exist/without/variable").expand_or_raise) 
		
		if os.name == "nt":
			pwv = Path("without\variable") # for win use \
		else:
			pwv = Path("without/variable")
			
		assert pwv.expand_or_raise() == pwv
		
		first_var = os.environ.iterkeys().next()
		expanded = Path("$%s/something" % first_var).expand_or_raise()
		assert os.environ[first_var] in expanded
