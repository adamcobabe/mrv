"""B{byronimo.nodes.types}

Deals with types of objects and mappings between them 

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
import maya.OpenMaya as api


####################
### CACHES ########
##################
nodeTypeTree = None



#####################
#### META 		####
##################


#####################
#### META 		####
##################

class MetaClassCreatorNodes( MetaClassCreator ):
	"""Builds the base hierarchy for the given classname based on our typetree
	@todo: build classes with slots only as members are pretermined"""
	
	nameToTreeMap = set( [ 'FurAttractors', 'FurCurveAttractors', 'FurGlobals', 'FurDescription','FurFeedback' ] ) 
	targetModule = None
	
	def __new__( metacls, name, bases, clsdict ):
		""" Called to create the class with name """
		global nodeTypeTree
		
		def func_nameToTree( name ):
			if name in metacls.nameToTreeMap:
				return name
			return uncapitalize( name )

		newcls = super( MetaClassCreatorNodes, metacls ).__new__( nodeTypeTree, metacls.targetModule, 
																metacls, name, bases, clsdict, 
																nameToTreeFunc = func_nameToTree )
				
		# TODO: attach methods from the function set(s) most suitable for the class
		return newcls


###################################
#### Initialization Methods   ####
#################################

def init_nodehierarchy( ):
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
	global nodeTypeTree
	nodeTypeTree = bmaya._dagTreeFromTupleList( hierarchylist )
	
def init_wrappers( targetmodule ):
	""" Create Standin Classes that will delay the creation of the actual class till 
	the first instance is requested
	@param targetmodule: the module to which to put the wrappers"""	 
	global nodeTypeTree
	bmaya._initWrappers( targetmodule, nodeTypeTree.nodes_iter(), MetaClassCreatorNodes )
	
