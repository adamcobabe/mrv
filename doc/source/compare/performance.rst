
***********
Performance
***********
Although all performance tests are synthetic and will not give a real indication  of the actual runtime of your scripts, they are able to give a hint about the general performance of certain operations.

The numbers have been produced on a 2Ghz Dual Core Machine running Xubuntu 8.04.  Maya 2010 [#perfm10]_ has been preloaded by the systems virtual memory system, and all temporary  directories are RAM disks (tmpfs).

The tests were run one time only. All MRV performance tests can be found in the  ``mrv.test.maya.performance`` module and run using  ``test/bin/tmrv [maya_version] test/maya/performance``.

All PyMel tests can be found on the github fork at  http://github.com/Byron/pymel/tree/performancetests, and run using  ``tests/pymel_test.py tests/performance``.

All test cases are presented with their actual code, omitting the code needed to measure the actual time. The final results are presented in a table.

Mesh Iteration
===============
MRV mesh iteration tests can be found in ``mrv/test/maya/performance/test_geometry.py``.

PyMel mesh iteration tests can be found in ``pymel/tests/performance/test_geometry.py``.

* **Iter Vtx No-Op**

 * The test provides a basis to compute the pure iteration overhead.
 * **PyMel**::
 	 
 	m = PyNode('mesh40k')
 	nc = 0
	for it in m.vtx:
		nc += 1
	
 * **MRV**::
 	 
 	m = Node('mesh40k')
 	nc = 0
	for it in m.vtx:
		nc += 1
	
* **Iter Vtx Index**

 * Iterate vertices and query the index. It show how a very light operation affects iteration performance
 * **PyMel**::
 	 
 	for it in m.vtx:
		it.index()

 * **MRV**::
 	 
 	for it in m.vtx:
		it.getIndex()
	
* **Iter Vtx Position**

 * Iterate vertices and query their local space position. This operation is more costly due to the potential space transformation.
 * **PyMel**::
 	 
 	for it in m.vtx:
		it.getPosition() 
 	 
 * **MRV**::
 	 
 	for it in m.vtx:
		it.position()
	
* **Iter Edge Position**

 * Iterate edges and query their vertice's positions in local space
 * **PyMel**::
 	 
 	for it in m.e:
		it.getPoint(0)
		it.getPoint(1) 
 	 
 * **MRV**::
 	 
 	for it in m.e:
		it.point(0)
		it.point(1)

* **Iter Poly Position**

 * Iterate polygons and query all the polygon's vertex positions in localspace
  
 * **PyMel**::
 	 
 	for it in m.f:
		it.getVertices()
 	 
 * **MRV**::
 	 
 	ia = api.MIntArray()
 	for it in m.f:
		it.getVertices(ia)

====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Iter Vtx No-Op 			4,96s ( 8.018 vtx/s )								0,019s ( 2.009.699 vtx/s )
Iter Vtx Index 			4,95s ( 8.035 vtx/s )								0,037s ( 1.065.929 vtx/s )
Iter Vtx Position		23,69s ( 1.679 vtx/s )								0,070s ( 565.626 vtx/s )
Iter Edge Position		59,82s ( 665 e/s )									0,329s ( 120.621 e/s )
Iter Poly Position		13,36s ( 2.977 f/s )								0,065s ( 609.627 f/s )
====================   ================================================== ==================================================

Set Vertex Colors
=================
This more complex example performs an actual computation. It will set the verex color relative to the average length of the edges connected to the vertex in question.

* **PyMel**::

	obj = PyNode('mesh40k')
		
	cset = 'edgeLength'
	obj.createColorSet(cset)
	obj.setCurrentColorSetName(cset)
	colors = []
	el = api.MIntArray()
	el.setLength(obj.numVertices())
	maxLen = 0.0
	for vid, vtx in enumerate(obj.vtx):
		edgs = vtx.connectedEdges()
		totalLen=0
		for edg in edgs:
			totalLen += edg.getLength()
	
		avgLen=totalLen / len(edgs)
		maxLen = max(avgLen, maxLen)
		el[vid] = avgLen
		colors.append(Color.black)
	
	for vid, col in enumerate(colors):
		col.b = el[vid] / maxLen
	
	obj.setColors( colors )
 
* **MRV**::
	
	cset = 'edgeLength'
	m = Node('mesh40k')
	
	m.createColorSetWithName(cset)
	m.setCurrentColorSetName(cset)
	
	lp = api.MPointArray()
	m.getPoints(lp)
	
	colors = api.MColorArray()
	colors.setLength(m.numVertices())
	
	vids = api.MIntArray()
	vids.setLength(len(colors))
	
	el = api.MFloatArray()
	el.setLength(len(colors))
	cvids = api.MIntArray()
	
	# compute average edge-lengths
	max_len = 0.0
	for vid, vit in enumerate(m.vtx):
		vit.getConnectedVertices(cvids)
		cvp = lp[vid]
		accum_edge_len=0.0
		for cvid in cvids:
			accum_edge_len += (lp[cvid] - cvp).length()
		avg_len = accum_edge_len / len(cvids)
		max_len = max(avg_len, max_len)
		el[vid] = avg_len
		vids[vid] = vid
	
	for cid in xrange(len(colors)):
		c = colors[cid]
		c.b = el[cid] / max_len
		colors[cid] = c
	
	m.setVertexColors(colors, vids, api.MDGModifier())


====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Set Vertex Colors 		153,07s ( 259 colors/s )							1,715s ( 23.198 colors/s )
====================   ================================================== ==================================================
	

Node Wrapping
=============
Both frameworks rely on custom types which wrap the underlying API object to provide a more convenient programming interface. The process of wrapping an API object in an instance of a custom type can be costly, and as both frameworks return these by default, node wrapping performance directly affects the performance of all operations.

The scene loaded for the test contains more than 2500 DAG and DG nodes which are to be wrapped.

As preparation, strings of all nodes in the scene are stored in the node_strings list. All (Py)Nodes are stored for later extraction of the API objects.

* **Wrap from String**

 * **PyMel**::
 	 
 	for name in nodes_strings:
 		PyNode(name)
 
 * **MRV**::
 	 
	for name in nodenames:
		Node( name )
	
* **Wrap from String2**

 * MRV supports a fast constructor which can be used to construct Node instances from strings only. There is no equivalent in PyMel 
 
 * **MRV**::
 	 
 	for name in nodenames:
		tmplist.append(NodeFromStr(name))

* **Wrap from API Obj**

 * **PyMel**::
 	 
 	for apiobj in nodes_apiobjects:
		PyNode(apiobj)
	
 * **MRV**::
 	 
 	for apiobj in nodes_apiobjects:
		Node(apiobj)
 
* **Wrap from API Obj2**

 * MRV supports fast constructors which get right to the point, and are more specialized. There is no equivalent in PyMel 
 
 * **MRV**::
 	 
 	for apiobj in nodes_apiobjects:
		NodeFromObj(apiobj)
 	 
====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Wrap from String 		1,84s ( 5.928 Nodes/s )								0,469s ( 15.553 nodes/s )
Wrap from String2 		xxxxxxxxxxxxxxxxxxxxxxx								0,426s ( 17.539 nodes/s )
Wrap from API Obj		0,727s ( 15.068 nodes/s)							0,112s ( 67.264 nodes/s )
Wrap from API Obj2		xxxxxxxxxxxxxxxx									0,079s ( 94.665 nodes/s )
====================   ================================================== ==================================================


Node Handling
=============
Nodes can be created, renamed, and their DAG relationships may change through parenting and instancing.

The following test creates 1000 dg nodes ( ``network`` ) as well as 1000 dag nodes ( ``transform`` ) and renames them afterwards. The code shown here is only comprised of the lines which are of actual importance, some boilerplate code is omitted.

* **Create DG Nodes** and **Create DAG Nodes**

 * **PyMel**::
 	 
 	for node_type in ('network', 'transform'):
 		for number in xrange(nn):
			createNode(node_type)

 * **MRV**::
 	 
 	for node_type in ('network', 'transform'):
 		for number in xrange(nn):
			createNode(node_type, node_type) 

* **Rename DG Nodes** and ** Rename DAG Nodes**

* **PyMel**::
 	 
 	for node in nodes:
		node.rename(node.name()[:-1])

 * **MRV**::
 	 
 	for node in node_list:
		node.rename(node.basename()[:-1])

====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Create DG Nodes 		0,456s ( 2.190 Nodes/s )							0,436s ( 2.290 nodes/s )
Create DAG Nodes 		0,425s ( 2.348 Nodes/s )							0,504s ( 1.983 nodes/s )
Rename DG Nodes 		0,553s ( 1.807 Nodes/s )							0,290s ( 3.437 nodes/s )
Rename DAG Nodes 		0,465s ( 2.148 Nodes/s )							0,339s ( 2.941 nodes/s )
====================   ================================================== ==================================================
	
Attributes and Plugs
====================
Whether you want to access data, or make new connections to alter the data flow, MPlugs (MRV) and Attributes (PyMel) are required to do it.

The following tests take part in a scene with more than 21000 animation nodes and plenty of corresponding animated DAG and DG nodes of different types. The animation nodes are first retrieved, then their output plugs are accessed.

* **Get Anim Nodes**

 * **PyMel**::
 	 
 	anim_nodes = ls(type="animCurve")

 * **MRV**::
 	 
 	anim_nodes = list(iterDgNodes(Node.Type.kAnimCurve))


* **Access Plug/Attr**

 * **PyMel**::
 	 
 	for anode in anim_nodes:
		anode.output

 * **MRV**::
 	 
 	for anode in anim_nodes:
		anode.output
		
* **Access Plug**

 * In MRV, one can access the plug using an MFn method. In PyMel, its not possible to receive the plug 

 * **MRV**::
 	 
 	for anode in anim_nodes:
		anode.findPlug('output')

	
The following tests are to determine the performance of the retrieval of simple floating point data, using the plug/attribute as well as an MFnMethod.

The variable ``p`` is a PyNode/Node of the perspective camera ( shape ). The loop is set to 50000 iterations.

* **Access Plug/Attr 2**

 * Access the same plug/attribute repeatedly on the same node
 
 * **PyMel**::
 	 
 	for iteration in xrange(na):
		p.fl

 * **MRV**::
 	 
	for iteration in xrange(na):
		p.fl

* **Get Plug/Attr Data**

 * **PyMel**::
 	 
 	for iteration in xrange(na):
		p.fl.get()
	
 * **MRV**::
 	 
 	for iteration in xrange(na):
		p.fl.asFloat()
	
* **MFnMethod Access**

 * **PyMel**::
 	 
 	for iteration in xrange(na):
		p.getFocalLength
	
 * **MRV**::
 	 
 	for iteration in xrange(na):
		p.focalLength

* **MFnMethod Call**

 * **PyMel**::
 	 
 	for iteration in xrange(na):
		p.getFocalLength()
	
 * **MRV**::
 	 
 	for iteration in xrange(na):
		p.focalLength()
	
* **Plug/Attr Connection**

 * The test contains two network nodes which feature multi-message plugs/attributes. 5000 of these are connected with each other, from one network node to another. A utility is used to produce the required element plugs/attributes. 
 * Please note that single connecting plugs is inefficient, in case of MRV its better to use ``MPlug.mconnectMultiToMulti`` to get 10x the performance.
 
 * **PyMel**::
 	 
 	for source, dest in zip(pir(sn.a, r), pir(tn.ab, r)):
		source > dest
	
 * **MRV**::
 	 
 	for source, dest in zip(pir(sn.a, r), pir(tn.ab, r)):
		source.mconnectTo(dest)
	
====================   ================================================== ==================================================
Test                   PyMel 1.0.1											MRV 1.0.0 Preview
====================   ================================================== ==================================================
Get Anim Nodes 			10,26s ( 2.086 nodes/s )							0,393s ( 54.357 nodes/s )
Access Plug/Attr		3,99s ( 5.363 attrs/s )								0,309s ( 69.872 plugs/s )
Access Plug				xxxxxxxxxxxxxxxxxxxxxxx								0,275s ( 77.771 plugs/s )
Access Plug/Attr 2		6,51s ( 7.671 attrs/s )								0,718s ( 69.579 plugs/s )
Get Plug/Attr Data		14,04 ( 3.559 values/s )							1,03s ( 48.483 values/s )
MFnMethod Access		0,0079s( 6.260.342 accesses/s )					0,0061s ( 8.184.646 accesses/s )
MFnMethod Call			0,470s ( 106.234 calls/s )							0,286 ( 174.749 calls/s )
Plug/Attr Connection	1,35s ( 3698 connections/s )						1,072 ( 4662 connections/s )
====================   ================================================== ==================================================
	
Startup Time and Memory Consumption
===================================
When using a framework, it should ideally unfold its capabilities as fast as possible thanks to minimal loading times, and be as small as possible in main memory to keep more available for the actual task.

This test regards two different scenarios: Usage in the script editor in gui mode and usage as part of a program running in a standalone python interpreter. The version running in the script editor should have all functionality available in the root namespace and imports everything, whereas the program will only import core functionality.

In Gui mode, the time actually measured is the time it takes to import the respective modules from a freshly started maya with no plugins loaded. 

In standalone mode, the time it takes to startup the interpreter and import the core framework modules is measured - they are assumed to initialize maya standalone. In MRV, undo is enabled even in standalone mode to be more comparable to PyMel which doesn't allow that. In MRVs case, the time and memory it takes to load a plugin could be saved otherwise.

The memory consumption is measure by checking the resident memory of the program before and after the import of the respective modules.

All GUI tests are performed in Maya 2011 on OSX - I could not activate my trial on linux. The OSX machine is a 2ghz dual core with 4GB of RAM. 
All standalone tests are performed on Maya 2011 on Xubuntu linux as it nicely shows how fast maya can be startup.

All tests have been performed at least two times, the best time was used.

* **GUI Import Time**

 * **PyMel**::
 	 
 	 from pymel.all import *
	
 * **MRV**::
 	 
 	 from mrv.maya.all import *
 	 
* **OpenMaya Memory/Time**

 * As both frameworks use OpenMaya and import all modules, the memory it takes to do so as well as the time it takes to load is included in the measurements::
 	 
 	import maya.OpenMaya
 	import maya.OpenMayaMPx
 	import maya.OpenMayaRender
 	import maya.OpenMayaFX
 	import maya.OpenMayaAnim
 	 
* **GUI Memory**

 * The memory was measured once before importing the modules using the code above, and once after the import.

* **Standalone Startup**

 * **PyMel**::
 	 
 	$ time mrv 2011 -c "import pymel.core"
 	 
 * Please note that the line above always crashed while deflating the database using zip ( for some strange reason ), so I had to use another line which worked::
 		
 	$ time mrv 2011 -c "import pymel.all"
 	
 * The line above did not terminate maya correctly, but it was at least started up so a time could be extracted.
 
 * **MRV**::
 	 
 	$ time mrv 2011 -c "import mrv.maya.nt"
 
* **Standalone Memory**

 * The memory is measured in a python interactive shell due to its persistent nature. The base memory is measured after manually initializing maya standalone. Afterwards, the respective core modules are imported::
 	 
 	import maya.standalone
 	maya.standalone.initialize()
 	
 * **PyMel**::
 	 
 	import pymel.core
 	
 * Please note that the above line would crash at the same spot as it did during the startup test, so the following line worked so far::
 
 	import pymel.all
 	 
 * **MRV**::
 	 
 	import mrv.maya.nt

=====================  ================================================== ==================================================
Test                   PyMel 1.0.1                                        MRV 1.0.0 Preview
=====================  ================================================== ==================================================
OpenMaya Memory/Time   203,5 MB -> 215,7 MB == 12,2 MB in 0,22s           see left side
GUI Import Time        2,37s                                              0.62s
GUI Memory             203,5 MB -> 291,1 MB == 87,6 MB                    203,5 MB -> 224,5 MB == 21,0 MB
Standalone  Startup    8,24s (*invalid run due to repeatable crash*)      5,74s
Standalone Memory      123,7 MB -> 253,9 MB == 130,2 MB (*invalid run*)   123,7 MB -> 153,1 MB == 29,4 MB
=====================  ================================================== ==================================================

.. note:: During testing, it is recommended to use maya 8.5 or 2008 as they will be ready in 3,2s (8.5) to 3,8s (2008).


--------------------------------------------------------------------------------

.. [#perfm10] Maya 2010 is the fastest release so far regarding the python performance. Maya 2011 is about 7% slower.
