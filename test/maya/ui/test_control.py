# -*- coding: utf-8 -*-
from mrv.test.maya import *
from util import *
import mrv.maya.ui as ui

import maya.cmds as cmds

if not cmds.about(batch=1):
	class TestControls(unittest.TestCase):
		def test_base(self):
			win = ui.Window(title="Controls Test")
			col = ui.ColumnLayout(adj=True)
			
			tsl = ui.TextScrollList(allowMultiSelection=True)
			tsl.p_append = "one"
			tsl.p_append = "two"
			
			assert tsl.selectedIndex() == -1
			assert len(tsl.selectedIndices()) == 0
			
			tsl.p_selectIndexedItem = 1
			assert tsl.selectedIndex() == 1
			assert len(tsl.selectedIndices()) == 1
			
			tsl.p_selectIndexedItem = 2
			# just shows the first selected one
			assert tsl.selectedIndex() == 1
			assert len(tsl.selectedIndices()) == 2 
			
			win.show()
