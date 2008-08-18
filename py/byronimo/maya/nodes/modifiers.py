"""B{byronimo.nodes.modifiers}

Contains modifiers able to alter the dag and dg ( uncluding undo support ).
All byronimo classes use them.

@todo: more documentation about how to use the system and how it actually works 

@newfield revision: Revision
@newfield id: SVN Id """

__author__='$Author: byron $'
__contact__='byron@byronimo.de'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id: configuration.py 16 2008-05-29 00:30:46Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import maya.OpenMaya as om
import byronimo.maya.undo as undo
from byronimo.util import MetaCopyClsMembers
import sys

class DGModifier( om.MDGModifier, undo.Operation ):
	"""Undo-aware DG Modifier - using it will automatically put it onto the API undo queue
	@note: You MUST call doIt() before once you have instantiated an instance, even though you 
	have nothing on it. This requiredment is related to the undo queue mechanism"""
	def __init__( self ):
		"""Initialize our base classes explicitly"""
		om.MDGModifier.__init__( self )
		undo.Operation.__init__( self )
		
	def _on_deletion_( self ):
		"""general handler to do general operation handling on deletion
		@note: NOT ( YET ) USED"""
		if not self._doitcalled:
			try:
				ownindex = sys._maya_stack.index( self )
				#print "ownindex == " + str( ownindex )
			except ValueError:
				pass
			else:
				# delete us from the queue - undo should not be called on us
				# as we have not done anything 
				del( sys._maya_stack[ ownindex ] )
		# END if doit not called before deletion - need to get us off the queue

	
class DagModifier( om.MDagModifier, undo.Operation ):
	"""undo-aware DAG modifier, copying all extra functions from DGModifier"""
	__metaclass__ = MetaCopyClsMembers
	
	__virtual_bases__ = ( DGModifier, )
	
	def __init__( self ):
		"""Intiailize our base explicitly"""
		om.MDagModifier.__init__( self )
		undo.Operation.__init__( self )
		
		
	
# keep aliases
#{ Aliases 

MDGModifier = DGModifier
MDagModifier = DagModifier

#}
