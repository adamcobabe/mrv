	
********************
Plugs and Attributes 
********************
Persons without experience with the MayaAPI might be confused at first as MEL always uses the term ``attr`` when dealing with plugs *and* attributes. The MayaAPI, as well as MRV differentiate these.

 * Attributes define the type of data to be stored, its name and a suitable default value. They do not hold any other data themselves.
 
 * Plugs allow accessing Data as identified by an attribute on a given Node. plugs are valid only if they refer to a valid Node and one of the Node's attributes. Plugs can be connected to each other, input connections are exclusive, hence a plug may have multiple output connection, but only one input connection.

Plugs
======
To access data on a node, you need to retrieve a plug to it, which is represented by the patched API type ``MPlug``. Whenever you deal with data and connections within MRV, you deal with plugs::
	
	assert isinstance(p.translate, api.MPlug)
	assert p.translate == p.findPlug('t')
	assert p.t == p.translate 
	
The ``MPlug`` type has been extended with various convenience methods which are well worth an separate study, here we focus on the most important functionality only.
	
Connections
-----------
Connect and disconnect plugs using simple, chainable methods::
	
	p.tx.mconnectTo(p.ty).mconnectTo(p.tz)
	assert p.tx.misConnectedTo(p.ty)
	assert p.ty.misConnectedTo(p.tz)
	assert not p.tz.misConnectedTo(p.ty)
		
	p.tx.mdisconnectFrom(p.ty).mdisconnectFrom(p.tz)
	assert len(p.ty.minputs()) + len(p.tz.minputs()) == 0
	assert p.tz.minput().isNull()
	
	p.tx.mconnectTo(p.tz, force=False)
	p.ty.mconnectTo(p.tz, force=False)     # raises as tz is already connected
	p.ty.mconnectTo(p.tz)                  # force the connection, force defaults True
	p.tz.mdisconnect()                     # disconnect all

Querying Values
---------------
Primitive values, like ints, floats, values with units as well as strings can easily be retrieved using one of the dedicated ``MPlug.asType`` functions::
	
	assert isinstance(p.tx.asFloat(), float)
	assert isinstance(t.outTime.asMTime(), api.MTime)
	
All other data is returned as an MObject serving as a container for the possibly copied data. Data-specific function sets can operate on this data. You need to know which function set is actually compatible with the ``MObject`` at hand, or use a MRV data wrapper::
	
	ninst = p.getInstanceNumber()
	assert p.isInstancedAttribute(p.attribute('wm')) 
	pewm = p.worldMatrix.elementByLogicalIndex(ninst)
		
	matfn = api.MFnMatrixData(pewm.asMObject())
	matrix = matfn.matrix()                       # wrap data manually
		
	dat = pewm.masData()                          # or get a wrapped version right away
	assert matrix == dat.matrix()
	
.. note:: Wrapping data automatically using ``masData`` is relatively inefficient as all known data function sets will be tried for a compatible one. Afterwards the data is copied into a ``Data`` compatible object which gives convenient access to the data ( this can be very inefficient depending on how the data type is actually implemented ). If you favor performance over convenience, initialize the respective MFnFunctionSet yourself. 

Setting Values
--------------
Primitive value types can be handled easily using their corresponding ``MPlug.setType`` functions. Please note that the methods prefixed with 'm' are MRV specific and feature undo support::
	
	newx = 10.0
	p.tx.msetDouble(newx)
	assert p.tx.asDouble() == newx
	
All other types need to be created and adjusted using their respective data function sets. The following example extracts mesh data defining a cube, deletes a face, creates a new mesh shape to be filled with the adjusted data so that it shows up in the scene::
	
	meshdata = m.outMesh.asMObject()
	meshfn = api.MFnMesh(meshdata)
	meshfn.deleteFace(0)                        # delete one face of copied cube data
	assert meshfn.numPolygons() == 5
		
	mc = Mesh()                                 # create new empty mesh to 
	mc.cachedInMesh.msetMObject(meshdata)       # hold the new mesh in the scene
	assert mc.numPolygons() == 5
	assert m.numPolygons() == 6
	
.. note:: As you see, the mesh data extracted initially has been copied at some point - if the data type does not implement copy-on-write, this can be very inefficient on large meshes, especially if you are just examining the data without any intention to alter it.
	
Compound Plugs and Plug-Arrays
------------------------------
Compound Attributes are attributes which by themselves only serve as a parent for one or more child attributes. Array attributes are attributes which can have any amount of homogeneous elements. Compound- and Array Attributes can be combined to create complex special purpose Attribute types.

The ``MPlug`` type has functions to traverse the plugs of the corresponding attributes

A simple example for a compound plug is the translate attribute of a transform, which has 3 child plugs, translateX, translateY and translatZ.

Array plugs are used to access the transform's worldMatrix data, which contains one world matrix per instance of the transform.

The following example shows the traversal of these attribute types::
	
	ptc = p.t.mchildren()
	assert len(ptc) == 3
	assert (ptc[0] == p.tx) and (ptc[1] == p.ty)
	assert ptc[2] == p.t.mchildByName('tz')
	assert p.tx.parent() == p.t
	assert p.t.isCompound()
	assert p.tx.isChild()
		
	assert p.wm.isArray()
	assert len(p.wm) == 1
		
	for element_plug in p.wm:
		assert element_plug.isElement()

Graph Travseral
----------------
Using the ``miter(Input|Output)Graph`` methods, complex and fast traversals of the dependency graph are made easy::
	
	mihistory = list(m.inMesh.miterInputGraph())
	assert len(mihistory) > 2
	assert mihistory[0] == m.inMesh
	assert mihistory[2] == pc.output        # ignore groupparts
		
	pcfuture = list(pc.output.miterOutputGraph())
	assert len(pcfuture) > 2
	assert pcfuture[0] == pc.output
	assert pcfuture[2] == m.inMesh          # ignore groupparts 
	
Please note that the traversal can be configured in many ways to meet your specific requirements, as it is implemented by ``iterGraph``.
	
Attributes
==========
As attributes are just describing the type and further meta information of data, their most interesting purpose is to create new attributes which can be customized to fully suit your needs. 

The following example will use facilities of MRV to create a complex attribute.

* master ( Compound, Array )
 
 * String
 * Point ( double3, Compound )
  
  * x ( double )
  * y ( double )
  * z ( double )
   
 * message ( Message, Array )

The code looks like this::
	
	cattr = CompoundAttribute.create("compound", "co")
	cattr.setArray(True)
	if cattr:
		sattr = TypedAttribute.create("string", "str", Data.Type.kString)
		pattr = NumericAttribute.createPoint("point", "p")
		mattr = MessageAttribute.create("message", "msg")
		mattr.setArray(True)
			
		cattr.addChild(sattr)
		cattr.addChild(pattr)
		cattr.addChild(mattr)
	# END compound attribute

Now the only thing left to do is to add the newly created attribute to a node::
	
	n = Network()
	n.addAttribute(cattr)
	assert n.compound.isArray()
	assert n.compound.isCompound()
	assert len(n.compound.children()) == 3
	assert n.compound['mymessage'].isArray() 
	
Finally, remove the attribute - either using the attribute we kept, ``cattr`` or by finding the attribute::
	
	n.removeAttribute(n.compound.attribute())

