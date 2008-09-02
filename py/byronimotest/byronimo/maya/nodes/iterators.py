"""B{byronimotest.byronimo.maya.nodes.iterators}

Test node iterators 

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
import maya.OpenMaya as api
from byronimo.maya.nodes.iterators import *
import byronimotest.byronimo.maya as common
import byronimo.maya as bmaya
import byronimo.maya.nodes as nodes


class TestGeneral( unittest.TestCase ):
	""" Test general maya framework """
	
	def __init__( self, *args, **kwargs ):
		super( TestGeneral, self ).__init__( *args, **kwargs )
		#benchfile = common.get_maya_file( "large_scene_%i.mb" % 2500 )
		#bmaya.Scene.open( benchfile, force = 1 )

		
	def test_dagIter( self ):
		"""byronimo.maya.nodes.iterators: simple DAG iteration"""
		bmaya.Scene.new( force=1 )
		trans = nodes.createNode( "trans", "transform" )
		trans2 = nodes.createNode( "trans2", "transform" )
		transinst = trans.addInstancedChild( trans2 )
		mesh = nodes.createNode( "parent|mesh", "mesh" )
		nurbs = nodes.createNode( "parent|nurbs", "nurbsSurface" )
		
		
		self.failUnless( len( list( iterDagNodes( dagpath=1 ) ) ) == 16 )
		self.failUnless( len( list( iterDagNodes( dagpath=0 ) ) ) == 15 )
		
		# BREADTH FIRST
		################
		dagiter = iterDagNodes( dagpath=1,depth=0,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue 
			# now the following ones are known !
			self.failUnless( dagiter.next() == trans2 )
			break
		
		# DEPTH FIRST 
		##############
		dagiter = iterDagNodes( dagpath=1,depth=1,asNode=1 )
		for item in dagiter:
			if item != trans:
				continue 
			self.failUnless( dagiter.next() == transinst )
			break
		
		# ROOT 
		########
		# dagpath
		dagiter = iterDagNodes( root=trans._apidagpath,depth=1,asNode=1 )
		self.failUnless( dagiter.next() == trans )		# 
		self.failUnless( dagiter.next() == transinst )
		
		# apiobj
		dagiter = iterDagNodes( root=trans._apiobj,depth=1,asNode=1 )
		self.failUnless( dagiter.next() == trans )
		self.failUnless( dagiter.next() == transinst )
		
		# TYPES 
		# single
		dagiter = iterDagNodes(api.MFn.kMesh, asNode=1 )
		self.failUnless( len( list( dagiter ) ) == 1 )
		
		# multiple 
		dagiter = iterDagNodes( api.MFn.kMesh,api.MFn.kNurbsSurface, asNode=1 )
		self.failUnless( len( list( dagiter ) ) == 2 )
		
	
	def test_dggraph( self ):
		"""byronimo.maya.nodes.iterators: simple dg graph iteration"""
		pass 
	
		
	def test_dgiter( self ):
		"""byronimo.maya.nodes.iterators: simple DG iteration"""
		bmaya.Scene.new( force=1 )
		trans = nodes.createNode( "trans", "transform" )
		mesh = nodes.createNode( "trans|mesh", "mesh" )
		
		gid = nodes.createNode( "gid", "groupId" )
		fac = nodes.createNode( "fac", "facade" )
		fac1 = nodes.createNode( "fac1", "facade" )
		oset = nodes.createNode( "set", "objectSet" )
		
		# one type id
		self.failUnless( len( list( iterDgNodes( api.MFn.kFacade ) ) ) == 2 )
		self.failUnless( oset in iterDgNodes( api.MFn.kSet, asNode=1 ) )
		
		# multiple type ids 
		filteredNodes = list( iterDgNodes( api.MFn.kSet, api.MFn.kGroupId, asNode=1 ) )
		for node in [ gid, oset ]:
			self.failUnless( node in filteredNodes )
		
		
