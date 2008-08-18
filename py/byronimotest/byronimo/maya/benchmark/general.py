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
import maya.cmds as cmds
import byronimo.maya.undo as undo
from byronimotest.byronimo.maya.undo import TestUndoQueue
import sys
import string 
import random



class TestGeneralPerformance( unittest.TestCase ):
	"""Tests to benchmark general performance"""
	
	def test_createNodes( self ):
		"""byronimo.maya.benchmark.general: test random node creation performance"""
		nslist = genNestedNamesList( 3, (0,3), genRandomNames(10,(3,8)),":" )
		print nslist
		print genNodeNames( 10, (0,5),(3,8),nslist )
		
	

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
