
.. _dist-workflow-label:

#####################
Distribution Workflow
#####################

Preparing a distribution at some point is as easy as running ``make release`` ( on windows it would be something like ``make-release.bat`` ). Until that point is reached though, one will have to go through an iterative setup and testing procedure which will be described here.

The workflow guide assumes that you have a default setup of your :doc:`info module <pinfo>` and :doc:`setup.py script <setup>`, and if you started from the :ref:`template project <template-project-label>` this will already be in working order. Once your project grows and you decide to distribute only parts of it, the somewhat advanced techniques described here later on will help getting good results faster.

In the following sections it will also be assumed that you made yourself familiar with the :ref:`setup.py script <setup-label>` and its general use.

*********************
Distribution Tracking
*********************
No matter what kind of distribution you are going to create, it is wise to setup good means of tracking them. The MRV distribution system supports this by integrating git, using tags, branches, and commit messages to track where each distribution came from and from which source tree it was created. 

This is vital in case patches need to be back-ported to existing releases, to mention just one example.

To enable git when creating a distribution, set the ``--use-git`` flag to 1 on the setup script.

Details about the git-handling can be found :ref:`in the setup script's documentation <setup-git-label>`.

*****************
Quality Assurance
*****************
One thing you want to do *before* most releases is to run the unit-tests in the most possible variations and on all supported platforms. In practice this won't always be possible, but MRV facilitates this through the integration of regression testing provided by the :ref:`tmrv tool <tmrvr-label>`. 

It will run all tests on all installed maya versions and report failure if one test fails.

Depending on your distribution target, you would set the ``--regression-tests`` flag to *1*.

********************
Distribution Targets
********************
The final decision would be to determine which kind of distributions you need. 

Currently there is native support for source and binary distributions, possibly distinguishing between *beta* or *final release* distributions. The first ones mentioned are less strict with their version and git tags, by allowing the program version to remain the same, by simply moving the same tag around. This can be accomplished by the ``--force-git-tag`` distribution flag.

The documentation usually needs to be build from an intermediate markup language, which is accomplished by :doc:`makedoc <docs>`, hence it an own distribution target.

Each distribution target usually ends up in one compressed archive and possibly in a dedicated git branch to connect it to previous versions of the respective distribution target.

All of these targets can be combined freely according to your needs.

***********************
The Source Distribution
***********************
This kind of distribution is the most complex as it :ref:`turns out <setup-intimacies-label>`, and starts by creating a MANIFEST.in file.

With it you define the exact set of files to distribute.

Once you are sure about the set of files to include in your source distribution, adjust your :ref:`Manifest Template <setup-manifestin-label>` accordingly.

The following command will prepare a source distribution and create a zip archive from it::
    
    $ python setup.py sdist --format=zip
    
You will find the zip archive in the ``dist`` folder. But is this source distribution complete ? Are all files included that the project needs to run ?

To verify that it is operational, it is required to re-run the unit-tests, using the given maya version::
    
    $ python setup.py sdist --format=zip --post-testing=2011
    
If that works as well, you have a good indication that you are ready to proceed to the next step, `The Binary Distribution`_, which is required if you would like the user to be able to automatically install your project into his python installation. It is somewhat unfortunate that you can't just go with the working source package.

Please note that the commandline presented here represented the bare minimum, one which might be more suitable for final releases would look more like this::
    
    $ python setup.py --use-git=1 --regression-tests=1 sdist --format=zip --post-testing=8.5,2011 --root-remotes=origin --dist-remotes=distro,hubdistro
    
The preceding command tells the distribution system to run all regression tests, setup a git tag in your root repository with the proper version number, create a source distribution, run all unit tests in that distribution for maya 8.5 and 2011, to finally push the tagged changes in the root repository ( containing your sources ) to the remote named *origin*, and the tagged distribution data itself to the remotes named *distro* and *hubdistro*.

