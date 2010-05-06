
***********************
About Methods and Types
***********************
Wrapped Nodes make their function set methods available directly. If they have a  wrappable return value, like an MObject resembling an Attribute or a DepdendencyNode, it will be wrapped automatically into the respectve MRV Type::
	
	p = Node("persp")
	ps = p.child(0)			# method originally on MFnDagNode
	assert isinstance(ps, DagNode)

At the current time, input values of function set methods that resemble Objects as MObject or MDagPath will not allow a wrapped Node, but require the manual extraction of the object or dagpath::
	
	ps.hasSamePerspective(ps)	# will raise a TypeError
	assert ps.hasSamePerspective(ps.dagPath())		# method on MFnCamera, needs MDagPath
	
If a MFnFunction has not been explicitly wrapped by MRV, it will not support undo.

In future, automatic type conversions as well undo support are planned to be provided for all MFnFunctions, see the :doc:`../roadmap`.
