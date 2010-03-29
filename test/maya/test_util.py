# -*- coding: utf-8 -*-
""" Test utility classes """
from mrv.test.maya import *
from mrv.maya.util import *

class TestUtil( unittest.TestCase ):
	def test_optionvardict( self ):

		# test whether value get and set is without conversion errors
		for key in optionvars.keys( ):
			value = optionvars[ key ]
			optionvars[ key ] = value

			nvalue = optionvars[ key ]
			assert value == nvalue 		# its tuples
		# END for each key in option vars dict
		
		self.failUnlessRaises(KeyError, optionvars.__getitem__, 'doesntExist')

		assert len( list( optionvars.iterkeys() ) ) == len( optionvars.keys() ) 

		# iterate values
		for val in optionvars.itervalues():
			pass

		# iterate paris
		for key,val in optionvars.iteritems():
			assert optionvars[ key ] == val 


		# create some option vars
		values = ( "string", False, 2, 10.5, ( "a","b" ), ( unicode("ua"),unicode("ub") ),
				  (True,False), ( 1,2 ), ( 2.5, 3.5 ) )
		for i,value in enumerate( values ):
			key = "test%i" % i
			optionvars[ key ] = value
			assert optionvars.has_key( key ) 
			assert key in optionvars 
			assert optionvars[ key ] == value 

			poppedval = optionvars.pop( key )
			assert key not in optionvars 

			# will return unicode, although we put in strings
			if isinstance( poppedval, (tuple,list) ):
				for pval,val in zip( poppedval, value ):
					assert pval == val 
			else:
				assert poppedval == value 
		# END for each testvalue
