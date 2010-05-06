
**********
References
**********
References within maya can be referred to by Path or by Reference Node. The latter one is a stable entity in your scene, whereas the first one is dependent on the amount of references as well as the actual reference file.

Dealing with references correctly can be complex in times, but the ``FileReference`` type in MRV greatly facilitates this.

Maya organizes its references hierarchically, which can be queried using the ``iDagItem`` interface of the FileReference type. Additional functionality includes reference creation, import, removal as well as to query information and to iterate its contained nodes.

The example uses files from the test system and respective utilities::
	
	from mrv.maya.ref import FileReference
	refa = FileReference.create(get_maya_file('ref8m.ma'))     # file with 8 meshes
	refb = FileReference.create(get_maya_file('ref2re.ma'))    # two subreferences with subreferences
		
	assert refb.isLoaded()
	assert len(FileReference.ls()) == 2
		
	assert len(refa.children()) == 0 and len(refb.children()) == 2
	subrefa, subrefb = refb.children()
		
	assert subrefa.namespace() != subrefb.namespace()
	assert subrefa.path() == subrefb.path()
	assert subrefa.parent() == refb
		
	refa.setLoaded(False)
	assert not refa.isLoaded()
	assert refa.setLoaded(True).isLoaded()
		
	assert len(list(refa.iterNodes(api.MFn.kMesh))) == 8
		
	refa.remove(); refb.remove()
	assert not refa.exists() and not refb.exists()
	assert len(FileReference.ls()) == 0
