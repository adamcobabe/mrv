"""B{byronimo.automation.attributes}
Contains specialized attributes that judge value based on different criteria, 
allowing more elaborate typecheckingr

@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-08-12 15:33:55 +0200 (Tue, 12 Aug 2008) $"
__revision__="$Revision: 50 $"
__id__="$Id: configuration.py 50 2008-08-12 13:33:55Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'

from byronimo.dgengine import Attribute

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
			
