#######
License
#######

********
Software
********
This software is licensed under the **New BSD License**. A version for human beings with translations into many languages can be found here: http://creativecommons.org/licenses/BSD:

Copyright (c) 2009-2010, `Sebastian Thiel <http://de.linkedin.com/in/sebastianthiel>`_
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of the <organization> nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SEBASTIAN THIEL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Other Software Licenses
=======================
The following parts of the software are derived or taken from other software packages. These software packages, including their license, are listed here together with the names of the used entities. Within the source code, these entities contain a comment indicating their origin.

PyMel
-----
``PyMel`` is licensed under the ``New BSD License`` ( http://creativecommons.org/licenses/BSD )
 * mrv.util.uncapitalize ``( code copy )``
 * mrv.maya.util.Mel ``( copy + customizations )``
 * mrv.maya.util.OptionVarDict ``( copy +  modifications )``
 
 
Submodules
==========
The following projects are used by MRV as a submodule.
 
NetworkX
--------
`NetworkX <http://networkx.lanl.gov>`_ is licensed under the ``BSD License`` ( http://networkx.lanl.gov/reference/legal.html ).

.. note:: Truncated to the modules actually used by MRV to speed up loading times - networkX imports everything into the root package.

Pydot
-----
`Pydot <http://code.google.com/p/pydot/>`_ is licensed under the ``MIT License`` ( http://www.opensource.org/licenses/mit-license.php ).

Pyparsing
---------
`Pyparsing <http://pyparsing.wikispaces.com>`_ is licensed under the ``MIT License`` ( http://www.opensource.org/licenses/mit-license.php ).

 
*************
Documentation
*************
This work is licensed under the Creative Commons Attribution 3.0 Germany License. To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/de/ or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.

##############
Special Thanks
##############
The following people, countries and tools are mentioned because they helped during the development of the project in one way or another:

* The people I worked with in Stockholm, who waited patiently for 3 months until the first actual feature came out of me - this is the time it took to get the first MRV version ready for their pipeline.
 
 * ``Sweden`` in general as its quite a dark and cold country most of the year making it easy to live in the office. Yes, thanks to Sweden :) ! 
 
* ``Martin Freitag``, who survived having me as a colleague and teacher, and generously converted his beloved AnimIO from MEL to MRV, providing it as a first demo tool from which others might be able to learn something.
 
* ``PyMel`` for being a source of inspiration and for hinting me at more advanced python techniques without which MRV wouldn't be possible.
  
* ``Python`` for being such a flexible and sometimes mind-bending language especially if you come from statically typed languages like C++, and for forcing me into Test-Driven-Development as MRV would be totally unreliable without it.
