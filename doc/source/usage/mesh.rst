
************************
Mesh Component Iteration
************************
Meshes can be handled nicely through their wrapped ``MFnMesh`` methods, but in addition it is possible to quickly iterate its components using very pythonic syntax::
	
	m = Mesh()
	PolyCube().output.mconnectTo(m.inMesh)
	average_x = 0.0
	for vit in m.vtx:                  # iterate the whole mesh
		average_x += vit.position().x
	average_x /= m.numVertices()
	assert m.vtx.iter.count() == m.numVertices()
		
	sid = 3
	for vit in m.vtx[sid:sid+3]:       # iterate subsets
		assert sid == vit.index()
		sid += 1
		
	for eit in m.e:                    # iterate edges
		eit.point(0); eit.point(1)
			
	for fit in m.f:                    # iterate faces
		fit.isStarlike(); fit.isPlanar()
			
	for mit in m.map:                  # iterate face-vertices
		mit.faceId(); mit.vertId() 
	
As it has only been hinted at in the example, it should be clarified that all shortcuts supported by Components, i.e. ``m.cf[1,3,5]`` will work with iterators as well.