***********************
The Binary Distribution
***********************
This step is required if you want to make your distribution installable, or if you don't want to distribute the sources of your project. In the latter case please keep in mind that you will have to byte-compile for each minor version of the python interpreter, each interpreter represents a separate distribution target.

If you are coming from `The Source Distribution`_, you were used to simple and straightforward definition of the files and folders to distribute. This nice time might be over now, depending on the complexity of your project of course.

The cause of this is mainly the lack of something like the MANIFEST template, hence the files to ``build`` need to be specified using keyword arguments given to the ``setup()`` routine of your *setup.py* script.

This information is bundled in the ``setup_kwargs`` member variable in your :doc:`info module <pinfo>`. Here it is best to have a look at *MRV*\ s well documented version of this file. 

Generally, you have to watch out for the following:

* If you have scripts that should end up as executables on the target system, specify them in the ``scripts`` keyword.
* If you have modules that require additional data, specify the data files using the ``package_data`` keyword.
* If you have additional (external) packages outside of the default ``ext`` directory, provide the ``package_search_dirs`` keyword which expects a list of relative directories.
* Specific setup subcommands are fed directly with the ``options`` keyword
 
 * To exclude specific modules from byte-compilation, list patterns in the ``exclude_from_compile`` keyword of the ``build_py`` command.
 * To exclude packages, modules and data files from being included in the build, list the modules in the ``exclude_items`` keyword of the ``build_py`` command.
 * To prevent scripts you previously supplied in the ``scripts`` keyword from being installed, mention their paths in the ``exclude_scripts`` keyword of the ``build_scripts`` command.
 
* ... and if none of the mentioned issues apply to your project, you can as well continue without a change.

Now you would execute a simple build and go back and forth between your ``info module`` configuration and the execution of this line until the unit-tests succeed and the distribution as contained in the ``build`` directory passes your visual examination::
    
    $ python setup.py --maya-version=2011 build build_py--compile
    
The specified ``--maya-version`` indicates the target platform and is required whenever you want to compile your sources, which is optional by the way. Specifying build first makes sure we get a complete build of everything, while telling ``build_py`` to compile the sources. Its hard to know which subcommands are executed implicitly without studying the sources of the distutils or without trying to get smart from studying the scattered `distutils`_ documentation.

Once everything appears to be okay, you are free to produce optimized byte code to have smaller files ( as docstrings will be stripped ), which will automatically exclude the unit test library::
    
    $ python setup.py --maya-version=2011 build build_py--optimize=2

A fully upgraded binary distribution could look like this::
    
    $ python setup.py --use-git=1 --regression-tests=1 build build_py --compile --post-testing=8.5,2011 --root-remotes=origin --dist-remotes=distro,hubdistro bdist bdist_dumb --format=zip
    
The given commandline will create a full build into the ``build`` subdirectory, ``build_py`` byte-compiles the sources and deletes the source files afterwards. The directory contents will be picked up by ``bdist`` to be put into an archive which will extract into the right spot of your platform. ``bdist`` allows to specify other target platforms as well, as to be read in the `official bdist documentation <http://docs.python.org/distutils/builtdist.html>`_. 

******************************
The Documentation Distribution
******************************
The documentation needs to be built as well, and there is a specialized command which does exactly that by calling ``./doc/makedoc`` ( or whatever you have specified in your ``info module`` ).

To be sure the documentation reflects the modules actually used in your source or binary distribution, use the ``--from-build-version`` flag. If your distribution does not omit any files, it is usually alright to create ( and possibly reuse ) documentation in your root project which happens if the said flag is not specified.

A basic example would be::
    
    $ python setup.py sdist docdist --from-build-version

The doc-distribution can also be combined with the source or the binary distribution, just append the ``docdist`` part presented here to the commandlines shown in the preceding sections.

