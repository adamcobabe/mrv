# -*- coding: utf-8 -*-
"""
Test utility classes



"""



import unittest
import mayarv.maya as bmaya
import maya.cmds as cmds
from mayarv.maya.util import *

class TestUtil( unittest.TestCase ):

	def test_optionvardict( self ):
		"""mayarv.maya.util: test optionvars dict"""

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
		"""mayarv.maya.util: test misc. methods"""
		assert padScalar( 2, 4 ) == "0002"
		assert padScalar( 2, 1 ) == "2"
		assert padScalar( 2, 0 ) == "2"
		assert padScalar( 2, -1 ) == "2"
		assert padScalar( 22, 2 ) == "22"
