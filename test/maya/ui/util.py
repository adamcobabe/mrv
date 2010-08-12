# -*- coding: utf-8 -*-
"""Provide UI testing utilities"""
import mrv.maya.ui as ui
import traceback

__all__ = ("NotificatorWindow", )


class TestSection(object):
	"""Simple structure keeping section information"""
	__slots__ = ('prepare_cb', 'check_cb', 'prepare_text', 'check_text')
	def __init__(self, prepare_cb, check_cb, prepare_text, check_text):
		self.prepare_cb = prepare_cb
		self.check_cb = check_cb
		self.prepare_text = prepare_text
		self.check_text = check_text

class TestRecord(object):
	"""Simple structure to keep multiple TestSections"""
	__slots__ = ('name', 'sections', 'cur_section_index', 'fail_info', 
					'initialize', 'shutdown', 'data')
	
	def __init__(self, name, initialize, shutdown):
		self.name = name
		self.cur_section_index = 0
		self.sections = list()
		self.initialize = initialize
		self.shutdown = shutdown
		self.data = dict()
		
		self.fail_info = None
		

class NotificatorWindow(ui.Window):
	"""Utility window, which is used to provide instructions to the user
	who has to click some buttons on screen."""
	
	k_no_instruction = "No instruction available"
	
	def __init__(self):
		self.p_title = "Instructor"
		h = 100
		self.p_wh = (150, h)
		self.p_rtf = True
		
		ui.ColumnLayout(adj=True)
		self.text = ui.ScrollField(editable=False, wordWrap=True)
		self.text.p_h = h
		
		self.b_prepare = ui.Button(manage=False)
		self.b_check = ui.Button(manage=False)
		self.b_prepare.e_released = self._test_button_pressed
		self.b_check.e_released = self._test_button_pressed
		
		self._is_recording = False
		self._cur_record_index = 0
		self._cur_record = None
		self._records = list()
		
	#{ Interface
		
	def notify(self, text):
		"""Set the given textual instruction to te window"""
		self.text.p_text = text
		
	def start_test_recording(self, test_name, initialize=None, shutdown=None):
		"""Start a test with the given name. If there is no test currently running, 
		your test will be enabled in the UI once stop_test_recording was called.
		If a test is already running, your test will be scheduled and may run
		once the running test succeeded or failed.
		As you can record multiple tests, which will be shown in order, it is recommended
		to keep a global instance of the NotificationWindow as a shared resource for 
		all participating Unittests.
		:param test_name: string id for the test to run
		:param initialize: if not None, a function to call before running any test in this
			test case,  signature is fun(data), where data is a dictionary for your own data
			that could be initialized here. It wil be passed to all subsequent test sections
		:param shutdown: if not None, functino to call after all tests were run"""
		if self._is_recording:
			raise AssertionError("Call stop_test_recording before starting a new one")
		# END assertion
		self._is_recording = True
		
		self._records.append(TestRecord(test_name, initialize, shutdown))
		
	def add_test_section(self, prepare_fun=None, check_fun=None, prepare_text=None, check_text=None):
		"""Add a new test section
		:param prepare_fun: function to prepare the section, fun()
			It may give instructions through the window's ``notify`` method.
			May be None in case no preparation is required
			signature is fun(data)
		:param check_fun: Check function to check the result, fun()
			It is a failure if it raises, success otherwise.
			Signature is fun(data)
			May be None in case no check is required
		:param prepare_text: if not None, text with instructions for the preparation, telling 
			the user what to do next.
		:param check_text: Text shown before runnning the check function"""
		if not self._is_recording:
			raise AssertionError("Call start_test_recording before adding sections")
		# END assertion
		assert prepare_fun or check_fun, "Need to provide at least one function"
		self._records[-1].sections.append(TestSection(prepare_fun, check_fun, prepare_text, check_text))
		
	def stop_test_recording(self):
		"""Indicate that you are done recording. This also starts the first test
		case in the UI in case no one else is in progress.
		Additionally we assure the Notificator is shown."""
		if not self._is_recording:
			raise AssertionError("Call start_test_recording before stopping it")
		# END asesrtion
		
		if not self._records[-1].sections:
			raise AssertionError("You must add at least one test section")
		# END assertion
		
		self._is_recording = False
		
		if self._active_record() is None:
			self._set_active_record(len(self._records)-1)
		# END set first active record
		
		# update title according to changed settings
		self._set_active_record_title()
		self.show()
	
	#} END interface
	
	#{ Internal
	def _active_record(self):
		""":return: active record instance or None"""
		return self._cur_record
	
	def _set_active_record_title(self):
		"""Update the title to reflect the current test"""
		title = "Test %s (%i of %i)" % (self._cur_record.name, self._cur_record_index+1, len(self._records))
		self.p_title = title
	
	def _set_active_record(self, record_index):
		self._cur_record_index = record_index
		self._cur_record = self._records[record_index]
		
		self._set_active_record_title()
		self._set_active_section(0)
		
	def _set_active_section(self, section_index):
		self._cur_record.cur_section_index = section_index
		section = self._cur_record.sections[section_index]
		
		section_info = "(%i of %i)" % (section_index+1, len(self._cur_record.sections))
		
		is_managed = False
		if section.prepare_cb is not None:
			is_managed=True
			self.b_prepare.p_enable=True
			self.b_prepare.p_label = "Prepare Test %s" % section_info
			self.notify(section.prepare_text or self.k_no_instruction)
		# END hanlde prepare callback
		self.b_prepare.p_manage=is_managed
		
		is_managed=False
		if section.check_cb is not None:
			is_managed = True
			self.b_check.p_enable=section.prepare_cb is None
			self.b_check.p_label = "Post-Test Check %s" % section_info
			if section.prepare_cb is None:
				self.notify(section.check_text or self.k_no_instruction)
		# END handle check callback
		self.b_check.p_manage=is_managed
	
	def _test_button_pressed(self, button, *args):
		"""We currently figure out whether the prepare or check button was pressed
		by checking our internal state only. 
		This call handles calling the individual functions to prepare and check the 
		tests, as well as to alter the UI to represent the test-section in question, 
		up until the final test summary"""
		record = self._cur_record
		section = record.sections[record.cur_section_index]
		
		go_to_next_section=True
		try:
			if record.initialize:
				record.initialize(record.data)
				record.initialize = None
			# END execute initializer
			
			if button is self.b_prepare:
				if section.check_cb:
					go_to_next_section=False
					self.b_prepare.p_enable=False
					self.b_check.p_enable=True
				# END handle additional check
				
				# if we have a check, update the notification now.
				# Just keep showing the prepare instruction if there is no 
				# check instruction available, refresh the prepare instruction
				# in case a prior notify() call removed it
				if section.check_cb is not None and section.check_text:
					self.notify(section.check_text)
				elif section.prepare_text:
					self.notify(section.prepare_text)
				# END section text
				
				# execute function
				section.prepare_cb(record.data)
			else:
				# check pressed - just execute function, check result
				section.check_cb(record.data)
			# END handle button identity
		except Exception, e:
			print "Error when executing test %r, section %i" % (record.name, record.cur_section_index) 
			traceback.print_exc()
			record.fail_info = e
		# END exception handling
		
		# If the section failed, skip to the next section right away
		if record.fail_info is not None:
			go_to_next_section = True
			record.cur_section_index = len(record.sections) - 1
		# END handle errors
		
		if go_to_next_section:
			new_section_index = record.cur_section_index + 1
			if new_section_index == len(record.sections):
				# go to next test, if possible
				new_record_index = self._cur_record_index + 1
				
				# before changing records, try to call shutdown
				try:
					if record.shutdown:
						record.shutdown()
						record.shutdown = None
					# END handle shutdown
				except Exception, e:
					print "Failed during shutdown function"
					traceback.print_exc()
				# END handle shutdown exceptions
				
				if new_record_index == len(self._records):
					# prepare final report
					report_lines = list()
					for rec in self._records:
						if rec.fail_info is None:
							report_lines.append(rec.name + " OK")
						else:
							report_lines.append(rec.name + " FAIL")
							report_lines.extend("\t" + l for l in str(rec.fail_info).split("\n"))
						# END if record had failure
					# END for each record
					self.notify("\n".join(report_lines))
					
					self.b_prepare.p_manage=False
					self.b_check.p_manage=False
				else:
					# go to next record
					self._set_active_record(new_record_index) 
				# END handle records done
			else:
				# go to next section
				self._set_active_section(new_section_index)
			# END handle sections done
		# END handle go to next section
		
	#} END internal
	
	