**************************
Verifying the Installation
**************************
If you were following the previous steps, you have two or three zip files ( and a bunch of new commits in your root and distribution repositories ). These zip files correspond to the source-, the binary- and the documentation distribution. 

Now one has to verify that these packages actually install correctly. For the sake of brevity, we skip 'dumb' binary- and documentation installations as these just extract into place, but focus on the source distribution which has to be installed using your very own setup.py script that previously created the distribution package.

=========
Distutils
=========
To test the source distribution with the `distutils`_, we need to extract it into place, change directory into it to execute the following line::
    
    $ python setup.py install --prefix=install
    
The purpose of this test is to see whether the script succeeds - if it does the ``install`` subdirectory will contain our scripts and modules, by default these have been precompiled to byte-code with the interpreter that ran the setup script. Internally it uses ``build_py`` which we already verified to produce a consistent distribution in a prior step, hence it is not strictly required to rerun the unit tests.

=========================
Setuptools (easy_install)
=========================
Another way to install an archive is by using `easy_install`_. For the end-user, this is a much more convenient way of installing a package, provided that you have uploaded it to the `Python Package Index`_ before, allowing lines like these::
    
    $ easy_install your_project
    
Internally, the ``ez_setup`` implementation will call ``setup.py install``. One could assume that it will work if your ``distutil`` installation worked, but this is not necessarily true.

Easy_install runs your installation routine within a sandboxed environment that restricts certain operation that try to alter files outside of the installation directory. Unfortunately the implementation does not provide the exact signatures of common ``os`` methods, which in turn could cause your script to fail even though you didn't try anything 'forbidden'.

The following commandline tells easy_install not to use pypi, but instead to use your package directly from the ``dist`` directory with your distribution archives. Please note that it will install the package in your system, hence you need root permissions and to possibly manually remove the installed egg afterwards.::
    
    $ easy_install<-py-version> --allow-hosts None --find-links dist your_project
    
Where <``-py-version``> is the python version you want to use for the installation. If the installation succeeds, you should be able to use your package and scripts right away in an interactive python session::
    
    $ python<py-version>
    $ >>> import your_project
    
===========================
Multi-Platform Verification
===========================
If you are handling paths a lot and manipulate them, or in short, use plenty of operating system facilities, it is vital to make sure your installation works on other platforms as well. 

If feasible, run your unit-tests on all supported platforms and try the installation yourself. Usually, the first time you try it on another system, it won't work, but is fixable with trivial patches. It good though that you find out about it before the end-user does.

If software doesn't work right after the installation, the first impression of "your project is not working" is hard to get rid of later.

**********
Automation
**********
Once the actual commandlines have been figured out and are definitely working, its just about aliasing them to make their execution easy. 

On Linux, the simplest way is to write a *makefile* which contains a few phony targets, this way you can easily choose the distribution targets like::
    
    $ make preview
    $ make beta-release
    $ make final-release
    $ make binary-release
    
Writing shell scripts would be possible as well, its up to your personal preference.

On Windows, one might want to resort to writing batch files which serve as an alias, allowing to write something like::
    
    $ make-preview.bat
    $ make-beta-release.bat
    $ make-final-release.bat
    $ make-binary-release.bat
    
.. note:: It is very recommended to maintain targets which are for release-testing only, hence the do not interact with git. This is especially important in the case of the ``--post-testing`` flag as it will always do the testing *after* the changes were pushed to the git repositories, and if the test fails, the changes possibly already reached the public repository. A good insurance against post-testing failures are pre-distribution regression tests, but as these apply to a possibly different file set, post-testing might still fail.
    
************************
The Python Package Index
************************
The `Python Package Index`_ helps you to store your release archives in a central place, which makes it available to ``easy_install`` automatically. Additionally it provides a spot for your static html documentation, the zip archive ``docdist`` creates can be uploaded with just one click.

.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _distutils: http://docs.python.org/distutils
.. _Python Package Index: http://pypi.python.org/pypi
