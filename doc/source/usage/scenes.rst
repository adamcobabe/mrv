
**************
Scene Handling
**************
The 'Scene' is a singleton class which may be used to interact with maya's currently opened scene and to manage scene messages. It is a mix of functionality from the ``file`` MEL command and the ``MSceneMessage`` API type. The following example uses utilities and scenes from the test system::
	
	import mrv.maya as mrv
	empty_scene = get_maya_file('empty.ma')
	mrv.Scene.open(empty_scene, force=1)
	assert mrv.Scene.name() == empty_scene
		
	files = list()
	def beforeAndAfterNewCB( data ):
		assert data is None
		files.append(mrv.Scene.name())
			
	mrv.Scene.beforeNew = beforeAndAfterNewCB
	mrv.Scene.afterNew = beforeAndAfterNewCB
		
	assert len(files) == 0
	mrv.Scene.new()
	assert len(files) == 2
	assert files[0] == empty_scene
	
It is important to remove callbacks once you are done with them to allow the corresponding maya callbacks to be cleaned up properly::
	
	mrv.Scene.beforeNew.remove(beforeAndAfterNewCB)
	mrv.Scene.afterNew.remove(beforeAndAfterNewCB)

