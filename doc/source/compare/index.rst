
###################
Comparison to PyMel
###################
MRV is not the first attempt to make the use of Python within Maya more convenient. PyMel is an excellent feature packed Framework which is, as the name suggests,  more closely affiliated to MEL than to the Maya API, but which allows you to  access the latter one as well.

Wherever applicable, tables have been used. Otherwise a numbered list is provided which allows to match the respective list items one on one. If list items are  presented in an unnumbered fashion, they indicate a feature which is exclusive to the respective framework or cannot be compared because its too different after all.

.. note:: The following comparison was created solely based on a single person's judgment, a person which also happens to be the author of MRV. This is why the comparison may be biased towards MRV, miss important features of PyMel or may even be wrong in parts due to an insufficient insight into the PyMel project. The author does not intent to postulate any outrageously incorrect statements, and will be glad to make adjustments if necessary.


********
Ideology
********
Both projects have been created with a certain idea in mind

**PyMel**: 
	#. PyMEL originally builds on the cmds module and allows access to compatible MFn methods as well as respective MEL methods which can be accessed in an object oriented manner.
	#. PyMEL uses MEL semantics.
	#. PyMEL is as convenient and easy-to-use as possible, hiding details about the MayaAPI even if it is used. Direct operation of the MayaAPI is not intended.
	#. Smart methods which take multiple of input types make its use easier and more intuitive.
	#. Type-Handling should be convenient.
	

**MRV**
	#. MRV builds on the MayaAPI and allows access to compatible MFn methods in an object oriented manner. The cmds module is not handled at all.
	#. MRV uses MayaAPI semantics.
	#. MRV wants to make using the MayaAPI more productive, trying to keep its own impact on performance as low as possible. It is possible and  valid to operate on the native MayaAPI if beneficial for performance.
	#. Specialized methods take very specific input types. There are some general functions which support multiple input types to ease interactive use.
	#. Type-Handling should be explicit.
	
********
In Depth
********

.. toctree::
   :maxdepth: 2
   
   features
   performance
   usage
   
   
