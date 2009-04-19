# -*- coding: utf-8 -*-
"""B{byronimo.maya.util}

Test utility classes

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
import byronimo.maya as bmaya
import maya.cmds as cmds
from byronimo.maya.util import *

class TestUtil( unittest.TestCase ):

	def test_optionvardict( self ):
		"""byronimo.maya.util: test optionvars dict"""

		# test whether value get and set is without conversion errors
		for key in optionvars.keys( ):
			value = optionvars[ key ]
			optionvars[ key ] = value

			nvalue = optionvars[ key ]
			self.failUnless( value == nvalue )		# its tuples
		# END for each key in option vars dict

		self.failUnless( len( list( optionvars.iterkeys() ) ) == len( optionvars.keys() ) )

		# iterate values
		for val in optionvars.itervalues():
			pass

		# iterate paris
		for key,val in optionvars.iteritems():
			self.failUnless( optionvars[ key ] == val )


		# create some option vars
		values = ( "string", False, 2, 10.5, ( "a","b" ), ( unicode("ua"),unicode("ub") ),
				  (True,False), ( 1,2 ), ( 2.5, 3.5 ) )
		for i,value in enumerate( values ):
			key = "test%i" % i
			optionvars[ key ] = value
			self.failUnless( optionvars.has_key( key ) )
			self.failUnless( key in optionvars )
			self.failUnless( optionvars[ key ] == value )

			poppedval = optionvars.pop( key )
			self.failUnless( key not in optionvars )

			# will return unicode, although we put in strings
			if isinstance( poppedval, (tuple,list) ):
				for pval,val in zip( poppedval, value ):
					self.failUnless( pval == val )
			else:
				self.failUnless( poppedval == value )
		# END for each testvalue

	def test_misc( self ):
		"""byronimo.maya.util: test misc. methods"""
		assert padScalar( 2, 4 ) == "0002"
		assert padScalar( 2, 1 ) == "2"
		assert padScalar( 2, 0 ) == "2"
		assert padScalar( 2, -1 ) == "2"
		assert padScalar( 22, 2 ) == "22"
