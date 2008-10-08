"""B{byronimotest.byronimo.maya.nodes.geometry}

Tests the geometric nodes, focussing on the set handling 

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
import byronimo.maya.nodes.storage as storage
import byronimo.maya.nodes as nodes
import maya.OpenMaya as api
import byronimo.maya as bmaya
import byronimotest.byronimo.maya as common

class TestGeometry( unittest.TestCase ):
	""" Test general maya framework """
	
	
	def test_setHandling( self ):
		"""byronimo.maya.nodes.geometry: set handling tests for different types"""
		bmaya.Scene.open( common.get_maya_file( "shadertest.ma" ), force = 1 )
		
		# these are all shapes
		p1 = nodes.Node( "p1" )		# one shader 
		p2 = nodes.Node( "p2" ) 	# 3 shaders, third has two faces
		s1 = nodes.Node( "s1" )		# subdivision surface 
		n1 = nodes.Node( "n1" )		# nurbs with one shader
		
		# the shading groups 
		sg1 = nodes.Node( "sg1" )
		sg2 = nodes.Node( "sg2" )
		sg3 = nodes.Node( "sg3" )
		
		# simple sets 
		set1 = nodes.Node( "set1" )
		set2 = nodes.Node( "set2" )
		
		
		
		# TEST OBJECT ASSIGNMENTS
		# simple assignments 
		for obj in ( p1, s1, n1 ):
			# shaders - object assignment method 
			setfilter = nodes.Shape.fSetsRenderable
			sets = obj.getConnectedSets( setFilter = setfilter )
			self.failUnless( len( sets ) == 1 and sets[0] == sg1 ) 
		
			# TEST OBJECT SET ASSIGNMENTS
			setfilter = nodes.Shape.fSetsObject
			sets = obj.getConnectedSets( setFilter = setfilter )
			
			self.failUnless( len( sets ) == 2 and sets[0] == set1 and sets[1] == set2 )
		# END assignmnet query
			
		
		# TEST COMPONENT ASSIGNMENT QUERY 
		# SHADERS - components method
		for obj in ( p1, p2 ):
			
			# OBJECT SET MEMBERSHIP
			# even this method can retrieve membership to default object sets
			setfilter = nodes.Shape.fSetsObject
			sets = obj.getComponentAssignments( setFilter = setfilter )
			self.failUnless( len( sets ) == 2 )
			
			# but the components must be 0, and it must have our sets 
			for setnode, comp in sets:
				self.failUnless( not comp )
				self.failUnless( setnode in ( set1, set2 ) )
			
			if obj != p2:
				continue 
			
			# COMPONENT ASSIGNMENTS
			##########################
			setfilter = nodes.Shape.fSetsRenderable
			setcomps = obj.getComponentAssignments( setFilter = setfilter )
			
			self.failUnless( len( setcomps ) == 3 )
			
			for setnode, component in setcomps:
				self.failUnless( not component.isEmpty() )
				
				if setnode == sg1:
					pass 
				if setnode == sg2:
					pass 
				if setnode == sg2:
					pass
			# END for each setcomponent 
			
		# END for each object 
		
