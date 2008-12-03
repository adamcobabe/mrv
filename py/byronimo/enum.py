# -*- coding: utf-8 -*-
"""B{byronimo.enum}
This module is designed to be the equivalent of the enum type in other
languages. An enumeration object is created at run time, and contains
named members that are the enumeration elements.

The enumeration is also a tuple of all of the values in it. You can iterate
through the values, perform 'in' tests, slicing, etc. It also includes
functions to lookup specific values by name, or names by value.

You can specify your own element values, or use the create factory method
to create default Elements. These elements are unique system wide, and are
ordered based on the order of the elements in the enumeration. They also
are _repr_'d by the name of the element, which is convenient for testing,
debugging, and generation text output.

Example Code:

# Using Element values
Colors = Enumeration.create('red', 'green', 'blue')

# Using explicitly specified values
Borders = Enumeration.create(('SUNKEN', 1),
							 ('RAISED', 32),
							 ('FLAT', 2))

x = Colors.red
y = Colors.blue

assert x < y
assert x == Colors('red')
assert Borders.FLAT == 2:
assert 1 in Borders

@note: slightly modified by Sebastian Thiel
@newfield revision: Revision
@newfield id: SVN Id
"""
__author__='Don Garret'
__contact__='garret at bgb dot cc'
__version__=1
__license__='freeware'
__date__="$Date: 2008-05-29 02:30:46 +0200 (Thu, 29 May 2008) $"
__revision__="$Revision: 16 $"
__id__="$Id:$"
__copyright__='(c) 2003 Don Garret'

class Element(object):
	"""Internal helper class used to represent an ordered abstract value.
	   
	The values have string representations, have strictly defined ordering
	(inside the set) and are never equal to anything but themselves.
	
	They are usually created through the create factory method as values
	for Enumerations.

	They assume that the enumeration member will be filled in before any
	comparisons are used. This is done by the Enumeration constructor.
	"""
	# we do not define slots to stay pickable ( without reimplementing things )
	def __init__(self, name, value):
		self.__name = name
		self.__value = value
		self.enumeration = None # Will be filled in later
		
	def __repr__(self):
		return self.__name

	def __cmp__(self, other):
		"""We override cmp only because we want the ordering of elements
		in an enumeration to reflect their position in the enumeration.
		"""
		if (self.__class__ == other.__class__ and
			self.enumeration is other.enumeration):
			# If we are both elements in the same enumeration, compare
			#	values for ordering
			return cmp(self.__value, other.__value)
		else:
			# Otherwise, fall back to the default
			return NotImplemented
			
	def getValue( self ):
		"""@return: own value - it is strictly read-only"""
		return self.__value
		

