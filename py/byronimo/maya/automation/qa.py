# -*- coding: utf-8 -*-
"""B{byronimo.maya.automation.qa}
Specialization of workflow to allow checks to be natively implemented in MEL


@newfield revision: Revision
@newfield id: SVN Id
"""

from byronimo.automation.qa import QACheck, QACheckAttribute, QACheckResult, QAProcessBase
from byronimo.maya.util import Mel
from byronimo.dgengine import _NodeBaseCheckMeta
import sys

class QAMELCheckAttribute( QACheckAttribute ):
	"""Attribute identifying a MEL check carrying additional mel specific attributes"""
	pass 

class QAMELCheck( QACheck ):
	"""Specialized version of the QACheck allowing to use our own MEL attribute
	contianiing more information"""
	check_attribute_cls = QAMELCheckAttribute
	

class QAMetaMel( _NodeBaseCheckMeta ):
	"""Metaclass allowing to create plugs based on a MEL implementation, allowing 
	to decide whether checks are Python or MEL implemented, but still running natively 
	in python"""
	
	def __new__( metacls, name, bases, clsdict ):
		"""Search for configuration attributes allowing to auto-generate plugs 
		referring to the respective mel implementation"""
		index_proc = clsdict.get( "mel_index_proc", None )
		check_cls = clsdict.get( "check_plug_cls", QAMELCheck )
		
		if index_proc and check_cls is not None:
			try:
				index = Mel.call( index_proc )
			except RuntimeError, e:
				sys.__stdout__.write( str( e ) )
			else:
				# assure its working , never fail here 
				if len( index ) % 3 == 0:
					iindex = iter( index )
					for checkname, description, can_fix in zip( iindex, iindex, iindex ):
						
						# check name - it may not contain spaces for now
						if " " in checkname:
							sys.__stdout__.write( "Invalid name: %s - it may not contain spaces, use CamelCase or underscores" % checkname )
							continue
						# END name check
						
						plug = check_cls( annotation = description, has_fix = int( can_fix ) )
						plug.setName( checkname )
						clsdict[ checkname ] = plug
					# END for each information tuple
				# END if index is valid 
				else:
					sys.__stdout__.write( "Invalid proc index returned by %s" % index_proc )
		# END create plugs 
		
		# finally create the class 
		newcls = super( QAMetaMel, metacls ).__new__( metacls, name, bases, clsdict )
		return newcls
		

class QAMELAdapter( object ):
	"""Base class allowing to process MEL baesd plugs as created by our metaclass
	@note: this class assumes it is used on a process
	
	Configuration 
	-------------
	The following variables MUST be used to setup this class once you have derived
	from it: 
	
	mel_index_proc:
	produdure name with signature func( ) returning string array in following 
	format 
	[n*3+0] = checkname : the name of the check, use CamelCase names or names_with_underscore
	The checkname is also used as id to identify the check lateron
	[n*3+1] = description: Single sentence desciption of the check targeted at the end user
	[n*3+2] = can_fix: 	Boolean value indicating whether the check can also fix the issue
	
	
	mel_check_proc
	procedure called to actually process the given check, signature is 
	func( check_name, should_fix )
	returning string[] as follows:
	[0] = x number of fixed items
	[1] = header 
	[1:1+x] = x fixed items 
	[2+x:n] = n invalid items
	items are either objects or in general anything you check for. The check is 
	considered to be failed if there is at least one invalid item.
	If you fixed items, all previously failed items should now be returned as 
	valid items
	"""
	__metaclass__ = QAMetaMel
	
	#{ Configuration 
	
	# see class docs
	mel_index_proc = None
	
	# see class docs 
	mel_check_proc = None
	
	# qa check result compatible class to be used as container for MEL return values
	check_result_cls = QACheckResult
	
	# qa check plug class to use for the plugs to be created - it will always default
	# to QACheck
	check_plug_cls = QAMELCheck
	#} END configuration 
	
	def listMELChecks( self ):
		"""@return: list all checks ( Plugs ) available on this class that are implemented
		in MEL"""
		return self.listChecks( predicate = lambda p: isinstance( p.attr , QAMELCheckAttribute ) )
	
	def isMELCheck( self, check ):
		"""@return: True if the given check plug is implemented in MEL and can be handled
		there accordingly"""
		plug = check
		try:
			plug = check.plug
		except AttributeError:
			pass 
			
		return isinstance( plug.attr, QAMELCheckAttribute )
		
	def _rval_to_checkResult( self, string_array, **kwargs ):
		"""@return: check result as parsed fom string array
		@param **kwargs: will be given to initializer of check result instance"""
		if not string_array:
			return self.check_result_cls( **kwargs )
		
		assert len( string_array ) > 1	# need a header at least
		
		num_fixed = int( string_array[0] )
		end_num_fixed = 2 + num_fixed
		
		kwargs[ 'header' ] = string_array[1] 
		kwargs[ 'fixed_items' ] = string_array[ 2 : end_num_fixed ]
		kwargs[ 'failed_items' ] = string_array[ end_num_fixed : ]
		
		return self.check_result_cls( **kwargs ) 
		
	
	def handleMELCheck( self, check, mode ):
		"""Called to handle the given check in the given mode
		@raise RuntimeError: If MEL throws an error
		@return: QACheckResult of the result generated by MEL"""
		assert self.mel_check_proc
		assert isinstance( check.attr, QAMELCheckAttribute )
		
		rval = Mel.call( self.mel_check_proc, check.getName(), int( mode == self.eMode.fix ) ) 
		
		return self._rval_to_checkResult( rval )
	
