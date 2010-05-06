
**************
Usage Examples
**************
The listing concentrates on the code required to perform everyday and  simple tasks. It assumes that all required classes and functions have been  imported into the module where the code is run. This is done most easily using ``from pymel.all import *`` (``PyMel``) or ``from mrv.maya.all import *`` (``MRV``).

As a general difference you will notice that PyMel is very convenient to use through a variety of smart methods which handle many details behind the scenes.

MRV is derived from the MayaAPI, and uses its interface. Compared to MayaAPI code, its like a short hand writing style, yet it remains verbose compared to PyMel and very explicit.


Set Handling
============
Sets are a very nice feature in Maya, as well as their implementation. Handling of sets should be easy and intuitive in the framework you use.

* **PyMel**::
	
	p, t, f = PyNode('persp'), PyNode('top'), PyNode('front')
	s = sets()
	
	# add single
	s.add(p)
	assert p in s
	
	# add multiple - need sets command for undo support
	sets(s, add=(t,f))
	# same in MEL, argument meaning changed in PyMel
	cmds.sets(str(t), str(f), add=str(s))
	
	# remove single 
	s.remove(p)
	
	# remove multiple
	sets(s, rm=(t,f))
	assert sets(s, q=1, size=1) == 0

* **MRV**::
	
	p, t, f = Node('persp'), Node('top'), Node('front')
	s = ObjectSet()
	
	# add single - set centric or object centric
	s.add(p)
	p.addTo(s)
	assert p in s
	
	# add multiple
	s.add((t, f))
	
	# remove single - set or object centric
	s.discard(p)
	p.removeFrom(s)
	
	# remove multiple 
	s.discard((t, f))
	
	assert len(s) == 0
	
	
Shading Engine Handling
=======================
ShadingEngines are ObjectSets, but are specialized for the purpose of rendering. The renderPartition assures that one object or face is only handled by exactly one shading engine.

* **PyMel**::
	
	isg = PyNode("initialShadingGroup")
	rp = PyNode("renderPartition")
	
	# assign new shading engine to the render partition
	sg = createNode('shadingEngine')
	rp.sets.evaluateNumElements()
	
	# the partition plug is overridden by the 'partition' function of the 
	# underlying pseudostring
	# sg.partition > rp.sets[rp.sets.getNumElements()]
	sg.pa > rp.sets[rp.sets.getNumElements()]
	
	m = polySphere()[0].getShape()
	
	# assign all faces to the initial shading group
	# m is automatically part of the default shading engine
	isg.remove(m)
	isg.add(m.f)
	
	# assign 200 faces to another shading group
	# Cannot use object as it does not allow to force the membersship
	# sg.add(m.f[0:199])
	sets(sg, fe=m.f[0:199])
	
* **MRV**::
	
	# NOTE: this test is part of the pymel comparison
	isg = Node("initialShadingGroup")
	rp = Node("renderPartition")
	
	# assign new shading engine to the render partition
	sg = ShadingEngine()
	sg.setPartition(rp)
	
	
	# create a poly sphere
	m = Mesh()
	PolySphere().output.mconnectTo(m.inMesh)
	
	# assign all faces to the initial shading group
	# Cannot use the m.cf[:] shortcut to get a complete component as 
	# shading engines apparently don't deal with it properly
	m.addTo(isg, m.cf[:m.numPolygons()])
	
	# force the first 200 faces into another shading engine
	m.addTo(sg, m.cf[:200], force=True)


Mixed
=====

The following example was taken from the PyMel homepage at http://code.google.com/p/pymel/ as it goes through a few general tasks.

* **PyMel**::

	for x in ls( type='transform'):
		print x.longName()                # object oriented design
	
		x.sx >> x.sy                      # connection operator
		x.sx >> x.sz
		x.sx // x.sy                      # disconnection operator
		x.sx.disconnect()                 # smarter methods -- (automatically disconnects all inputs and outputs when no arg is passed)
	
	# add and set a string array attribute with the history of this transform's shape
		x.setAttr( 'newAt', x.getShape().history(), force=1 )
	
		# get and set some attributes
		x.rotate.set( [1,1,1] )
		trans = x.translate.get()
		trans *= x.scale.get()           # vector math
		x.translate.set( trans )         # ability to pass list/vector args
		# mel.myMelScript(x.type(), trans) # automatic handling of mel procedures

* **MRV**::
	
    import mrv.maya as mrvmaya                  # required for some utilities
    # later we query the shape, hence we must assure we actually have one
    # and setup a custom predicate
    for x in iterDagNodes(Node.Type.kTransform, predicate=lambda n: n.childCount()):
        print x.name()                          # name() always returns the full path name
    
        x.sx.mconnectTo(x.sy)                   # Convenience methods are located in the 'm' namespace of the MPlug type
        x.sx.mconnectTo(x.sz)
        x.sx.mdisconnectFrom(x.sy)
        x.sx.mdisconnect()
        
        default = StringArrayData.create(list())
        shapehistory = [n.name() for n in iterGraph(x[0], input=True)]
        x.addAttribute(TypedAttribute.create('newAt', 'na', Data.Type.kStringArray, default)).masData().set(shapehistory)
        
        x.rx.msetFloat(1.0)                     # using individual plugs to have undo support, otherwise you would use MFn methods, like setRotation(...)
        x.ry.msetFloat(1.0)
        x.rz.msetFloat(1.0)
        
        trans = x.getTranslation(api.MSpace.kTransform)
        dot = trans * x.getScale()                   # the dot product is a single float, MVector has no in-place dot-product as the type changes
        x.tx.msetFloat(dot)                   # have to use child plugs for undo support
        x.ty.msetFloat(dot)
        x.tz.msetFloat(dot)
        
        # mrvmaya.Mel.myScript(x.typeName(), trans) # its essentially the pymel implementation which is used here.
	

.. rubric:: Footnotes

