# -*- coding: utf-8 -*-
"""Contains specialized attributes that judge value based on different criteria,
allowing more elaborate typecheckingr """
from mayarv.dge import Attribute

class RegexStringAttr( Attribute ):
	"""Attribute that accepts string values matching a given regular expression"""

	def __init__( self, regexstring, *args, **kwargs ):
		"""Initialize the attribute with a glob filter
		@param regexstring: i.e. .*\..* or .*\.py or ^base_.*\.pyo"""
		import re
		self.regex = re.compile( regexstring )
		Attribute.__init__( self, *args, **kwargs )

	def getCompatabilityRate( self, value ):
		"""@return: rate of base class provided that the regex matches, 0 otherwise"""
		rate = Attribute.getCompatabilityRate( self, value )		# get default rate
		if not rate:
			return rate

		if self.regex.match( str(value) ):		# apply regex
			return rate

		return 0

