# -*- coding: utf-8 -*-
from mrv.test.maya import *
from util import *
import mrv.maya.ui as ui

from mrv.test.maya.ui import instructor

import maya.cmds as cmds

if not cmds.about(batch=1):
	class TestUITestingUtilities(unittest.TestCase):
		def test_base(self):
			instructor.notify("simple notification, multi-line")
			
			# cannot end before start
			self.failUnlessRaises(AssertionError, instructor.stop_test_recording)  
			
			# cannot add sections either
			self.failUnlessRaises(AssertionError, instructor.add_test_section, lambda: None)
			
			
			# FIRST RECORDING
			#################
			instructor.start_test_recording("first")
			
			# cannot start before stop
			self.failUnlessRaises(AssertionError, instructor.start_test_recording, "fail")
			
			# invalid not to add sections
			self.failUnlessRaises(AssertionError, instructor.stop_test_recording)
			
			
			def default_1(data):
				assert isinstance(data, dict)
			# END first 1
			
			def fail_1(data):
				raise AssertionError("I am failing for a good reason")
			# END fail 1
			
			# add one successful
			instructor.add_test_section(default_1, default_1, "first 1 text", "check 1 text")
			
			# add preparation only
			instructor.add_test_section(default_1, None, "first 2 text - no check")
			
			# add check only
			instructor.add_test_section(None, default_1, None, "first 3 - check only") 
			
			# catches unreasonable configuration
			self.failUnlessRaises(AssertionError, instructor.add_test_section, None, None)
			
			# methods without text
			instructor.add_test_section(default_1, default_1)
			
			# make it fail - preparation
			instructor.add_test_section(fail_1, None, "Preparation fails")
			
			
			instructor.stop_test_recording()
			
			
			
			# ADD SECOND RECORDING
			######################
			instructor.start_test_recording("second")
			
			# check fails
			instructor.add_test_section(None, fail_1, None, "Check fails")
			
			instructor.stop_test_recording()
			
			# ADD THIRD RECORDING
			#####################
			instructor.start_test_recording("third")
			
			# this one works, finally
			instructor.add_test_section(default_1, default_1, "working preps", "Working check")
			
			instructor.stop_test_recording()
			
			# now its up to the user to do the clicking
		
		
