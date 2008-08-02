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
from byronimo.path import Path
import tempfile 
import shutil
	
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
	
	def _runMessageTest( self, listenerID, sceneMessageID, function, callbackTriggerFunc ):
		""" Run a message test for the given sceneMessageID
		@param callbackTriggerFunc: called to trigger the callback we are testing"""
		sid = sceneMessageID
		ncb = len( Scene.Callbacks._callbacks.get( sid , [] ) )
		
		Scene.Callbacks.addListener( listenerID, function, sid )
		self.failUnless( len( Scene.Callbacks._callbacks[ sid ] ) == ncb + 1 )
		
		# make a new scene - we should be called
		callbackTriggerFunc()
		self.failUnless( self.called )
		
		Scene.Callbacks.removeListener( listenerID, sid )
		self.failUnless( len( Scene.Callbacks._callbacks[ sid ] ) == ncb )
	
	def test_cbgroup_zero( self ):
		"""byronimo.maya.scene: use group 0 check callbacks """
		if env.getAppVersion( )[0] == 8.5:
			return 
		
		self._runMessageTest( "test_two", om.MSceneMessage.kBeforeNewCheck, 
							 	lambda *args: TestSceneRunner.cbgroup_zero( self,*args ), 
								Scene.new )
		
	def test_cbgroup_one( self ):
		"""byronimo.maya.scene: check file callback """
		if env.getAppVersion( )[0] == 8.5:
			return 
		
		scenepath = TestSceneRunner.getScenePath( "sphere.ma" ) 
		triggerFunc = lambda : Scene.open( scenepath )
		self._runMessageTest( "test_one", om.MSceneMessage.kBeforeOpenCheck, 
							 	lambda *args: TestSceneRunner.cbgroup_one( self,*args ), 
								triggerFunc )
		
	def test_cbgroup_twp( self ):
		"""byronimo.maya.scene: Test ordinary scene callbacks """
		self._runMessageTest( "test_two", om.MSceneMessage.kBeforeNew, 
							 	lambda *args: TestSceneRunner.cbgroup_two( self,*args ), 
								Scene.new )
		
	def test_open( self ):
		"""byronimo.maya.scene: open file"""
		self.failUnless( isinstance( Scene.open( self.getScenePath( "empty.ma" ), force=True ), Path ) )
		
	def test_new( self ):
		"""byronimo.maya.scene: force a new scene """
		self.failUnless( isinstance( Scene.new( force=1 ), Path ) )
		
	def test_saveAs( self ):
		"""byronimo.maya.scene: safe a file under new names and with different formats"""
		tmppath = Path( tempfile.gettempdir() ) / "maya_save_test"
		files = [ "mafile.ma" , "mb.mb", "ma.ma" ]
		for filename in files:
			mayafile = tmppath / filename
			Scene.save( mayafile , force=1 )
			self.failUnless( mayafile.exists() )
		shutil.rmtree( tmppath )	# cleanup	
		
	def tearDown( self ):
		""" Cleanup """
		pass 
	
