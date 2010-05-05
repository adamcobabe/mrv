
***************
Making Releases
***************
Although there is a build and release system, at the time of writing ( |today| ), it was not used to create the release you have. It will be revised and documented for 1.0.0.


Building Docs
=============
Currently, building of the full documentation requires sphinx and epydoc to be installed in your python interpreter. 

If that is the case, the following line will build the docs you are currently reading, in the version you have checked out locally::
	
	$ cd doc
	$ makedoc
	
	$ # to redo existing docs from scratch
	$ makedoc --clean
	$ makedoc

The built documentation can be found in ``mrv/doc/build/html``.

