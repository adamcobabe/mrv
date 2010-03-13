

=========================
Graphical User Interfaces
=========================
MayaRV wraps all ( maybe most ) user interface commands into python classes and places these into a hierarchy to allow polymorphic behaviour through inheritance. Even though inheritance relationships within the set of Maya User Interface commands was boiled down to flat commands, there is such a relation ship.

The ``ColumnLayout`` for example, is a ``Layout``, a ``UIContainer``, a ``SizedControl`` and a ``NamedUI``, inheriting functionality from all its bases. 


All user interface classes live in the ``mayarv.maya.ui`` package, and are implemented in descriptive subpackages such as ``ui.layout``, ``ui.control``, ``ui.panel`` and ``ui.editor``.

Instantiation
==============
Creating new interface elements is straightforward, and the fact that all user interface elements call MEL in the background becomes obvious when looking at the way they are created::
	>>> from mayarv.maya.ui import *
	
	>>> win = Window(title="demo")

All keyword arguments passed to the ``Window`` class are exactly the same as if they would have been passed to window MEL command, in that case ``window -title "demo"``. The returned instance though will be an instance of type ``Window`` which is also a string::
	>>> assert isinstance(win, basestring)
	
Properties
==========
In this example, we have set the title of the Window to 'demo'. In MEL it would be quite easy to query or to change this, just call ``window -q -title $win`` or ``window -e -title "property demo" $win`` respectively. 

In MayaRV, everything that is *at least* queryable is a property. Properties are prefixed with *p_* and hence live in their own namespace. The name of the properties follow the capitalization of the MEL flag which they represent. 
Some properties can only be queried, and you will get an AttributeError if you try to query them::
	>>> assert "demo" == win.p_title
	>>> win.p_title = "property demo"
	>>> assert "property demo" == win.p_title
	>>> # win.p_numberOfMenus = 3 # raises AttributeError
	
Layouts
=======
Layouts behave like containers as they will keep other user interface element. Additionally they define their spatial arrangement.

They will only receive newly created controls if they are set to be the current, newly created Layouts and Windows will automatically set the parent to be themselves. 

In MayaRV you may either set a specific Container active using ``container.setActive()`` or the previous parent using ``container.setParentActive()``::
	>>> form = FormLayout( )        # an empty form layout
	>>> win.setActive()
		
	>>> col = ColumnLayout(adj=1)   # put two buttons into the layout
	>>> b1 = Button(label="one")
	>>> b2 = Button(label="two")
	>>> col.setParentActive()
		
If you use Maya2008 and later, you may also use the ``with`` statement, which takes care of the current parent automatically. The previous part creating the column layout could be rewritten like that::
	>>> with ColumnLayout(adj=1) as col:
	>>> 	...
	>>> # implicit setParentActive()
	
As it is practical to indicate the hierachical level using indentations, you may also consider the following writing style::
	>>> col = ColumnLayout()
	>>> if col:
	>>>		b1 = Button()
	>>>	col.setParentActive()
	
Events
======
To make interface elements respond to user interaction like mouse clicks and keyboard inputs in a specific way, one must assure that the own code gets called when these events happen.

The Maya UI System provides simple string or python callbacks which will be executed when the event occours. This has the inherent disadvantage that there may be only listener for each event - workaround have to be implemented manually.

With MayaRV, events are properties of the class prefixed with *e_*. You can assign any amount of callable objects to them. Any MEL command flag ending with *somethingCommand* is available under the name with the 'Command' portion removed, i.e. *e_something*. 
	>>> def adjust_button( sender ):
	>>> 	sender.p_label = "pressed"
	>>> 	b2.p_label = "affected"
	>>> # END call
		
	>>> b1.e_released = adjust_button

Show the window to see a simple UI with two vertically arranged buttons, if 'one' is pressed, 'two' will be affected::
	>>> win.show()

Managing Instance Lifetime
==========================
The user interface elements created from within python are only wrappers, hence they are not linked to the lifetime of the actual UI element by default.

This implies that they will be destroyed once they go out of scope ( and the pyhton reference count reaches zero ).

In conjunction with events, this can be fatal as the event receiver might just have been deleted. To prevent this, all ``e_eventName`` events will strongly bind their event receivers, keeping the wrapper objects alive. This is possible by passing a strong reference of the event sender object to the maya event, which will then dispatch the event to all strongly bound event receivers.

Once the UI gets deleted though, maya does *not* properly destroy the callback objects which binds the event sender, hence it would never go out of scope, as well as its event receivers will keep floating around.

A partial aid is implemented with the ``uiDeleted`` callback. If overridden, it should be used to register own events and to remove own event receivers. 
Nonetheless, your own instance is unlikely to ever be deleted as the callback registered to maya still holds a reference to your instance, although it will never fire. Its equivalent to a memory leak.

This means you should refrain from storing large amounts of data on an instance which also registers events using ``e_eventName``, and if so, to implemented the ``uiDeleted`` method to release all your memory yourself as good as possible, by deleting your respective member variables.

Building Modular User Interfaces
=================================
With these basics, you are already able to define user interfaces and make them functional. Quickly you will realize that you will always end up with first defining the UI and events, and secondly you define individual controls are supposed to behave on user interaction. 

More complex user interface easily have several layouts in complex hierarchical relationships, updating the user interface properly and efficiently becomes a daunting task.

The solution is to pack the user interface elements into modules which are not doing anything else than fulfilling a specific task. These modules provide an interface to interact with them, and events to react to them.

This way, complex user interfaces can be assembled in a more controllable fashion, events bind the different indepenent modules together::
	>>> class Additor(Button):
	>>> 	e_added = Signal()
	>>> 	def __init__(self, *args, **kwarg):
	>>> 		self.reset(0)
	>>> 		
	>>> 	def reset(self, base, add=1):
	>>> 		self._val = base
	>>> 		self._add = add
	>>> 		self.p_label = str(self._val)
	>>> 		
	>>> 	def add(self, *args):
	>>> 		self._val += self._add
	>>> 		self.p_label = str(self._val)
	>>> 		self.e_added(self._val)
	>>> # END additor
	>>> 
	>>> class Collector(Text):
	>>> 	def __init__(self, *args, **kwargs):
	>>> 		self.p_label = ""
	>>> 		
	>>>	def collect(self, value):
	>>> 		self.p_label = self.p_label + ", %i" % value
	>>> # END collector
	>>> 
	>>> class AdditionWindow(Window):
	>>> 	def __init__(self, *args, **kwargs):
	>>> 		col = ColumnLayout()
	>>> 		lb = Additor()
	>>> 		rb = Additor()
	>>> 		c = Collector()
	>>> 		
	>>> 		lb.e_released = rb.add
	>>> 		rb.e_released = lb.add
	>>> 		lb.e_added = c.collect
	>>> 		rb.e_added = c.collect
	>>> 		col.setParentActive()
	>>> # END addition window
	>>> AdditionWindow().show()

You can customize your constructors as well, or constrain and manipulate the way your module is created.

