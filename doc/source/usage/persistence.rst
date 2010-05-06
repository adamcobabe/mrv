
***********
Persistence
***********
Being able to use python data natively within your program is a great plus - unfortunately there is no default way to store that data in a native format within the maya scene. Everyone who desires to store python data would need to implement marshaling functions to convert python data to maya compatible data to be stored in nodes, and vice versa, which is time consuming and a possible source of bugs.

MRV tackles the problem by providing a generic storage node which comes as part of the ``nt`` package. It is implemented as a plugin node which allows to store data and connections::
	
	did = 'dataid'
	sn = StorageNode()
	snn = sn.name()
	pd = sn.pythonData( did, autoCreate = True )
		
	pd[0] = "hello"
	pd['l'] = [1,2,3]
		
	tmpscene = tempfile.gettempdir() + "/persistence.mb"
	mrv.Scene.save(tmpscene)
	mrv.Scene.open(tmpscene)
		
	sn = Node(snn)
	pd = sn.pythonData( did )
	assert len(pd) == 2
	assert pd[0]  == "hello"
	assert pd['l'] == [1,2,3]
		
Additionally you may organize objects in sets, and these sets in partitions::
	
	objset = sn.objectSet(did, 0, autoCreate=True)
	objset.add(Transform())
	
	mrv.Scene.save(tmpscene)
	mrv.Scene.open(tmpscene)
		
	assert len(Node(snn).objectSet(did, 0)) == 1
	
The ``mrv.maya.nt.storage`` module is built to make it easy to create own node types that are compatible to the storage interface, which also enables you to write your own and more convenient interface to access data.

