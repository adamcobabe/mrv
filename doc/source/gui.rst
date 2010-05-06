#########################
Graphical User Interfaces
#########################
MRV wraps all ( maybe most ) user interface commands into python classes and places these into a hierarchy to allow polymorphic behaviour through inheritance. This inheritance becomes evident when studying the corresponding MEL commands, which indeed share their flags in a well defined manner.

The ``ColumnLayout`` for example, is a ``Layout``, a ``UIContainer``, a ``SizedControl`` and a ``NamedUI``, inheriting functionality from all its bases. 


All user interface classes live in the ``mrv.maya.ui`` package, and are implemented in descriptive subpackages such as ``ui.layout``, ``ui.control``, ``ui.panel`` and ``ui.editor``.

*************
Instantiation
*************
Creating new interface elements is straightforward, and the fact that all user interface elements call MEL in the background becomes obvious when looking at the way they are created::
	
	from mrv.maya.ui import *
	win = Window(title="demo")

All keyword arguments passed to the ``Window`` class are exactly the same as if they would have been passed to window MEL command, in that case ``window -title "demo"``. The returned instance though will be an instance of type ``Window`` which is also a string::
	
	assert isinstance(win, basestring)
	
**********
Properties
**********
In this example, we have set the title of the Window to 'demo'. In MEL it would be quite easy to query or to change this, just call ``window -q -title $win`` or ``window -e -title "property demo" $win`` respectively. 

In MRV, everything that is *at least* queryable is a property. Properties are prefixed with *p_* and hence live in their own namespace. The name of the properties follow the capitalization of the MEL flag which they represent. 
Some properties can only be queried, and you will get an AttributeError if you try to set them::
	
	assert "demo" == win.p_title
	win.p_title = "property demo"
	assert "property demo" == win.p_title
	# win.p_numberOfMenus = 3 # raises AttributeError
	
*******
Layouts
*******
Layouts behave like containers as they will keep other user interface elements. Additionally they define their spatial arrangement.

They will only receive newly created interface elements if they are set to be the active parent, newly created Layouts and Windows will automatically set the parent to themselves. 

In MRV you may either set a specific container active using ``container.setActive()`` or the container's parent using ``container.setParentActive()``::
	
	form = FormLayout( )        # an empty form layout
	win.setActive()
		
	col = ColumnLayout(adj=1)   # put two buttons into the layout
	b1 = Button(label="one")
	b2 = Button(label="two")
	col.setParentActive()       # set the window to be the active parent
		
If you use Maya2008 and later, you may also use the ``with`` statement, which takes care of the current parent automatically. The previous part creating the column layout could be rewritten like that::
	
	with ColumnLayout(adj=1) as col:
		...
	# implicit setParentActive()
	
Please note that using the ``with`` statement is not very portable as it is only natively available in maya 2010 or newer, or python 2.6 respectively.
	
As it is practical to indicate the hierarchical level using indentations, you may also consider the following writing style::
	
	col = ColumnLayout()
	if col:
		b1 = Button()
		col.setParentActive()
	
In case you are interested to keep the actual child instances that you create,  its good to know that Layouts inherit from ``UIContainerBase`` which provides just that functionality::
	
	col = ColumnLayout()
	if col:
		b1 = col.add(Button())
		assert b1 is col.listChildren()[0] 
		col.setParentActive()
	

******
Events
******
To make interface elements respond to user interaction like mouse clicks and keyboard inputs, one must assure that the own code gets called when these events happen.

The Maya UI System provides simple string or python callbacks which will be executed when the event occurs. This has the inherent disadvantage that there may be only listener for each event - workarounds have to be implemented manually.

With MRV, events are properties of the class prefixed with *e_*. You can assign any amount of callable objects to them. Any MEL command flag ending with *somethingCommand* is available under the name with the 'Command' portion removed, i.e. *e_something*::
	
	def adjust_button( sender ):
		sender.p_label = "pressed"
		b2.p_label = "affected"
	# END call
	
	b1.e_released = adjust_button

Show the window to see a simple UI with two vertically arranged buttons, if 'one' is pressed, 'two' will be affected::
	win.show()

.. _signals-label:
	
*******
Signals
*******
Signals are custom events which are named after the `Signals and Slots <http://doc.trolltech.com/4.6/signalsandslots.html>`_ mechanism introduced by QT.

Signals help to write truly modular user interface elements which can be combined flexibly. The way they respond to each other is solely defined by Signals send to receivers which provide methods to be called.

