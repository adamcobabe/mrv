# -*- coding: utf-8 -*-
"""Test misc utility classes """
import unittest
import sys
import mrv
from mrv.util import *
from mrv.interface import *
import re
import weakref
import mrv.info as info

class TestDAGTree( unittest.TestCase ):

	def test_dagMethods( self ):
		self.tree = DAGTree( )
		self.tree.add_edge( 0,1 )
		self.tree.add_edge( 0,2 )
		self.tree.add_edge( 0,3 )
		self.tree.add_edge( 1,4 )
		self.tree.add_edge( 4,5 )

		self.failUnless( self.tree.parent( 1 ) == 0 )
		self.failUnless( self.tree.parent( 5 ) == 4 )
		self.failUnless( len( list( self.tree.parent_iter( 5 ) ) ) == 3 )

	def test_filters( self ):
		# AND
		sequence = [ 1,1,1,1,0,1,1 ]
		self.failUnless( len( filter( And( bool, bool, bool ), sequence ) ) == len( sequence ) - 1 )

		sequence = [ 0, 0, 0, 0, 0, 0 ]
		self.failUnless( len( filter( And( bool ), sequence ) ) == 0 )
		self.failUnless( len( filter( And( lambda x: not bool(x) ), sequence ) ) == len( sequence ) )

		# OR
		sequence = [ 0, 0, 1 ]
		self.failUnless( len( filter( Or( bool, lambda x: not bool(x) ), sequence ) ) == 3 )

	def test_interfaceBase( self ):
		class IMasterTest( InterfaceMaster ):
			im_provide_on_instance = True

		class Interface( object ):
			pass
		# END simple interface

		class TrackedInterface( InterfaceMaster.InterfaceBase ):
			def __init__( self, testinst ):
				self.test = testinst
				super( TrackedInterface, self ).__init__( )

			def testcall( self, targetcallers, targetcallerid ):
				self.test.failUnless( self.numCallers( ) == targetcallers )
				self.test.failUnless( self.callerId( ) == targetcallerid )
		# END tracked interface


		# SIMPLE INTERFACE
		#####################
		imaster = IMasterTest()
		iinst = Interface()
		imaster.setInterface( "iTest", iinst )

		self.failUnless( len( imaster.listInterfaces() ) == 1 and imaster.listInterfaces()[0] == "iTest" )
		self.failUnless( iinst == imaster.interface( "iTest" ) )
		self.failUnless( iinst == imaster.iTest )


		# del interface
		imaster.setInterface( "iTest", None )
		imaster.setInterface( "iTest", None )  # multiple
		imaster.setInterface( "iTest2", None ) # non-existing

		self.failUnlessRaises( AttributeError, getattr, imaster, "iTest" )
		self.failUnlessRaises( ValueError, imaster.interface, "iTest" )


		# NO CLASS ACCESS
		imaster.im_provide_on_instance = False
		imaster.setInterface( "iTest", iinst )

		self.failUnlessRaises( AttributeError, getattr, imaster, "iTest" )
		self.failUnless( imaster.interface( "iTest" ) == iinst )
		imaster.setInterface( "iTest", None )

		self.failUnless( len( imaster.listInterfaces( ) ) == 0 )


		# TRACKED INTERFACE
		###################
		binst = TrackedInterface( self )
		imaster.im_provide_on_instance = True
		imaster.setInterface( "iTest", binst )

		caller = imaster.interface( "iTest" )
		self.failUnless( type( caller ) == InterfaceMaster._InterfaceHandler )
		caller.testcall( 1, 0 )

		caller2 = imaster.iTest
		caller2.testcall( 2, 1 )

		caller.testcall( 2, 0 )

		del( caller2 )
		caller.testcall( 1, 0 )

		del( caller )
		self.failUnless( binst._num_callers == 0 )
		self.failUnless( binst._current_caller_id == -1 )

		imaster.setInterface( "iTest", None )
		self.failUnless( len( imaster.listInterfaces( ) ) == 0 )

	def test_choiceDialog( self ):
		c1 = "single choice"
		choice_dialog = iChoiceDialog( t = "my title", m = "my message", c = c1 )
		self.failUnless( choice_dialog.choice() == c1 )

		c2 = "other choice"
		choice_dialog = iChoiceDialog( t = "my title", m = "my message", c = (c1,c2) )
		self.failUnless( choice_dialog.choice() == c1 )

	def test_prompt( self ):
		assert iPrompt( m="Enter your name:", d="test", ct="Enter" ).prompt() == "test"

	def test_progressIndicator( self ):
		maxrange = 10
		progress = iProgressIndicator( min = 0, max = maxrange, is_relative = 1 )

		# RELATIVE ITERATION
		progress.begin()
		for i in range( maxrange ):
			progress.set( i, "my message" )
		progress.end()


		# RANGE CHECK
		progress.set( -10 )
		self.failUnless( progress.get() == 0 )

		progress.set( maxrange * 2 )
		print progress.get()
		self.failUnless( progress.get() == 100.0 )


		# ABSOLUTE ITERATION
		progress.setRelative( False )
		progress.begin()
		for i in range( maxrange ):
			progress.set( i, "my message" )
		progress.end()


		# RANGE CHECK
		progress.set( -10 )
		self.failUnless( progress.get() == 0 )

		progress.set( maxrange * 2 )
		self.failUnless( progress.get() == maxrange )

		# use setup
		progress.setup( (0,99), True, False, True )
		progress.setup( (0,99), relative=None, abortable=True, begin=False )
		# round-robin
		assert progress.roundRobin() == False
		progress.setup( (0,10), relative=False, round_robin=True)
		assert progress.roundRobin() == True
		
		# absolute 
		progress.set( 15 )
		assert progress.value() == 15
		assert progress.get() == 5
		progress.set( 10 )
		assert progress.get() == 0
		
		# relative 
		progress.setRelative(True)
		progress.set( 15 )
		assert progress.get() == 50.0
		assert progress.value() == 15
		
		
	def test_weak_inst(self):
		# we must be able to handle it in sets
		s = set()
		wif = WeakInstFunction(self.test_weak_inst)
		
		s.add(wif)
		s.add(wif)
		assert len(s) == 1
		s.remove(wif)
		assert len(s) == 0
		
		wifsame = WeakInstFunction(self.test_weak_inst)
		wifother = WeakInstFunction(self.test_callback_base)
		s.add(wif)
		s.add(wifsame)
		assert len(s) == 1
		
		s.add(wifother)
		assert len(s) == 2
		
		# a different instance is not the same function
		s = set()
		class Sender(object):
			def method(self):
				pass
		# END class 
		
		s1 = Sender()
		s2 = Sender()
		wifi1 = WeakInstFunction(s1.method)
		wifi2 = WeakInstFunction(s2.method)
		s.add(wifi1)
		s.add(wifi2)
		s.add(wifi2)
		assert len(s) == 2
		
		
	def test_callback_base(self):
		class Sender(EventSender):
			sender_as_argument = True
			
			eweak = Event(weak=True, sender_as_argument=False)
			estrong = Event(weak=False)
			eremove = Event(remove_failed=True)
			
			def needs_sender(self, sender, arg2):
				self.needs_sender_called = 1
				assert sender is self.sender()
			
			def weak_call(self):
				self.weak_call_called = 1
			
			def needs_sender2(self, sender, arg2):
				self.needs_sender_called2 = 1
				assert sender is self.sender()
				
			def weak_call2(self):
				self.weak_call_called2 = 1
			
			def error(self, *args):
				raise AssertionError("need to be removed")
			
			def make_assertion(self):
				assert hasattr(self, 'needs_sender_called')
				assert hasattr(self, 'needs_sender_called2')
				assert hasattr(self, 'weak_call_called')
				assert hasattr(self, 'weak_call_called2')
		# END test class
		
		assert len(Sender.listEventNames()) == 3
		
		# set functions
		sender = Sender()
		sender.estrong = Sender.needs_sender
		sender.estrong = Sender.needs_sender2
		assert len(sender.estrong._getFunctionSet(sender)) == 2
		
		sender.eweak = sender.weak_call
		sender.eweak = sender.weak_call2
		assert len(sender.eweak._getFunctionSet(sender)) == 2
		
		sender.eremove = sender.error
		assert len(sender.eremove._getFunctionSet(sender)) == 1
		
		# call 
		sender.estrong(1, 2)
		sender.eweak.send()
		
		sender.make_assertion()
		
		sender.eremove()
		assert len(sender.eremove._getFunctionSet(sender)) == 0
		
		# remove
		sender.estrong.remove(Sender.needs_sender)
		assert len(sender.estrong._getFunctionSet(sender)) == 1
		
		sender.eweak.remove(sender.weak_call)
		assert len(sender.eweak._getFunctionSet(sender)) == 1
		
		
		# assure deletion of sender truly removes it ( weakref check )
		sw = weakref.ref(sender)
		del(sender)
		assert sw() is None
		
		
		# clear all events
		sender = Sender()
		sender.estrong = Sender.needs_sender
		sender.clearAllEvents()
		assert not sender.estrong._getFunctionSet(sender)
		
	def test_info(self):
		assert len(info.version) == 5
		major, minor, micro, level, serial = info.version
		assert major == 1 and minor == 0 and micro == 0 and isinstance(level, basestring) and serial == 0
