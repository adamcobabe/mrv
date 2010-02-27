# -*- coding: utf-8 -*-
"""
Test general performance



"""
import unittest
import mayarv.maya as bmaya
import mayarv.maya.nodes as nodes
from mayarv.maya.nodes import Node
import mayarv.test.maya as common
import sys
import maya.cmds as cmds
import maya.OpenMaya as api
import string
import random
import time
import mayarv.maya.nodes.it as it
import mayarv.test.maya.benchmark as bcommon

class TestGeneralPerformance( unittest.TestCase ):
	"""Tests to benchmark general performance"""

	deptypes =[ "facade", "groupId", "objectSet"  ]
	dagtypes =[ "nurbsCurve", "nurbsSurface", "subdiv", "transform" ]

	def _createNodeFromName( self, name ):
		"""@return: newly created maya node named 'name', using the respective
		type depending on its path ( with pipe or without"""
		nodetype = None
		if '|' in name:			# name decides whether dag or dep node is created
			nodetype = random.choice( self.dagtypes )
		else:
			nodetype = random.choice( self.deptypes )

		return nodes.createNode( name, nodetype, renameOnClash=True )


	def _test_buildTestScene( self ):
		"""mayarv.maya.benchmark.general: build test scene with given amount of nodes  """
		return 	# disabled
		numNodes = 100000
		cmds.undoInfo( st=0 )
		targetFile = common.get_maya_file( "large_scene_%i.mb" % numNodes )
		bmaya.Scene.new( force = True )

		print 'Creating benchmark scene at "%s"' % targetFile

		nslist = genNestedNamesList( numNodes / 100, (0,3), genRandomNames(10,(3,8)),":" )
		nodenames = genNodeNames( numNodes, (1,8),(3,8),nslist )

		for i, name in enumerate( nodenames ):
			try:
				self._createNodeFromName( name )
			except NameError:
				pass

			if i % 500 == 0:
				print "%i of %i nodes created" % ( i, numNodes )
		# END for each nodename

		cmds.undoInfo( st=1 )
		bmaya.Scene.save( targetFile )


	def test_dagwalking( self ):
		"""mayarv.maya.benchmark.general.dagWalking: see how many nodes per second we walk"""
		if not bcommon.mayRun( "dagwalk" ): return

		# numnodes = [ 2500, 25000, 100000 ]
		numnodes = [ 2500 ]
		for nodecount in numnodes:
			benchfile = common.get_maya_file( "large_scene_%i.mb" % nodecount )
			bmaya.Scene.open( benchfile, force = 1 )


			# DAGPATHS NO NODE CONVERSION
			starttime = time.time( )
			for dagpath in it.iterDagNodes( dagpath = 1, asNode = 0 ):
				pass
			elapsed = time.time() - starttime
			print "Walked %i dag nodes from dagpaths in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

			# DIRECT ITERATOR USE
			starttime = time.time( )
			iterObj = api.MItDag( )
			while not iterObj.isDone( ):
				dPath = api.MDagPath( )
				iterObj.getPath( dPath )
				iterObj.next()
			# END for each dagpath
			elapsed = time.time() - starttime
			print "Walked %i nodes directly in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

			starttime = time.time( )
			for dagpath in it.iterDagNodes( dagpath = 1, asNode = 1 ):
				pass
			elapsed = time.time() - starttime
			print "Walked %i WRAPPED dag nodes from dagpaths in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

			# from ls
			starttime = time.time( )
			sellist = nodes.toSelectionListFromNames( cmds.ls( type="dagNode" ) )
			for node in it.iterSelectionList( sellist, handlePlugs = False, asNode = False ):
				pass
			elapsed = time.time() - starttime
			print "Listed %i nodes with ls in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

			# from active selection
			starttime = time.time( )
			cmds.select( cmds.ls( type="dagNode" ) )
			sellist = api.MSelectionList()
			api.MGlobal.getActiveSelectionList( sellist )
			for node in it.iterSelectionList( sellist, handlePlugs = False, asNode = False ):
				pass
			elapsed = time.time() - starttime
			print "Listed %i nodes from active selection in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )


			# WITH NODE CONVERSION
			starttime = time.time( )
			for node in it.iterDagNodes( asNode = 1, dagpath=False ):
				pass
			elapsed = time.time() - starttime
			print "Walked %i WRAPPED nodes from MObjects in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )


			# BREADTH
			starttime = time.time( )
			for dagpath in it.iterDagNodes( depth = 0, dagpath=False ):
				pass
			elapsed = time.time() - starttime
			print "Walked %i nodes from MObjects BREADTH FIRST in %f s ( %f / s )" % ( nodecount, elapsed, nodecount / elapsed )

		# END for each run

	def test_createNodes( self ):
		"""mayarv.maya.benchmark.general: test random node creation performance"""
		if not bcommon.mayRun( "createnode" ): return
		bmaya.Scene.new( force = True )
		runs = [ 100,2500 ]
		all_elapsed = []

		numObjs = len( cmds.ls() )
		print "\n"
		for numNodes in runs:

			nslist = genNestedNamesList( numNodes / 100, (0,3), genRandomNames(10,(3,8)),":" )
			nodenames = genNodeNames( numNodes, (1,5),(3,8),nslist )

			starttime = time.time( )
			undoobj = undo.StartUndo( )
			for nodename in nodenames:
				try:	# it can happen that he creates dg and dag nodes with the same name
					self._createNodeFromName( nodename )
				except NameError:
					pass
			# END for each node
			del( undoobj )	# good if we raise runtime errors ( shouldnt happend )

			elapsed = time.time() - starttime
			all_elapsed.append( elapsed )
			print "Created %i nodes in %f s ( %f / s )" % ( numNodes, elapsed, numNodes / elapsed )

			# UNDO OPERATION
			starttime = time.time()
			cmds.undo()
			elapsed = time.time() - starttime
			print "Undone Operation in %f s" % elapsed

		# END for each run

		# assure the scene is the same as we undo everything
		self.failUnless( len( cmds.ls() ) == numObjs )


		# TEST MAYA NODE CREATION RATE
		#################################
		# redo last operation to get lots of nodes
		cmds.redo( )
		nodenames = cmds.ls( l=1 )
		Nodes = []

		starttime = time.time( )
		for name in nodenames:
			Nodes.append( Node( name ) )

		elapsed = time.time() - starttime
		print "Created %i WRAPPED Nodes ( from STRING ) in %f s ( %f / s )" % ( len( nodenames ), elapsed, len( nodenames ) / elapsed )


		# CREATE MAYA NODES FROM DAGPATHS AND OBJECTS
		starttime = time.time( )
		tmplist = list()	# previously we measured the time it took to append the node as well
		for node in Nodes:
			if isinstance( node, nodes.DagNode ):
				tmplist.append( Node( node._apidagpath ) )
			else:
				tmplist.append( Node( node._apiobj ) )
		# END for each wrapped node

		api_elapsed = time.time() - starttime
		print "Created %i WRAPPED Nodes ( from APIOBJ ) in %f s ( %f / s ) -> %f %% faster" % ( len( nodenames ), api_elapsed, len( nodenames ) / api_elapsed, (elapsed / api_elapsed) * 100 )


	def test_wrappedFunctionCall( self ):
		"""mayarv.maya.benchmark.general: test wrapped funtion calls and compare them"""
		if not bcommon.mayRun( "funccall" ): return

		bmaya.Scene.new( force = True )

		p = Node('perspShape')

		# node wrapped
		a = time.time()
		for i in range( 10000 ):
			p.focalLength()  # this wraps the API
		b = time.time()
		print "%f s : node.focalLength()" % ( b - a )

		# node speedwrapped
		a = time.time()
		for i in range( 10000 ):
			p._api_focalLength()  # this wraps the API directly
		b = time.time()
		print "%f s : node._api_focalLength()" % ( b - a )

		# node speedwrapped + cached
		a = time.time()
		api_get_focal_length = p._api_focalLength
		for i in range( 10000 ):
			api_get_focal_length()  # get rid of the dictionary lookup
		b = time.time()
		print "%f s : _api_focalLength()" % ( b - a )

		# mfn recreate
		a = time.time()
		for i in range( 10000 ):
			camfn = api.MFnCamera( p.getObject() )
			camfn.focalLength()  # this wraps the API
		b = time.time()
		print "%f s : recreated + call" % ( b - a )

		# mfn directly
		camfn = api.MFnCamera( p.getObject() )
		a = time.time()
		for i in range( 10000 ):
			camfn.focalLength()  # this wraps the API
		b = time.time()
		print "%f s : mfn.focalLenght()" % ( b - a )

		# plug wrapped
		a = time.time()
		for i in range( 10000 ):
			p.fl.asFloat()  # this wraps the API
		b = time.time()
		print "%f s : node.plug.asFloat()" % ( b - a )

		# plug cached
		a = time.time()
		fl = p.fl
		for i in range( 10000 ):
			fl.asFloat()  # this wraps the API
		b = time.time()
		print "%f s : plug.asFloat()" % ( b - a )



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