class Enumeration(tuple):
	"""This class represents an enumeration. You should not normally create
	multiple instances of the same enumeration, instead create one with
	however many references are convenient.

	The enumeration is a tuple of all of the values in it. You can iterate
	through the values, perform 'in' tests, slicing, etc. It also includes
	functions to lookup specific values by name, or names by value.

	You can specify your own element values, or use the create factory method
	to create default Elements. These elements are unique system wide, and are
	ordered based on the order of the elements in the enumeration. They also
	are _repr_'d by the name of the element, which is convenient for testing,
	debugging, and generation text output.
	
	@note: pickling this class with Elements will fail as they contain cyclic 
	references that it cannot deal with
	@todo: implement proper pickle __getstate__ and __setstate__ that deal with 
	that problem
	"""
	_slots_ = ( "_nameMap", "_valueMap" )

	def __new__(self, names, values):
		"""This method is needed to get the tuple parent class to do the
		Right Thing(tm). """
		return tuple.__new__(self, values)

	def __setattr__( self, name, value ):
		"""Do not allow to change this instance"""
		if name in self._slots_:
			return super( Enumeration, self ).__setattr__( name, value )
			
		raise AttributeError( "No assignments allowed" )

	def __getattr__( self , attr ):
		"""Prefer to return value from our value map"""
		try:
			return self.valueFromName( attr )
		except KeyError:
			raise AttributeError( "Element %s is not part of the enumeration" % attr )
	

	def __init__(self, names, values):
		"""The arguments needed to construct this class are a list of
		element names (which must be unique strings), and element values
		(which can be any type of value). If you don't have special needs,
		then it's recommended that you use Element instances for the values.

		This constructor is normally called through the create factory (which
		will create Elements for you), but that is not a requirement.
		"""

		assert len(names) == len(values)

		# We are a tuple of our values, plus more....
		tuple.__init__(self, values)

		self._nameMap = {}
		self._valueMap = {}


		for i in xrange(len(names)):
			name = names[i]
			value = values[i]

			# Tell the elements which enumeration they belong too
			if type(value) == Element:
				value.enumeration = self
			
			# Prove that all names are unique
			assert not name in self._nameMap

			# create mappings from name to value, and vice versa
			self._nameMap[name] = value
			self._valueMap[value] = name


	def _initSelfWithNamesAndValues( self, names, values ):
		"""Initilize our maps"""


	def valueFromName(self, name):
		"""Look up the enumeration value for a given element name.
		"""
		return self._nameMap[name]
		
	def nameFromValue(self, value):
		"""Look up the name of an enumeration element, given it's value.
			
		If there are multiple elements with the same value, you will only
		get a single matching name back. Which name is undefined.
		"""
		return self._valueMap[value]
		
	def _nextOrPrevious( self, element, direction, wrap_around ):
		"""do-it method, see L{next} and L{previous}
		@param direction: -1 = previous, 1 = next """
		curindex = -1
		for i,elm in enumerate( self ):
			if elm == element:
				curindex = i
				break
			# END if elms match
		# END for each element 
		
		assert curindex != -1
		
		nextindex = curindex + direction
		validnextindex = nextindex
		
		if nextindex >= len( self ):
			validnextindex = 0 
		elif nextindex < 0:
			validnextindex = len( self ) - 1
		
		if not wrap_around and ( validnextindex != nextindex ):
			raise ValueError( "'%s' has no element in direction %i" % ( element, direction ) )
			
		return self[ validnextindex ]
		
	
	def next( self, element, wrap_around = False ):
		"""@return: element following after given element
		@param element: element whose successor to return
		@param wrap_around: if True, the first Element will be returned if there is 
		no next element
		@raise ValueError: if wrap_around is False and there is no next element"""
		return self._nextOrPrevious( element, 1, wrap_around )
		
	def previous( self, element, wrap_around = False ):
		"""@return: element coming before the given element
		@param element: element whose predecessor to return 
		@param wrap_around: see L{next}
		@raise ValueError: if wrap_around is False and there is no previous element"""
		return self._nextOrPrevious( element, -1, wrap_around )
		
	
	#{ Pickle Protocol  
	def __getnewargs__( self ):
		"""Allows us to properly recreate ourselves"""
		print "CALLLED ME"
		return self._nameMap.keys(), self._valueMap.keys()
	#} END pickle protocol 
			
	
	__call__ = valueFromName
	


def create(*elements, **kwargs ):
	"""Factory method for Enumerations. Accepts of list of values that
	can either be strings or (name, value) tuple pairs. Strings will
	have an Element created for use as their value.

	Example:  Enumeration.create('fred', 'bob', ('joe', 42))
	Example:  Enumeration.create('fred', cls = EnumerationSubClass )
	
	@param cls: The class to create an enumeration with, must be an instance of 
	Enumeration
	@param elmcls: The class to create elements from, must be instance of Element
	"""
	cls = kwargs.get( "cls", Enumeration )
	elmcls = kwargs.get( "elmcls", Element )
	
	assert Enumeration in cls.mro()
	assert Element in elmcls.mro()
	
	names = []
	values = []

	for element in elements:
		if type(element) == tuple:
			assert len(element) == 2
			
			names.append(element[0])
			values.append(element[1])

		elif type(element) in (str, unicode):
			values.append(Element(element, len(names)))		# zero based ids 
			names.append(element)
				
		else:
			raise "Unsupported element type"

	return cls( names, values )

