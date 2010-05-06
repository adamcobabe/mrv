
**********
Selections
**********
There are several utility methods to aid in handling selections. They are mostly used during interactive sessions, although general utilities like ``select`` and ``activeSelectionList`` may also prove practical in scripts. 

The following examples show some of the most common functions::
	
	select(p.t, "time1", p, ps)
	assert len(selection()) == 4
		
	# simple filtering
	assert activeSelectionList().miterPlugs().next() == p.t
	assert selection(api.MFn.kTransform)[-1] == p
		
	# adjustments
	sl = activeSelectionList()
	sl.remove(0)                                 # remove plug
	select(sl)
	assert len(activeSelectionList()) == len(selection()) == 3
	
Please note that many of the selection utilities operate on wrapped Nodes by default, which may not be desired in performance critical areas.  

Advanced filtering can be implemented using the ``predicate`` of iterators, allowing to return only those items for which the predicate function returns a True value. Something like ``ls -ro`` would look like this::
	
	assert len(selection(predicate=lambda n: n.isReferenced())) == 0

Expanders, such as in ``ls -sl -dag`` could be implemented with adapter iterators, which expand dag nodes to the list of their children recursively.

Its worth noting though that very complex filters operating on large datasets could possibly be faster if they are handled by ``ls`` directly instead of reprogramming them using the python MayaAPI.

Selecting Components and Plugs
==============================
Selecting components is comparable to component assignments of sets and shading engines. In case of selections, one first creates a selection list to be selected, and adds the mesh as well as the components::
	
	sl = api.MSelectionList()
	sl.add(m.dagPath(), m.cf[:4])			# first 4 faces
	select(sl)
	assert len(activeSelectionList().miterComponents().next()[1].elements()) == 4

Plugs are can be selected exactly the same way as nodes::
	
	sl.clear()
	sl.add(p.t)
	sl.add(m.outMesh)
	select(sl)
	assert len(selection()) == 2