Signals can be used just like any other event predefined by the system - the only difference is that you may call them yourself, and that the sender of the Signal will not automatically be sent to the receiver as first method argument, as it is the case with Events::
	
	class Sensor(Button):
		e_pushed = Signal() 		# pushedWith(pressure)
		def __init__(self, *args, **kwargs):
			self.e_pressed = lambda *args: self.e_pushed(50)
			self.p_label = "Pressure Sensor"
	
	class Receiver(TextField):
		def pushedWith(self, pressure):
			self.p_text = "%s pressure is %i" % (self.sender().basename(), pressure)
	
	win = Window()
	ColumnLayout(adj=1)
	s = Sensor()
	r = Receiver()
	s.e_pushed = r.pushedWith
	win.show() 

In this example, the Sensor is a button which reacts to its own button-pressed events. Whenever this event occours, it sends out a custom Signal with a pressure level. The Receiver is a TextField which can receive a pressure level, and displays it together with the sender, as retrieved using the ``sender()`` method which is shared by all MRV user interface elements.

The Signal gets connected to the corresponding method using a simple assignment: ``s.e_pushed = r.pushedWith``.

Its important that both interfaces in fact do not know each other, and don't need to know each other - this way they stay self-contained and care about nothing else than implementing their interface correctly.

Even though the underpinnings of the UI Wrap are still based on MEL ( until and including Maya 2010 ), you are enabled to program much more advanced, independent modules that are easier to reuse, and are based on more maintainable code.
	
**************************
Managing Instance Lifetime
**************************
The user interface elements created from within python are only wrappers, hence they are not linked to the lifetime of the actual UI element by default.

This implies that they will be destroyed once they go out of scope as the pyhton reference count reaches zero.

In conjunction with events, this can be fatal as the event receiver might just have been deleted. To prevent this, all ``e_eventName`` events will strongly bind their event receivers, keeping the wrapper objects alive. This is possible by passing a strong reference of the event sender object to the maya event, which will then dispatch the event to all strongly bound event receivers.

Once the UI gets deleted though, maya does *not* properly destroy the callback objects which binds the event sender, hence it would never go out of scope, as well as its event receivers will keep floating around.

A partial aid is implemented with the ``uiDeleted`` callback. If overridden, it should be used to unregister own events and to remove own event receivers. 
Nonetheless, your own instance is unlikely to ever be deleted as the callback registered to maya still holds a reference to it, although it will never fire. Its equivalent to a memory leak.

This means you should refrain yourself from storing large amounts of data on an instance which also registers events using ``e_eventName``, and if so, to implemented the ``uiDeleted`` method to release all your memory yourself as good as possible, by deleting your respective member variables.

********************************
Building Modular User Interfaces
********************************
With these basics, you are already able to define user interfaces and make them functional. Quickly you will realize that you will always end up with first defining the UI and events, and secondly you define individual controls are supposed to behave on user interaction. 

More complex user interface easily have several layouts in complex hierarchical relationships, updating the user interface properly and efficiently becomes a daunting task.

The solution is to pack the user interface elements into modules which are not doing anything else than fulfilling a specific task. These modules provide an interface to interact with them, they send :ref:`Signals <signals-label>` in order for others to respond to them, or they receive Signals of others themselves.

This way, complex user interfaces can be assembled in a more controllable fashion, events bind the different independent modules together::
	
	class Additor(Button):
		e_added = Signal()
		def __init__(self, *args, **kwarg):
			self.reset(0)
			
		def reset(self, base, add=1):
			self._val = base
			self._add = add
			self.p_label = str(self._val)
			
		def add(self, *args):
			self._val += self._add
			self.p_label = str(self._val)
			self.e_added(self._val)
	# END additor
	
	class Collector(Text):
		def __init__(self, *args, **kwargs):
			self.p_label = ""
			
	def collect(self, value):
		self.p_label = self.p_label + ", %i" % value
	# END collector
	
	class AdditionWindow(Window):
		def __init__(self, *args, **kwargs):
			col = ColumnLayout()
			lb = Additor()
			rb = Additor()
			c = Collector()
			
			lb.e_released = rb.add
			rb.e_released = lb.add
			lb.e_added = c.collect
			rb.e_added = c.collect
			col.setParentActive()
	# END addition window
	AdditionWindow().show()

You can customize your constructors as well, or constrain and manipulate the way your UI-element is created.

