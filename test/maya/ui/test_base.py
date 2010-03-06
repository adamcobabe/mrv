import unittest
from mayarv.maya.ui import *
import maya.cmds as cmds


class TestGraphicalUserInterface( unittest.TestCase ):

	def test_doc_demo_basics( self ):
		if cmds.about( batch=1 ):
			return
		# creation
		win = Window(title="demo")
		assert isinstance(win, basestring)
		
		# properties
		assert "demo" == win.p_title
		win.p_title = "property demo"
		assert "property demo" == win.p_title
		self.failUnlessRaises(AttributeError, setattr, win, 'p_numberOfMenus', 3)
		
		# layouts 
		form = FormLayout( )
		win.setActive()
		
		col = ColumnLayout(adj=1)
		b1 = Button(label="one")
		b2 = Button(label="two")
		col.setParentActive()
		
		
		# events 
		def adjust_button( sender, *args ):
			print args
			sender.p_label = "pressed"
			b2.p_label = "affected"
		# END call
		
		b1.e_released = adjust_button
		
		win.show()
		
		
	def test_doc_demo_modules(self):
		if cmds.about( batch=1 ):
			return
		
		class Additor(Button):
			e_added = Signal('added')
			def __init__(self, *args, **kwarg):
				self.reset(0)
				
			def reset(self, base, add=1):
				self._val = base
				self._add = add
				self.p_label = str(self._val)
				
			def add(self, *args):
				self._val += self._add
				self.p_label = str(self._val)
				self.e_added.send(self._val)
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
				
				