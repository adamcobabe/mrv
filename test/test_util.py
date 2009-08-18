# -*- coding: utf-8 -*-
"""Test misc utility classes


@newfield revision: Revision
@newfield id: SVN Id
"""

__author__='$Author: byron $'
__contact__='byronimo <.a.t.> gmail <.> com'
__version__=1
__license__='MIT License'
__date__="$Date: 2008-05-06 12:45:38 +0200 (Tue, 06 May 2008) $"
__revision__="$Revision: 8 $"
__id__="$Id: decorators.py 8 2008-05-06 10:45:38Z byron $"
__copyright__='(c) 2008 Sebastian Thiel'


import unittest
from mayarv.util import *
import re

class TestDAGTree( unittest.TestCase ):

	def test_dagMethods( self ):
		"""mayarv.util.DAGTree: Test general methods"""
		self.tree = DAGTree( )
		self.tree.add_edge( (0,1) )
		self.tree.add_edge( (0,2) )
		self.tree.add_edge( (0,3) )
		self.tree.add_edge( (1,4) )
		self.tree.add_edge( (4,5) )

		self.failUnless( self.tree.parent( 1 ) == 0 )
		self.failUnless( self.tree.parent( 5 ) == 4 )
		self.failUnless( len( list( self.tree.parent_iter( 5 ) ) ) == 3 )

	def test_filters( self ):
		"""mayarv.util: test generalized filters"""
		# AND
		sequence = [ 1,1,1,1,0,1,1 ]
		self.failUnless( len( filter( And( bool, bool, bool ), sequence ) ) == len( sequence ) - 1 )

		sequence = [ 0, 0, 0, 0, 0, 0 ]
		self.failUnless( len( filter( And( bool ), sequence ) ) == 0 )
		self.failUnless( len( filter( And( lambda x: not bool(x) ), sequence ) ) == len( sequence ) )

		# OR
		sequence = [ 0, 0, 1 ]
		self.failUnless( len( filter( Or( bool, lambda x: not bool(x) ), sequence ) ) == 3 )

		# regex
		regex = re.compile( "\w" )
		seq = [ "%", "s" ]
		self.failUnless( len( filter( RegexHasMatch( regex ), seq ) ) == 1 )


	def test_intGenerator( self ):
		"""mayarv.util: test IntKeygenerator"""
		for i in IntKeyGenerator( [ 1,2,3 ] ):
			self.failUnless( isinstance( i, int ) )


	def test_interfaceBase( self ):
		"""mayarv.util: interface base testing of main functionality"""
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
				self.test.failUnless( self.getNumCallers( ) == targetcallers )
				self.test.failUnless( self.getCallerId( ) == targetcallerid )
		# END tracked interface


		# SIMPLE INTERFACE
		#####################
		imaster = IMasterTest()
		iinst = Interface()
		imaster.setInterface( "iTest", iinst )

		self.failUnless( len( imaster.listInterfaces() ) == 1 and imaster.listInterfaces()[0] == "iTest" )
		self.failUnless( iinst == imaster.getInterface( "iTest" ) )
		self.failUnless( iinst == imaster.iTest )


		# del interface
		imaster.setInterface( "iTest", None )
		imaster.setInterface( "iTest", None )  # multiple
		imaster.setInterface( "iTest2", None ) # non-existing

		self.failUnlessRaises( AttributeError, getattr, imaster, "iTest" )
		self.failUnlessRaises( ValueError, imaster.getInterface, "iTest" )


		# NO CLASS ACCESS
		imaster.im_provide_on_instance = False
		imaster.setInterface( "iTest", iinst )

		self.failUnlessRaises( AttributeError, getattr, imaster, "iTest" )
		self.failUnless( imaster.getInterface( "iTest" ) == iinst )
		imaster.setInterface( "iTest", None )

		self.failUnless( len( imaster.listInterfaces( ) ) == 0 )


		# TRACKED INTERFACE
		###################
		binst = TrackedInterface( self )
		imaster.im_provide_on_instance = True
		imaster.setInterface( "iTest", binst )

		caller = imaster.getInterface( "iTest" )
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
		"""mayarv.interfaces.iChoiceDialog: quick choicebox test"""
		c1 = "single choice"
		choice_dialog = iChoiceDialog( t = "my title", m = "my message", c = c1 )
		self.failUnless( choice_dialog.getChoice() == c1 )

		c2 = "other choice"
		choice_dialog = iChoiceDialog( t = "my title", m = "my message", c = (c1,c2) )
		self.failUnless( choice_dialog.getChoice() == c1 )

	def test_prompt( self ):
		"""mayarv.interfaces.iPrompt"""
		assert iPrompt( m="Enter your name:", d="test", ct="Enter" ).prompt() == "test"

	def test_progressIndicator( self ):
		"""mayarv.utils.iProgressIndicator: do some simple progress testing"""
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
