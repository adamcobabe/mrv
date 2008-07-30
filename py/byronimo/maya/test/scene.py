"""B{byronimo.maya.test.scene}

Test the scene methods  

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
from byronimo.maya.scene import Scene
import maya.OpenMaya as om
import os.path as path
import byronimo.maya.env as env
	
class TestSceneRunner( unittest.TestCase ):
	""" Test the database """
	
	def setUp( self ):
		""" Initialize test scene """
		self.called = False				# reset callback check
	
	
	#{ Callback methods
	def cbgroup_zero( self, boolStatusRef, clientData ):
		self.called = True
	
	def cbgroup_one( self, retcode, fileobj, clientData ):
		self.called = True
	
	def cbgroup_two( self, clientData ):
		self.called = True
	#}
	
	
	#{ Utilities 
	@staticmethod 
	def getScenePath( filename ):
		""" @return: path to maya test file of the given name """
		return path.join( path.split( __file__ )[0], "ma/"+filename )
	#}
	
	def test_cbgroup_zero( self ):
		"""ws.maya.scene: use group 0 check callbacks """
		if env.getAppVersion( )[0] == 8.5:
			return 
		
		Scene.Callbacks.addListener( "test_zero", lambda *args: TestSceneRunner.cbgroup_zero( self,*args ), om.MSceneMessage.kBeforeNewCheck )
		self.failUnless( len( Scene.Callbacks._callbacks[0] ) != 0 )
		
		
		Scene.Callbacks.removeListener( "test_zero", om.MSceneMessage.kBeforeNewCheck )
		self.failUnless( len( Scene.Callbacks._callbacks[0] ) == 0 )
		
	
	def test_cbgroup_one( self ):
		"""ws.maya.scene: check file callback """
		if env.getAppVersion( )[0] == 8.5:
			return 
			
		Scene.Callbacks.addListener( "test_one", lambda *args: TestSceneRunner.cbgroup_one( self,*args ), om.MSceneMessage.kBeforeOpenCheck )
		self.failUnless( len( Scene.Callbacks._callbacks[1] ) != 0 )
		
		scenepath = TestSceneRunner.getScenePath( "sphere.ma" ) 
		Scene.open( scenepath )
		self.failUnless( self.called )
		
		Scene.Callbacks.removeListener( "test_one", om.MSceneMessage.kBeforeNew )
		self.failUnless( len( Scene.Callbacks._callbacks[1] ) == 0 )
	
	def test_cbgroup_twp( self ):
		"""ws.maya.scene: Test ordinary scene callbacks """
		Scene.Callbacks.addListener( "test_two", lambda *args: TestSceneRunner.cbgroup_two( self,*args ), om.MSceneMessage.kBeforeNew )
		self.failUnless( len( Scene.Callbacks._callbacks[2] ) != 0 )
		
		# make a new scene - we should be called
		Scene.new()
		self.failUnless( self.called )
		
		Scene.Callbacks.removeListener( "test_two", om.MSceneMessage.kBeforeNew )
		self.failUnless( len( Scene.Callbacks._callbacks[2] ) == 0 )
		
	def tearDown( self ):
		""" Cleanup """
		pass 
	
