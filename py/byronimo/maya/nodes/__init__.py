"""B{byronimo.maya.nodes}

All classes required to wrap maya nodes in an object oriented manner into python objects
and allow easy handling of them.

These python classes wrap the API representations of their respective nodes - most general 
commands will be natively working on them.

These classes follow the node hierarchy as supplied by the maya api.

Optionally: Attribute access is as easy as using properties like 
  node.translateX
  
@note: it is important not to cache these as the underlying obejcts my change over time.
For long-term storage, use handles instead.

Default maya commands will require them to be used as string variables instead.

@todo: more documentation

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

env = __import__( "byronimo.maya.env", globals(), locals(), ['env'] )

from byronimo.maya.util import MetaClassCreator
import byronimo.maya as bmaya
from byronimo.path import Path
from byronimo.util import uncapitalize
import re

#####################
#### META 		####
##################

class MetaClassCreatorNodes( MetaClassCreator ):
	"""Builds the base hierarchy for the given classname based on our typetree"""
	
	nameToTreeMap = set( [ 'FurAttractors', 'FurCurveAttractors', 'FurGlobals', 'FurDescription','FurFeedback' ] ) 
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global _typetree
		global _thismodule
		
		def func_nameToTree( name ):
			if name in metacls.nameToTreeMap:
				return name
			return uncapitalize( name )

		newcls = super( MetaClassCreatorNodes, metacls ).__new__( _typetree, _thismodule, 
																metacls, name, bases, clsdict, 
																nameToTreeFunc = func_nameToTree )
				
		# print newcls.mro()
		return newcls


####################
### CACHES ########
##################
_thismodule = __import__( "byronimo.maya.nodes", globals(), locals(), ['nodes'] )
_typetree = None


############################
#### INITIALIZATION   ####
#########################


def init_classhierarchy( ):
	""" Parse the nodes hiearchy from the maya doc and create an Indexed tree from it
	@todo: cache the pickled tree and try to load it instead  """
	mfile = Path( __file__ ).p_parent.p_parent
	mfile = mfile / ( "cache/nodeHierarchy_%s.html" % env.getAppVersion()[0] )
	lines = mfile.lines( retain=False )			# just read them in one burst
	
	hierarchylist = []
	regex = re.compile( "<tt>([ >]*)</tt><.*?>(\w+)" )	# matches level and name
	rootOffset = 1
	
	hierarchylist.append( (0,"mayaNode" ) )
	
	for line in lines:
		m = regex.match( line )
		if not m: continue
		
		levelstr, name = m.groups()
		level = levelstr.count( '>' ) + rootOffset
		
		hierarchylist.append( ( level, name ) )
	# END for each line 
	global _typetree
	_typetree = bmaya._dagTreeFromTupleList( hierarchylist )
	
def init_wrappers( ):
	""" Create Standin Classes that will delay the creation of the actual class till 
	the first instance is requested"""	 
	global _typetree
	global _thismodule
	bmaya._initWrappers( _thismodule, _typetree.nodes_iter(), MetaClassCreatorNodes )

if 'init_done' not in locals():
	init_done = False
	
if not init_done:
	# assure we do not run several times
	init_classhierarchy( )
	init_wrappers( )
	
	from base import *
	
init_done = True
