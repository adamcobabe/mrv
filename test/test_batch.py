# -*- coding: utf-8 -*-
"""Tests for the batch processing tool"""
from mayarv.test.lib import *

# shouldn't import anything
try:
	from mayarv.batch import *
except TypeError:
	pass		# expected
else:
	raise AssertionError("It should not be possible to import all items from batch module")
# END check import all 


import mayarv.batch as batch

class TestBatch( unittest.TestCase ):

	def test_base( self ):
		# currently we only test import
		pass 

