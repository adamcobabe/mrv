"""B{byronimotest.byronimo.maya.benchmark.general}

Test general performance

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


import unittest
import byronimo.maya as bmaya
import byronimo.maya.nodes as nodes
import sys
import maya.cmds as cmds
import byronimo.maya.undo as undo
import string 
import random
import time



class TestGeneralPerformance( unittest.TestCase ):
	"""Tests to benchmark general performance"""
	
	def test_createNodes( self ):
		"""byronimo.maya.benchmark.general: test random node creation performance"""
		runs = [ 100,2500 ]
		deptypes =[ "facade", "groupId", "objectSet"  ]
		dagtypes =[ "nurbsCurve", "nurbsSurface", "subdiv", "transform" ]
		all_elapsed = []
		
		numObjs = len( cmds.ls() )
		
		print "\n"
		for numNodes in runs:
			
			nslist = genNestedNamesList( numNodes / 100, (0,3), genRandomNames(10,(3,8)),":" )
			nodenames = genNodeNames( numNodes, (1,5),(3,8),nslist )
			
			starttime = time.clock( )
			undoobj = undo.StartUndo()
			for nodename in nodenames:
				nodetype = None
				if '|' in nodename:			# name decides whether dag or dep node is created
					nodetype = random.choice( dagtypes )
				else:
					nodetype = random.choice( deptypes )
				
				try:	# it can happen that he creates dg and dag nodes with the same name 
					nodes.createNode( nodename, nodetype, autoRename=True )
				except NameError:
					pass 
			# END for each node
			del( undoobj )	# good if we raise runtime errors ( shouldnt happend )
			
			elapsed = time.clock() - starttime
			all_elapsed.append( elapsed )
			print "Created %i nodes in %f s ( %f / s )" % ( numNodes, elapsed, numNodes / elapsed )
			
			# UNDO OPERATION 
			starttime = time.clock()
			cmds.undo()
			elapsed = time.clock() - starttime
			print "Undone Operation in %f s" % elapsed 
			
		# END for each run
			  
		# assure the scene is the same as we undo everything
		self.failUnless( len( cmds.ls() ) == numObjs )
		
		
		# TEST MAYA NODE CREATION RATE 
		#################################
		# redo last operation to get lots of nodes
		cmds.redo( )
		nodenames = cmds.ls(  )
		starttime = time.clock()
		
		for name in nodenames:
			n =nodes.MayaNode( name )
		
		elapsed = time.clock() - starttime
		print "Created %i MayaNodes in %f s ( %f / s )" % ( len( nodenames ), elapsed, len( nodenames ) / elapsed )
		
		
	

#{ Name Generators
def genRandomNames( numNames, wordLength ):
	"""Generate random names from characters allowed by maya
	@param wordLength: length of the generated word
	@return: list of names
	@note: currently we do not use numbers"""
	outlist = []
	for n in xrange( numNames ):
		name = ''
		for i in xrange( random.randint( wordLength[0], wordLength[1] ) ):
			name += random.choice( string.ascii_letters )
		outlist.append( name )
	# END for each name 
	return outlist

def genNestedNamesList( numNames, nestingRange, wordList, sep ):
	"""Create a random list of nested names where each subname is separated by sep, like
	[ 'asdf:efwsf','asdfic:oeafsdf:asdfas' ]
	@param numNames: number of names to generate
	@param maxNestingLevel: tuple( min,max ) 0 for single names, other for names combined using sep
	@param wordList: words we may choose from to create nested names 
	@param sep: separator between name tokens
	@return: list of nested words"""
	outnames = []
	for n in xrange( numNames ):
		nlist = []
		for t in xrange( random.randint( nestingRange[0], nestingRange[1] ) ):
			nlist.append( random.choice( wordList ) )
		outnames.append( sep.join( nlist ) )
	return outnames

def genNodeNames( numNames, dagLevelRange, wordRange, nslist ):
	"""Create  random nodenames with a dag path as depe as maxDagLevel using
	@param numNames: number of names to generate 
	@param dagLevelRange: tuple( min, max ), defining how deept the nesting may be 
	@param wordRange: tuple ( min,max ), defining the minimum and maximum word length
	@note: subnamespaces can repeat in name 
	@return: the generated name """
	# gen names
	nodenames = genRandomNames( numNames, wordRange )
	dagpaths = genNestedNamesList( numNames, dagLevelRange, nodenames, '|' )
	if not nslist:
		return dagpaths
		
	# otherwise put the namespaces in there, random pick
	nsdagpaths = []
	for dagpath in dagpaths:
		tokens = dagpath.split( '|' )
		for i in xrange( len( tokens ) ):
			tokens[ i ] = random.choice( nslist ) + ":" + tokens[ i ]
		nsdagpaths.append( '|'.join( tokens ) )
	# END for each dagpath 
	return nsdagpaths
	
#} END name generators
