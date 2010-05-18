	
****
Undo
****
The MayaAPI, the very basis of MRV, has limited support for undo as it clearly focuses on performance. Changes to the dependency graph can only be made through a utility which supports undo, but changes to values through plugs for instance  are not covered by that. To allow MRV to be used within user scripts, full undo was implemented wherever needed. This is indicated by the ``undoable`` decorator. Whenever a method which changes the state cannot be undone for whichever reason, it is decorated with ``notundoable``.

As you are unlikely going to need undo support when running in batch mode or standalone, you can disable the undo system by setting MRV_UNDO_ENABLED to 0, which causes the undo implementation to completely disappear in many cases, reducing the overhead considerably as well as the memory usage.

In case your method or function uses an undoable method, it must be decorated with ``undoable`` as well. If you fail doing so, undo will pick up your individual undoable calls, and a single invocation of maya's undo will just undo one of them ( instead of all the changes your method introduced ).

To implement a simple undoable function yourself, you create a functor of type ``GenericOperation`` which will be told what to do to apply your operation, and to undo it.

The following example shows how multiple undoable operations are bundled into a single undoable operation::
	
	import maya.cmds as cmds
	@undoable
	def undoable_func( delobj ):
		p.tx.mconnectTo(p.tz)
		delobj.delete()
		
	p = Node("persp")
	t = Transform()
	assert not p.tx.misConnectedTo(p.tz)
	assert t.isValid() and t.isAlive()
	undoable_func(t)
	assert p.tx.misConnectedTo(p.tz)
	assert not t.isValid() and t.isAlive()
		
	cmds.undo()
	assert not p.tx.misConnectedTo(p.tz)
	assert t.isValid() and t.isAlive()
	
Whenever non-overridden MFnFunctions are called, these will not support undo by default unless it gets implemented specifically within MRV.

It is planned to improve this in :doc:`future releases <../roadmap>`.

Recording your Changes
======================
MRV keeps an own undo stack for its undoable commands which integrates itself with maya's undo queue using a custom MEL command. Effectively it records every change on that stack, once the main undoable method completes, the stack is moved onto maya's own undo queue.

This allows for interesting uses considering that you can, at any time undo, your own doing in a controlled and safe fashion. This can be very useful to prepare a scene for export by changing it, and then undo your changes once you are done. This way, the user wouldn't have to reload the ( possibly huge ) scene::
	
	import mrv.maya.undo as undo
	ur = undo.UndoRecorder()
	ur.startRecording()
	p.tx.mconnectTo(p.ty)
	p.tx.mconnectTo(p.tz)
	ur.stopRecording()
	p.t.mconnectTo(t.t)
		
	assert p.tx.misConnectedTo(p.ty)
	assert p.tx.misConnectedTo(p.tz)
	assert p.t.misConnectedTo(t.t)
	ur.undo()
	assert not p.tx.misConnectedTo(p.ty)
	assert not p.tx.misConnectedTo(p.tz)
	assert p.t.misConnectedTo(t.t)
