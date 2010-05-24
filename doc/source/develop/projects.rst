
.. _template-project-label:

####################
The Template Project
####################

As MRV calls itself a 'Development Framework', it must be simple to create new tools based upon it. The template project gives you a kick-start to do exactly that.

At this stage, the template project itself is still to be created, however, there is a demo project from which it will be derived one day - its called `AnimIO <http://gitorious.org/animio>`_  by Martin Freitag, and allows to export and import animation of nodes.

AnimIO was initially created as MEL script, which makes it especially interesting to see it re-implemented in python, using an Object-Based design and TDD.

The interested reader may have a look at its code. After cloning the repository at http://gitorious.org/animio ( ``git clone`` ), it is required to recursively initialize the submodules ( ``git submodule update --init --recursive`` ). Now you would be ready to run the tests. To sum it up::
	
	$ git clone git://gitorious.org/animio/mainline.git animio
	$ cd animio
	$ git submodule update --init --recursive
	
	$ # Test the library
	$ ext/mrv/test/bin/tmrv [<maya version>]
	
	$ # Test the performance
	$ ext/mrv/test/bin/tmrv [<maya version>] test/performance
	
	$ # Test the user interface
	$ ext/mrv/test/bin/tmrv [<maya version>] --mrv-maya test/ui
	

*********
TODO
*********

* About info module, link to distribute documentation
* Explain which release type to use, distributed source or developer version
* Provide examples for different setup file configurations, including proper binary distribution with mrv post-testing support, and mrv source distribution with post-testing support.
