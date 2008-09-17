"""B{byronimo.automation.processes.selectors}
Contains processes manipulating selections   

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

from base import PassThroughProcess, InputError

__all__ = []

class SelectorBase( PassThroughProcess ):
	"""Base class for all selectors"""
	__all__.append( "SelectorBase" )
		
	def getSupportedTargetTypes( self ):
		"""No types suppoorted by default"""
		return []
		
		

class InputPriorityBoost( SelectorBase ):
	"""Boost the priority value of all it's inputs to make it appear more suitable"""
	__all__.append( "InputPriorityBoost" )
	
	def __init__( self, workflow, multiplier ):
		self.multiplier = multiplier
		super( InputPriorityBoost, self ).__init__( "PriorityBoost", "boosing priority by %s" % multiplier, workflow )
		
	
	def canOutputTarget( self, target ):
		"""Multiply rating of target"""
		# could fail - this is okay though
		try:
			inputprocess = self._getSuitableProcess( target )
		except InputError:
			return 0
		
		return inputprocess.canOutputTarget( target ) * self.multiplier
		
		
class BestSuitableInput( SelectorBase ):
	"""Just a do - nothing process that is used to indicate that a good working process
	will be used depending on the priority of its inputs. This is the normal behaviour 
	of all process though, so there is no more work to do here ( for now )
	@note: this class might be extended to handle clashes more smartly, but ... lets see"""
	__all__.append( "BestSuitableInput" )
	
	def __init__( self, workflow ):
		super( BestSuitableInput, self ).__init__( "BestSuitableInput", "choosing best suitable", workflow )
	
